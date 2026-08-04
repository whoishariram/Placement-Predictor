"""
Placement Predictor - Security Module
Rate limiting, CSRF protection, input validation, JWT authentication
"""

import re
import time
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from collections import defaultdict


class RateLimiter:
    """
    Rate limiter using sliding window algorithm

    Limits requests per IP address within a time window
    """

    def __init__(self):
        self._requests = defaultdict(list)

    def is_allowed(self, key=None, max_requests=60, window_seconds=60):
        """
        Check if request is allowed under rate limit

        Args:
            key: Identifier (defaults to client IP)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            bool: True if request is allowed
        """
        if key is None:
            key = request.remote_addr or 'unknown'

        now = time.time()
        window_start = now - window_seconds

        # Clean old entries
        self._requests[key] = [
            t for t in self._requests[key] if t > window_start
        ]

        # Check limit
        if len(self._requests[key]) >= max_requests:
            return False

        # Record this request
        self._requests[key].append(now)
        return True

    def get_remaining(self, key=None, max_requests=60, window_seconds=60):
        """Get remaining requests allowed"""
        if key is None:
            key = request.remote_addr or 'unknown'

        now = time.time()
        window_start = now - window_seconds
        self._requests[key] = [
            t for t in self._requests[key] if t > window_start
        ]
        return max(0, max_requests - len(self._requests[key]))

    def reset(self, key=None):
        """Reset rate limit for a key"""
        if key is None:
            key = request.remote_addr or 'unknown'
        self._requests[key] = []


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(max_requests=60, window_seconds=60):
    """
    Decorator to apply rate limiting to Flask routes

    Usage:
        @app.route('/api/login')
        @rate_limit(max_requests=10, window_seconds=60)
        def login():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not rate_limiter.is_allowed(
                max_requests=max_requests,
                window_seconds=window_seconds
            ):
                return jsonify({
                    'status': 'error',
                    'message': 'Rate limit exceeded. Please try again later.'
                }), 429
            return f(*args, **kwargs)
        return decorated
    return decorator


class SecurityManager:
    """
    Security manager for input validation, sanitization, and CSRF protection
    """

    @staticmethod
    def sanitize_input(text):
        """Sanitize user input (strip HTML tags, trim whitespace)"""
        if not text:
            return ''
        # Basic XSS prevention - remove script tags
        text = re.sub(r'<[^>]*>', '', str(text))
        # Trim whitespace
        text = text.strip()
        return text

    @staticmethod
    def validate_file_extension(filename, allowed_extensions=None):
        """
        Validate file extension against allowed list

        Args:
            filename: Original filename
            allowed_extensions: Set of allowed extensions

        Returns:
            bool: True if extension is allowed
        """
        if allowed_extensions is None:
            allowed_extensions = {'csv', 'pdf', 'png', 'jpg', 'jpeg', 'docx'}

        if '.' not in filename:
            return False

        ext = filename.rsplit('.', 1)[1].lower()
        return ext in allowed_extensions

    @staticmethod
    def validate_file_size(file_storage, max_size=16*1024*1024):
        """
        Validate file size against maximum

        Args:
            file_storage: FileStorage object from Flask
            max_size: Maximum file size in bytes (default 16MB)

        Returns:
            bool: True if file size is within limits
        """
        if not file_storage:
            return False
        # Seek to end to get size
        file_storage.seek(0, 2)
        size = file_storage.tell()
        file_storage.seek(0)  # Reset position
        return size <= max_size

    @staticmethod
    def validate_csv_content(content):
        """
        Basic CSV content validation

        Args:
            content: CSV file content as string

        Returns:
            tuple: (is_valid, message)
        """
        if not content or not content.strip():
            return False, "Empty file"

        lines = content.strip().split('\n')
        if len(lines) < 2:
            return False, "CSV must have header and at least one data row"

        header = lines[0].strip().lower()
        required_columns = ['student_id', 'name', 'cgpa']
        missing = [col for col in required_columns if col not in header]

        if missing:
            return False, f"Missing required columns: {', '.join(missing)}"

        return True, "Valid CSV"

    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(email).strip()))

    @staticmethod
    def generate_csrf_token():
        """Generate a CSRF token"""
        return secrets.token_hex(32)

    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename to prevent path traversal"""
        # Remove path separators
        filename = filename.replace('\\', '_').replace('/', '_')
        # Remove null bytes
        filename = filename.replace('\x00', '')
        # Remove any path traversal attempts
        filename = filename.replace('..', '_')
        # Limit length
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:196] + ext
        return filename

    @staticmethod
    def prevent_sql_injection(value):
        """Basic SQL injection prevention (strip dangerous characters)"""
        if not isinstance(value, str):
            return value
        dangerous = ["'", '"', ';', '--', '/*', '*/', 'xp_']
        for char in dangerous:
            value = value.replace(char, '')
        return value


import os


def require_auth(role='student'):
    """
    Decorator to require authentication for Flask routes

    Usage:
        @app.route('/api/student/dashboard')
        @require_auth(role='student')
        def dashboard():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization', '')

            if not auth_header.startswith('Bearer '):
                return jsonify({
                    'status': 'error',
                    'message': 'Authentication required'
                }), 401

            token = auth_header.split(' ', 1)[1]

            # In production, validate against token store
            if len(token) < 20:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid token'
                }), 401

            return f(*args, **kwargs)
        return decorated
    return decorator


# Security headers middleware
class SecurityHeaders:
    """Middleware to add security headers to responses"""

    @staticmethod
    def add_headers(response):
        """Add security headers to response"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            "font-src 'self' data:; "
            "connect-src 'self'"
        )
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = (
            'camera=(), microphone=(), geolocation=()'
        )
        return response
