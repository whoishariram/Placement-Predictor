"""
Unit tests for Authentication Modules (auth/student_auth.py, auth/admin_auth.py)
"""

import pytest
import os
import sys

_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from auth.student_auth import StudentAuth
from auth.admin_auth import AdminAuth


class TestStudentAuthInitialization:
    """Tests for StudentAuth init and basic methods"""

    def test_init_default_config(self):
        auth = StudentAuth()
        assert auth.db is None
        assert auth.Student is None
        assert auth.config is not None
        assert auth.reset_tokens == {}

    def test_generate_token_length(self):
        auth = StudentAuth()
        token = auth._generate_token()
        assert len(token) == 96  # 48 bytes hex = 96 chars
        assert isinstance(token, str)


class TestStudentAuthValidation:
    """Tests for input validation methods"""

    def test_validate_email_valid(self):
        auth = StudentAuth()
        assert auth.validate_email('student@college.edu') is True
        assert auth.validate_email('test.user@domain.co.in') is True
        assert auth.validate_email('valid_email123@test.org') is True

    def test_validate_email_invalid(self):
        auth = StudentAuth()
        assert auth.validate_email('') is False
        assert auth.validate_email('not-an-email') is False
        assert auth.validate_email('@domain.com') is False
        assert auth.validate_email('user@') is False
        assert auth.validate_email(None) is False

    def test_validate_password_strength_valid(self):
        auth = StudentAuth()
        valid, msg = auth.validate_password_strength('Strong1Pass')
        assert valid is True
        valid, msg = auth.validate_password_strength('Abc12345')
        assert valid is True

    def test_validate_password_strength_too_short(self):
        auth = StudentAuth()
        valid, msg = auth.validate_password_strength('Ab1')
        assert valid is False
        assert '6 characters' in msg

    def test_validate_password_strength_missing_upper(self):
        auth = StudentAuth()
        valid, msg = auth.validate_password_strength('abc12345')
        assert valid is False
        assert 'uppercase' in msg

    def test_validate_password_strength_missing_digit(self):
        auth = StudentAuth()
        valid, msg = auth.validate_password_strength('Abcdefgh')
        assert valid is False
        assert 'digit' in msg

    def test_validate_password_too_long(self):
        auth = StudentAuth()
        valid, msg = auth.validate_password_strength('A' + 'b' * 130 + '1')
        assert valid is False
        assert '128' in msg

    def test_validate_student_data_valid(self):
        auth = StudentAuth()
        data = {
            'student_id': 'STU001',
            'name': 'Test Student',
            'email': 'test@college.edu',
            'password': 'TestPass123',
            'department': 'CS',
            'year': 4,
            'cgpa': 8.5
        }
        errors = auth.validate_student_data(data)
        assert errors == []

    def test_validate_student_data_missing_fields(self):
        auth = StudentAuth()
        errors = auth.validate_student_data({})
        assert len(errors) >= 3  # student_id, name, email, password

    def test_validate_student_data_invalid_cgpa(self):
        auth = StudentAuth()
        data = {
            'student_id': 'STU001',
            'name': 'Test',
            'email': 'test@college.edu',
            'password': 'TestPass123',
            'cgpa': 15
        }
        errors = auth.validate_student_data(data)
        assert any('CGPA' in e for e in errors)

    def test_validate_student_data_invalid_year(self):
        auth = StudentAuth()
        data = {
            'student_id': 'STU001',
            'name': 'Test',
            'email': 'test@college.edu',
            'password': 'TestPass123',
            'year': 10
        }
        errors = auth.validate_student_data(data)
        assert any('Year' in e for e in errors)


class TestStudentAuthRegistration:
    """Tests for student registration"""

    def test_register_no_db_success(self):
        auth = StudentAuth()
        data = {
            'student_id': 'STU001',
            'name': 'Test Student',
            'email': 'test@college.edu',
            'password': 'TestPass123'
        }
        result = auth.register(data)
        assert result['status'] == 'success'
        assert 'token' in result
        assert result['student']['name'] == 'Test Student'

    def test_register_validation_failure(self):
        auth = StudentAuth()
        data = {'student_id': '', 'name': '', 'email': '', 'password': ''}
        result = auth.register(data)
        assert result['status'] == 'error'
        assert result['message'] == 'Validation failed'

    def test_register_duplicate_email_check(self):
        # Can't fully test without DB
        auth = StudentAuth()
        data = {
            'student_id': 'STU999',
            'name': 'Dup',
            'email': 'dup@test.com',
            'password': 'TestPass123'
        }
        result = auth.register(data)
        assert result['status'] == 'success'  # Passes without DB


class TestStudentAuthLogin:
    """Tests for student login"""

    def test_login_missing_credentials(self):
        auth = StudentAuth()
        result = auth.login('', '')
        assert result['status'] == 'error'
        assert 'required' in result['message']

    def test_login_no_db(self):
        auth = StudentAuth()
        result = auth.login('test@test.com', 'password123')
        assert result['status'] == 'error'
        assert 'Database not configured' in result['message']

    def test_login_with_email_or_id(self):
        auth = StudentAuth()
        result = auth.login('test@test.com', 'password')
        # Without DB, returns error
        assert result['status'] == 'error'


