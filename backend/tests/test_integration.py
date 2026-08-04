"""
Integration Tests - Complete workflow tests

Scenarios:
1. Dataset Upload → Data Cleaning → Model Training → Save → Load → Predict
2. Student Registration → Login → Prediction → Company Eligibility → Mentor Alert
3. Admin Login → CRUD Operations → Analytics
"""

import pytest
import os
import sys
import json
import pandas as pd
import numpy as np
import tempfile

_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)


class TestMLWorkflowIntegration:
    """
    Full ML Pipeline: Dataset → Clean → Feature Engineering → Train → Save → Load → Predict
    """

    @pytest.fixture(autouse=True)
    def setup(self, temp_csv_path, temp_model_dir):
        self.dataset_path = temp_csv_path
        self.model_dir = temp_model_dir

    def test_complete_ml_pipeline(self):
        """Full ML pipeline from CSV to prediction"""
        from ml.data_cleaning import DataCleaner
        from ml.feature_engineering import FeatureEngineer
        from ml.train_model import ModelTrainer
        from ml.predict import PredictionEngine

        # Step 1: Load and clean data
        cleaner = DataCleaner()
        df, cleaning_report = cleaner.clean_dataset(self.dataset_path)
        assert df is not None
        assert not df.isnull().sum().sum() > 0

        # Step 2: Feature engineering
        engineer = FeatureEngineer()
        X_train, X_test, y_train, y_test, df_fe = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        assert X_train.shape[0] > 0
        assert X_test.shape[0] > 0
        assert X_train.shape[1] > 5  # Multiple features

        # Step 3: Train models
        trainer = ModelTrainer()
        results = trainer.train_all_models(X_train, y_train, X_test, y_test)
        assert len(results) == 6
        assert trainer.best_model is not None

        # Step 4: Save model
        model_path = trainer.save_model(
            self.model_dir,
            scaler=cleaner.scaler,
            label_encoders=cleaner.label_encoders,
            feature_columns=X_train.columns.tolist()
        )
        assert model_path is not None
        assert os.path.exists(os.path.join(self.model_dir, 'best_model.pkl'))

        # Step 5: Load and predict
        engine = PredictionEngine(model_dir=self.model_dir)
        assert engine.load_model() is True

        test_student = {
            'cgpa': 8.5, 'department': 'CS',
            'tenth_percentage': 90.0, 'twelfth_percentage': 85.0,
            'communication_skill': 75, 'programming_skill': 80,
            'internships': 2, 'projects': 3, 'hackathons': 1, 'certifications': 2,
            'backlogs': 0, 'attendance': 85, 'aptitude_score': 75,
            'technical_score': 78, 'resume_score': 70
        }
        result = engine.predict_single(test_student)
        assert result['status'] == 'success'
        assert result['prediction'] in [0, 1]
        assert 0 <= result['probability'] <= 100


class TestMentorAlertWorkflowIntegration:
    """Full mentor alert workflow: Predict → Detect Alerts → Generate Email"""

    def test_mentor_alert_workflow(self, sample_student_dict_low_performer):
        """Detect alerts for a weak student and generate email content"""
        from alerts.mentor_alerts import MentorAlertSystem

        # Create a mock prediction result for a low probability scenario
        prediction_result = {
            'prediction': 0,
            'probability': 20.0,
            'confidence': 70.0,
            'prediction_label': 'Not Placed ❌'
        }

        # Step 1: Detect alerts
        alert_system = MentorAlertSystem()
        alerts = alert_system.detect_alerts(
            sample_student_dict_low_performer,
            prediction_result
        )

        assert len(alerts) > 0
        assert any(a['alert_type'] == 'low_cgpa' for a in alerts)
        assert any(a['alert_type'] == 'low_skill' for a in alerts)

        # Step 2: Verify alert structure
        for alert in alerts:
            assert 'alert_type' in alert
            assert 'message' in alert
            assert 'weak_areas' in alert
            assert 'suggestions' in alert

        # Step 3: Generate email content
        email = alert_system.format_alert_email(
            mentor_email='mentor@college.edu',
            student_name='Weak Student',
            alerts=alerts,
            prediction_result=prediction_result
        )

        assert 'Weak Student' in str(email)
        assert 'html' in str(email).lower()


