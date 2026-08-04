"""
Placement Predictor - Application Configuration
"""

import os
import secrets

class Config:
    """Base configuration"""
    
    # Application
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Database
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'placement.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{DATABASE_PATH}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CSV Database
    DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
    STUDENT_CSV_PATH = os.path.join(DATASET_DIR, 'student_data.csv')
    COMPANIES_CSV_PATH = os.path.join(DATASET_DIR, 'companies.csv')
    PREDICTIONS_CSV_PATH = os.path.join(DATASET_DIR, 'predictions.csv')
    
    # Model
    MODEL_DIR = os.path.join(BASE_DIR, 'model')
    MODEL_PATH = os.path.join(MODEL_DIR, 'best_model.pkl')
    ENCODER_PATH = os.path.join(MODEL_DIR, 'label_encoders.pkl')
    SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')
    FEATURES_PATH = os.path.join(MODEL_DIR, 'feature_columns.pkl')
    
    # Uploads
    UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
    RESUMES_DIR = os.path.join(BASE_DIR, 'resumes')
    REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
    
    # File upload limits
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'csv', 'pdf', 'png', 'jpg', 'jpeg', 'docx'}
    
    # Session
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    
    # CORS
    CORS_ORIGINS = os.environ.get(
        'CORS_ORIGINS',
        'http://localhost:3000,http://localhost:5000'
    ).split(',')
    
    # Email Configuration (Gmail SMTP)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'placement.predictor@edu.in')
    
    # ML Model Parameters
    MODEL_TEST_SIZE = float(os.environ.get('MODEL_TEST_SIZE', 0.2))
    MODEL_RANDOM_STATE = int(os.environ.get('MODEL_RANDOM_STATE', 42))
    MODEL_CV_FOLDS = int(os.environ.get('MODEL_CV_FOLDS', 5))
    
    # Mentor Alert Thresholds
    ALERT_LOW_CGPA = float(os.environ.get('ALERT_LOW_CGPA', 7.0))
    ALERT_LOW_RESUME = int(os.environ.get('ALERT_LOW_RESUME', 40))
    ALERT_LOW_PROGRAMMING = int(os.environ.get('ALERT_LOW_PROGRAMMING', 40))
    ALERT_LOW_COMMUNICATION = int(os.environ.get('ALERT_LOW_COMMUNICATION', 40))
    ALERT_LOW_PROBABILITY = float(os.environ.get('ALERT_LOW_PROBABILITY', 35.0))
    
    # Pagination
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', 20))
    
    @staticmethod
    def init_app(app):
        """Initialize application directories"""
        for dir_path in [
            Config.DATASET_DIR,
            Config.MODEL_DIR,
            Config.UPLOAD_DIR,
            Config.RESUMES_DIR,
            Config.REPORTS_DIR,
            Config.STATIC_DIR,
            Config.TEMPLATES_DIR,
            os.path.join(Config.BASE_DIR, 'database')
        ]:
            os.makedirs(dir_path, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
