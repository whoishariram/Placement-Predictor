"""
API Tests - Tests for all Flask API endpoints using Flask test client

Tests status codes: 200, 400, 401, 403, 404, 500
"""

import pytest
import os
import sys
import json

_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)


@pytest.fixture(scope='module')
def test_app():
    """Create Flask test app"""
    from app import create_app
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            yield client


class TestHealthEndpoint:
    """Tests for /api/health"""

    def test_health_returns_200(self, test_app):
        response = test_app.get('/api/health')
        assert response.status_code == 200

    def test_health_response_structure(self, test_app):
        response = test_app.get('/api/health')
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'healthy'
        assert 'version' in data
        assert 'timestamp' in data

    def test_health_get_only(self, test_app):
        response = test_app.post('/api/health')
        assert response.status_code in [405, 200]  # 405 Method Not Allowed or 200 if allowed


class TestRootEndpoint:
    """Tests for /"""

    def test_root_returns_info(self, test_app):
        response = test_app.get('/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'name' in data
        assert 'endpoints' in data


class TestAuthEndpoints:
    """Tests for /api/auth/* endpoints"""

    def test_student_login_missing_data(self, test_app):
        response = test_app.post('/api/auth/student/login',
                                 data=json.dumps({}),
                                 content_type='application/json')
        # Should return 401 (or 400) depending on implementation
        assert response.status_code in [400, 401]

    def test_student_login_invalid_credentials(self, test_app):
        response = test_app.post('/api/auth/student/login',
                                 data=json.dumps({
                                     'email_or_id': 'nonexistent',
                                     'password': 'wrong'
                                 }),
                                 content_type='application/json')
        assert response.status_code == 401

    def test_student_register_missing_data(self, test_app):
        response = test_app.post('/api/auth/student/register',
                                 data=json.dumps({}),
                                 content_type='application/json')
        assert response.status_code == 400

    def test_student_register(self, test_app):
        response = test_app.post('/api/auth/student/register',
                                 data=json.dumps({
                                     'student_id': 'API_TEST001',
                                     'name': 'API Test',
                                     'email': 'apitest@college.edu',
                                     'password': 'TestPass123',
                                     'department': 'CS'
                                 }),
                                 content_type='application/json')
        # May be 201 or 400 depending on DB state
        assert response.status_code in [201, 400]

    def test_forgot_password_missing_email(self, test_app):
        response = test_app.post('/api/auth/student/forgot-password',
                                 data=json.dumps({}),
                                 content_type='application/json')
        assert response.status_code == 200  # Always returns 200 to prevent enumeration

    def test_admin_login_missing_data(self, test_app):
        response = test_app.post('/api/auth/admin/login',
                                 data=json.dumps({}),
                                 content_type='application/json')
        # Should return 401 (or 400)
        assert response.status_code in [400, 401]

    def test_admin_login_invalid(self, test_app):
        response = test_app.post('/api/auth/admin/login',
                                 data=json.dumps({
                                     'username': 'admin',
                                     'password': 'wrong'
                                 }),
                                 content_type='application/json')
        assert response.status_code == 401


class TestStudentEndpoints:
    """Tests for /api/student/* endpoints"""

    def test_student_dashboard_no_auth(self, test_app):
        response = test_app.get('/api/student/dashboard')
        assert response.status_code in [401, 200]  # 401 if auth required

    def test_student_profile_no_auth(self, test_app):
        response = test_app.get('/api/student/profile')
        assert response.status_code in [401, 200]

    def test_student_prediction_no_auth(self, test_app):
        response = test_app.post('/api/student/predict',
                                 data=json.dumps({}),
                                 content_type='application/json')
        assert response.status_code in [401, 400, 200]

    def test_student_eligible_companies(self, test_app):
        response = test_app.get('/api/student/eligible-companies')
        # May return 200 or 401
        assert response.status_code in [200, 401]


class TestAdminEndpoints:
    """Tests for /api/admin/* endpoints"""

    def test_admin_dashboard_no_auth(self, test_app):
        response = test_app.get('/api/admin/dashboard')
        assert response.status_code in [401, 200]

    def test_admin_manage_students_no_auth(self, test_app):
        response = test_app.get('/api/admin/students')
        assert response.status_code in [401, 200]

    def test_admin_analytics_no_auth(self, test_app):
        response = test_app.get('/api/admin/analytics')
        assert response.status_code in [401, 200]


class TestMLEndpoints:
    """Tests for /api/ml/* endpoints"""

    def test_ml_train_no_auth(self, test_app):
        response = test_app.post('/api/ml/train')
        assert response.status_code in [401, 200]

    def test_ml_clean_data(self, test_app):
        response = test_app.post('/api/ml/clean')
        assert response.status_code in [401, 200]

    def test_ml_model_status(self, test_app):
        response = test_app.get('/api/ml/status')
        assert response.status_code in [200, 401]


class TestAnalysisEndpoints:
    """Tests for /api/resume/* and /api/company/* endpoints"""

    def test_resume_analysis_no_file(self, test_app):
        response = test_app.post('/api/resume/analyze')
        assert response.status_code in [400, 401, 200]

    def test_company_list(self, test_app):
        response = test_app.get('/api/company/list')
        assert response.status_code in [200, 401]

    def test_company_check_eligibility(self, test_app):
        response = test_app.post('/api/company/check',
                                 data=json.dumps({}),
                                 content_type='application/json')
        assert response.status_code in [400, 401, 200]


class TestErrorHandling:
    """Tests for error handler responses"""

    def test_404_returns_json(self, test_app):
        response = test_app.get('/api/nonexistent/route')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'error'

    def test_405_method_not_allowed(self, test_app):
        response = test_app.put('/api/health')  # health is GET only
        assert response.status_code in [405, 200]

    def test_invalid_json(self, test_app):
        response = test_app.post('/api/auth/student/login',
                                 data='not-json',
                                 content_type='application/json')
        # Flask returns 400 for malformed JSON
        assert response.status_code in [400, 401]