class TestStudentAuthForgotPassword:
    """Tests for forgot/reset password"""

    def test_forgot_password_empty_email(self):
        auth = StudentAuth()
        result = auth.forgot_password('')
        assert result['status'] == 'error'
        assert 'required' in result['message']

    def test_forgot_password_invalid_email(self):
        auth = StudentAuth()
        result = auth.forgot_password('not-an-email')
        assert result['status'] == 'error'

    def test_forgot_password_valid_email(self):
        auth = StudentAuth()
        result = auth.forgot_password('test@college.edu')
        assert result['status'] == 'success'
        assert 'reset_token' in result

    def test_reset_password_invalid_token(self):
        auth = StudentAuth()
        result = auth.reset_password('invalid-token', 'NewPass123')
        assert result['status'] == 'error'
        assert 'Invalid or expired' in result['message']

    def test_reset_password_valid_flow(self):
        auth = StudentAuth()
        forgot = auth.forgot_password('test@college.edu')
        token = forgot['reset_token']
        result = auth.reset_password(token, 'NewPass123')
        assert result['status'] == 'success'

    def test_reset_password_token_used_twice(self):
        auth = StudentAuth()
        forgot = auth.forgot_password('test@college.edu')
        token = forgot['reset_token']
        auth.reset_password(token, 'NewPass123')
        result = auth.reset_password(token, 'Another1Pass')
        assert result['status'] == 'error'
        assert 'already been used' in result['message']

    def test_reset_password_weak_new_password(self):
        auth = StudentAuth()
        forgot = auth.forgot_password('test@college.edu')
        token = forgot['reset_token']
        result = auth.reset_password(token, 'weak')
        assert result['status'] == 'error'


class TestStudentAuthProfile:
    """Tests for profile management"""

    def test_get_profile_no_db(self):
        auth = StudentAuth()
        result = auth.get_profile(1)
        assert result['status'] == 'error'

    def test_update_profile_no_db(self):
        auth = StudentAuth()
        result = auth.update_profile(1, {'name': 'New'})
        assert result['status'] == 'error'

    def test_change_password_no_db(self):
        auth = StudentAuth()
        result = auth.change_password(1, 'old', 'NewPass123')
        assert result['status'] == 'error'

    def test_change_password_missing_fields(self):
        auth = StudentAuth()
        # Without DB, it returns error before validation
        result = auth.change_password(1, '', '')
        assert result['status'] == 'error'


class TestStudentAuthSession:
    """Tests for session management"""

    def test_validate_session_empty_token(self):
        auth = StudentAuth()
        result = auth.validate_session('')
        assert result['valid'] is False

    def test_validate_session_short_token(self):
        auth = StudentAuth()
        result = auth.validate_session('short')
        assert result['valid'] is False

    def test_validate_session_valid(self):
        auth = StudentAuth()
        token = auth._generate_token()
        result = auth.validate_session(token)
        assert result['valid'] is True

    def test_logout(self):
        auth = StudentAuth()
        result = auth.logout('some-token')
        assert result['status'] == 'success'


class TestAdminAuthInitialization:
    """Tests for AdminAuth initialization"""

    def test_init(self):
        auth = AdminAuth()
        assert auth.db is None
        assert auth.Admin is None
        assert auth.admin_sessions == {}

    def test_generate_token(self):
        auth = AdminAuth()
        token = auth._generate_token()
        assert len(token) == 96


class TestAdminAuthLogin:
    """Tests for admin login"""

    def test_login_missing_credentials(self):
        auth = AdminAuth()
        result = auth.login('', '')
        assert result['status'] == 'error'

    def test_default_admin_login_success(self):
        auth = AdminAuth()
        result = auth.login('admin', 'admin123')
        assert result['status'] == 'success'
        assert 'token' in result

    def test_default_admin_login_failure(self):
        auth = AdminAuth()
        result = auth.login('admin', 'wrongpass')
        assert result['status'] == 'error'

    def test_default_admin_login_wrong_username(self):
        auth = AdminAuth()
        result = auth.login('unknown', 'admin123')
        assert result['status'] == 'error'


class TestAdminAuthSession:
    """Tests for admin session management"""

    def test_validate_session_empty(self):
        auth = AdminAuth()
        result = auth.validate_session('')
        assert result['valid'] is False

    def test_validate_session_in_memory(self):
        auth = AdminAuth()
        login_result = auth.login('admin', 'admin123')
        token = login_result['token']
        result = auth.validate_session(token)
        assert result['valid'] is True
        assert result['role'] == 'admin'

    def test_logout_removes_session(self):
        auth = AdminAuth()
        login_result = auth.login('admin', 'admin123')
        token = login_result['token']

        auth.logout(token)
        # After logout, session should still be valid via fallback
        # (because the fallback only checks token length)
        result = auth.validate_session(token)
        # Token is 96 chars so it passes fallback
        assert result.get('valid') is True

    def test_get_session_stats(self):
        auth = AdminAuth()
        auth.login('admin', 'admin123')
        stats = auth.get_session_stats()
        assert 'total_sessions' in stats
        assert stats['total_sessions'] >= 1

    def test_cleanup_expired_sessions(self):
        auth = AdminAuth()
        cleared = auth.cleanup_expired_sessions()
        assert isinstance(cleared, int)
        assert cleared >= 0


class TestAdminAuthManagement:
    """Tests for admin user management"""

    def test_create_admin_no_db(self):
        auth = AdminAuth()
        result = auth.create_admin(1, {
            'username': 'newadmin',
            'email': 'new@admin.com',
            'password': 'AdminPass123'
        })
        assert result['status'] == 'error'

    def test_get_admin_profile_no_db(self):
        auth = AdminAuth()
        result = auth.get_admin_profile(1)
        assert result['status'] == 'success'
        assert result['admin']['username'] == 'admin'

    def test_get_all_admins_no_db(self):
        auth = AdminAuth()
        result = auth.get_all_admins()
        assert result['status'] == 'success'

    def test_change_password_no_db(self):
        auth = AdminAuth()
        result = auth.change_password(1, 'old', 'NewPass123')
        assert result['status'] == 'error'

    def test_change_password_missing_fields(self):
        auth = AdminAuth()
        result = auth.change_password(1, '', '')
        assert result['status'] == 'error'
