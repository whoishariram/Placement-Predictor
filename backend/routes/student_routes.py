"""
Placement Predictor - Student API Routes
Handles all student-facing API endpoints
"""

import os
from flask import Blueprint, request, jsonify, session
from functools import wraps
from datetime import datetime

student_bp = Blueprint('student', __name__, url_prefix='/api/student')


def student_required(f):
    """Decorator to require student authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'status': 'error', 'message': 'Authentication required'}), 401
        # In production, validate token against database/store
        return f(*args, **kwargs)
    return decorated


@student_bp.route('/dashboard', methods=['GET'])
@student_required
def get_dashboard():
    """Get student dashboard data"""
    try:
        from models import Student, Prediction, db

        student_id = request.args.get('student_id', 1)
        student = Student.query.get(int(student_id)) if student_id else None

        if not student:
            # Return demo data
            return jsonify({
                'status': 'success',
                'dashboard': {
                    'profile': {
                        'name': 'Demo Student', 'student_id': 'STU2024001',
                        'department': 'Computer Science', 'year': 4, 'cgpa': 8.2,
                        'attendance': 92, 'projects': 4, 'internships': 2,
                        'programming_skill': 78, 'communication_skill': 72
                    },
                    'latest_prediction': {
                        'result': 'Placed 🎉', 'probability': 87.5, 'date': '2024-03-15'
                    },
                    'stats': {
                        'total_predictions': 5, 'eligible_companies': 8,
                        'resume_score': 72, 'placement_readiness': 'High'
                    }
                }
            })

        # Get latest prediction
        latest_pred = Prediction.query.filter_by(student_id=student.id)\
            .order_by(Prediction.created_at.desc()).first()

        return jsonify({
            'status': 'success',
            'dashboard': {
                'profile': student.to_dict(),
                'latest_prediction': latest_pred.to_dict() if latest_pred else None,
                'stats': {
                    'total_predictions': Prediction.query.filter_by(student_id=student.id).count(),
                    'eligible_companies': 8,
                    'resume_score': student.resume_score or 0
                }
            }
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@student_bp.route('/predict', methods=['POST'])
@student_required
def get_prediction():
    """Get placement prediction for a student"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        from ml.predict import predict_from_student_data

        result = predict_from_student_data(data)

        if result.get('status') == 'error':
            # Return demo prediction if model not available
            return jsonify({
                'status': 'success',
                'prediction': {
                    'prediction': 1 if data.get('cgpa', 0) >= 7 else 0,
                    'prediction_label': 'Placed 🎉' if data.get('cgpa', 0) >= 7 else 'Not Placed ❌',
                    'probability': round(min(95, max(10, (data.get('cgpa', 7) * 10) + 10)), 2),
                    'confidence': 85.5,
                    'model_used': 'Random Forest (Demo)',
                    'key_reasons': ['✅ Good academic profile', '✅ Strong skills'],
                    'suggestions': ['Continue building on your strengths'],
                    'status': 'success'
                }
            })

        # Save prediction to history
        try:
            from models import Prediction, db
            student_id = data.get('student_id')
            if student_id:
                from models import Student
                student = Student.query.filter_by(student_id=student_id).first()
                if student:
                    pred = Prediction(
                        student_id=student.id,
                        prediction_result=result['prediction'],
                        probability=result['probability'],
                        confidence=result.get('confidence', 0),
                        model_used=result.get('model_used', 'Unknown'),
                        cgpa=data.get('cgpa'),
                        department=data.get('department'),
                        key_reasons='\n'.join(result.get('key_reasons', [])),
                        suggestions='\n'.join(result.get('suggestions', []))
                    )
                    db.session.add(pred)
                    db.session.commit()
        except Exception:
            pass  # Non-critical

        return jsonify({'status': 'success', 'prediction': result})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@student_bp.route('/predictions', methods=['GET'])
