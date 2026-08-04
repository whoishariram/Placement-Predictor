"""
Placement Predictor - Structured Logging Module
Logs login attempts, predictions, model training, errors with timestamps
"""

import os
import sys
import logging
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'module': record.name,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        if hasattr(record, 'extra_data'):
            log_entry['extra'] = record.extra_data
        if record.exc_info and record.exc_info[0]:
            log_entry['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


class Logger:
    """
    Structured logger for the Placement Predictor application

    Logs to:
    - Console (stdout) for development
    - Rotating files for production
    - Separate files for specific log categories
    """

    _instances = {}

    def __new__(cls, name='placement_predictor', log_dir=None):
        if name not in cls._instances:
            instance = super().__new__(cls)
            instance._initialized = False
            cls._instances[name] = instance
        return cls._instances[name]

    def __init__(self, name='placement_predictor', log_dir=None):
        if self._initialized:
            return
        self._initialized = True

        self.name = name
        if log_dir is None:
            _base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            log_dir = os.path.join(os.path.dirname(_base), 'logs')
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

        # Create main logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

        # Console handler (INFO level)
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(console)

        # File handler (DEBUG level) - rotating files, max 10MB each, keep 5 backups
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, f'{name}.log'),
            maxBytes=10_000_000,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(file_handler)

        # Create category-specific loggers
        self._category_loggers = {}
        self._setup_category_loggers()

    def _setup_category_loggers(self):
        """Create separate loggers for specific categories"""
        categories = ['auth', 'prediction', 'training', 'upload', 'error', 'email']
        for cat in categories:
            cat_logger = logging.getLogger(f'{self.name}.{cat}')
            cat_logger.setLevel(logging.DEBUG)
            cat_handler = RotatingFileHandler(
                os.path.join(self.log_dir, f'{cat}.log'),
                maxBytes=5_000_000,
                backupCount=3,
                encoding='utf-8'
            )
            cat_handler.setLevel(logging.DEBUG)
            cat_handler.setFormatter(JSONFormatter())
            cat_logger.addHandler(cat_handler)
            cat_logger.propagate = False
            self._category_loggers[cat] = cat_logger

    def _log(self, level, message, category=None, extra=None):
        """Internal log method"""
        logger = self._category_loggers.get(category, self.logger)
        extra_data = extra or {}

        if level == 'debug':
            logger.debug(message, extra={'extra_data': extra_data} if extra_data else None)
        elif level == 'info':
            logger.info(message, extra={'extra_data': extra_data} if extra_data else None)
        elif level == 'warning':
            logger.warning(message, extra={'extra_data': extra_data} if extra_data else None)
        elif level == 'error':
            logger.error(message, extra={'extra_data': extra_data} if extra_data else None)
        elif level == 'critical':
            logger.critical(message, extra={'extra_data': extra_data} if extra_data else None)

    # Public methods
    def debug(self, message, category=None, **extra):
        self._log('debug', message, category, extra)

    def info(self, message, category=None, **extra):
        self._log('info', message, category, extra)

    def warning(self, message, category=None, **extra):
        self._log('warning', message, category, extra)

    def error(self, message, category=None, **extra):
        self._log('error', message, category, extra)

    def critical(self, message, category=None, **extra):
        self._log('critical', message, category, extra)

    # Convenience methods for specific categories
    def log_login(self, user_type, user_id, success, ip=None):
        self.info(
            f"{'✅' if success else '❌'} {user_type} login attempt",
            category='auth',
            user_type=user_type,
            user_id=user_id,
            success=success,
            ip_address=ip
        )

    def log_prediction(self, student_id, prediction, probability, confidence):
        self.info(
            f"🔮 Prediction for student {student_id}: {prediction} ({probability:.1f}%)",
            category='prediction',
            student_id=student_id,
            prediction=prediction,
            probability=round(probability, 2),
            confidence=round(confidence, 2)
        )

    def log_training(self, model_name, accuracy, metrics=None):
        self.info(
            f"🤖 Model trained: {model_name} (accuracy: {accuracy:.2f}%)",
            category='training',
            model=model_name,
            accuracy=accuracy,
            metrics=metrics
        )

    def log_upload(self, file_type, filename, size, status):
        self.info(
            f"📁 {file_type} upload: {filename} ({size} bytes) - {status}",
            category='upload',
            file_type=file_type,
            filename=filename,
            size=size,
            status=status
        )

    def log_email(self, recipient, subject, status):
        self.info(
            f"📧 Email to {recipient}: '{subject}' - {status}",
            category='email',
            recipient=recipient,
            subject=subject,
            status=status
        )

    def log_error(self, error_type, message, details=None):
        self.error(
            f"❌ {error_type}: {message}",
            category='error',
            error_type=error_type,
            details=details
        )


# Singleton accessor
def get_logger(name='placement_predictor'):
    """Get or create a logger instance"""
    return Logger(name)


# Module-level convenience functions
def log_login_attempt(user_type, user_id, success, ip=None):
    get_logger().log_login(user_type, user_id, success, ip)


def log_prediction_request(student_id, prediction, probability, confidence):
    get_logger().log_prediction(student_id, prediction, probability, confidence)


def log_model_training(model_name, accuracy, metrics=None):
    get_logger().log_training(model_name, accuracy, metrics)


def log_file_upload(file_type, filename, size, status):
    get_logger().log_upload(file_type, filename, size, status)


def log_email_sent(recipient, subject, status):
    get_logger().log_email(recipient, subject, status)


def log_application_error(error_type, message, details=None):
    get_logger().log_error(error_type, message, details)
