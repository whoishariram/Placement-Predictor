"""
Placement Predictor - Resume Analysis Module
Parses PDF resumes, extracts text, calculates scores, and suggests improvements
"""

import os
import re
import json
from datetime import datetime

# PDF Parsing Libraries
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    import pdfplumber
    PDFPLUMBER_SUPPORT = True
except ImportError:
    PDFPLUMBER_SUPPORT = False

try:
    from pdfminer.high_level import extract_text
    PDFMINER_SUPPORT = True
except ImportError:
    PDFMINER_SUPPORT = False


# Skill database for keyword matching
SKILL_DATABASE = {
    'programming_languages': [
        'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift',
        'kotlin', 'go', 'rust', 'typescript', 'scala', 'perl', 'r', 'matlab',
        'dart', 'lua', 'haskell', 'shell', 'bash', 'sql', 'pl/sql', 'c'
    ],
    'web_technologies': [
        'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
        'spring', 'spring boot', 'html', 'css', 'html5', 'css3', 'bootstrap',
        'tailwind', 'jquery', 'asp.net', 'php', 'laravel', 'next.js', 'nuxt.js',
        'svelte', 'gatsby', 'graphql', 'rest api', 'redux', 'webpack'
    ],
    'cloud_devops': [
        'aws', 'azure', 'google cloud', 'gcp', 'docker', 'kubernetes', 'jenkins',
        'terraform', 'ansible', 'chef', 'puppet', 'ci/cd', 'github actions',
        'gitlab ci', 'heroku', 'netlify', 'vercel', 'linux', 'unix'
    ],
    'data_science_ml': [
        'machine learning', 'deep learning', 'data science', 'tensorflow',
        'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
        'seaborn', 'tableau', 'power bi', 'nlp', 'computer vision', 'llm',
        'artificial intelligence', 'data analysis', 'statistics', 'big data',
        'hadoop', 'spark', 'sql', 'database', 'data mining'
    ],
    'databases': [
        'mysql', 'postgresql', 'mongodb', 'oracle', 'sqlite', 'redis',
        'cassandra', 'elasticsearch', 'mariadb', 'firebase', 'supabase',
        'dynamodb', 'couchdb', 'neo4j'
    ],
    'soft_skills': [
        'communication', 'leadership', 'teamwork', 'problem solving',
        'critical thinking', 'time management', 'presentation', 'public speaking',
        'project management', 'agile', 'scrum', 'analytical', 'adaptability',
        'collaboration', 'creativity', 'decision making'
    ],
    'certifications': [
        'aws certified', 'google cloud certified', 'microsoft certified',
        'oracle certified', 'cisco certified', 'comptia', 'pmp', 'scrum master',
        'azure certified', 'red hat', 'ceh', 'cissp', 'itil', 'prince2'
    ],
    'tools': [
        'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence', 'slack',
        'vscode', 'pycharm', 'eclipse', 'intellij', 'postman', 'docker',
        'kubernetes', 'jenkins', 'figma', 'photoshop', 'illustrator', 'canva'
    ],
    'domains': [
        'full stack', 'frontend', 'backend', 'devops', 'data science',
        'machine learning', 'artificial intelligence', 'cloud computing',
        'cybersecurity', 'blockchain', 'iot', 'mobile development',
        'web development', 'software engineering', 'database administration'
    ]
}


