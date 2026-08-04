"""
pytest configuration and shared fixtures for ML module tests
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import sys

# Add backend to path for imports
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)


@pytest.fixture(scope="session")
def sample_student_data():
    """Generate a small synthetic dataset for testing ML pipeline"""
    np.random.seed(42)
    n = 50

    data = {
        'student_id': [f'STU{i:04d}' for i in range(n)],
        'name': [f'Student {i}' for i in range(n)],
        'department': np.random.choice(
            ['Computer Science', 'Electronics', 'Mechanical', 'Civil', 'Electrical'],
            n
        ),
        'year': np.random.choice([3, 4], n),
        'cgpa': np.round(np.random.uniform(5.0, 10.0, n), 2),
        'tenth_percentage': np.round(np.random.uniform(60, 100, n), 1),
        'twelfth_percentage': np.round(np.random.uniform(55, 98, n), 1),
        'communication_skill': np.random.randint(20, 100, n),
        'programming_skill': np.random.randint(10, 100, n),
        'internships': np.random.randint(0, 5, n),
        'projects': np.random.randint(0, 8, n),
        'hackathons': np.random.randint(0, 6, n),
        'certifications': np.random.randint(0, 6, n),
        'backlogs': np.random.randint(0, 5, n),
        'attendance': np.random.randint(50, 100, n),
        'aptitude_score': np.random.randint(20, 100, n),
        'technical_score': np.random.randint(15, 100, n),
        'resume_score': np.random.randint(20, 100, n),
        'placement_status': np.random.choice([0, 1], n, p=[0.4, 0.6]),
        'email': [f'student{i}@college.edu' for i in range(n)],
        'mentor_email': ['mentor@college.edu'] * n,
    }
    return pd.DataFrame(data)


@pytest.fixture(scope="session")
def sample_student_data_with_missing():
    """Generate data with intentional missing values for cleaning tests"""
    np.random.seed(42)
    n = 30

    data = {
        'student_id': [f'STU{i:04d}' for i in range(n)],
        'name': [f'Student {i}' for i in range(n)],
        'department': np.random.choice(['CS', 'EC', 'ME', 'CE'], n),
        'cgpa': np.round(np.random.uniform(4.0, 10.0, n), 2),
        'tenth_percentage': np.round(np.random.uniform(50, 100, n), 1),
        'twelfth_percentage': np.round(np.random.uniform(50, 100, n), 1),
        'communication_skill': np.random.randint(20, 100, n),
        'programming_skill': np.random.randint(10, 100, n),
        'internships': np.random.randint(0, 5, n),
        'projects': np.random.randint(0, 8, n),
        'hackathons': np.random.randint(0, 6, n),
        'certifications': np.random.randint(0, 6, n),
        'backlogs': np.random.randint(0, 5, n),
        'attendance': np.random.randint(40, 100, n),
        'aptitude_score': np.random.randint(20, 100, n),
        'technical_score': np.random.randint(15, 100, n),
        'resume_score': np.random.randint(20, 100, n),
        'placement_status': np.random.choice([0, 1], n, p=[0.4, 0.6]),
    }

    df = pd.DataFrame(data)

    # Inject missing values in specific columns
    df.loc[0:2, 'cgpa'] = np.nan
    df.loc[3:4, 'tenth_percentage'] = np.nan
    df.loc[5, 'programming_skill'] = np.nan
    df.loc[6:7, 'department'] = np.nan

    # Inject duplicate rows
    dup = df.iloc[0].copy()
    df = pd.concat([df, pd.DataFrame([dup])], ignore_index=True)

    # Inject invalid values (out of range)
    df.loc[len(df)] = ['STU9999', 'Invalid', 'CS', 15.0, 110, 95, 80, 85, 2, 4,
                        1, 2, 0, 95, 85, 90, 75, 1]  # cgpa=15 > 10
    df.loc[len(df)] = ['STU9998', 'Invalid2', 'EC', 7.5, 120, 85, 80, 85, 2, 4,
                        1, 2, 0, 95, 85, 90, 75, 0]  # tenth=120 > 100

    return df


@pytest.fixture(scope="session")
def sample_student_dict():
    """Single student record as dict for predict module tests"""
    return {
        'student_id': 'TEST001',
        'name': 'Test Student',
        'department': 'Computer Science',
        'year': 4,
        'cgpa': 8.5,
        'tenth_percentage': 92.0,
        'twelfth_percentage': 88.0,
        'communication_skill': 75,
        'programming_skill': 85,
        'internships': 2,
        'projects': 4,
        'hackathons': 2,
        'certifications': 3,
        'backlogs': 0,
        'attendance': 90,
        'aptitude_score': 80,
        'technical_score': 82,
        'resume_score': 78
    }


@pytest.fixture(scope="session")
def sample_student_dict_low_performer():
    """Student with weak profile for testing prediction edge cases"""
    return {
        'student_id': 'TEST002',
        'name': 'Weak Student',
        'department': 'Mechanical',
        'year': 4,
        'cgpa': 5.5,
        'tenth_percentage': 62.0,
        'twelfth_percentage': 58.0,
        'communication_skill': 30,
        'programming_skill': 25,
        'internships': 0,
        'projects': 0,
        'hackathons': 0,
        'certifications': 0,
        'backlogs': 4,
        'attendance': 55,
        'aptitude_score': 30,
        'technical_score': 25,
        'resume_score': 20
    }


@pytest.fixture(scope="session")
def temp_csv_path(sample_student_data):
    """Write sample data to a temporary CSV and return the path"""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
        sample_student_data.to_csv(f, index=False)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture(scope="session")
def temp_csv_path_with_missing(sample_student_data_with_missing):
    """Write sample data with missing values to a temp CSV"""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
        sample_student_data_with_missing.to_csv(f, index=False)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)


@pytest.fixture(scope="session")
def temp_model_dir():
    """Create a temporary model directory for save/load tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def cleaned_dataframe(sample_student_data_with_missing):
    """Return a df that has been run through the full DataCleaner pipeline"""
    from ml.data_cleaning import DataCleaner
    cleaner = DataCleaner()
    df = sample_student_data_with_missing.copy()

    # Ensure placement_status is int
    if 'placement_status' in df.columns:
        df['placement_status'] = df['placement_status'].astype(int)

    cleaner.df = df
    cleaner.original_shape = df.shape
    cleaner.handle_missing_values()
    cleaner.remove_duplicates()
    cleaner.remove_invalid_entries()
    cleaner.convert_categorical()
    cleaner.normalize_features()
    return cleaner


@pytest.fixture(scope="session")
def engineered_dataframe(cleaned_dataframe):
    """Return a df run through the full FeatureEngineer pipeline"""
    from ml.feature_engineering import FeatureEngineer
    engineer = FeatureEngineer()
    df = cleaned_dataframe.df.copy()
    df = engineer.create_interaction_features(df)
    df = engineer.create_aggregate_features(df)
    result = engineer.create_department_features(df)
    return result, engineer
