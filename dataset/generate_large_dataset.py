"""
Placement Predictor - Large Dataset Generator
Generates synthetic student datasets of various sizes for testing and benchmarking

Usage:
    python generate_large_dataset.py --size 1000 --output student_data_1000.csv
    python generate_large_dataset.py --size 10000 --output student_data_10000.csv
"""

import os
import sys
import csv
import random
import argparse
import time
from datetime import datetime


# Add backend to path
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)


class DatasetGenerator:
    """
    Generate synthetic student datasets with realistic values

    Supports sizes: 100, 500, 1000, 5000, 10000
    """

    DEPARTMENTS = [
        'Computer Science', 'Electronics', 'Mechanical',
        'Civil', 'Electrical', 'Information Technology',
        'Chemical', 'Biotechnology', 'Aerospace'
    ]

    FIRST_NAMES = [
        'Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Pranav',
        'Dhruv', 'Krishna', 'Shaurya', 'Aanya', 'Diya', 'Myra', 'Sara',
        'Anaya', 'Ishita', 'Aaradhya', 'Jia', 'Riya', 'Ananya',
        'Rohan', 'Amit', 'Priya', 'Neha', 'Vikram', 'Divya', 'Rahul',
        'Kavya', 'Siddharth', 'Meera', 'Ankit', 'Pooja', 'Harsh', 'Nisha',
        'Raj', 'Sneha', 'Aryan', 'Tanvi', 'Kunal', 'Shreya'
    ]

    LAST_NAMES = [
        'Sharma', 'Verma', 'Patel', 'Kumar', 'Singh', 'Gupta', 'Reddy',
        'Joshi', 'Nair', 'Menon', 'Iyer', 'Desai', 'Shah', 'Das',
        'Banerjee', 'Chatterjee', 'Mukherjee', 'Sen', 'Bose', 'Choudhury'
    ]

    def __init__(self, seed=42):
        """Initialize generator with random seed for reproducibility"""
        self.seed = seed
        random.seed(seed)

    def generate_student(self, index):
        """Generate a single student record with realistic values"""
        first = random.choice(self.FIRST_NAMES)
        last = random.choice(self.LAST_NAMES)

        # CGPA (normal distribution around 7.0 with some very high/low)
        cgpa = round(random.gauss(7.0, 1.2), 2)
        cgpa = max(4.0, min(10.0, cgpa))

        # Percentages (correlated with CGPA)
        tenth_base = 60 + (cgpa - 4.0) * 5 + random.uniform(-5, 5)
        twelfth_base = 55 + (cgpa - 4.0) * 5 + random.uniform(-5, 5)

        # Skills (correlated with CGPA)
        comm_skill = min(100, max(10, int(40 + cgpa * 4 + random.gauss(0, 12))))
        prog_skill = min(100, max(10, int(35 + cgpa * 5 + random.gauss(0, 10))))

        # Experience (some correlation with CGPA)
        internships = min(5, max(0, int(random.gauss(cgpa * 0.3 - 1, 0.8))))
        projects = min(8, max(0, int(random.gauss(cgpa * 0.5 - 1, 1.2))))
        hackathons = min(6, max(0, int(random.gauss(cgpa * 0.3 - 0.5, 1))))
        certifications = min(8, max(0, int(random.gauss(cgpa * 0.4 - 1, 1))))

        # Backlogs (inverse correlation with CGPA)
        backlogs = max(0, int(random.gauss(5 - cgpa * 0.5, 0.8)))
        backlogs = min(8, backlogs)

        # Attendance (some correlation with CGPA)
        attendance = min(100, max(40, int(60 + cgpa * 3 + random.gauss(0, 8))))

        # Scores
        aptitude = min(100, max(10, int(40 + cgpa * 4 + random.gauss(0, 10))))
        technical = min(100, max(10, int(35 + cgpa * 5 + random.gauss(0, 10))))
        resume_score = min(100, max(10, int(30 + cgpa * 4 + projects * 2 + internships * 3 + random.gauss(0, 8))))

        # Placement status (determined by features)
        placement_prob = (
            0.1 +                           # base
            (cgpa / 10.0) * 0.25 +          # CGPA contribution
            (prog_skill / 100.0) * 0.20 +   # Programming contribution
            (aptitude / 100.0) * 0.15 +     # Aptitude contribution
            (technical / 100.0) * 0.10 +    # Technical contribution
            min(internships, 2) * 0.05 +     # Internship bonus
            min(projects, 3) * 0.03 -        # Project bonus
            backlogs * 0.05 -                # Backlog penalty
            0.05                             # Margin
        )
        placement_prob = max(0.05, min(0.98, placement_prob))
        placed = 1 if random.random() < placement_prob else 0

        # Package (only if placed)
        if placed:
            package = round(random.gauss(6 + cgpa * 1.5, 3), 2)
            package = max(2.5, min(50, package))
            company = random.choice([
                'Google', 'Microsoft', 'Amazon', 'TCS', 'Infosys',
                'Wipro', 'Accenture', 'Deloitte', 'Cognizant', 'IBM',
                'Goldman Sachs', 'JPMC', 'Flipkart', 'Uber', 'Meta'
            ])
        else:
            package = 0
            company = ''

        student = {
            'student_id': f'STU{2024}{index:04d}',
            'name': f'{first} {last}',
            'department': random.choice(self.DEPARTMENTS),
            'year': random.choice([3, 4]),
            'cgpa': cgpa,
            'tenth_percentage': round(tenth_base, 1),
            'twelfth_percentage': round(twelfth_base, 1),
            'communication_skill': comm_skill,
            'programming_skill': prog_skill,
            'internships': internships,
            'projects': projects,
            'hackathons': hackathons,
            'certifications': certifications,
            'backlogs': backlogs,
            'attendance': attendance,
            'aptitude_score': aptitude,
            'technical_score': technical,
            'resume_score': min(100, resume_score),
            'placement_status': placed,
            'package': package,
            'company': company,
            'email': f'student{index}@college.edu',
            'mentor_email': f'mentor.{index % 50 + 1}@college.edu'
        }

        return student

    FIELD_NAMES = [
        'student_id', 'name', 'department', 'year', 'cgpa',
        'tenth_percentage', 'twelfth_percentage',
        'communication_skill', 'programming_skill',
        'internships', 'projects', 'hackathons', 'certifications',
        'backlogs', 'attendance', 'aptitude_score', 'technical_score',
        'resume_score', 'placement_status', 'package', 'company',
        'email', 'mentor_email'
    ]

    def generate_dataset(self, size, output_path=None):
        """
        Generate a dataset with specified number of records

        Args:
            size: Number of students to generate (100, 500, 1000, 5000, 10000)
            output_path: Path to save CSV file

        Returns:
            Tuple of (path, time_taken)
        """
        valid_sizes = [100, 500, 1000, 5000, 10000]
        if size not in valid_sizes:
            print(f"⚠️  Size {size} not in standard sizes {valid_sizes}. Generating anyway.")

        if output_path is None:
            dataset_dir = os.path.dirname(os.path.abspath(__file__))
            output_path = os.path.join(dataset_dir, f'student_data_{size}.csv')

        print(f"🔄 Generating {size} student records...")
        start_time = time.time()

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELD_NAMES)
            writer.writeheader()

            for i in range(size):
                student = self.generate_student(i + 1)
                writer.writerow(student)

                # Progress indicator
                if size > 1000 and (i + 1) % 1000 == 0:
                    pct = (i + 1) / size * 100
                    print(f"   Progress: {i + 1}/{size} ({pct:.0f}%)")

        elapsed = time.time() - start_time
        file_size = os.path.getsize(output_path)

        print(f"✅ Generated {size} records in {elapsed:.2f}s")
        print(f"   Output: {output_path}")
        print(f"   File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")

        return output_path, elapsed

    def generate_all_sizes(self, output_dir=None):
        """Generate datasets at all standard sizes"""
        if output_dir is None:
            output_dir = os.path.dirname(os.path.abspath(__file__))

        results = []
        sizes = [100, 500, 1000]  # Small ones for quick generation
        # Add larger sizes (can be slow)
        # sizes.extend([5000, 10000])

        print("=" * 60)
        print("📊 DATASET GENERATION BENCHMARK")
        print("=" * 60)

        for size in sizes:
            output_path = os.path.join(output_dir, f'student_data_{size}.csv')
            path, elapsed = self.generate_dataset(size, output_path)
            results.append({'size': size, 'time': elapsed, 'path': path})

        print("\n" + "=" * 60)
        print("📋 GENERATION SUMMARY")
        print("=" * 60)
        print(f"{'Size':<10} {'Time (s)':<12} {'Records/s':<12}")
        print("-" * 60)
        for r in results:
            rate = r['size'] / r['time'] if r['time'] > 0 else 0
            print(f"{r['size']:<10} {r['time']:<12.4f} {rate:<12.0f}")
        print("=" * 60)

        return results


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Generate synthetic placement dataset for testing'
    )
    parser.add_argument(
        '--size', type=int, default=1000,
        help='Number of records (100, 500, 1000, 5000, 10000)'
    )
    parser.add_argument(
        '--output', type=str, default=None,
        help='Output CSV file path'
    )
    parser.add_argument(
        '--all', action='store_true',
        help='Generate all standard sizes'
    )

    args = parser.parse_args()

    generator = DatasetGenerator(seed=42)

    if args.all:
        generator.generate_all_sizes()
    else:
        generator.generate_dataset(args.size, args.output)


if __name__ == '__main__':
    main()
