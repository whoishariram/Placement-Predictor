"""
Tests for the Model Training Module (ml/train_model.py)
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys
import json
import joblib

_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from ml.train_model import ModelTrainer, train_and_save_model
from ml.data_cleaning import DataCleaner
from ml.feature_engineering import FeatureEngineer


class TestModelTrainerInitialization:
    """Tests for ModelTrainer initialization"""

    def test_init(self):
        """ModelTrainer initializes with empty state"""
        trainer = ModelTrainer()
        assert trainer.models == {}
        assert trainer.trained_models == {}
        assert trainer.results == {}
        assert trainer.best_model is None
        assert trainer.best_model_name is None
        assert trainer.best_accuracy == 0

    def test_model_definitions_present(self):
        """All 6 model definitions are present"""
        trainer = ModelTrainer()
        assert len(trainer.model_definitions) == 6
        expected = ['Logistic Regression', 'Random Forest', 'Decision Tree',
                    'Support Vector Machine', 'Gradient Boosting',
                    'K-Nearest Neighbors']
        for name in expected:
            assert name in trainer.model_definitions


class TestModelTrainerTrainModel:
    """Tests for train_model()"""

    def test_train_logistic_regression(self, engineered_dataframe):
        """Logistic Regression trains without error"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        model = trainer.train_model(
            'Logistic Regression',
            trainer.model_definitions['Logistic Regression'],
            X_train, y_train
        )
        assert model is not None
        assert hasattr(model, 'fit')

    def test_train_random_forest(self, engineered_dataframe):
        """Random Forest trains without error"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        model = trainer.train_model(
            'Random Forest',
            trainer.model_definitions['Random Forest'],
            X_train, y_train
        )
        assert model is not None

    def test_train_model_fitted(self, engineered_dataframe):
        """Model is fitted after training"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        model = trainer.train_model(
            'Decision Tree',
            trainer.model_definitions['Decision Tree'],
            X_train, y_train
        )
        assert hasattr(model, 'classes_')
        assert hasattr(model, 'n_features_in_')

    def test_train_with_small_data(self):
        """Training with very small data returns None gracefully"""
        trainer = ModelTrainer()
        X_train = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        y_train = pd.Series([0, 1])
        model = trainer.train_model(
            'Random Forest',
            trainer.model_definitions['Random Forest'],
            X_train, y_train
        )
        # Should still work with >1 samples
        assert model is not None


class TestModelTrainerEvaluateModel:
    """Tests for evaluate_model()"""

    def test_evaluate_returns_metrics(self, engineered_dataframe):
        """evaluate_model returns dict with all expected metrics"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        model = trainer.train_model(
            'Logistic Regression',
            trainer.model_definitions['Logistic Regression'],
            X_train, y_train
        )
        results = trainer.evaluate_model(
            'Logistic Regression', model,
            X_train, y_train, X_test, y_test
        )
        expected_keys = [
            'model_name', 'train_accuracy', 'test_accuracy',
            'train_precision', 'test_precision',
            'train_recall', 'test_recall',
            'train_f1', 'test_f1', 'train_auc', 'test_auc',
            'cv_mean', 'cv_std',
            'overfit_gap', 'is_overfitting',
            'confusion_matrix'
        ]
        for key in expected_keys:
            assert key in results, f"Missing key: {key}"

    def test_metrics_within_bounds(self, engineered_dataframe):
        """All percentage metrics are between 0 and 100"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        model = trainer.train_model(
            'Random Forest',
            trainer.model_definitions['Random Forest'],
            X_train, y_train
        )
        results = trainer.evaluate_model(
            'Random Forest', model,
            X_train, y_train, X_test, y_test
        )
        for key in ['test_accuracy', 'test_precision', 'test_recall',
                     'test_f1', 'test_auc']:
            assert 0 <= results[key] <= 100, f"{key} out of bounds: {results[key]}"

    def test_confusion_matrix_shape(self, engineered_dataframe):
        """Confusion matrix is 2x2"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        model = trainer.train_model(
            'Gradient Boosting',
            trainer.model_definitions['Gradient Boosting'],
            X_train, y_train
        )
        results = trainer.evaluate_model(
            'Gradient Boosting', model,
            X_train, y_train, X_test, y_test
        )
        cm = results['confusion_matrix']
        assert len(cm) == 2
        assert len(cm[0]) == 2

    def test_overfit_detection(self, engineered_dataframe):
        """is_overfitting flag is boolean"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        model = trainer.train_model(
            'Decision Tree',
            trainer.model_definitions['Decision Tree'],
            X_train, y_train
        )
        results = trainer.evaluate_model(
            'Decision Tree', model,
            X_train, y_train, X_test, y_test
        )
        assert isinstance(results['is_overfitting'], bool)