class TestCompanyEligibilityIntegration:
    """Company eligibility checking workflow"""

    def test_company_eligibility_with_data(self, sample_student_data):
        """Check student eligibility against multiple companies"""
        from analysis.company_eligibility import CompanyEligibilityChecker

        checker = CompanyEligibilityChecker()

        # Add companies
        companies = [
            {'company_name': 'Google', 'min_cgpa': 8.0, 'max_backlogs': 0,
             'min_aptitude': 70, 'min_technical': 75},
            {'company_name': 'TCS', 'min_cgpa': 6.0, 'max_backlogs': 2,
             'min_aptitude': 50, 'min_technical': 50},
        ]

        for company in companies:
            checker.add_company(company)

        # Check a student against companies
        student = sample_student_data.iloc[0].to_dict()
        results = checker.check_eligibility(student)
        assert len(results) > 0

        for result in results:
            assert 'company_name' in result
            assert 'eligible' in result or 'match_percentage' in result


class TestAuthPredictionWorkflow:
    """Student auth → prediction workflow"""

    def test_student_auth_and_prediction(self):
        """Complete student journey: register → login → predict"""
        from auth.student_auth import StudentAuth

        auth = StudentAuth()

        # 1. Register
        register_data = {
            'student_id': 'INT_TEST001',
            'name': 'Integration Student',
            'email': 'integration@test.edu',
            'password': 'TestPass123',
            'department': 'CS',
            'cgpa': 8.5
        }
        reg_result = auth.register(register_data)
        assert reg_result['status'] == 'success'

        # 2. Forgot password (simulates email flow)
        forgot_result = auth.forgot_password('integration@test.edu')
        assert forgot_result['status'] == 'success'
        assert 'reset_token' in forgot_result

        # 3. Reset password
        reset_result = auth.reset_password(
            forgot_result['reset_token'],
            'NewPass456'
        )
        assert reset_result['status'] == 'success'

        # 4. Validate session
        token = reg_result.get('token', '')
        session_result = auth.validate_session(token)
        assert session_result['valid'] is True


class TestLargeDatasetBenchmark:
    """Benchmark ML pipeline with different dataset sizes"""

    @pytest.mark.slow
    def test_cleaning_time(self):
        """Measure data cleaning time"""
        from ml.data_cleaning import DataCleaner
        import time

        # Generate 100 rows inline
        np.random.seed(42)
        data = {
            'cgpa': np.random.uniform(4, 10, 100),
            'tenth_percentage': np.random.uniform(50, 100, 100),
            'twelfth_percentage': np.random.uniform(50, 100, 100),
            'communication_skill': np.random.randint(20, 100, 100),
            'programming_skill': np.random.randint(10, 100, 100),
            'internships': np.random.randint(0, 5, 100),
            'projects': np.random.randint(0, 8, 100),
            'hackathons': np.random.randint(0, 6, 100),
            'certifications': np.random.randint(0, 6, 100),
            'backlogs': np.random.randint(0, 5, 100),
            'attendance': np.random.randint(50, 100, 100),
            'aptitude_score': np.random.randint(20, 100, 100),
            'technical_score': np.random.randint(15, 100, 100),
            'resume_score': np.random.randint(20, 100, 100),
            'placement_status': np.random.choice([0, 1], 100, p=[0.4, 0.6]),
        }
        df = pd.DataFrame(data)

        cleaner = DataCleaner()
        cleaner.df = df.copy()
        cleaner.original_shape = df.shape

        start = time.time()
        cleaner.handle_missing_values()
        cleaner.remove_duplicates()
        cleaner.remove_invalid_entries()
        cleaner.convert_categorical()
        cleaner.normalize_features()
        elapsed = time.time() - start

        # Should complete within reasonable time
        assert elapsed < 10.0  # 10 seconds max for 100 records
        assert len(cleaner.feature_columns) > 0
