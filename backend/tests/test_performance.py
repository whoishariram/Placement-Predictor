"""
Performance Benchmark Tests
Measures execution time for critical operations across different dataset sizes
"""

import pytest
import os
import sys
import time
import pandas as pd
import numpy as np
import tempfile

_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)


class TimingResult:
    """Helper to collect and display timing results"""
    _results = []

    @classmethod
    def record(cls, operation, size, elapsed):
        cls._results.append({
            'operation': operation,
            'size': size,
            'elapsed': round(elapsed, 4)
        })

    @classmethod
    def print_report(cls):
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE BENCHMARK REPORT")
        print("=" * 60)
        print(f"{'Operation':<35} {'Size':<8} {'Time (s)':<10}")
        print("-" * 60)
        for r in cls._results:
            print(f"{r['operation']:<35} {r['size']:<8} {r['elapsed']:<10.4f}")
        print("=" * 60)
        cls._results.clear()


def generate_test_dataframe(n_rows):
    """Generate a DataFrame with n_rows for performance testing"""
    np.random.seed(42)
    return pd.DataFrame({
        'student_id': [f'PERF{i:04d}' for i in range(n_rows)],
        'name': [f'Student {i}' for i in range(n_rows)],
        'department': np.random.choice(['CS', 'EC', 'ME', 'CE', 'EE'], n_rows),
        'year': np.random.choice([3, 4], n_rows),
        'cgpa': np.round(np.random.uniform(4.0, 10.0, n_rows), 2),
        'tenth_percentage': np.round(np.random.uniform(50, 100, n_rows), 1),
        'twelfth_percentage': np.round(np.random.uniform(50, 100, n_rows), 1),
        'communication_skill': np.random.randint(10, 100, n_rows),
        'programming_skill': np.random.randint(10, 100, n_rows),
        'internships': np.random.randint(0, 5, n_rows),
        'projects': np.random.randint(0, 8, n_rows),
        'hackathons': np.random.randint(0, 6, n_rows),
        'certifications': np.random.randint(0, 6, n_rows),
        'backlogs': np.random.randint(0, 8, n_rows),
        'attendance': np.random.randint(40, 100, n_rows),
        'aptitude_score': np.random.randint(10, 100, n_rows),
        'technical_score': np.random.randint(10, 100, n_rows),
        'resume_score': np.random.randint(10, 100, n_rows),
        'placement_status': np.random.choice([0, 1], n_rows, p=[0.4, 0.6]),
    })


@pytest.mark.slow
class TestCSVLoadingPerformance:
    """Benchmark CSV loading time"""

    SIZES = [100, 500, 1000]

    def test_csv_load_time(self):
        """Measure CSV load time for different sizes"""
        from ml.data_cleaning import DataCleaner

        for size in self.SIZES:
            df = generate_test_dataframe(size)
            with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
                df.to_csv(f, index=False)
                csv_path = f.name

            cleaner = DataCleaner()
            start = time.time()
            cleaner.load_dataset(csv_path)
            elapsed = time.time() - start

            TimingResult.record('CSV Load', size, elapsed)
            assert elapsed < 2.0, f"CSV loading {size} rows took too long: {elapsed:.4f}s"
            os.unlink(csv_path)

        TimingResult.print_report()


@pytest.mark.slow
class TestDataCleaningPerformance:
    """Benchmark data cleaning time"""

    SIZES = [100, 500]

    def test_data_cleaning_time(self):
        """Measure complete data cleaning pipeline time"""
        from ml.data_cleaning import DataCleaner

        for size in self.SIZES:
            df = generate_test_dataframe(size)
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

            TimingResult.record('Data Cleaning', size, elapsed)
            assert elapsed < 5.0, f"Data cleaning {size} rows took too long: {elapsed:.4f}s"

        TimingResult.print_report()


@pytest.mark.slow
class TestFeatureEngineeringPerformance:
    """Benchmark feature engineering time"""

    SIZES = [100, 500]

    def test_feature_engineering_time(self):
        """Measure feature engineering pipeline time"""
        from ml.feature_engineering import FeatureEngineer

        for size in self.SIZES:
            df = generate_test_dataframe(size)
            engineer = FeatureEngineer()

            start = time.time()
            engineer.create_interaction_features(df)
            engineer.create_aggregate_features(df)
            result = engineer.create_department_features(df)
            elapsed = time.time() - start

            TimingResult.record('Feature Engineering', size, elapsed)
            assert elapsed < 3.0, f"Feature engineering {size} rows took too long: {elapsed:.4f}s"

        TimingResult.print_report()


@pytest.mark.slow
class TestPredictionPerformance:
    """Benchmark prediction time"""

    @pytest.fixture(autouse=True)
    def setup(self, engineered_dataframe, temp_model_dir):
        """Train a model once for prediction benchmarks"""
        from ml.train_model import ModelTrainer
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        trainer.save_model(temp_model_dir, feature_columns=X_train.columns.tolist())
        self.model_dir = temp_model_dir
        self.num_features = X_train.shape[1]

    def test_single_prediction_time(self):
        """Single prediction should be fast (< 1s)"""
        from ml.predict import PredictionEngine
        engine = PredictionEngine(model_dir=self.model_dir)
        engine.load_model()

        test_student = {f'feature_{i}': 0.5 for i in range(self.num_features)}
        test_student['cgpa'] = 8.0

        start = time.time()
        for _ in range(10):
            engine.predict_single(test_student)
        elapsed = time.time() - start
        avg = elapsed / 10

        TimingResult.record('Single Prediction (avg)', 10, avg)
        assert avg < 1.0, f"Single prediction too slow: {avg:.4f}s"

        TimingResult.print_report()

    def test_batch_prediction_time(self):
        """Batch prediction should be efficient"""
        from ml.predict import PredictionEngine
        import pandas as pd

        engine = PredictionEngine(model_dir=self.model_dir)
        engine.load_model()

        # Create batch of 50 students
        batch = pd.DataFrame([
            {f'feature_{i}': 0.5 for i in range(self.num_features)}
            for _ in range(50)
        ])

        start = time.time()
        results = engine.predict_batch(batch)
        elapsed = time.time() - start

        TimingResult.record('Batch Prediction (50)', 50, elapsed)
        assert elapsed < 5.0, f"Batch prediction too slow: {elapsed:.4f}s"
        assert len(results) == 50

        TimingResult.print_report()