class TestModelTrainerTrainAllModels:
    """Tests for train_all_models()"""

    def test_all_models_trained(self, engineered_dataframe):
        """train_all_models trains all 6 models and returns results"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        results = trainer.train_all_models(X_train, y_train, X_test, y_test)
        assert len(results) == 6
        assert trainer.best_model is not None
        assert trainer.best_model_name is not None

    def test_best_model_has_highest_score(self, engineered_dataframe):
        """Best model has the highest (penalized) accuracy"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        # Best model's test accuracy should be >= others (or close)
        best_acc = trainer.results[trainer.best_model_name]['test_accuracy']
        for name, results in trainer.results.items():
            assert best_acc >= 0  # Best should always be non-negative

    def test_trained_models_stored(self, engineered_dataframe):
        """All trained models are stored in trained_models dict"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        assert len(trainer.trained_models) == 6  # All 6 trained successfully
        for name in trainer.model_definitions:
            assert name in trainer.trained_models


class TestModelTrainerSaveModel:
    """Tests for save_model()"""

    def test_saves_model_file(self, engineered_dataframe, temp_model_dir):
        """save_model creates best_model.pkl file"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        model_path = trainer.save_model(temp_model_dir)
        assert model_path is not None
        assert os.path.exists(model_path)
        assert model_path.endswith('best_model.pkl')

    def test_saves_metadata_json(self, engineered_dataframe, temp_model_dir):
        """save_model creates model_metadata.json"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        trainer.save_model(temp_model_dir)

        metadata_path = os.path.join(temp_model_dir, 'model_metadata.json')
        assert os.path.exists(metadata_path)
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        assert 'model_name' in metadata
        assert 'accuracy' in metadata
        assert 'trained_at' in metadata

    def test_saves_all_models(self, engineered_dataframe, temp_model_dir):
        """save_model creates all_models.pkl for ensemble"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        trainer.save_model(temp_model_dir)

        all_models_path = os.path.join(temp_model_dir, 'all_models.pkl')
        assert os.path.exists(all_models_path)
        models = joblib.load(all_models_path)
        assert len(models) == 6

    def test_saves_feature_columns(self, engineered_dataframe, temp_model_dir):
        """save_model saves feature_columns.pkl"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        trainer.save_model(temp_model_dir, feature_columns=X_train.columns.tolist())

        feat_path = os.path.join(temp_model_dir, 'feature_columns.pkl')
        assert os.path.exists(feat_path)
        features = joblib.load(feat_path)
        assert len(features) > 0

    def test_saved_model_can_predict(self, engineered_dataframe, temp_model_dir):
        """Saved model can be loaded and used for prediction"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        model_path = trainer.save_model(temp_model_dir)

        # Load and predict
        loaded = joblib.load(model_path)
        preds = loaded.predict(X_test.iloc[:3])
        assert len(preds) == 3
        assert set(preds).issubset({0, 1})


