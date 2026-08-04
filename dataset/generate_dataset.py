"""
Placement Predictor - Dataset Generator
Generates synthetic student data for ML model training
"""

import pandas as pd
import numpy as np
import random
from faker import Faker
import os

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

DEPARTMENTS = [
    'Computer Science',
    'Information Technology',
    'Electronics & Communication',
    'Electrical Engineering',
    'Mechanical Engineering',
    'Civil Engineering',
    'Artificial Intelligence & ML',
    'Data Science'
]

COMPANIES = [
    'Google', 'Microsoft', 'Amazon', 'Apple', 'Meta',
    'Infosys', 'TCS', 'Wipro', 'Accenture', 'Deloitte',
    'Goldman Sachs', 'JP Morgan', 'Flipkart', 'Uber', 'Adobe'
]

SKILLS_LIST = [
    'Python', 'Java', 'C++', 'JavaScript', 'SQL',
    'Machine Learning', 'Deep Learning', 'AWS', 'Docker',
    'Kubernetes', 'React', 'Angular', 'Node.js', 'Django',
    'Flask', 'TensorFlow', 'PyTorch', 'Data Structures',
    'Algorithms', 'DBMS', 'OS', 'Computer Networks'
]

CERTIFICATIONS_LIST = [
    'AWS Certified', 'Google Cloud Certified', 'Microsoft Azure Certified',
    'Oracle Certified', 'CISCO Certified', 'Red Hat Certified',
    'PMP', 'Scrum Master', 'Data Science Professional',
    'Machine Learning Specialization', 'Full Stack Development',
    'Cloud Computing', 'Cybersecurity', 'AI Engineering'
]

def generate_student_data(num_students=1000):
    """Generate synthetic student dataset"""
    
    data = []
    
    for i in range(1, num_students + 1):
        # Basic Info
        student_id = f'STU{i:04d}'
        name = fake.name()
        email = fake.email()
        mentor_email = fake.email()
        
        # Academic Info
        department = random.choice(DEPARTMENTS)
        year = random.choice([3, 4])  # Final year students
        cgpa = round(random.uniform(5.0, 10.0), 2)
        tenth_pct = round(random.uniform(60.0, 98.0), 2)
        twelfth_pct = round(random.uniform(55.0, 98.0), 2)
        
        # Skills Assessment (0-100 scale)
        comm_skill = min(100, max(0, int(np.random.normal(65, 15))))
        prog_skill = min(100, max(0, int(np.random.normal(60, 20))))
        
        # Experience & Achievements
        internships = random.choices([0, 1, 2, 3, 4], weights=[30, 35, 20, 10, 5])[0]
        projects = random.choices([1, 2, 3, 4, 5, 6], weights=[10, 20, 30, 25, 10, 5])[0]
        hackathons = random.choices([0, 1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 3, 2])[0]
        certifications = random.choices([0, 1, 2, 3, 4, 5], weights=[25, 30, 25, 12, 5, 3])[0]
        
        # Academic Issues
        backlogs = random.choices([0, 0, 0, 0, 1, 1, 2, 3], weights=[40, 20, 15, 10, 8, 4, 2, 1])[0]
        
        # Attendance
        attendance = min(100, max(50, int(np.random.normal(80, 10))))
        
        # Test Scores
        aptitude_score = min(100, max(0, int(np.random.normal(65, 18))))
        technical_score = min(100, max(0, int(np.random.normal(60, 20))))
        
        # Resume Score (based on various factors)
        resume_factors = (
            (internships * 10) +
            (min(projects, 4) * 8) +
            (hackathons * 5) +
            (certifications * 7) +
            (prog_skill * 0.2) +
            (comm_skill * 0.1)
        )
        resume_score = min(100, max(0, int(resume_factors)))
        
        # Placement Status Logic
        # Combined score determines placement probability
        combined_score = (
            (cgpa / 10.0 * 25) +
            (tenth_pct / 100.0 * 5) +
            (twelfth_pct / 100.0 * 5) +
            (comm_skill / 100.0 * 10) +
            (prog_skill / 100.0 * 15) +
            (internships * 5) +
            (min(projects, 4) * 3) +
            (hackathons * 2) +
            (certifications * 3) +
            (aptitude_score / 100.0 * 10) +
            (technical_score / 100.0 * 10) +
            (resume_score / 100.0 * 5) -
            (backlogs * 8) +
            ((attendance - 50) / 50.0 * 3)
        )
        
        # Normalize to 0-100
        combined_score = max(0, min(100, combined_score))
        
        # Determine placement based on combined score with some randomness
        placement_prob = combined_score / 100.0
        
        # Add noise for realism
        placement_prob += np.random.normal(0, 0.1)
        placement_prob = max(0, min(1, placement_prob))
        
        is_placed = 1 if placement_prob > 0.45 else 0
        
        # Package for placed students
        package = 0
        company = ''
        if is_placed:
            if combined_score > 80:
                package = round(random.uniform(15, 45), 2)
                company = random.choice(['Google', 'Microsoft', 'Amazon', 'Meta', 'Apple'])
            elif combined_score > 65:
                package = round(random.uniform(8, 18), 2)
                company = random.choice(['Adobe', 'Flipkart', 'Uber', 'Goldman Sachs', 'JP Morgan'])
            elif combined_score > 50:
                package = round(random.uniform(4, 10), 2)
                company = random.choice(['Infosys', 'TCS', 'Wipro', 'Accenture', 'Deloitte'])
            else:
                package = round(random.uniform(2.5, 6), 2)
                company = random.choice(['TCS', 'Infosys', 'Wipro', 'Accenture'])
        
        data.append({
            'student_id': student_id,
            'name': name,
            'department': department,
            'year': year,
            'cgpa': cgpa,
            'tenth_percentage': tenth_pct,
            'twelfth_percentage': twelfth_pct,
            'communication_skill': comm_skill,
            'programming_skill': prog_skill,
            'internships': internships,
            'projects': projects,
            'hackathons': hackathons,
            'certifications': certifications,
            'backlogs': backlogs,
            'attendance': attendance,
            'aptitude_score': aptitude_score,
            'technical_score': technical_score,
            'resume_score': resume_score,
            'placement_status': is_placed,
            'package': package,
            'company': company,
            'email': email,
            'mentor_email': mentor_email
        })
    
    return pd.DataFrame(data)

