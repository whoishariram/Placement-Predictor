"""
Security Tests - Password hashing, input validation, file upload validation, rate limiting
"""

import pytest
import os
import sys
from io import BytesIO

_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)


class TestPasswordHashing:
    """Tests for secure password hashing in models"""

    def test_set_password_creates_hash(self):
        """set_password should store salt:hash format"""
        from models import Student
        student = Student(
            student_id='SEC001',
            name='Security Test',
            email='sec@test.com'
        )
        student.set_password('TestPass123')
        assert student.password_hash is not None
        assert ':' in student.password_hash

    def test_hash_contains_salt_and_hash(self):
        """Hash format should be 'salt:hash'"""
        student = __import__('models').Student(
            student_id='SEC002', name='Test', email='t@t.com'
        )
        student.set_password('TestPass123')
        parts = student.password_hash.split(':')
        assert len(parts) == 2
        assert len(parts[0]) == 64  # 32 bytes salt = 64 hex chars
        assert len(parts[1]) == 64  # SHA256 = 64 hex chars

    def test_check_password_correct(self):
        """check_password should return True for correct password"""
        from models import Student
        student = Student(
            student_id='SEC003', name='Test', email='t2@t.com'
        )
        student.set_password('CorrectPass1')
        assert student.check_password('CorrectPass1') is True

    def test_check_password_incorrect(self):
        """check_password should return False for wrong password"""
        from models import Student
        student = Student(
            student_id='SEC004', name='Test', email='t3@t.com'
        )
        student.set_password('RealPass123')
        assert student.check_password('WrongPass') is False

    def test_same_password_different_hashes(self):
        """Same password should produce different hashes each time"""
        from models import Student
        s1 = Student(student_id='SEC005', name='A', email='a@t.com')
        s2 = Student(student_id='SEC006', name='B', email='b@t.com')
        s1.set_password('SamePass1')
        s2.set_password('SamePass1')
        assert s1.password_hash != s2.password_hash

    def test_empty_password(self):
        """Empty password should still create a hash"""
        from models import Student
        student = Student(
            student_id='SEC007', name='Test', email='t4@t.com'
        )
        student.set_password('')
        assert student.password_hash is not None


class TestInputValidationSecurity:
    """Tests for security input validation"""

    def test_sanitize_input_removes_html(self):
        """sanitize_input should strip HTML tags"""
        from utils.security import SecurityManager
        result = SecurityManager.sanitize_input('<script>alert("xss")</script>Hello')
        assert '<script>' not in result
        assert 'alert' not in result
        assert 'Hello' in result

    def test_sanitize_input_trims_whitespace(self):
        from utils.security import SecurityManager
        result = SecurityManager.sanitize_input('  hello world  ')
        assert result == 'hello world'

    def test_sanitize_input_handles_none(self):
        from utils.security import SecurityManager
        assert SecurityManager.sanitize_input(None) == ''
        assert SecurityManager.sanitize_input('') == ''

    def test_validate_email_security(self):
        from utils.security import SecurityManager
        assert SecurityManager.validate_email('test@test.com') is True
        assert SecurityManager.validate_email('') is False
        assert SecurityManager.validate_email('not-email') is False
        assert SecurityManager.validate_email('user@') is False

    def test_prevent_sql_injection(self):
        from utils.security import SecurityManager
        dangerous = "Robert'; DROP TABLE Students;--"
        clean = SecurityManager.prevent_sql_injection(dangerous)
        assert "'" not in clean
        assert ';' not in clean
        assert '--' not in clean

    def test_generate_csrf_token(self):
        from utils.security import SecurityManager
        token = SecurityManager.generate_csrf_token()
        assert len(token) == 64  # 32 bytes hex
        assert isinstance(token, str)