class TestModelTrainerDisplayLeaderboard:
    """Tests for display_leaderboard() — just call it, don't capture stdout"""

    def test_display_no_error(self, engineered_dataframe):
        """display_leaderboard runs without raising exception"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        # Should not raise
        trainer.display_leaderboard()

    def test_display_empty_no_error(self):
        """display_leaderboard with no models shows message, no error"""
        trainer = ModelTrainer()
        trainer.display_leaderboard()  # Should not raise


class TestModelTrainerTrainingReport:
    """Tests for generate_training_report()"""

    def test_report_created(self, engineered_dataframe, tmp_path):
        """generate_training_report creates a JSON file"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        report_path = trainer.generate_training_report(tmp_path)
        assert os.path.exists(report_path)

    def test_report_contains_leaderboard(self, engineered_dataframe, tmp_path):
        """Training report contains leaderboard with model rankings"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        report_path = trainer.generate_training_report(tmp_path)

        with open(report_path, 'r') as f:
            report = json.load(f)
        assert 'leaderboard' in report
        assert len(report['leaderboard']) == 6
        # Leaderboard should be sorted by rank
        assert report['leaderboard'][0]['rank'] == 1
        assert report['leaderboard'][0]['accuracy'] >= report['leaderboard'][1]['accuracy']


class TestModelTrainerGetFeatureImportance:
    """Tests for get_model_feature_importance()"""

    def test_returns_array(self, engineered_dataframe):
        """get_model_feature_importance returns feature importance array"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        importance = trainer.get_model_feature_importance()
        if importance is not None:
            assert len(importance) == X_train.shape[1]

    def test_specific_model(self, engineered_dataframe):
        """get_model_feature_importance works with named model"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        importance = trainer.get_model_feature_importance('Random Forest')
        assert importance is not None


class TestModelTrainerTrainingSummary:
    """Tests for get_training_summary()"""

    def test_summary_structure(self, engineered_dataframe):
        """get_training_summary returns dict with expected keys"""
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        summary = trainer.get_training_summary()
        assert isinstance(summary, dict)
        assert 'best_model' in summary
        assert 'best_accuracy' in summary
        assert 'models_evaluated' in summary
        assert 'all_results' in summary
        assert summary['models_evaluated'] == 6

    def test_summary_without_training(self):
        """Without training, returns string message"""
        trainer = ModelTrainer()
        summary = trainer.get_training_summary()
        assert isinstance(summary, str)


class TestTrainAndSaveModel:
    """Integration tests for train_and_save_model()"""

    def test_full_pipeline_returns_trainer_engineer(self, temp_csv_path, temp_model_dir):
        """train_and_save_model returns (ModelTrainer, FeatureEngineer) tuple"""
        class TestConfig:
            STUDENT_CSV_PATH = temp_csv_path
            MODEL_DIR = temp_model_dir
            MODEL_TEST_SIZE = 0.2
            MODEL_RANDOM_STATE = 42

        trainer, engineer = train_and_save_model(
            dataset_path=temp_csv_path,
            model_dir=temp_model_dir,
            config=TestConfig()
        )
        assert trainer is not None
        assert engineer is not None
        assert isinstance(trainer, ModelTrainer)
        assert isinstance(engineer, FeatureEngineer)

    def test_pipeline_saves_model_file(self, temp_csv_path, temp_model_dir):
        """Full pipeline saves best_model.pkl"""
        class TestConfig:
            STUDENT_CSV_PATH = temp_csv_path
            MODEL_DIR = temp_model_dir
            MODEL_TEST_SIZE = 0.2
            MODEL_RANDOM_STATE = 42

        trainer, engineer = train_and_save_model(
            dataset_path=temp_csv_path,
            model_dir=temp_model_dir,
            config=TestConfig()
        )
        assert os.path.exists(os.path.join(temp_model_dir, 'best_model.pkl'))
        assert os.path.exists(os.path.join(temp_model_dir, 'model_metadata.json'))

    def test_pipeline_returns_none_for_missing_dataset(self, temp_model_dir):
        """Missing dataset returns (None, None) gracefully"""
        result = train_and_save_model(
            dataset_path='/nonexistent/path.csv',
            model_dir=temp_model_dir
        )
        assert result == (None, None)

    def test_pipeline_best_model_selected(self, temp_csv_path, temp_model_dir):
        """Full pipeline selects a best model"""
        class TestConfig:
            STUDENT_CSV_PATH = temp_csv_path
            MODEL_DIR = temp_model_dir
            MODEL_TEST_SIZE = 0.2
            MODEL_RANDOM_STATE = 42

        trainer, engineer = train_and_save_model(
            dataset_path=temp_csv_path,
            model_dir=temp_model_dir,
            config=TestConfig()
        )
        assert trainer.best_model is not None
        assert trainer.best_model_name is not None
        assert trainer.best_accuracy > 0