class ResumeAnalyzer:
    """Resume analysis engine for parsing and scoring PDF resumes"""

    def __init__(self):
        self.extracted_text = ""
        self.resume_data = {}
        self.skills_found = {}
        self.score_breakdown = {}
        self.total_score = 0
        self.file_path = None

    def extract_text_from_pdf(self, file_path):
        """
        Extract text from PDF resume using available PDF library

        Tries PyPDF2 -> pdfplumber -> pdfminer.six
        """
        self.file_path = file_path
        text = ""

        if not os.path.exists(file_path):
            return ""

        # Try PyPDF2 first
        if PDF_SUPPORT:
            try:
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                if text.strip():
                    self.extracted_text = text
                    return text
            except Exception:
                pass

        # Try pdfplumber next (better table handling)
        if PDFPLUMBER_SUPPORT:
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                if text.strip():
                    self.extracted_text = text
                    return text
            except Exception:
                pass

        # Try pdfminer as fallback
        if PDFMINER_SUPPORT:
            try:
                text = extract_text(file_path)
                if text.strip():
                    self.extracted_text = text
                    return text
            except Exception:
                pass

        # If all libraries fail, try basic extraction
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                # Try to decode as text (works for some text-based PDFs)
                text = content.decode('utf-8', errors='ignore')
                # Clean up PDF artifacts
                text = re.sub(r'[^\x20-\x7E\n]', ' ', text)
                if len(text.strip()) > 100:
                    self.extracted_text = text
                    return text
        except Exception:
            pass

        return text

    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX resume"""
        try:
            import docx
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            self.extracted_text = text
            return text
        except Exception:
            return ""

    def extract_text(self, file_path):
        """Extract text from resume file (PDF or DOCX)"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext == '.docx':
            return self.extract_text_from_docx(file_path)
        else:
            # Try as plain text
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                self.extracted_text = text
                return text
            except Exception:
                return ""

    def extract_contact_info(self):
        """Extract contact information from resume text"""
        text = self.extracted_text
        info = {'email': None, 'phone': None, 'linkedin': None, 'github': None}

        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            info['email'] = emails[0]

        # Phone (Indian and international formats)
        phone_patterns = [
            r'\b\d{10}\b',  # Simple 10-digit
            r'\b\+91[-\s]?\d{10}\b',  # Indian mobile
            r'\b\+1[-\s]?\d{3}[-\s]?\d{3}[-\s]?\d{4}\b',  # US format
            r'\b\d{3}[-\s]?\d{3}[-\s]?\d{4}\b',  # XXX-XXX-XXXX
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                info['phone'] = phones[0]
                break

        # LinkedIn
        linkedin_patterns = [
            r'linkedin\.com/in/[A-Za-z0-9_-]+',
            r'linkedin\.com/[A-Za-z0-9_-]+'
        ]
        for pattern in linkedin_patterns:
            links = re.findall(pattern, text, re.IGNORECASE)
            if links:
                info['linkedin'] = 'https://www.' + links[0]
                break

        # GitHub
        github_patterns = [
            r'github\.com/[A-Za-z0-9_-]+',
            r'github\.com/in/[A-Za-z0-9_-]+'
        ]
        for pattern in github_patterns:
            links = re.findall(pattern, text, re.IGNORECASE)
            if links:
                info['github'] = 'https://www.' + links[0]
                break

        self.resume_data['contact'] = info
        return info

    def extract_education(self):
        """Extract education details from resume"""
        text = self.extracted_text
        education = {
            'degrees': [],
            'institutions': [],
            'gpa_mentioned': False,
            'year_mentioned': False
        }

        # Common degree patterns
        degree_patterns = [
            r'(B\.?(Tech|E|Sc|A|Com))|(Bachelor(\'s)?\s+of\s+\w+)',
            r'(M\.?(Tech|E|Sc|A|Com))|(Master(\'s)?\s+of\s+\w+)',
            r'Ph\.?D\.?',
            r'MBA',
            r'BCA|MCA|BBA|BCom|MCom|BSc|MSc|BTech|MTech|BE|ME'
        ]

        for pattern in degree_patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            for f in found:
                if isinstance(f, tuple):
                    degree = f[0] if f[0] else f[1] if len(f) > 1 else None
                else:
                    degree = f
                if degree and degree.strip() not in education['degrees']:
                    education['degrees'].append(degree.strip())

        # Institution names (basic pattern)
        institution_keywords = [
            r'[A-Z][a-z]+ (Institute|University|College|School)',
            r'IIT [A-Za-z]+', r'NIT [A-Za-z]+', r'IIIT [A-Za-z]+',
            r'[A-Z][a-z]+ Institute of Technology',
            r'[A-Z][a-z]+ University'
        ]
        for pattern in institution_keywords:
            found = re.findall(pattern, text)
            for f in found:
                if f not in education['institutions']:
                    education['institutions'].append(f)

        # CGPA/GPA mention
        if re.search(r'\b(CGPA|GPA|CPI)\b', text, re.IGNORECASE):
            education['gpa_mentioned'] = True

        # Year mention
        if re.search(r'\b(20\d{2})\b', text):
            education['year_mentioned'] = True

        self.resume_data['education'] = education
        return education

    def extract_experience(self):
        """Extract work experience details from resume"""
        text = self.extracted_text
        experience = {
            'has_experience_section': False,
            'companies': [],
            'total_years_estimate': 0,
            'has_internships': False
        }

        # Check for experience section
        exp_section_patterns = [
            r'(EXPERIENCE|WORK EXPERIENCE|PROFESSIONAL EXPERIENCE|EMPLOYMENT)',
            r'(INTERNSHIP|INTERN)'
        ]
        for pattern in exp_section_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                experience['has_experience_section'] = True
                if 'INTERN' in pattern:
                    experience['has_internships'] = True
                break

        # Extract company names after experience section
        company_patterns = [
            r'(?:at|@|with)\s+([A-Z][A-Za-z\s]+)',
            r'(?:Company|Organization):\s*([A-Z][A-Za-z\s]+)',
        ]

        # Known companies from text
        known_companies = [
            'Google', 'Microsoft', 'Amazon', 'Apple', 'Meta', 'Infosys',
            'TCS', 'Wipro', 'Accenture', 'Deloitte', 'Goldman Sachs',
            'JP Morgan', 'Flipkart', 'Uber', 'Adobe', 'IBM', 'Oracle',
            'Intel', 'Cisco', 'Dell', 'HP', 'Samsung', 'Salesforce'
        ]
        for company in known_companies:
            if company.lower() in text.lower():
                if company not in experience['companies']:
                    experience['companies'].append(company)

        # Extract year ranges (e.g., 2020 - 2022)
        year_ranges = re.findall(r'20\d{2}\s*[-–to]+\s*(?:20\d{2}|Present|Current)', text, re.IGNORECASE)
        if year_ranges:
            total_years = 0
            for range_str in year_ranges:
                years = re.findall(r'20\d{2}', range_str)
                if len(years) == 2:
                    try:
                        total_years += int(years[1]) - int(years[0])
                    except ValueError:
                        pass
            experience['total_years_estimate'] = total_years

        # Detect if any work duration mentions
        if re.search(r'\d+\+?\s*(years?|yrs?)', text, re.IGNORECASE):
            matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)', text, re.IGNORECASE)
            if matches:
                experience['total_years_estimate'] = max(
                    experience['total_years_estimate'],
                    int(matches[0])
                )

        self.resume_data['experience'] = experience
        return experience

    def extract_skills(self):
        """Extract skills from resume text using skill database"""
        text = self.extracted_text.lower()
        skills_found = {
            'programming_languages': [],
            'web_technologies': [],
            'cloud_devops': [],
            'data_science_ml': [],
            'databases': [],
            'soft_skills': [],
            'certifications': [],
            'tools': [],
            'domains': []
        }

        for category, skills in SKILL_DATABASE.items():
            for skill in skills:
                # Use word boundary matching for accuracy
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text, re.IGNORECASE):
                    skills_found[category].append(skill)

        self.skills_found = skills_found
        self.resume_data['skills'] = skills_found

        # Calculate skills metrics
        total_skills = sum(len(v) for v in skills_found.values())
        self.resume_data['total_skills_found'] = total_skills
        self.resume_data['skill_categories_covered'] = sum(
            1 for v in skills_found.values() if v
        )

        return skills_found

    def extract_projects(self):
        """Extract project information from resume"""
        text = self.extracted_text
        projects = {
            'has_projects_section': False,
            'project_count_estimate': 0,
            'project_keywords_found': []
        }

        # Check for project section
        if re.search(r'(PROJECTS|PROJECT|ACADEMIC PROJECTS|PERSONAL PROJECTS)', text, re.IGNORECASE):
            projects['has_projects_section'] = True

        # Count project mentions
        project_mentions = re.findall(
            r'(?:Project|Project)[:\s-]+["\']?([^"\'\n]{10,80})',
            text, re.IGNORECASE
        )
        projects['project_count_estimate'] = max(
            len(project_mentions),
            len(re.findall(r'(?:^|\n)\s*[-•*]\s+(?:Built|Developed|Created|Designed|Implemented)',
                           text, re.MULTILINE))
        )

        # Limit to reasonable range
        projects['project_count_estimate'] = min(projects['project_count_estimate'], 15)

        # Check for project-related keywords
        project_keywords = [
            'developed', 'built', 'created', 'designed', 'implemented',
            'deployed', 'managed', 'led', 'architected', 'engineered',
            'optimized', 'automated', 'integrated', 'configured', 'migrated'
        ]
        for kw in project_keywords:
            if re.search(r'\b' + kw + r'\b', text, re.IGNORECASE):
                projects['project_keywords_found'].append(kw)

        self.resume_data['projects'] = projects
        return projects

    def extract_certifications(self):
        """Extract certification information"""
        text = self.extracted_text
        certs = {
            'certifications_found': [],
            'certification_count': 0
        }

        # Check for certification section
        if re.search(r'(CERTIFICATIONS|CERTIFICATION|CERTIFICATES|CERTIFICATE)', text, re.IGNORECASE):
            # Extract certification names
            cert_pattern = r'(?:^|\n)\s*[-•*]\s*([^,\n]{10,100})'
            # Look after certification section header
            sections = re.split(r'(?:CERTIFICATIONS|CERTIFICATION|CERTIFICATES|CERTIFICATE)', text, flags=re.IGNORECASE)
            if len(sections) > 1:
                cert_section = sections[1][:500]  # First 500 chars after section
                certs_found = re.findall(cert_pattern, cert_section, re.MULTILINE)
                for c in certs_found:
                    c = c.strip()
                    if len(c) > 5 and c not in certs['certifications_found']:
                        certs['certifications_found'].append(c)

        # Also match known certification names in text
        for cert in SKILL_DATABASE['certifications']:
            if cert.lower() in text.lower() and cert not in certs['certifications_found']:
                certs['certifications_found'].append(cert)

        certs['certification_count'] = len(certs['certifications_found'])
        self.resume_data['certifications'] = certs
        return certs

    def extract_achievements(self):
        """Extract achievements and awards"""
        text = self.extracted_text
        achievements = {
            'has_achievements_section': False,
            'achievements_found': [],
            'achievement_count': 0
        }

        if re.search(r'(ACHIEVEMENTS|ACHIEVEMENT|AWARDS|HONORS|RECOGNITION)', text, re.IGNORECASE):
            achievements['has_achievements_section'] = True

        # Count achievement-related sentences
        achievement_patterns = [
            r'(?:won|awarded|achieved|ranked|secured|received|honored|recognized)',
            r'(?:first|second|third)\s+(?:prize|place|rank|position)',
            r'(?:gold|silver|bronze)\s*(?:medal|prize)?',
        ]
        for pattern in achievement_patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            achievements['achievements_found'].extend(found)

        achievements['achievement_count'] = len(set(achievements['achievements_found']))
        self.resume_data['achievements'] = achievements
        return achievements

    def calculate_resume_score(self):
        """
        Calculate comprehensive resume score (0-100)

        Scoring criteria:
        - Contact Info: 5 points (email, phone, LinkedIn)
        - Education: 15 points (degrees, institutions, GPA)
        - Skills: 30 points (technical skills, categories)
        - Experience: 20 points (internships, work exp, years)
        - Projects: 15 points (project count, keywords)
        - Certifications: 10 points (cert count)
        - Achievements: 5 points (awards, recognitions)
        """
        score_breakdown = {
            'contact_info': self._score_contact_info(),
            'education': self._score_education(),
            'skills': self._score_skills(),
            'experience': self._score_experience(),
            'projects': self._score_projects(),
            'certifications': self._score_certifications(),
            'achievements': self._score_achievements(),
            'formatting': self._score_formatting()
        }

        self.score_breakdown = score_breakdown
        self.total_score = sum(score_breakdown.values())
        self.resume_data['total_score'] = self.total_score
        self.resume_data['score_breakdown'] = score_breakdown
        self.resume_data['score_grade'] = self._get_grade(self.total_score)

        return self.total_score

    def _score_contact_info(self):
        """Score contact information section (max 5 points)"""
        score = 0
        contact = self.resume_data.get('contact', {})

        if contact.get('email'):
            score += 2
        if contact.get('phone'):
            score += 1
        if contact.get('linkedin'):
            score += 1
        if contact.get('github'):
            score += 1

        return score

    def _score_education(self):
        """Score education section (max 15 points)"""
        score = 0
        education = self.resume_data.get('education', {})

        degrees = education.get('degrees', [])
        if len(degrees) >= 2:
            score += 5
        elif len(degrees) == 1:
            score += 3

        institutions = education.get('institutions', [])
        if len(institutions) >= 2:
            score += 5
        elif len(institutions) == 1:
            score += 3

        if education.get('gpa_mentioned'):
            score += 3

        if education.get('year_mentioned'):
            score += 2

        return min(score, 15)

    def _score_skills(self):
        """Score skills section (max 30 points)"""
        score = 0
        skills = self.skills_found

        # Points for each skill category
        category_weights = {
            'programming_languages': 6,
            'web_technologies': 4,
            'cloud_devops': 4,
            'data_science_ml': 5,
            'databases': 4,
            'soft_skills': 3,
            'certifications': 2,
            'tools': 1,
            'domains': 1
        }

        for category, weight in category_weights.items():
            skills_in_category = skills.get(category, [])
            if skills_in_category:
                # Proportional score based on skills found
                max_skills = 5  # Max skills considered per category
                skill_count = min(len(skills_in_category), max_skills)
                score += (skill_count / max_skills) * weight

        return min(int(score), 30)

    def _score_experience(self):
        """Score experience section (max 20 points)"""
        score = 0
        experience = self.resume_data.get('experience', {})

        if experience.get('has_experience_section'):
            score += 5

        if experience.get('has_internships'):
            score += 5

        companies = experience.get('companies', [])
        score += min(len(companies) * 2, 5)

        years = experience.get('total_years_estimate', 0)
        score += min(years * 2, 5)

        return min(score, 20)

    def _score_projects(self):
        """Score projects section (max 15 points)"""
        score = 0
        projects = self.resume_data.get('projects', {})

        if projects.get('has_projects_section'):
            score += 5

        # Project count
        project_count = projects.get('project_count_estimate', 0)
        if project_count >= 4:
            score += 5
        elif project_count >= 2:
            score += 3
        elif project_count >= 1:
            score += 1

        # Action keywords
        keywords = projects.get('project_keywords_found', [])
        score += min(len(keywords), 5)

        return min(score, 15)

    def _score_certifications(self):
        """Score certifications section (max 10 points)"""
        score = 0
        certs = self.resume_data.get('certifications', {})
        count = certs.get('certification_count', 0)

        if count >= 3:
            score = 10
        elif count == 2:
            score = 7
        elif count == 1:
            score = 4
        elif certs.get('certifications_found'):
            score = 2

        return score

    def _score_achievements(self):
        """Score achievements section (max 5 points)"""
        score = 0
        achievements = self.resume_data.get('achievements', {})

        if achievements.get('has_achievements_section'):
            score += 2

        count = achievements.get('achievement_count', 0)
        score += min(count, 3)

        return score

    def _score_formatting(self):
        """Score resume formatting and completeness (max 5 points)"""
        score = 0
        text = self.extracted_text

        # Check for sections
        sections = ['EDUCATION', 'SKILLS', 'EXPERIENCE', 'PROJECTS']
        found_sections = sum(1 for s in sections if re.search(r'\b' + s + r'\b', text, re.IGNORECASE))
        score += found_sections

        # Check overall length (good resume should be 300-800 words for students)
        word_count = len(text.split())
        if 300 <= word_count <= 1000:
            score += 1
        elif word_count > 200:
            score += 0.5

        return int(min(score, 5))

    def _get_grade(self, score):
        """Get letter grade for resume score"""
        if score >= 85:
            return 'A+', 'Excellent Resume'
        elif score >= 75:
            return 'A', 'Very Good Resume'
        elif score >= 65:
            return 'B+', 'Good Resume'
        elif score >= 55:
            return 'B', 'Average Resume'
        elif score >= 45:
            return 'C', 'Needs Improvement'
        else:
            return 'D', 'Significant Improvement Needed'

    def generate_suggestions(self):
        """Generate improvement suggestions based on analysis"""
        suggestions = []
        score = self.resume_data
        total = self.total_score

        # Contact info suggestions
        contact = score.get('contact', {})
        if not contact.get('email'):
            suggestions.append({
                'category': 'Contact',
                'priority': 'High',
                'suggestion': 'Add your email address'
            })
        if not contact.get('phone'):
            suggestions.append({
                'category': 'Contact',
                'priority': 'Medium',
                'suggestion': 'Add your phone number'
            })
        if not contact.get('linkedin'):
            suggestions.append({
                'category': 'Contact',
                'priority': 'Medium',
                'suggestion': 'Add LinkedIn profile URL - many recruiters look for this'
            })
        if not contact.get('github'):
            suggestions.append({
                'category': 'Contact',
                'priority': 'Low',
                'suggestion': 'Add GitHub profile to showcase your projects'
            })

        # Education suggestions
        education = score.get('education', {})
        if not education.get('gpa_mentioned'):
            suggestions.append({
                'category': 'Education',
                'priority': 'Medium',
                'suggestion': 'Include your CGPA/GPA if it\'s above 7.0'
            })
        if len(education.get('degrees', [])) < 2:
            suggestions.append({
                'category': 'Education',
                'priority': 'Low',
                'suggestion': 'Clearly mention your degree name and specialization'
            })

        # Skills suggestions
        skill_categories = score.get('skills', {})
        missing_categories = []
        for category, skills in skill_categories.items():
            if not skills and category in ['programming_languages', 'web_technologies', 'databases']:
                missing_categories.append(category.replace('_', ' ').title())

        for cat in missing_categories:
            suggestions.append({
                'category': 'Skills',
                'priority': 'High' if cat == 'Programming Languages' else 'Medium',
                'suggestion': f'Add your {cat} skills to the resume'
            })

        total_skills = score.get('total_skills_found', 0)
        if total_skills < 5:
            suggestions.append({
                'category': 'Skills',
                'priority': 'High',
                'suggestion': 'List more technical skills relevant to your target roles (aim for 10+)'
            })

        # Experience suggestions
        experience = score.get('experience', {})
        if not experience.get('has_experience_section'):
            suggestions.append({
                'category': 'Experience',
                'priority': 'High',
                'suggestion': 'Add an Experience section detailing internships and work experience'
            })
        if not experience.get('has_internships'):
            suggestions.append({
                'category': 'Experience',
                'priority': 'Medium',
                'suggestion': 'Include internship details with responsibilities and achievements'
            })

        # Project suggestions
        projects = score.get('projects', {})
        if not projects.get('has_projects_section'):
            suggestions.append({
                'category': 'Projects',
                'priority': 'High',
                'suggestion': 'Add a Projects section highlighting 2-3 key projects'
            })
        elif projects.get('project_count_estimate', 0) < 2:
            suggestions.append({
                'category': 'Projects',
                'priority': 'Medium',
                'suggestion': 'Add more projects (aim for 3-5) with tech stack descriptions'
            })

        # Action verb suggestions
        keywords = projects.get('project_keywords_found', [])
        strong_verbs = ['developed', 'built', 'designed', 'implemented', 'deployed']
        missing_verbs = [v for v in strong_verbs if v not in keywords]
        if missing_verbs:
            suggestions.append({
                'category': 'Projects',
                'priority': 'Medium',
                'suggestion': f'Use strong action verbs like: {", ".join(missing_verbs[:3])}'
            })

        # Certification suggestions
        certs = score.get('certifications', {})
        if certs.get('certification_count', 0) < 2:
            suggestions.append({
                'category': 'Certifications',
                'priority': 'Low',
                'suggestion': 'Add relevant certifications (AWS, Google Cloud, Coursera, etc.)'
            })

        # Achievement suggestions
        achievements = score.get('achievements', {})
        if not achievements.get('has_achievements_section'):
            suggestions.append({
                'category': 'Achievements',
                'priority': 'Low',
                'suggestion': 'Add an Achievements section for awards, hackathon wins, or recognitions'
            })

        # Formatting suggestions
        word_count = len(self.extracted_text.split())
        if word_count < 200:
            suggestions.append({
                'category': 'Formatting',
                'priority': 'High',
                'suggestion': 'Resume is too short. Add more details about skills, projects, and experience'
            })
        elif word_count > 1200:
            suggestions.append({
                'category': 'Formatting',
                'priority': 'Medium',
                'suggestion': 'Resume is too long. Keep it concise and focused (1 page preferred)'
            })

        # ATS suggestions
        suggestions.append({
            'category': 'ATS Optimization',
            'priority': 'High',
            'suggestion': 'Use standard section headings (Education, Experience, Skills, Projects) for ATS compatibility'
        })

        # General suggestions based on total score
        if total < 40:
            suggestions.append({
                'category': 'General',
                'priority': 'High',
                'suggestion': 'Consider using a professional resume template and highlight quantifiable achievements'
            })
        elif total < 60:
            suggestions.append({
                'category': 'General',
                'priority': 'Medium',
                'suggestion': 'Add more specific numbers and metrics to describe your achievements'
            })

        self.resume_data['suggestions'] = suggestions
        return suggestions

    def analyze_resume(self, file_path):
        """
        Complete resume analysis pipeline

        Args:
            file_path: Path to resume file (PDF/DOCX/TXT)

        Returns:
            Dict containing full analysis results
        """
        print("=" * 60)
        print("📄 RESUME ANALYSIS PIPELINE")
        print("=" * 60)

        # Step 1: Extract text
        print(f"\n📂 Loading resume: {os.path.basename(file_path)}")
        text = self.extract_text(file_path)
        if not text:
            print("❌ Failed to extract text from resume")
            return {
                'status': 'error',
                'message': 'Could not extract text from the resume file',
                'file_name': os.path.basename(file_path)
            }

        word_count = len(text.split())
        print(f"✅ Text extracted: ~{word_count} words")

        # Step 2: Extract information
        print("\n🔍 Extracting resume information...")
        self.extract_contact_info()
        self.extract_education()
        self.extract_experience()
        self.extract_skills()
        self.extract_projects()
        self.extract_certifications()
        self.extract_achievements()

        print(f"   Contact: Email={self.resume_data.get('contact', {}).get('email', '✗')}")
        print(f"   Education: {len(self.resume_data.get('education', {}).get('degrees', []))} degrees")
        print(f"   Skills Found: {self.resume_data.get('total_skills_found', 0)}")

        # Step 3: Calculate score
        print("\n📊 Calculating resume score...")
        score = self.calculate_resume_score()
        grade, grade_label = self._get_grade(score)
        print(f"   Total Score: {score}/100 ({grade} - {grade_label})")

        # Step 4: Generate suggestions
        print("\n💡 Generating improvement suggestions...")
        suggestions = self.generate_suggestions()
        print(f"   {len(suggestions)} suggestions generated")

        # Build response
        result = {
            'status': 'success',
            'file_name': os.path.basename(file_path),
            'file_path': file_path,
            'word_count': word_count,
            'total_score': score,
            'grade': grade,
            'grade_label': grade_label,
            'score_breakdown': self.score_breakdown,
            'contact_info': self.resume_data.get('contact', {}),
            'education': self.resume_data.get('education', {}),
            'experience': self.resume_data.get('experience', {}),
            'skills': self.skills_found,
            'total_skills_found': self.resume_data.get('total_skills_found', 0),
            'skill_categories_covered': self.resume_data.get('skill_categories_covered', 0),
            'projects': self.resume_data.get('projects', {}),
            'certifications': self.resume_data.get('certifications', {}),
            'achievements': self.resume_data.get('achievements', {}),
            'suggestions': suggestions,
            'analyzed_at': datetime.now().isoformat()
        }

        print("\n" + "=" * 60)
        print(f"✅ RESUME ANALYSIS COMPLETE! Score: {score}/100")
        print("=" * 60)

        return result

    def get_summary(self):
        """Get a concise summary of the resume analysis"""
        if not self.resume_data:
            return "No resume analyzed yet."

        return {
            'total_score': self.total_score,
            'score_breakdown': self.score_breakdown,
            'total_skills': self.resume_data.get('total_skills_found', 0),
            'suggestions_count': len(self.resume_data.get('suggestions', [])),
            'contact': self.resume_data.get('contact', {}),
            'education': self.resume_data.get('education', {}),
            'experience': self.resume_data.get('experience', {}),
        }