def add_companies_csv():
    """Generate company eligibility data"""
    companies_data = [
        {'company_name': 'Google', 'min_cgpa': 8.5, 'max_backlogs': 0, 'required_skills': 'Python,Java,Data Structures,Algorithms,SQL',
         'required_certifications': 'AWS Certified,Google Cloud Certified', 'min_aptitude': 80, 'min_technical': 85, 'allowed_departments': 'Computer Science,Information Technology,Artificial Intelligence & ML,Data Science'},
        {'company_name': 'Microsoft', 'min_cgpa': 8.0, 'max_backlogs': 0, 'required_skills': 'Python,C++,Java,Data Structures,Algorithms',
         'required_certifications': 'Microsoft Azure Certified', 'min_aptitude': 78, 'min_technical': 82, 'allowed_departments': 'Computer Science,Information Technology,Artificial Intelligence & ML,Data Science'},
        {'company_name': 'Amazon', 'min_cgpa': 7.5, 'max_backlogs': 1, 'required_skills': 'Java,Python,AWS,SQL,Data Structures',
         'required_certifications': 'AWS Certified', 'min_aptitude': 75, 'min_technical': 78, 'allowed_departments': 'Computer Science,Information Technology,Electronics & Communication,Artificial Intelligence & ML,Data Science'},
        {'company_name': 'Meta', 'min_cgpa': 8.0, 'max_backlogs': 0, 'required_skills': 'JavaScript,React,Python,Data Structures,Algorithms',
         'required_certifications': '', 'min_aptitude': 80, 'min_technical': 82, 'allowed_departments': 'Computer Science,Information Technology,Artificial Intelligence & ML,Data Science'},
        {'company_name': 'Infosys', 'min_cgpa': 6.0, 'max_backlogs': 2, 'required_skills': 'Python,Java,SQL,DBMS',
         'required_certifications': '', 'min_aptitude': 60, 'min_technical': 55, 'allowed_departments': 'Computer Science,Information Technology,Electronics & Communication,Electrical Engineering,Mechanical Engineering,Civil Engineering,Artificial Intelligence & ML,Data Science'},
        {'company_name': 'TCS', 'min_cgpa': 5.5, 'max_backlogs': 3, 'required_skills': 'Python,Java,SQL',
         'required_certifications': '', 'min_aptitude': 55, 'min_technical': 50, 'allowed_departments': 'Computer Science,Information Technology,Electronics & Communication,Electrical Engineering,Mechanical Engineering,Civil Engineering,Artificial Intelligence & ML,Data Science'},
        {'company_name': 'Wipro', 'min_cgpa': 6.0, 'max_backlogs': 2, 'required_skills': 'Python,Java,SQL,DBMS',
         'required_certifications': '', 'min_aptitude': 58, 'min_technical': 55, 'allowed_departments': 'Computer Science,Information Technology,Electronics & Communication,Electrical Engineering,Mechanical Engineering,Civil Engineering,Artificial Intelligence & ML,Data Science'},
        {'company_name': 'Accenture', 'min_cgpa': 6.5, 'max_backlogs': 2, 'required_skills': 'Python,Java,SQL,Communication',
         'required_certifications': '', 'min_aptitude': 60, 'min_technical': 55, 'allowed_departments': 'All'},
        {'company_name': 'Adobe', 'min_cgpa': 7.5, 'max_backlogs': 1, 'required_skills': 'JavaScript,C++,Python,React,Data Structures',
         'required_certifications': '', 'min_aptitude': 72, 'min_technical': 75, 'allowed_departments': 'Computer Science,Information Technology,Artificial Intelligence & ML,Data Science'},
        {'company_name': 'Goldman Sachs', 'min_cgpa': 7.5, 'max_backlogs': 1, 'required_skills': 'Python,Java,SQL,Data Structures,Algorithms',
         'required_certifications': '', 'min_aptitude': 75, 'min_technical': 72, 'allowed_departments': 'Computer Science,Information Technology,Artificial Intelligence & ML,Data Science'},
        {'company_name': 'Flipkart', 'min_cgpa': 7.0, 'max_backlogs': 1, 'required_skills': 'Python,Java,JavaScript,SQL,Data Structures',
         'required_certifications': '', 'min_aptitude': 70, 'min_technical': 70, 'allowed_departments': 'Computer Science,Information Technology,Artificial Intelligence & ML,Data Science'},
        {'company_name': 'Deloitte', 'min_cgpa': 6.5, 'max_backlogs': 2, 'required_skills': 'Python,Java,SQL,Communication',
         'required_certifications': '', 'min_aptitude': 65, 'min_technical': 60, 'allowed_departments': 'Computer Science,Information Technology,Electronics & Communication,Artificial Intelligence & ML,Data Science'},
        {'company_name': 'Apple', 'min_cgpa': 8.5, 'max_backlogs': 0, 'required_skills': 'Swift,Python,C++,Data Structures,Algorithms,OS',
         'required_certifications': '', 'min_aptitude': 82, 'min_technical': 85, 'allowed_departments': 'Computer Science,Information Technology,Artificial Intelligence & ML,Data Science'},
        {'company_name': 'Uber', 'min_cgpa': 7.5, 'max_backlogs': 1, 'required_skills': 'Python,Java,JavaScript,Data Structures,System Design',
         'required_certifications': '', 'min_aptitude': 73, 'min_technical': 75, 'allowed_departments': 'Computer Science,Information Technology,Artificial Intelligence & ML,Data Science'},
        {'company_name': 'JP Morgan', 'min_cgpa': 7.0, 'max_backlogs': 1, 'required_skills': 'Python,Java,SQL,Data Structures',
         'required_certifications': '', 'min_aptitude': 70, 'min_technical': 68, 'allowed_departments': 'Computer Science,Information Technology,Artificial Intelligence & ML,Data Science'}
    ]
    return pd.DataFrame(companies_data)

