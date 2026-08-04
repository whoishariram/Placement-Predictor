"""
Placement Predictor - Student Authentication Module
Handles student registration, login, forgot password, and session management
"""

import hashlib
import os
import re
import json
import secrets
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText


class StudentAuth:
    """
    Student authentication system

    Handles:
    - Student Registration
    - Student Login
    - Forgot Password
    - Password Reset
    - Session Token Management
    """

    def __init__(self, db_session=None, student_model=None, config=None):
        """
        Initialize student authentication

        Args:
            db_session: SQLAlchemy database session
            student_model: Student model class
            config: Configuration object
        """
        self.db = db_session
        self.Student = student_model
        self.config = config or self._get_default_config()
        self.reset_tokens = {}  # In-memory token store (use DB in production)

    def _get_default_config(self):
        """Get default configuration"""
        class DefaultConfig:
            SECRET_KEY = 'default-secret-key-change-in-production'
            MAIL_SERVER = 'smtp.gmail.com'
            MAIL_PORT = 587
            MAIL_USE_TLS = True
            MAIL_USERNAME = ''
            MAIL_PASSWORD = ''
            MAIL_DEFAULT_SENDER = 'placement.predictor@edu.in'

        return DefaultConfig()

    def _generate_token(self) -> str:
        """Generate a secure random token"""
        return secrets.token_hex(48)

    # Password hashing is delegated to the Student model's set_password()/check_password()
    # to ensure consistency with database-backed credential storage.

    # ============================================================
    # INPUT VALIDATION
    # ============================================================

    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email.strip()))

    def validate_password_strength(self, password: str) -> tuple:
        """
        Validate password strength

        Returns:
            Tuple of (is_valid, message)
        """
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"

        if len(password) > 128:
            return False, "Password must be less than 128 characters"

        # Check for at least one uppercase, one lowercase, one digit
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))

        if not (has_upper and has_lower and has_digit):
            return False, "Password must contain uppercase, lowercase, and digit"

        return True, "Password is strong"

    def validate_student_data(self, data: dict) -> list:
        """
        Validate student registration data

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Required fields
        required_fields = ['student_id', 'name', 'email', 'password']
        for field in required_fields:
            if field not in data or not str(data.get(field, '')).strip():
                errors.append(f"{field.replace('_', ' ').title()} is required")

        if errors:
            return errors

        # Email validation
        if not self.validate_email(data['email']):
            errors.append("Invalid email format")

        # Password validation
        valid, msg = self.validate_password_strength(data['password'])
        if not valid:
            errors.append(msg)

        # Student ID format (alphanumeric)
        if not re.match(r'^[A-Za-z0-9_-]+$', str(data['student_id'])):
            errors.append("Student ID must be alphanumeric (letters, numbers, hyphens, underscores)")

        # Validate optional fields if present
        if 'cgpa' in data and data['cgpa']:
            try:
                cgpa = float(data['cgpa'])
                if cgpa < 0 or cgpa > 10:
                    errors.append("CGPA must be between 0 and 10")
            except ValueError:
                errors.append("Invalid CGPA value")

        if 'year' in data and data['year']:
            try:
                year = int(data['year'])
                if year < 1 or year > 6:
                    errors.append("Year must be between 1 and 6")
            except ValueError:
                errors.append("Invalid year value")

        return errors

    # ============================================================
    # REGISTRATION
    # ============================================================

    def register(self, data: dict) -> dict:
        """
        Register a new student

        Args:
            data: Dict with student_id, name, email, password, and optional fields

        Returns:
            Dict with status and student data or error
        """
        # Validate input
        errors = self.validate_student_data(data)
        if errors:
            return {
                'status': 'error',
                'message': 'Validation failed',
                'errors': errors
            }

        # Check if student already exists
        if self.db and self.Student:
            existing = self.Student.query.filter(
                (self.Student.email == data['email'].strip().lower()) |
                (self.Student.student_id == data['student_id'].strip())
            ).first()

            if existing:
                if existing.email == data['email'].strip().lower():
                    return {'status': 'error', 'message': 'Email already registered'}
                return {'status': 'error', 'message': 'Student ID already exists'}

        try:
            if self.db and self.Student:
                # Create student via model (password is set via set_password for proper hashing)
                student = self.Student(
                    student_id=data['student_id'].strip(),
                    name=data['name'].strip(),
                    email=data['email'].strip().lower()
                )
                student.set_password(data['password'])

                # Set optional fields
                optional_fields = [
                    'department', 'year', 'cgpa', 'tenth_percentage',
                    'twelfth_percentage', 'mentor_email', 'phone'
                ]
                for field in optional_fields:
                    if field in data and data[field]:
                        setattr(student, field, data[field])

                self.db.session.add(student)
                self.db.session.commit()

                # Generate session token
                token = self._generate_token()
                session_data = {
                    'user_id': student.id,
                    'student_id': student.student_id,
                    'name': student.name,
                    'email': student.email,
                    'role': 'student',
                    'token': token
                }

                return {
                    'status': 'success',
                    'message': 'Registration successful! Welcome aboard 🎉',
                    'student': session_data,
                    'token': token
                }
            else:
                # No DB available - return success (for testing)
                return {
                    'status': 'success',
                    'message': 'Registration successful (DB not configured)',
                    'student': {
                        'student_id': data['student_id'].strip(),
                        'name': data['name'].strip(),
                        'email': data['email'].strip().lower(),
                        'department': data.get('department', ''),
                        'year': data.get('year', '')
                    },
                    'token': self._generate_token()
                }

        except Exception as e:
            if self.db:
                self.db.session.rollback()
            return {
                'status': 'error',
                'message': f'Registration failed: {str(e)}'
            }

    # ============================================================
    # LOGIN
    # ============================================================

    def login(self, email_or_id: str, password: str) -> dict:
        """
        Authenticate a student

        Args:
            email_or_id: Student email or student ID
            password: Plain text password

        Returns:
            Dict with status and session data or error
        """
        if not email_or_id or not password:
            return {'status': 'error', 'message': 'Email/ID and password are required'}

        if not self.db or not self.Student:
            return {'status': 'error', 'message': 'Database not configured'}

        try:
            # Find student by email or student_id
            student = self.Student.query.filter(
                (self.Student.email == email_or_id.strip().lower()) |
                (self.Student.student_id == email_or_id.strip())
            ).first()

            if not student:
                return {'status': 'error', 'message': 'Invalid credentials'}

            # Verify password
            if not student.check_password(password):
                return {'status': 'error', 'message': 'Invalid credentials'}

            # Update last login
            student.last_login = datetime.utcnow()
            self.db.session.commit()

            # Generate session data
            token = self._generate_token()
            session_data = {
                'user_id': student.id,
                'student_id': student.student_id,
                'name': student.name,
                'email': student.email,
                'department': student.department,
                'year': student.year,
                'cgpa': student.cgpa,
                'role': 'student',
                'token': token,
                'last_login': student.last_login.isoformat() if student.last_login else None
            }

            return {
                'status': 'success',
                'message': f'Welcome back, {student.name}! 👋',
                'student': session_data,
                'token': token
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Login failed: {str(e)}'
            }

    # ============================================================
    # FORGOT PASSWORD
    # ============================================================

    def forgot_password(self, email: str) -> dict:
        """
        Initiate forgot password process

        Sends a password reset link to the student's email

        Args:
            email: Student email address

        Returns:
            Dict with status
        """
        if not email:
            return {'status': 'error', 'message': 'Email is required'}

        if not self.validate_email(email):
            return {'status': 'error', 'message': 'Invalid email format'}

        # Check if student exists
        student = None
        if self.db and self.Student:
            student = self.Student.query.filter_by(email=email.strip().lower()).first()

        # Always return success to prevent email enumeration
        if not student:
            return {
                'status': 'success',
                'message': 'If the email is registered, you will receive a password reset link'
            }

        try:
            # Generate reset token
            reset_token = self._generate_token()
            self.reset_tokens[reset_token] = {
                'email': email.strip().lower(),
                'student_id': student.id,
                'expires_at': datetime.utcnow() + timedelta(hours=1),
                'used': False
            }

            # Send reset email
            email_sent = self._send_reset_email(email, reset_token, student.name)

            if email_sent:
                return {
                    'status': 'success',
                    'message': 'Password reset link sent to your email 📧',
                    'reset_token': reset_token  # Include in response for testing
                }
            else:
                return {
                    'status': 'success',
                    'message': 'If the email is registered, you will receive a password reset link',
                    'reset_token': reset_token  # For development/testing without email
                }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to process request: {str(e)}'
            }

    def reset_password(self, reset_token: str, new_password: str) -> dict:
        """
        Reset password using reset token

        Args:
            reset_token: Password reset token
            new_password: New password

        Returns:
            Dict with status
        """
        # Validate token
        if reset_token not in self.reset_tokens:
            return {'status': 'error', 'message': 'Invalid or expired reset token'}

        token_data = self.reset_tokens[reset_token]

        # Check if expired
        if datetime.utcnow() > token_data['expires_at']:
            del self.reset_tokens[reset_token]
            return {'status': 'error', 'message': 'Reset token has expired'}

        # Check if already used
        if token_data['used']:
            return {'status': 'error', 'message': 'Reset token has already been used'}

        # Validate new password
        valid, msg = self.validate_password_strength(new_password)
        if not valid:
            return {'status': 'error', 'message': msg}

        # Update password
        if self.db and self.Student:
            try:
                student = self.Student.query.get(token_data['student_id'])
                if not student:
                    return {'status': 'error', 'message': 'Student not found'}

                student.set_password(new_password)
                self.db.session.commit()

                # Mark token as used
                self.reset_tokens[reset_token]['used'] = True

                return {
                    'status': 'success',
                    'message': 'Password reset successful! You can now login with your new password 🔑'
                }

            except Exception as e:
                self.db.session.rollback()
                return {'status': 'error', 'message': f'Failed to reset password: {str(e)}'}

        # For testing without DB
        self.reset_tokens[reset_token]['used'] = True
        return {
            'status': 'success',
            'message': 'Password reset successful!'
        }

    def _send_reset_email(self, email: str, reset_token: str, student_name: str) -> bool:
        """Send password reset email"""
        if not self.config.MAIL_USERNAME or not self.config.MAIL_PASSWORD:
            return False

        try:
            reset_link = f"http://localhost:3000/reset-password?token={reset_token}"

            html = f"""
            <!DOCTYPE html>
            <html>
            <head><meta charset="UTF-8"></head>
            <body style="font-family: 'Segoe UI', Arial, sans-serif; background: #f3f4f6; padding: 20px;">
                <div style="max-width: 500px; margin: auto; background: #fff; border-radius: 12px; overflow: hidden;">
                    <div style="background: linear-gradient(135deg, #1e40af, #3b82f6); padding: 30px; text-align: center;">
                        <h1 style="color: #fff; margin: 0; font-size: 22px;">🔑 Password Reset</h1>
                    </div>
                    <div style="padding: 30px;">
                        <p>Hi <strong>{student_name}</strong>,</p>
                        <p>We received a request to reset your password for the Placement Predictor system.</p>
                        <p>Click the button below to set a new password:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_link}" style="background: #3b82f6; color: #fff; padding: 12px 30px; border-radius: 8px; text-decoration: none; display: inline-block;">Reset Password</a>
                        </div>
                        <p style="color: #6b7280; font-size: 13px;">This link will expire in 1 hour.</p>
                        <p style="color: #6b7280; font-size: 13px;">If you didn't request this, please ignore this email.</p>
                    </div>
                    <div style="background: #f9fafb; padding: 20px; text-align: center; color: #9ca3af; font-size: 12px;">
                        Placement Predictor System
                    </div>
                </div>
            </body>
            </html>
            """

            msg = MIMEText(html, 'html')
            msg['Subject'] = 'Placement Predictor - Password Reset Request'
            msg['From'] = self.config.MAIL_DEFAULT_SENDER
            msg['To'] = email

            with smtplib.SMTP(self.config.MAIL_SERVER, self.config.MAIL_PORT, timeout=10) as server:
                if self.config.MAIL_USE_TLS:
                    server.starttls()
                if self.config.MAIL_USERNAME and self.config.MAIL_PASSWORD:
                    server.login(self.config.MAIL_USERNAME, self.config.MAIL_PASSWORD)
                server.send_message(msg)

            return True

        except Exception:
            return False

    # ============================================================
    # SESSION MANAGEMENT
    # ============================================================

    def validate_session(self, token: str) -> dict:
        """
        Validate a session token

        Args:
            token: Session token

        Returns:
            Dict with validation result
        """
        if not token:
            return {'valid': False, 'message': 'No token provided'}

        # In a production system, validate against a token store
        # For now, basic validation
        if len(token) < 10:
            return {'valid': False, 'message': 'Invalid token format'}

        return {'valid': True, 'message': 'Session valid', 'role': 'student'}

    def logout(self, token: str) -> dict:
        """
        Invalidate a session

        Args:
            token: Session token to invalidate

        Returns:
            Dict with status
        """
        # In production, remove token from session store
        return {
            'status': 'success',
            'message': 'Logged out successfully'
        }

    # ============================================================
    # PROFILE MANAGEMENT
    # ============================================================

    def update_profile(self, student_id: int, data: dict) -> dict:
        """
        Update student profile information

        Args:
            student_id: Student user ID
            data: Dict of fields to update

        Returns:
            Dict with updated profile
        """
        if not self.db or not self.Student:
            return {'status': 'error', 'message': 'Database not configured'}

        try:
            student = self.Student.query.get(student_id)
            if not student:
                return {'status': 'error', 'message': 'Student not found'}

            # Allowed updatable fields with type coercion
            allowed_fields = {
                'department': str,
                'year': int,
                'cgpa': float,
                'tenth_percentage': float,
                'twelfth_percentage': float,
                'communication_skill': int,
                'programming_skill': int,
                'internships': int,
                'projects': int,
                'hackathons': int,
                'certifications': int,
                'backlogs': int,
                'attendance': float,
                'aptitude_score': int,
                'technical_score': int,
                'resume_score': int,
                'mentor_email': str,
                'phone': str
            }

            updated_fields = []
            for field, field_type in allowed_fields.items():
                if field in data and data[field] is not None:
                    try:
                        coerced = field_type(data[field])
                        setattr(student, field, coerced)
                        updated_fields.append(field)
                    except (ValueError, TypeError):
                        pass  # Skip invalid values silently

            student.updated_at = datetime.utcnow()
            self.db.session.commit()

            return {
                'status': 'success',
                'message': 'Profile updated successfully',
                'updated_fields': updated_fields,
                'student': student.to_dict()
            }

        except Exception as e:
            self.db.session.rollback()
            return {'status': 'error', 'message': f'Update failed: {str(e)}'}

    def get_profile(self, student_id: int) -> dict:
        """
        Get student profile

        Args:
            student_id: Student user ID

        Returns:
            Dict with student profile
        """
        if not self.db or not self.Student:
            return {'status': 'error', 'message': 'Database not configured'}

        try:
            student = self.Student.query.get(student_id)
            if not student:
                return {'status': 'error', 'message': 'Student not found'}

            return {
                'status': 'success',
                'student': student.to_dict()
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def change_password(self, student_id: int, current_password: str,
                        new_password: str) -> dict:
        """
        Change student password

        Args:
            student_id: Student user ID
            current_password: Current password for verification
            new_password: New password

        Returns:
            Dict with status
        """
        if not self.db or not self.Student:
            return {'status': 'error', 'message': 'Database not configured'}

        # Validate inputs
        if not current_password or not new_password:
            return {'status': 'error', 'message': 'Current and new password are required'}

        valid, msg = self.validate_password_strength(new_password)
        if not valid:
            return {'status': 'error', 'message': msg}

        try:
            student = self.Student.query.get(student_id)
            if not student:
                return {'status': 'error', 'message': 'Student not found'}

            # Verify current password
            if not student.check_password(current_password):
                return {'status': 'error', 'message': 'Current password is incorrect'}

            # Update password
            student.set_password(new_password)
            student.updated_at = datetime.utcnow()
            self.db.session.commit()

            return {
                'status': 'success',
                'message': 'Password changed successfully 🔑'
            }

        except Exception as e:
            self.db.session.rollback()
            return {'status': 'error', 'message': f'Failed to change password: {str(e)}'}


def register_student(data: dict, db_session=None, student_model=None) -> dict:
    """
    Convenience function for student registration

    Args:
        data: Student registration data
        db_session: SQLAlchemy session
        student_model: Student model

    Returns:
        Dict with result
    """
    auth = StudentAuth(db_session, student_model)
    return auth.register(data)


def login_student(email_or_id: str, password: str, db_session=None,
                   student_model=None) -> dict:
    """
    Convenience function for student login

    Args:
        email_or_id: Email or student ID
        password: Plain text password
        db_session: SQLAlchemy session
        student_model: Student model

    Returns:
        Dict with result
    """
    auth = StudentAuth(db_session, student_model)
    return auth.login(email_or_id, password)


if __name__ == '__main__':
    print("=" * 60)
    print("🔐 STUDENT AUTHENTICATION TEST")
    print("=" * 60)

    # Initialize auth system (without DB for testing)
    auth = StudentAuth()

    # Test registration
    print("\n📝 Testing Registration...")
    result = auth.register({
        'student_id': 'STU2024001',
        'name': 'John Doe',
        'email': 'john.doe@college.edu',
        'password': 'TestPass123',
        'department': 'Computer Science',
        'year': 4,
        'cgpa': 8.5
    })
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")

    # Test password validation
    print("\n🔐 Testing Password Validation...")
    tests = ['weak', 'NoNumber', 'nodigit1', 'Valid1Pass']
    for pwd in tests:
        valid, msg = auth.validate_password_strength(pwd)
        print(f"   '{pwd}': {'✅' if valid else '❌'} {msg}")

    # Test email validation
    print("\n📧 Testing Email Validation...")
    emails = ['valid@email.com', 'invalid-email', 'another@test.edu']
    for email in emails:
        print(f"   '{email}': {'✅' if auth.validate_email(email) else '❌'}")

    # Test forgot password
    print("\n🔑 Testing Forgot Password...")
    result = auth.forgot_password('john.doe@college.edu')
    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    if result.get('reset_token'):
        print(f"   Reset Token: {result['reset_token'][:20]}...")

        # Test reset password
        print("\n🔄 Testing Password Reset...")
        result = auth.reset_password(result['reset_token'], 'NewStr0ngPass')
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")

    print("\n" + "=" * 60)
    print("✅ AUTH TEST COMPLETE")
    print("=" * 60)
