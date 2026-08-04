"""
Placement Predictor - Company Eligibility Checker Module
Checks student eligibility against company requirements and manages company criteria
"""

import pandas as pd
import os
import json
from datetime import datetime


# Predefined skill categories for eligibility matching
SKILL_CATEGORIES = {
    'programming': ['python', 'java', 'c++', 'javascript', 'c#', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'typescript'],
    'web': ['react', 'angular', 'vue', 'node.js', 'django', 'flask', 'html', 'css', 'bootstrap', 'jquery'],
    'cloud': ['aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'terraform', 'jenkins'],
    'data': ['sql', 'mongodb', 'mysql', 'postgresql', 'machine learning', 'data science', 'tensorflow', 'pytorch'],
    'core_cs': ['data structures', 'algorithms', 'dbms', 'os', 'computer networks', 'oop', 'system design']
}


class CompanyEligibilityChecker:
    """Check student eligibility against company requirements"""

    def __init__(self, companies_csv_path=None):
        self.companies = []
        self.companies_csv_path = companies_csv_path

        if companies_csv_path is None:
            self.companies_csv_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'dataset', 'companies.csv'
            )

    def load_companies(self, filepath=None):
        """Load company eligibility criteria from CSV"""
        if filepath:
            self.companies_csv_path = filepath

        if not os.path.exists(self.companies_csv_path):
            print(f"⚠️  Companies file not found: {self.companies_csv_path}")
            # Use default companies
            self.companies = self._get_default_companies()
            return self.companies

        try:
            df = pd.read_csv(self.companies_csv_path)
            self.companies = df.to_dict('records')
            print(f"✅ Loaded {len(self.companies)} companies")
            return self.companies
        except Exception as e:
            print(f"❌ Error loading companies: {str(e)}")
            self.companies = self._get_default_companies()
            return self.companies

    def _get_default_companies(self):
        """Return default company eligibility data"""
        return [
            {
                'company_name': 'Google',
                'min_cgpa': 8.5, 'max_backlogs': 0,
                'required_skills': 'Python,Java,Data Structures,Algorithms,SQL',
                'required_certifications': 'AWS Certified,Google Cloud Certified',
                'min_aptitude': 80, 'min_technical': 85,
                'min_communication': 75, 'min_projects': 3, 'min_internships': 1,
                'allowed_departments': 'Computer Science,Information Technology,Artificial Intelligence & ML,Data Science'
            },
            {
                'company_name': 'Microsoft',
                'min_cgpa': 8.0, 'max_backlogs': 0,
                'required_skills': 'Python,C++,Java,Data Structures,Algorithms',
                'required_certifications': 'Microsoft Azure Certified',
                'min_aptitude': 78, 'min_technical': 82,
                'min_communication': 72, 'min_projects': 3, 'min_internships': 1,
                'allowed_departments': 'Computer Science,Information Technology,Artificial Intelligence & ML,Data Science'
            },
            {
                'company_name': 'Amazon',
                'min_cgpa': 7.5, 'max_backlogs': 1,
                'required_skills': 'Java,Python,AWS,SQL,Data Structures',
                'required_certifications': 'AWS Certified',
                'min_aptitude': 75, 'min_technical': 78,
                'min_communication': 70, 'min_projects': 3, 'min_internships': 1,
                'allowed_departments': 'Computer Science,Information Technology,Electronics & Communication,Artificial Intelligence & ML,Data Science'
            },
            {
                'company_name': 'Infosys',
                'min_cgpa': 6.0, 'max_backlogs': 2,
                'required_skills': 'Python,Java,SQL,DBMS',
                'required_certifications': '',
                'min_aptitude': 60, 'min_technical': 55,
                'min_communication': 55, 'min_projects': 2, 'min_internships': 0,
                'allowed_departments': 'Computer Science,Information Technology,Electronics & Communication,Electrical Engineering,Mechanical Engineering,Civil Engineering,Artificial Intelligence & ML,Data Science'
            },
            {
                'company_name': 'TCS',
                'min_cgpa': 5.5, 'max_backlogs': 3,
                'required_skills': 'Python,Java,SQL',
                'required_certifications': '',
                'min_aptitude': 55, 'min_technical': 50,
                'min_communication': 50, 'min_projects': 1, 'min_internships': 0,
                'allowed_departments': 'All'
            },
            {
                'company_name': 'Accenture',
                'min_cgpa': 6.5, 'max_backlogs': 2,
                'required_skills': 'Python,Java,SQL,Communication',
                'required_certifications': '',
                'min_aptitude': 60, 'min_technical': 55,
                'min_communication': 60, 'min_projects': 2, 'min_internships': 0,
                'allowed_departments': 'All'
            },
            {
                'company_name': 'Flipkart',
                'min_cgpa': 7.0, 'max_backlogs': 1,
                'required_skills': 'Python,Java,JavaScript,SQL,Data Structures',
                'required_certifications': '',
                'min_aptitude': 70, 'min_technical': 70,
                'min_communication': 65, 'min_projects': 3, 'min_internships': 1,
                'allowed_departments': 'Computer Science,Information Technology,Artificial Intelligence & ML,Data Science'
            },
            {
                'company_name': 'Goldman Sachs',
                'min_cgpa': 7.5, 'max_backlogs': 1,
                'required_skills': 'Python,Java,SQL,Data Structures,Algorithms',
                'required_certifications': '',
                'min_aptitude': 75, 'min_technical': 72,
                'min_communication': 70, 'min_projects': 3, 'min_internships': 1,
                'allowed_departments': 'Computer Science,Information Technology,Artificial Intelligence & ML,Data Science'
            },
            {
                'company_name': 'Adobe',
                'min_cgpa': 7.5, 'max_backlogs': 1,
                'required_skills': 'JavaScript,C++,Python,React,Data Structures',
                'required_certifications': '',
                'min_aptitude': 72, 'min_technical': 75,
                'min_communication': 68, 'min_projects': 3, 'min_internships': 1,
                'allowed_departments': 'Computer Science,Information Technology,Artificial Intelligence & ML,Data Science'
            },
            {
                'company_name': 'Deloitte',
                'min_cgpa': 6.5, 'max_backlogs': 2,
                'required_skills': 'Python,Java,SQL,Communication',
                'required_certifications': '',
                'min_aptitude': 65, 'min_technical': 60,
                'min_communication': 65, 'min_projects': 2, 'min_internships': 0,
                'allowed_departments': 'Computer Science,Information Technology,Electronics & Communication,Artificial Intelligence & ML,Data Science'
            }
        ]

    def check_eligibility(self, student_data, company=None):
        """
        Check a student's eligibility against a specific company or all companies

        Args:
            student_data: Dict of student information (cgpa, backlogs, skills, etc.)
            company: Company name to check (None = check all)

        Returns:
            List of eligibility results
        """
        if not self.companies:
            self.load_companies()

        results = []

        for comp in self.companies:
            if company and comp['company_name'].lower() != company.lower():
                continue

            eligibility = self._check_single_company(student_data, comp)
            results.append(eligibility)

        # Sort by eligibility score (most eligible first)
        results.sort(key=lambda x: x['match_percentage'], reverse=True)

        return results

    def _check_single_company(self, student_data, company):
        """
        Check eligibility for a single company

        Returns dict with eligibility details and match percentage
        """
        checks = {}
        total_weight = 0
        passed_weight = 0

        # CGPA Check (weight: 25)
        if 'cgpa' in student_data:
            cgpa = float(student_data.get('cgpa', 0))
            min_cgpa = float(company.get('min_cgpa', 0))
            checks['cgpa'] = {
                'required': min_cgpa,
                'student_value': cgpa,
                'passed': cgpa >= min_cgpa,
                'weight': 25
            }
            total_weight += 25
            if cgpa >= min_cgpa:
                passed_weight += 25
            elif cgpa >= min_cgpa * 0.9:  # Close to cutoff
                passed_weight += 15

        # Backlogs Check (weight: 20)
        if 'backlogs' in student_data:
            backlogs = int(student_data.get('backlogs', 0))
            max_backlogs = int(company.get('max_backlogs', 10))
            checks['backlogs'] = {
                'required': f"≤ {max_backlogs}",
                'student_value': backlogs,
                'passed': backlogs <= max_backlogs,
                'weight': 20
            }
            total_weight += 20
            if backlogs <= max_backlogs:
                passed_weight += 20
            elif backlogs <= max_backlogs + 1:
                passed_weight += 10  # Close

        # Department Check (weight: 10)
        if 'department' in student_data:
            dept = student_data.get('department', '')
            allowed = str(company.get('allowed_departments', 'All'))
            dept_match = allowed == 'All' or dept in allowed.split(',')
            checks['department'] = {
                'required': allowed,
                'student_value': dept,
                'passed': dept_match,
                'weight': 10
            }
            total_weight += 10
            if dept_match:
                passed_weight += 10

        # Aptitude Score Check (weight: 10)
        if 'aptitude_score' in student_data:
            aptitude = int(student_data.get('aptitude_score', 0))
            min_aptitude = int(company.get('min_aptitude', 0))
            checks['aptitude'] = {
                'required': min_aptitude,
                'student_value': aptitude,
                'passed': aptitude >= min_aptitude,
                'weight': 10
            }
            total_weight += 10
            if aptitude >= min_aptitude:
                passed_weight += 10
            elif aptitude >= min_aptitude * 0.85:
                passed_weight += 5

        # Technical Score Check (weight: 10)
        if 'technical_score' in student_data:
            tech = int(student_data.get('technical_score', 0))
            min_tech = int(company.get('min_technical', 0))
            checks['technical'] = {
                'required': min_tech,
                'student_value': tech,
                'passed': tech >= min_tech,
                'weight': 10
            }
            total_weight += 10
            if tech >= min_tech:
                passed_weight += 10
            elif tech >= min_tech * 0.85:
                passed_weight += 5

        # Communication Check (weight: 5)
        if 'communication_skill' in student_data:
            comm = int(student_data.get('communication_skill', 0))
            min_comm = int(company.get('min_communication', 0))
            checks['communication'] = {
                'required': min_comm,
                'student_value': comm,
                'passed': comm >= min_comm,
                'weight': 5
            }
            total_weight += 5
            if comm >= min_comm:
                passed_weight += 5

        # Projects Check (weight: 5)
        if 'projects' in student_data:
            projects = int(student_data.get('projects', 0))
            min_projects = int(company.get('min_projects', 0))
            checks['projects'] = {
                'required': min_projects,
                'student_value': projects,
                'passed': projects >= min_projects,
                'weight': 5
            }
            total_weight += 5
            if projects >= min_projects:
                passed_weight += 5

        # Internships Check (weight: 5)
        if 'internships' in student_data:
            internships = int(student_data.get('internships', 0))
            min_internships = int(company.get('min_internships', 0))
            checks['internships'] = {
                'required': min_internships,
                'student_value': internships,
                'passed': internships >= min_internships,
                'weight': 5
            }
            total_weight += 5
            if internships >= min_internships:
                passed_weight += 5

        # Skills Check (weight: 10)
        required_skills = str(company.get('required_skills', ''))
        if required_skills:
            required_list = [s.strip().lower() for s in required_skills.split(',') if s.strip()]

            # Normalize student skills to a single lowercase text blob for substring matching
            raw_skills = student_data.get('skills', '')
            if isinstance(raw_skills, list):
                student_skills_text = ' '.join(s.lower() for s in raw_skills)
            elif isinstance(raw_skills, str):
                student_skills_text = raw_skills.lower()
            else:
                # Fallback: search all student data fields
                student_skills_text = ' '.join(str(v).lower() for v in student_data.values())

            # Use substring matching so multi-word skills like "data structures" match
            skills_matched = [s for s in required_list if s in student_skills_text]
            skills_match_pct = len(skills_matched) / len(required_list) * 100 if required_list else 100

            checks['skills'] = {
                'required': required_list,
                'student_skills_matched': skills_matched,
                'matched_count': len(skills_matched),
                'total_required': len(required_list),
                'passed': skills_match_pct >= 60,  # 60% of skills required
                'weight': 10
            }
            total_weight += 10
            if skills_match_pct >= 60:
                passed_weight += 10
            elif skills_match_pct >= 40:
                passed_weight += 5

        # Calculate overall match percentage
        match_percentage = round((passed_weight / total_weight * 100) if total_weight > 0 else 0, 2)

        # Determine overall eligibility status
        all_critical_passed = all(
            check['passed'] for key, check in checks.items()
            if key in ['cgpa', 'backlogs', 'department']
        )

        if all_critical_passed and match_percentage >= 70:
            status = 'Eligible ✅'
        elif match_percentage >= 50:
            status = 'Partially Eligible ⚠️'
        else:
            status = 'Not Eligible ❌'

        # Generate failed criteria details
        failed_criteria = [
            key for key, check in checks.items()
            if not check['passed']
        ]

        return {
            'company_name': company['company_name'],
            'status': status,
            'match_percentage': match_percentage,
            'passed_checks': len(checks) - len(failed_criteria),
            'total_checks': len(checks),
            'checks': checks,
            'failed_criteria': failed_criteria,
            'all_critical_passed': all_critical_passed,
            'checked_at': datetime.now().isoformat()
        }

    def get_eligible_companies(self, student_data, min_match=50):
        """
        Get all companies a student is eligible for

        Args:
            student_data: Dict of student information
            min_match: Minimum match percentage required

        Returns:
            List of eligible companies with details
        """
        results = self.check_eligibility(student_data)

        eligible = [
            r for r in results
            if r['match_percentage'] >= min_match
        ]

        return eligible

    def get_ineligible_reasons(self, student_data, company_name):
        """
        Get specific reasons why a student is not eligible for a company

        Args:
            student_data: Dict of student info
            company_name: Name of company

        Returns:
            Dict with reasons and improvement suggestions
        """
        results = self.check_eligibility(student_data, company_name)

        if not results:
            return {
                'company_name': company_name,
                'error': 'Company not found'
            }

        result = results[0]
        reasons = []
        suggestions = []

        for check_name, check in result.get('checks', {}).items():
            if not check.get('passed', True):
                if check_name == 'cgpa':
                    gap = round(check['required'] - check['student_value'], 2)
                    reasons.append(f"CGPA is {check['student_value']}, needs {check['required']}+")
                    suggestions.append(f"Improve CGPA by {gap} points")

                elif check_name == 'backlogs':
                    reasons.append(f"Has {check['student_value']} backlogs, max allowed is {check['required']}")
                    suggestions.append("Clear backlogs to improve eligibility")

                elif check_name == 'department':
                    reasons.append(f"Department '{check['student_value']}' not in allowed list")
                    suggestions.append("Check with TPO if department is considered")

                elif check_name == 'aptitude':
                    gap = check['required'] - check['student_value']
                    reasons.append(f"Aptitude score is {check['student_value']}, needs {check['required']}+")
                    suggestions.append(f"Improve aptitude score by {gap} points")

                elif check_name == 'technical':
                    gap = check['required'] - check['student_value']
                    reasons.append(f"Technical score is {check['student_value']}, needs {check['required']}+")
                    suggestions.append(f"Strengthen technical skills to improve by {gap} points")

                elif check_name == 'communication':
                    gap = check['required'] - check['student_value']
                    reasons.append(f"Communication score is {check['student_value']}, needs {check['required']}+")

                elif check_name == 'projects':
                    gap = check['required'] - check['student_value']
                    reasons.append(f"Has {check['student_value']} projects, needs {check['required']}+")
                    suggestions.append(f"Build {gap} more projects")

                elif check_name == 'internships':
                    gap = check['required'] - check['student_value']
                    reasons.append(f"Has {check['student_value']} internships, needs {check['required']}+")
                    suggestions.append("Gain internship experience")

                elif check_name == 'skills':
                    matched = check.get('matched_count', 0)
                    total = check.get('total_required', 0)
                    missing = [s for s in check.get('required', [])
                              if s not in check.get('student_skills_matched', [])]
                    reasons.append(f"Matched {matched}/{total} required skills")
                    suggestions.append(f"Learn: {', '.join(missing[:5])}")

        return {
            'company_name': company_name,
            'eligible': result['match_percentage'] >= 70 and result.get('all_critical_passed', False),
            'match_percentage': result['match_percentage'],
            'reasons': reasons,
            'suggestions': suggestions,
            'status': result['status']
        }

    def add_company(self, company_data):
        """
        Add a new company eligibility criteria

        Args:
            company_data: Dict with company requirements

        Returns:
            Added company dict
        """
        # Validate required fields
        required_fields = ['company_name']
        for field in required_fields:
            if field not in company_data:
                raise ValueError(f"Missing required field: {field}")

        # Set defaults
        company = {
            'company_name': company_data['company_name'],
            'min_cgpa': float(company_data.get('min_cgpa', 0)),
            'max_backlogs': int(company_data.get('max_backlogs', 10)),
            'required_skills': company_data.get('required_skills', ''),
            'required_certifications': company_data.get('required_certifications', ''),
            'min_aptitude': int(company_data.get('min_aptitude', 0)),
            'min_technical': int(company_data.get('min_technical', 0)),
            'min_communication': int(company_data.get('min_communication', 0)),
            'min_projects': int(company_data.get('min_projects', 0)),
            'min_internships': int(company_data.get('min_internships', 0)),
            'allowed_departments': company_data.get('allowed_departments', 'All')
        }

        # Check for duplicate
        self.companies = [c for c in self.companies
                         if c['company_name'].lower() != company['company_name'].lower()]

        self.companies.append(company)
        self._save_companies_csv()

        return company

    def update_company(self, company_name, updated_data):
        """
        Update existing company criteria

        Args:
            company_name: Name of company to update
            updated_data: New data dict

        Returns:
            Updated company dict or None if not found
        """
        for i, comp in enumerate(self.companies):
            if comp['company_name'].lower() == company_name.lower():
                for key, value in updated_data.items():
                    if key in comp and key != 'company_name':
                        comp[key] = value
                self.companies[i] = comp
                self._save_companies_csv()
                return comp

        return None

    def delete_company(self, company_name):
        """
        Delete a company from the list

        Args:
            company_name: Name of company to delete

        Returns:
            bool: True if deleted, False if not found
        """
        original_count = len(self.companies)
        self.companies = [c for c in self.companies
                         if c['company_name'].lower() != company_name.lower()]

        if len(self.companies) < original_count:
            self._save_companies_csv()
            return True
        return False

    def _save_companies_csv(self):
        """Save companies list to CSV"""
        try:
            df = pd.DataFrame(self.companies)
            os.makedirs(os.path.dirname(self.companies_csv_path), exist_ok=True)
            df.to_csv(self.companies_csv_path, index=False)
            return True
        except Exception as e:
            print(f"❌ Error saving companies: {str(e)}")
            return False

    def get_company_details(self, company_name):
        """Get details of a specific company"""
        for comp in self.companies:
            if comp['company_name'].lower() == company_name.lower():
                return comp
        return None

    def get_all_companies(self):
        """Get all companies with basic info"""
        return [
            {
                'id': i + 1,
                'company_name': c['company_name'],
                'min_cgpa': c.get('min_cgpa', 0),
                'max_backlogs': c.get('max_backlogs', 10),
                'min_aptitude': c.get('min_aptitude', 0),
                'min_technical': c.get('min_technical', 0),
                'allowed_departments': c.get('allowed_departments', 'All'),
                'department_count': len(str(c.get('allowed_departments', '')).split(',')),
                'skills_required': c.get('required_skills', '').split(',') if c.get('required_skills') else []
            }
            for i, c in enumerate(self.companies)
        ]

    def get_eligibility_statistics(self, students_data):
        """
        Get eligibility statistics across all companies for a set of students

        Args:
            students_data: List of student dicts or DataFrame

        Returns:
            Dict with statistics
        """
        if isinstance(students_data, pd.DataFrame):
            students_data = students_data.to_dict('records')

        stats = {
            'total_students': len(students_data),
            'total_companies': len(self.companies),
            'company_stats': [],
            'department_eligibility': {}
        }

        for company in self.companies:
            eligible_count = 0
            eligible_students = []

            for student in students_data:
                result = self._check_single_company(student, company)
                if result['match_percentage'] >= 70 and result.get('all_critical_passed', False):
                    eligible_count += 1
                    eligible_students.append(student.get('student_id', ''))

            stats['company_stats'].append({
                'company_name': company['company_name'],
                'eligible_count': eligible_count,
                'eligible_percentage': round(eligible_count / len(students_data) * 100, 2) if students_data else 0,
                'min_cgpa': company.get('min_cgpa', 0)
            })

        return stats

    def compare_companies(self):
        """Get comparison data for all companies"""
        comparison = []
        for company in self.companies:
            comparison.append({
                'company_name': company['company_name'],
                'min_cgpa': company.get('min_cgpa', 0),
                'max_backlogs': company.get('max_backlogs', 10),
                'min_aptitude': company.get('min_aptitude', 0),
                'min_technical': company.get('min_technical', 0),
                'min_communication': company.get('min_communication', 0),
                'min_projects': company.get('min_projects', 0),
                'min_internships': company.get('min_internships', 0),
                'difficulty_score': self._calculate_difficulty(company)
            })

        return sorted(comparison, key=lambda x: x['difficulty_score'], reverse=True)

    def _calculate_difficulty(self, company):
        """Calculate company difficulty score (0-100)"""
        score = 0
        score += min(float(company.get('min_cgpa', 0)) * 5, 30)  # CGPA: max 30
        score += (10 - min(int(company.get('max_backlogs', 10)), 10)) * 2  # Backlogs: max 20
        score += float(company.get('min_aptitude', 0)) * 0.2  # Aptitude: max 20
        score += float(company.get('min_technical', 0)) * 0.2  # Technical: max 20
        score += float(company.get('min_communication', 0)) * 0.1  # Communication: max 10

        dept = company.get('allowed_departments', 'All')
        if dept != 'All':
            score += 10  # Restricted departments = harder

        return round(min(score, 100), 2)