@student_required
def get_prediction_history():
    """Get prediction history for a student"""
    from models import Prediction, Student

    try:
        student_id = request.args.get('student_id')
        if student_id:
            student = Student.query.filter_by(student_id=student_id).first()
            if student:
                predictions = Prediction.query.filter_by(student_id=student.id)\
                    .order_by(Prediction.created_at.desc()).limit(20).all()
                return jsonify({
                    'status': 'success',
                    'predictions': [p.to_dict() for p in predictions]
                })

        # Demo data
        return jsonify({
            'status': 'success',
            'predictions': [
                {
                    'id': 1, 'prediction_result': 1, 'probability': 87.5,
                    'confidence': 85.0, 'created_at': '2024-03-15T10:30:00',
                    'cgpa': 8.2, 'department': 'Computer Science'
                },
                {
                    'id': 2, 'prediction_result': 1, 'probability': 82.0,
                    'confidence': 80.0, 'created_at': '2024-02-20T14:00:00'
                }
            ]
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@student_bp.route('/upload-resume', methods=['POST'])
@student_required
def upload_resume():
    """Upload and analyze resume"""
    from config import Config

    if 'resume' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400

    # Validate file type
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in Config.ALLOWED_EXTENSIONS:
        return jsonify({'status': 'error', 'message': 'Invalid file type. Allowed: PDF, DOCX, PNG, JPG'}), 400

    try:
        # Save file
        filename = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        filepath = os.path.join(Config.RESUMES_DIR, filename)
        file.save(filepath)

        # Analyze resume
        from analysis.resume_analysis import analyze_resume_file
        result = analyze_resume_file(filepath)

        return jsonify({'status': 'success', 'analysis': result})

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to process resume: {str(e)}'}), 500


@student_bp.route('/eligible-companies', methods=['POST'])
@student_required
def get_eligible_companies():
    """Get companies the student is eligible for"""
    try:
        data = request.get_json() or {}
        student_data = {
            'cgpa': data.get('cgpa', 8.0),
            'backlogs': data.get('backlogs', 0),
            'department': data.get('department', 'Computer Science'),
            'aptitude_score': data.get('aptitude_score', 70),
            'technical_score': data.get('technical_score', 70),
            'communication_skill': data.get('communication_skill', 65),
            'projects': data.get('projects', 3),
            'internships': data.get('internships', 1),
            'skills': data.get('skills', 'Python,Java,SQL')
        }

        from analysis.company_eligibility import CompanyEligibilityChecker
        from config import Config

        checker = CompanyEligibilityChecker(Config.COMPANIES_CSV_PATH)
        checker.load_companies()

        results = checker.check_eligibility(student_data)
        eligible = [r for r in results if r['match_percentage'] >= 50]

        return jsonify({
            'status': 'success',
            'companies': eligible,
            'eligible_count': len(eligible),
            'total_companies': len(results)
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@student_bp.route('/profile', methods=['GET', 'PUT'])
@student_required
def handle_profile():
    """Get or update student profile"""
    from models import Student, db

    try:
        if request.method == 'GET':
            student_id = request.args.get('student_id')
            if student_id:
                student = Student.query.filter_by(student_id=student_id).first()
                if student:
                    return jsonify({'status': 'success', 'student': student.to_dict()})

            return jsonify({
                'status': 'success',
                'student': {
                    'name': 'Demo Student', 'student_id': 'STU2024001',
                    'email': 'demo@college.edu', 'department': 'Computer Science',
                    'year': 4, 'cgpa': 8.2, 'programming_skill': 78,
                    'communication_skill': 72, 'aptitude_score': 75,
                    'technical_score': 70, 'internships': 2, 'projects': 4,
                    'backlogs': 0, 'attendance': 92, 'resume_score': 72
                }
            })

        elif request.method == 'PUT':
            from auth.student_auth import StudentAuth
            data = request.get_json()
            auth = StudentAuth(db, Student)
            result = auth.update_profile(data.get('id'), data)
            return jsonify(result)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@student_bp.route('/notifications', methods=['GET'])
@student_required
def get_notifications():
    """Get student notifications"""
    return jsonify({
        'status': 'success',
        'notifications': [
            {'id': 1, 'type': 'info', 'message': 'New company registrations open', 'date': '2024-03-20', 'read': False},
            {'id': 2, 'type': 'success', 'message': 'Your resume analysis is ready', 'date': '2024-03-18', 'read': False},
            {'id': 3, 'type': 'warning', 'message': 'Placement training session tomorrow', 'date': '2024-03-15', 'read': True},
        ]
    })
