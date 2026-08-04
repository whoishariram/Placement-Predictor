"""
Placement Predictor - Admin Authentication Module
Handles admin login, session management, and admin user management
"""

import hashlib
import os
import re
import secrets
from datetime import datetime, timedelta


class AdminAuth:
    """
    Admin authentication system

    Handles:
    - Admin Login
    - Session Validation
    - Admin User Management (CRUD)
    - Activity Logging
    """

    def __init__(self, db_session=None, admin_model=None, activity_log_model=None,
                 config=None):
        """
        Initialize admin authentication

        Args:
            db_session: SQLAlchemy database session
            admin_model: Admin model class
            activity_log_model: ActivityLog model class
            config: Configuration object
        """
        self.db = db_session
        self.Admin = admin_model
        self.ActivityLog = activity_log_model
        self.config = config or self._get_default_config()
        self.admin_sessions = {}  # In-memory session store

    def _get_default_config(self):
        """Get default configuration"""
        class DefaultConfig:
            SECRET_KEY = 'admin-secret-key-change-in-production'
            SESSION_TIMEOUT_HOURS = 8

        return DefaultConfig()

    def _generate_token(self) -> str:
        """Generate a secure random session token"""
        return secrets.token_hex(48)

    # Password hashing is delegated to the Admin model's set_password()/check_password()
    # to ensure consistency with database-backed credential storage.

    def _log_activity(self, admin_id: int, action: str, details: str = None,
                      ip_address: str = None):
        """Log admin activity"""
        if self.db and self.ActivityLog:
            try:
                log = self.ActivityLog(
                    user_type='admin',
                    user_id=admin_id,
                    action=action,
                    details=details,
                    ip_address=ip_address
                )
                self.db.session.add(log)
                self.db.session.commit()
            except Exception:
                self.db.session.rollback()

    # ============================================================
    # LOGIN
    # ============================================================

    def login(self, username: str, password: str, ip_address: str = None) -> dict:
        """
        Authenticate an admin user

        Args:
            username: Admin username
            password: Plain text password
            ip_address: Optional IP address for logging

        Returns:
            Dict with status and session data or error
        """
        if not username or not password:
            return {'status': 'error', 'message': 'Username and password are required'}

        if not self.db or not self.Admin:
            return self._default_admin_login(username, password)

        try:
            # Find admin by username or email
            admin = self.Admin.query.filter(
                (self.Admin.username == username.strip()) |
                (self.Admin.email == username.strip().lower())
            ).first()

            if not admin:
                return {'status': 'error', 'message': 'Invalid credentials'}

            # Verify password
            if not admin.check_password(password):
                return {'status': 'error', 'message': 'Invalid credentials'}

            # Update last login
            admin.last_login = datetime.utcnow()
            self.db.session.commit()

            # Generate session
            token = self._generate_token()
            session_expires = datetime.utcnow() + timedelta(
                hours=self.config.SESSION_TIMEOUT_HOURS
            )

            session_data = {
                'admin_id': admin.id,
                'username': admin.username,
                'email': admin.email,
                'role': 'admin',
                'token': token,
                'expires_at': session_expires.isoformat(),
                'last_login': admin.last_login.isoformat() if admin.last_login else None
            }

            # Store session
            self.admin_sessions[token] = {
                'admin_id': admin.id,
                'username': admin.username,
                'expires_at': session_expires
            }

            # Log activity
            self._log_activity(admin.id, 'login', 'Admin logged in', ip_address)

            return {
                'status': 'success',
                'message': f'Welcome, Admin {admin.username}! 👋',
                'admin': session_data,
                'token': token
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Login failed: {str(e)}'
            }

    def _default_admin_login(self, username: str, password: str) -> dict:
        """
        Fallback login when database is not configured

        Uses hardcoded default admin credentials
        """
        if username == 'admin' and password == 'admin123':
            token = self._generate_token()
            return {
                'status': 'success',
                'message': 'Welcome, Admin! 👋',
                'admin': {
                    'admin_id': 1,
                    'username': 'admin',
                    'email': 'admin@placementpredictor.com',
                    'role': 'admin',
                    'token': token
                },
                'token': token
            }
        return {'status': 'error', 'message': 'Invalid credentials'}

    # ============================================================
    # SESSION MANAGEMENT
    # ============================================================

    def validate_session(self, token: str) -> dict:
        """
        Validate an admin session token

        Args:
            token: Session token

        Returns:
            Dict with validation result
        """
        if not token:
            return {'valid': False, 'message': 'No token provided'}

        # Check in-memory sessions
        if token in self.admin_sessions:
            session = self.admin_sessions[token]
            if datetime.utcnow() > session['expires_at']:
                del self.admin_sessions[token]
                return {'valid': False, 'message': 'Session expired'}

            return {
                'valid': True,
                'message': 'Session valid',
                'admin_id': session['admin_id'],
                'username': session['username'],
                'role': 'admin'
            }

        # Fallback: basic token format validation
        if len(token) >= 20:
            return {'valid': True, 'message': 'Session valid', 'role': 'admin'}

        return {'valid': False, 'message': 'Invalid session'}

    def logout(self, token: str) -> dict:
        """
        Invalidate an admin session

        Args:
            token: Session token

        Returns:
            Dict with status
        """
        admin_id = None
        if token in self.admin_sessions:
            admin_id = self.admin_sessions[token]['admin_id']
            del self.admin_sessions[token]

        if admin_id:
            self._log_activity(admin_id, 'logout', 'Admin logged out')

        return {
            'status': 'success',
            'message': 'Logged out successfully'
        }

    # ============================================================
    # ADMIN USER MANAGEMENT
    # ============================================================

    def create_admin(self, current_admin_id: int, data: dict) -> dict:
        """
        Create a new admin user (requires existing admin privileges)

        Args:
            current_admin_id: ID of admin creating the new admin
            data: Dict with username, email, password

        Returns:
            Dict with status
        """
        if not self.db or not self.Admin:
            return {'status': 'error', 'message': 'Database not configured'}

        required = ['username', 'email', 'password']
        for field in required:
            if field not in data or not str(data.get(field, '')).strip():
                return {'status': 'error', 'message': f'{field.title()} is required'}

        # Validate password strength
        if len(data['password']) < 6:
            return {'status': 'error', 'message': 'Password must be at least 6 characters'}

        # Check for existing admin
        existing = self.Admin.query.filter(
            (self.Admin.username == data['username'].strip()) |
            (self.Admin.email == data['email'].strip().lower())
        ).first()

        if existing:
            if existing.username == data['username'].strip():
                return {'status': 'error', 'message': 'Username already exists'}
            return {'status': 'error', 'message': 'Email already registered'}

        try:
            admin = self.Admin(
                username=data['username'].strip(),
                email=data['email'].strip().lower()
            )
            admin.set_password(data['password'])
            self.db.session.add(admin)
            self.db.session.commit()

            self._log_activity(
                current_admin_id, 'create_admin',
                f'Created admin: {admin.username}'
            )

            return {
                'status': 'success',
                'message': f'Admin {admin.username} created successfully'
            }

        except Exception as e:
            self.db.session.rollback()
            return {'status': 'error', 'message': f'Failed to create admin: {str(e)}'}

    def change_password(self, admin_id: int, current_password: str,
                        new_password: str) -> dict:
        """
        Change admin password

        Args:
            admin_id: Admin user ID
            current_password: Current password
            new_password: New password

        Returns:
            Dict with status
        """
        if not self.db or not self.Admin:
            return {'status': 'error', 'message': 'Database not configured'}

        if not current_password or not new_password:
            return {'status': 'error', 'message': 'Current and new password required'}

        if len(new_password) < 6:
            return {'status': 'error', 'message': 'New password must be at least 6 characters'}

        try:
            admin = self.Admin.query.get(admin_id)
            if not admin:
                return {'status': 'error', 'message': 'Admin not found'}

            if not admin.check_password(current_password):
                return {'status': 'error', 'message': 'Current password is incorrect'}

            admin.set_password(new_password)
            self.db.session.commit()

            self._log_activity(admin_id, 'change_password', 'Password changed')

            return {
                'status': 'success',
                'message': 'Password changed successfully 🔑'
            }

        except Exception as e:
            self.db.session.rollback()
            return {'status': 'error', 'message': f'Failed: {str(e)}'}

    def get_admin_profile(self, admin_id: int) -> dict:
        """
        Get admin profile

        Args:
            admin_id: Admin user ID

        Returns:
            Dict with admin profile
        """
        if not self.db or not self.Admin:
            return {
                'status': 'success',
                'admin': {
                    'id': 1,
                    'username': 'admin',
                    'email': 'admin@placementpredictor.com'
                }
            }

        try:
            admin = self.Admin.query.get(admin_id)
            if not admin:
                return {'status': 'error', 'message': 'Admin not found'}

            return {'status': 'success', 'admin': admin.to_dict()}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def get_all_admins(self) -> dict:
        """
        Get all admin users

        Returns:
            Dict with list of admins
        """
        if not self.db or not self.Admin:
            return {'status': 'success', 'admins': []}

        try:
            admins = self.Admin.query.all()
            return {
                'status': 'success',
                'admins': [a.to_dict() for a in admins]
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    # ============================================================
    # UTILITY
    # ============================================================

    def get_session_stats(self) -> dict:
        """
        Get active session statistics

        Returns:
            Dict with session stats
        """
        now = datetime.utcnow()
        active_sessions = [
            s for s in self.admin_sessions.values()
            if s['expires_at'] > now
        ]

        return {
            'total_sessions': len(self.admin_sessions),
            'active_sessions': len(active_sessions),
            'expired_sessions': len(self.admin_sessions) - len(active_sessions)
        }

    def cleanup_expired_sessions(self):
        """Remove expired sessions from memory"""
        now = datetime.utcnow()
        expired = [
            token for token, session in self.admin_sessions.items()
            if session['expires_at'] <= now
        ]
        for token in expired:
            del self.admin_sessions[token]
        return len(expired)


def login_admin(username: str, password: str, db_session=None,
                admin_model=None) -> dict:
    """
    Convenience function for admin login

    Args:
        username: Admin username
        password: Plain text password
        db_session: SQLAlchemy session
        admin_model: Admin model

    Returns:
        Dict with result
    """
    auth = AdminAuth(db_session, admin_model)
    return auth.login(username, password)


if __name__ == '__main__':
    print("=" * 60)
    print("🔐 ADMIN AUTHENTICATION TEST")
    print("=" * 60)

    # Initialize auth system
    auth = AdminAuth()

    # Test default admin login
    print("\n📝 Testing Default Admin Login...")
    result = auth.login('admin', 'admin123')
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    token = result.get('token', '')

    # Test session validation
    print("\n🔑 Testing Session Validation...")
    validation = auth.validate_session(token)
    print(f"   Valid: {validation.get('valid', False)}")
    print(f"   Role: {validation.get('role', 'N/A')}")

    # Test invalid login
    print("\n❌ Testing Invalid Login...")
    result = auth.login('admin', 'wrongpassword')
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")

    # Test logout
    print("\n🚪 Testing Logout...")
    result = auth.logout(token)
    print(f"   Status: {result['status']}")

    print("\n" + "=" * 60)
    print("✅ ADMIN AUTH TEST COMPLETE")
    print("=" * 60)
