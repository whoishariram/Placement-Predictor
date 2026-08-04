"""
Placement Predictor - Analysis API Routes
Resume analysis and company eligibility endpoints
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import os
from datetime import datetime

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'status': 'error', 'message': 'Auth required'}), 401
        return f(*args, **kwargs)
    return decorated


# ============================================
# RESUME ANALYSIS ENDPOINTS
# ============================================

@analysis_bp.route('/resume/analyze', methods=['POST'])
@token_required
def analyze_resume():
    """Upload and analyze a resume"""
    from config import Config

    if 'resume' not in request.files:
        return jsonify({'status': 'error', 'message': 'No resume file provided'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400

    # Validate extension
    allowed = {'pdf', 'docx', 'doc'}
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in allowed:
        return jsonify({'status': 'error', 'message': 'PDF or DOCX required'}), 400

    try:
        # Save file
        filename = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        filepath = os.path.join(Config.RESUMES_DIR, filename)
        os.makedirs(Config.RESUMES_DIR, exist_ok=True)
        file.save(filepath)

        # Analyze
        from analysis.resume_analysis import ResumeAnalyzer
        analyzer = ResumeAnalyzer()
        result = analyzer.analyze_resume(filepath)

        return jsonify({'status': 'success', 'analysis': result})

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Analysis failed: {str(e)}'}), 500


@analysis_bp.route('/resume/history', methods=['GET'])
@token_required
def get_resume_history():
    """Get resume analysis history"""
    return jsonify({
        'status': 'success',
        'history': [
            {'id': 1, 'filename': 'resume_v1.pdf', 'score': 72, 'date': '2024-03-15'},
            {'id': 2, 'filename': 'resume_v2.pdf', 'score': 85, 'date': '2024-03-20'},
        ]
    })


# ============================================
# COMPANY ELIGIBILITY ENDPOINTS
# ============================================

@analysis_bp.route('/company/check-eligibility', methods=['POST'])
@token_required
def check_eligibility():
    """Check student eligibility for companies"""
    from config import Config

    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    try:
        from analysis.company_eligibility import CompanyEligibilityChecker
        checker = CompanyEligibilityChecker(Config.COMPANIES_CSV_PATH)
        checker.load_companies()

        results = checker.check_eligibility(data)
        eligible = [r for r in results if r['match_percentage'] >= 50]

        return jsonify({
            'status': 'success',
            'all_companies': results,
            'eligible_companies': eligible,
            'eligible_count': len(eligible),
            'total_companies': len(results)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@analysis_bp.route('/company/list', methods=['GET'])
@token_required
def list_companies():
    """Get all companies with eligibility criteria"""
    from config import Config

    try:
        from analysis.company_eligibility import CompanyEligibilityChecker
        checker = CompanyEligibilityChecker(Config.COMPANIES_CSV_PATH)
        checker.load_companies()
        companies = checker.get_all_companies()
        return jsonify({'status': 'success', 'companies': companies})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@analysis_bp.route('/company/<string:company_name>', methods=['GET'])
@token_required
def get_company_details(company_name):
    """Get details of a specific company"""
    from config import Config

    try:
        from analysis.company_eligibility import CompanyEligibilityChecker
        checker = CompanyEligibilityChecker(Config.COMPANIES_CSV_PATH)
        checker.load_companies()
        details = checker.get_company_details(company_name)
        if details:
            return jsonify({'status': 'success', 'company': details})
        return jsonify({'status': 'error', 'message': 'Company not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@analysis_bp.route('/company/compare', methods=['GET'])
@token_required
def compare_companies():
    """Compare companies by difficulty"""
    from config import Config

    try:
        from analysis.company_eligibility import CompanyEligibilityChecker
        checker = CompanyEligibilityChecker(Config.COMPANIES_CSV_PATH)
        checker.load_companies()
        comparison = checker.compare_companies()
        return jsonify({'status': 'success', 'comparison': comparison})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
