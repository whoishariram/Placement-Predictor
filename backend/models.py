"""
Placement Predictor - Database Models
SQLAlchemy models for SQLite database
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib
import os

db = SQLAlchemy()


class Admin(db.Model):
    """Admin user model"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        """Hash and set password"""
        salt = os.urandom(32).hex()
        self.password_hash = salt + ':' + hashlib.sha256(
            (salt + password).encode()
        ).hexdigest()
    
    def check_password(self, password):
        """Verify password"""
        salt, hash_value = self.password_hash.split(':')
        return hash_value == hashlib.sha256(
            (salt + password).encode()
        ).hexdigest()
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class Student(db.Model):
    """Student model"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mentor_email = db.Column(db.String(120), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    
    # Academic Details
    cgpa = db.Column(db.Float, nullable=True)
    tenth_percentage = db.Column(db.Float, nullable=True)
    twelfth_percentage = db.Column(db.Float, nullable=True)
    
    # Skills
    communication_skill = db.Column(db.Integer, nullable=True, default=0)
    programming_skill = db.Column(db.Integer, nullable=True, default=0)
    
    # Achievements
    internships = db.Column(db.Integer, nullable=True, default=0)
    projects = db.Column(db.Integer, nullable=True, default=0)
    hackathons = db.Column(db.Integer, nullable=True, default=0)
    certifications = db.Column(db.Integer, nullable=True, default=0)
    
    # Academic Status
    backlogs = db.Column(db.Integer, nullable=True, default=0)
    attendance = db.Column(db.Float, nullable=True, default=0)
    
    # Test Scores
    aptitude_score = db.Column(db.Integer, nullable=True, default=0)
    technical_score = db.Column(db.Integer, nullable=True, default=0)
    resume_score = db.Column(db.Integer, nullable=True, default=0)
    
    # Placement
    placement_status = db.Column(db.Integer, nullable=True, default=0)
    package = db.Column(db.Float, nullable=True, default=0)
    company = db.Column(db.String(100), nullable=True)
    
    # Metadata
    resume_path = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    predictions = db.relationship('Prediction', backref='student', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        salt = os.urandom(32).hex()
        self.password_hash = salt + ':' + hashlib.sha256(
            (salt + password).encode()
        ).hexdigest()
    
    def check_password(self, password):
        """Verify password"""
        salt, hash_value = self.password_hash.split(':')
        return hash_value == hashlib.sha256(
            (salt + password).encode()
        ).hexdigest()
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'email': self.email,
            'mentor_email': self.mentor_email,
            'department': self.department,
            'year': self.year,
            'cgpa': self.cgpa,
            'tenth_percentage': self.tenth_percentage,
            'twelfth_percentage': self.twelfth_percentage,
            'communication_skill': self.communication_skill,
            'programming_skill': self.programming_skill,
            'internships': self.internships,
            'projects': self.projects,
            'hackathons': self.hackathons,
            'certifications': self.certifications,
            'backlogs': self.backlogs,
            'attendance': self.attendance,
            'aptitude_score': self.aptitude_score,
            'technical_score': self.technical_score,
            'resume_score': self.resume_score,
            'placement_status': self.placement_status,
            'package': self.package,
            'company': self.company,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Prediction(db.Model):
    """Prediction history model"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    prediction_result = db.Column(db.Integer, nullable=False)  # 1 = Placed, 0 = Not Placed
    probability = db.Column(db.Float, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    model_used = db.Column(db.String(50), nullable=True)
    
    # Feature values at prediction time
    cgpa = db.Column(db.Float, nullable=True)
    department = db.Column(db.String(100), nullable=True)
    communication_skill = db.Column(db.Integer, nullable=True)
    programming_skill = db.Column(db.Integer, nullable=True)
    internships = db.Column(db.Integer, nullable=True)
    projects = db.Column(db.Integer, nullable=True)
    hackathons = db.Column(db.Integer, nullable=True)
    certifications = db.Column(db.Integer, nullable=True)
    backlogs = db.Column(db.Integer, nullable=True)
    attendance = db.Column(db.Float, nullable=True)
    aptitude_score = db.Column(db.Integer, nullable=True)
    technical_score = db.Column(db.Integer, nullable=True)
    resume_score = db.Column(db.Integer, nullable=True)
    
    # Reasons influencing prediction
    key_reasons = db.Column(db.Text, nullable=True)
    suggestions = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'prediction_result': self.prediction_result,
            'probability': self.probability,
            'confidence': self.confidence,
            'model_used': self.model_used,
            'cgpa': self.cgpa,
            'department': self.department,
            'key_reasons': self.key_reasons,
            'suggestions': self.suggestions,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Company(db.Model):
    """Company eligibility criteria model"""
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), unique=True, nullable=False)
    min_cgpa = db.Column(db.Float, nullable=False, default=0)
    max_backlogs = db.Column(db.Integer, nullable=False, default=10)
    required_skills = db.Column(db.Text, nullable=True)  # Comma-separated
    required_certifications = db.Column(db.Text, nullable=True)
    min_aptitude = db.Column(db.Integer, nullable=False, default=0)
    min_technical = db.Column(db.Integer, nullable=False, default=0)
    min_communication = db.Column(db.Integer, nullable=False, default=0)
    min_projects = db.Column(db.Integer, nullable=False, default=0)
    min_internships = db.Column(db.Integer, nullable=False, default=0)
    allowed_departments = db.Column(db.Text, nullable=True)  # Comma-separated or "All"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'min_cgpa': self.min_cgpa,
            'max_backlogs': self.max_backlogs,
            'required_skills': self.required_skills,
            'required_certifications': self.required_certifications,
            'min_aptitude': self.min_aptitude,
            'min_technical': self.min_technical,
            'min_communication': self.min_communication,
            'min_projects': self.min_projects,
            'min_internships': self.min_internships,
            'allowed_departments': self.allowed_departments
        }


class MentorAlert(db.Model):
    """Mentor alert model"""
    __tablename__ = 'mentor_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    mentor_email = db.Column(db.String(120), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # low_cgpa, low_resume, low_skill, etc.
    alert_message = db.Column(db.Text, nullable=False)
    weak_areas = db.Column(db.Text, nullable=True)
    suggestions = db.Column(db.Text, nullable=True)
    prediction_result = db.Column(db.String(50), nullable=True)
    email_sent = db.Column(db.Integer, default=0)
    email_sent_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'mentor_email': self.mentor_email,
            'alert_type': self.alert_type,
            'alert_message': self.alert_message,
            'weak_areas': self.weak_areas,
            'suggestions': self.suggestions,
            'email_sent': self.email_sent,
            'email_sent_at': self.email_sent_at.isoformat() if self.email_sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ActivityLog(db.Model):
    """Activity log model"""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(20), nullable=False)  # 'admin' or 'student'
    user_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_type': self.user_type,
            'user_id': self.user_id,
            'action': self.action,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


def init_db(app):
    """Initialize database with default data"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        
        # Create default admin if not exists
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(
                username='admin',
                email='admin@placementpredictor.com'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin created: admin / admin123")
        
        print("✅ Database initialized successfully")