class TestFileUploadSecurity:
    """Tests for file upload validation"""

    def test_validate_file_extension_allowed(self):
        from utils.security import SecurityManager
        assert SecurityManager.validate_file_extension('resume.pdf') is True
        assert SecurityManager.validate_file_extension('data.csv') is True
        assert SecurityManager.validate_file_extension('photo.jpg') is True

    def test_validate_file_extension_denied(self):
        from utils.security import SecurityManager
        assert SecurityManager.validate_file_extension('malware.exe') is False
        assert SecurityManager.validate_file_extension('script.js') is False
        assert SecurityManager.validate_file_extension('file.sh') is False

    def test_validate_file_extension_no_extension(self):
        from utils.security import SecurityManager
        assert SecurityManager.validate_file_extension('Makefile') is False

    def test_sanitize_filename_removes_path(self):
        from utils.security import SecurityManager
        dangerous = '../../../etc/passwd'
        clean = SecurityManager.sanitize_filename(dangerous)
        assert '..' not in clean
        assert '/' not in clean

    def test_sanitize_filename_removes_null_bytes(self):
        from utils.security import SecurityManager
        dangerous = 'file\x00.pdf'
        clean = SecurityManager.sanitize_filename(dangerous)
        assert '\x00' not in clean

    def test_sanitize_filename_limit_length(self):
        from utils.security import SecurityManager
        long_name = 'a' * 300 + '.pdf'
        clean = SecurityManager.sanitize_filename(long_name)
        assert len(clean) <= 200

    def test_validate_csv_content_valid(self):
        from utils.security import SecurityManager
        csv_content = "student_id,name,cgpa\nSTU001,Test,8.5\nSTU002,Test2,7.0"
        valid, msg = SecurityManager.validate_csv_content(csv_content)
        assert valid is True

    def test_validate_csv_content_missing_columns(self):
        from utils.security import SecurityManager
        csv_content = "name,age\nTest,20"
        valid, msg = SecurityManager.validate_csv_content(csv_content)
        assert valid is False
        assert 'student_id' in msg or 'cgpa' in msg

    def test_validate_csv_content_empty(self):
        from utils.security import SecurityManager
        valid, msg = SecurityManager.validate_csv_content('')
        assert valid is False


class TestRateLimiter:
    """Tests for rate limiting"""

    def test_rate_limiter_init(self):
        from utils.security import RateLimiter
        limiter = RateLimiter()
        assert hasattr(limiter, '_requests')

    def test_rate_limiter_allows_first_request(self):
        from utils.security import RateLimiter
        limiter = RateLimiter()
        assert limiter.is_allowed(key='test', max_requests=3, window_seconds=60) is True

    def test_rate_limiter_blocks_excess(self):
        from utils.security import RateLimiter
        limiter = RateLimiter()
        key = 'block_test'
        # Use all 3 allowed requests
        assert limiter.is_allowed(key=key, max_requests=3, window_seconds=60) is True
        assert limiter.is_allowed(key=key, max_requests=3, window_seconds=60) is True
        assert limiter.is_allowed(key=key, max_requests=3, window_seconds=60) is True
        # 4th request should be blocked
        assert limiter.is_allowed(key=key, max_requests=3, window_seconds=60) is False

    def test_get_remaining(self):
        from utils.security import RateLimiter
        limiter = RateLimiter()
        key = 'remaining_test'
        limiter.is_allowed(key=key, max_requests=5, window_seconds=60)
        remaining = limiter.get_remaining(key=key, max_requests=5, window_seconds=60)
        assert remaining == 4

    def test_reset_clears_limits(self):
        from utils.security import RateLimiter
        limiter = RateLimiter()
        key = 'reset_test'
        limiter.is_allowed(key=key, max_requests=1, window_seconds=60)
        assert limiter.is_allowed(key=key, max_requests=1, window_seconds=60) is False
        limiter.reset(key=key)
        assert limiter.is_allowed(key=key, max_requests=1, window_seconds=60) is True

    def test_different_keys_independent(self):
        from utils.security import RateLimiter
        limiter = RateLimiter()
        key_a = 'user_a'
        key_b = 'user_b'
        limiter.is_allowed(key=key_a, max_requests=1, window_seconds=60)
        assert limiter.is_allowed(key=key_a, max_requests=1, window_seconds=60) is False
        assert limiter.is_allowed(key=key_b, max_requests=1, window_seconds=60) is True


class TestSecurityHeaders:
    """Tests for security headers middleware"""

    def test_security_headers_structure(self):
        """Security headers should contain all expected headers"""
        from utils.security import SecurityHeaders
        # Simulate a response object
        class MockResponse:
            def __init__(self):
                self.headers = {}

        response = MockResponse()
        result = SecurityHeaders.add_headers(response)

        assert 'X-Content-Type-Options' in result.headers
        assert result.headers['X-Content-Type-Options'] == 'nosniff'
        assert 'X-Frame-Options' in result.headers
        assert result.headers['X-Frame-Options'] == 'DENY'
        assert 'Strict-Transport-Security' in result.headers
        assert 'Content-Security-Policy' in result.headers