def analyze_resume_file(file_path):
    """
    Convenience function to analyze a resume file

    Args:
        file_path: Path to resume file

    Returns:
        Dict with analysis results
    """
    analyzer = ResumeAnalyzer()
    return analyzer.analyze_resume(file_path)


if __name__ == '__main__':
    print("=" * 60)
    print("📄 RESUME ANALYZER TEST")
    print("=" * 60)

    # Test with a sample text (simulated resume)
    test_resume_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'resumes',
        'sample_resume.pdf'
    )

    if os.path.exists(test_resume_path):
        result = analyze_resume_file(test_resume_path)
        print(f"\nScore: {result.get('total_score', 'N/A')}/100")
        print(f"Grade: {result.get('grade', 'N/A')}")
        print(f"Skills found: {result.get('total_skills_found', 0)}")
    else:
        print("\n⚠️  No sample resume found. Testing with simulated data...")
        # Create a temporary test
        analyzer = ResumeAnalyzer()
        analyzer.extracted_text = """
        John Doe
        john.doe@email.com
        +91-9876543210
        linkedin.com/in/johndoe
        
        EDUCATION
        Bachelor of Technology in Computer Science
        IIT Bombay
        CGPA: 8.5
        2020 - 2024
        
        SKILLS
        Python, Java, JavaScript, React, Node.js, SQL, AWS, Docker
        Machine Learning, Data Structures, Algorithms
        
        EXPERIENCE
        Software Engineering Intern at Google
        2023 - 2024
        Developed and deployed microservices using Python and AWS
        
        PROJECTS
        1. E-commerce Platform - Built using React and Node.js
        2. ML Model for Price Prediction - Used scikit-learn
        
        CERTIFICATIONS
        AWS Certified Cloud Practitioner
        Google Cloud Digital Leader
        
        ACHIEVEMENTS
        Won 1st place in Hackathon 2024
        Best Project Award in Computer Science Dept.
        """
        result = analyzer.analyze_resume("sample_resume.pdf")
        print(f"\nScore: {result.get('total_score', 'N/A')}/100")
        print(f"Grade: {result.get('grade', 'N/A')} ({result.get('grade_label', '')})")
        print(f"Skills found: {result.get('total_skills_found', 0)}")
        print(f"Contact: {result.get('contact_info', {})}")
        print(f"\nSuggestions:")
        for s in result.get('suggestions', []):
            print(f"  [{s['priority']}] {s['category']}: {s['suggestion']}")