def check_student_eligibility(student_data, company_name=None, companies_csv=None):
    """
    Convenience function to check student eligibility

    Args:
        student_data: Dict with student info
        company_name: Optional company filter
        companies_csv: Path to companies CSV

    Returns:
        Eligibility results
    """
    checker = CompanyEligibilityChecker(companies_csv)
    checker.load_companies()
    return checker.check_eligibility(student_data, company_name)


if __name__ == '__main__':
    print("=" * 60)
    print("🏢 COMPANY ELIGIBILITY CHECKER TEST")
    print("=" * 60)

    # Initialize checker
    checker = CompanyEligibilityChecker()
    checker.load_companies()

    # Test student
    test_student = {
        'student_id': 'TEST001',
        'name': 'Test Student',
        'department': 'Computer Science',
        'cgpa': 8.2,
        'backlogs': 0,
        'aptitude_score': 78,
        'technical_score': 80,
        'communication_skill': 75,
        'projects': 4,
        'internships': 2,
        'skills': 'Python,Java,JavaScript,React,SQL,Data Structures'
    }

    print(f"\n👤 Student: {test_student['name']}")
    print(f"   CGPA: {test_student['cgpa']}, Dept: {test_student['department']}\n")

    # Check all companies
    print("📊 Eligibility Results:")
    print("-" * 80)
    results = checker.check_eligibility(test_student)

    for result in results:
        icon = "✅" if "Eligible" in result['status'] else "⚠️" if "Partially" in result['status'] else "❌"
        print(f"   {icon} {result['company_name']:<20} | "
              f"Match: {result['match_percentage']:>5.1f}% | "
              f"{result['status']}")
    print("-" * 80)

    # Get eligible only
    eligible = checker.get_eligible_companies(test_student)
    print(f"\n✅ Eligible companies: {len(eligible)}/{len(results)}")

    # Show ineligible reasons
    print(f"\n📋 Detailed check for Google:")
    reasons = checker.get_ineligible_reasons(test_student, 'Google')
    if reasons.get('reasons'):
        for r in reasons['reasons']:
            print(f"   • {r}")
    if reasons.get('suggestions'):
        for s in reasons['suggestions']:
            print(f"   💡 {s}")
    else:
        print("   ✅ Meets all criteria!")

    # Compare companies
    print(f"\n📊 Company Difficulty Rankings:")
    comparison = checker.compare_companies()
    for i, comp in enumerate(comparison[:5], 1):
        print(f"   {i}. {comp['company_name']:<20} Difficulty: {comp['difficulty_score']:.1f}/100")