def main():
    """Main function to generate all datasets"""
    print("=" * 60)
    print("📊 PLACEMENT PREDICTOR - DATASET GENERATOR")
    print("=" * 60)
    
    # Create dataset directory
    dataset_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dataset')
    os.makedirs(dataset_dir, exist_ok=True)
    
    # Generate student data
    print("\n🔄 Generating student data...")
    num_students = 1000
    df = generate_student_data(num_students)
    
    # Save student dataset
    student_path = os.path.join(dataset_dir, 'student_data.csv')
    df.to_csv(student_path, index=False)
    print(f"✅ Generated {len(df)} student records")
    print(f"✅ Saved to: {student_path}")
    
    # Display statistics
    placed = df['placement_status'].sum()
    print(f"\n📈 Dataset Statistics:")
    print(f"   - Total Students: {len(df)}")
    print(f"   - Placed: {int(placed)} ({placed/len(df)*100:.1f}%)")
    print(f"   - Not Placed: {len(df)-int(placed)} ({(1-placed/len(df))*100:.1f}%)")
    print(f"   - Average CGPA: {df['cgpa'].mean():.2f}")
    print(f"   - Average Package: ₹{df[df['placement_status']==1]['package'].mean():.2f} LPA")
    
    # Generate companies data
    print("\n🔄 Generating company eligibility data...")
    companies_df = add_companies_csv()
    companies_path = os.path.join(dataset_dir, 'companies.csv')
    companies_df.to_csv(companies_path, index=False)
    print(f"✅ Generated {len(companies_df)} company records")
    print(f"✅ Saved to: {companies_path}")
    
    print("\n" + "=" * 60)
    print("✅ DATASET GENERATION COMPLETE!")
    print("=" * 60)

if __name__ == '__main__':
    main()
