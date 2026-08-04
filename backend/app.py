"""
Placement Predictor - Main Flask Application
Entry point for the Placement Predictor backend API
"""

import os
import sys
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_session import Session

# Add backend directory to path for reliable imports
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)


def create_app(config_name='default'):
    """
    Application factory for the Placement Predictor

    Args:
        config_name: Configuration environment ('development', 'production', 'testing', 'default')

    Returns:
        Configured Flask application instance
    """
    from config import config

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config.get(config_name, config['default']))
    config['default'].init_app(app)

    # Initialize extensions
    # CORS
    CORS(app, resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS', '*')}},
         supports_credentials=True)

    # Server-side session
    app.config['SESSION_TYPE'] = 'filesystem'
    session_dir = os.path.join(app.config.get('BASE_DIR', os.getcwd()), 'flask_session')
    os.makedirs(session_dir, exist_ok=True)
    app.config['SESSION_FILE_DIR'] = session_dir
    Session(app)

    # Initialize database
    from models import db, init_db
    db.init_app(app)
    with app.app_context():
        try:
            init_db(app)
        except Exception as e:
            print(f"⚠️  Database init warning: {e}")

    # Register route blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    # Print startup banner
    _print_startup_banner(app)

    return app


def _register_blueprints(app):
    """Register all API route blueprints"""
    from routes.student_routes import student_bp
    from routes.admin_routes import admin_bp
    from routes.ml_routes import ml_bp
    from routes.analysis_routes import analysis_bp

    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ml_bp)
    app.register_blueprint(analysis_bp)

    # Auth routes
    @app.route('/api/auth/student/login', methods=['POST'])
    def student_login():
        from flask import request
        from auth.student_auth import StudentAuth
        from models import Student, db
        data = request.get_json()
        auth = StudentAuth(db, Student)
        result = auth.login(data.get('email_or_id', ''), data.get('password', ''))
        return jsonify(result), 200 if result['status'] == 'success' else 401

    @app.route('/api/auth/student/register', methods=['POST'])
    def student_register():
        from flask import request
        from auth.student_auth import StudentAuth
        from models import Student, db
        data = request.get_json()
        auth = StudentAuth(db, Student)
        result = auth.register(data)
        return jsonify(result), 201 if result['status'] == 'success' else 400

    @app.route('/api/auth/student/forgot-password', methods=['POST'])
    def forgot_password():
        from flask import request
        from auth.student_auth import StudentAuth
        from config import Config
        data = request.get_json()
        auth = StudentAuth(config=Config)
        result = auth.forgot_password(data.get('email', ''))
        return jsonify(result)

    @app.route('/api/auth/student/reset-password', methods=['POST'])
    def reset_password():
        from flask import request
        from auth.student_auth import StudentAuth
        data = request.get_json()
        auth = StudentAuth()
        result = auth.reset_password(data.get('token', ''), data.get('password', ''))
        return jsonify(result)

    @app.route('/api/auth/admin/login', methods=['POST'])
    def admin_login():
        from flask import request
        from auth.admin_auth import AdminAuth
        from models import Admin, ActivityLog, db
        data = request.get_json()
        auth = AdminAuth(db, Admin, ActivityLog)
        result = auth.login(data.get('username', ''), data.get('password', ''),
                           ip_address=request.remote_addr)
        return jsonify(result), 200 if result['status'] == 'success' else 401

    # Health check
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'app': 'Placement Predictor',
            'version': '1.0.0',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })

    # Root
    @app.route('/')
    def index():
        return jsonify({
            'name': 'Placement Predictor API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth/*',
                'student': '/api/student/*',
                'admin': '/api/admin/*',
                'ml': '/api/ml/*',
                'analysis': '/api/resume/*, /api/company/*',
                'health': '/api/health'
            }
        })


def _register_error_handlers(app):
    """Register global error handlers"""
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'status': 'error', 'message': 'Bad request'}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'status': 'error', 'message': 'Forbidden'}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'status': 'error', 'message': 'Resource not found'}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'status': 'error', 'message': 'Method not allowed'}), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


def _print_startup_banner(app):
    """Print startup banner with configuration info"""
    print("""
    ╔══════════════════════════════════════════════════╗
    ║     🎓 Placement Predictor using ML             ║
    ║     Flask Backend API                           ║
    ╚══════════════════════════════════════════════════╝
    """)
    print(f"  Environment: {app.config.get('ENV', 'development')}")
    print(f"  Debug: {app.config.get('DEBUG', False)}")
    print(f"  Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'sqlite://')}")
    print(f"  Model dir: {app.config.get('MODEL_DIR', 'N/A')}")
    print(f"  Dataset dir: {app.config.get('DATASET_DIR', 'N/A')}")
    print(f"  CORS origins: {app.config.get('CORS_ORIGINS', 'N/A')}")
    print(f"  Email: {'✅ Configured' if app.config.get('MAIL_USERNAME') else '❌ Not configured'}")
    print(f"  ML Model: {'✅ Ready' if os.path.exists(os.path.join(app.config.get('MODEL_DIR', ''), 'best_model.pkl')) else '⚠️  Not trained'}")
    print()
    print("  Endpoints:")
    print("    📊 Health:    GET  /api/health")
    print("    🔐 Auth:      POST /api/auth/*")
    print("    👨‍🎓 Student:  GET/POST /api/student/*")
    print("    👨‍💼 Admin:    GET/POST /api/admin/*")
    print("    🤖 ML:        GET/POST /api/ml/*")
    print("    📄 Analysis:  POST /api/resume/*, /api/company/*")
    print()
    print("  🚀 Server starting...")


# Create the application instance
app = create_app()

# Entry point
if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'

    app.run(host=host, port=port, debug=debug)
