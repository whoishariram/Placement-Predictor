"""
Tests for the Prediction Engine Module (ml/predict.py)
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys
import json
import joblib
from unittest.mock import patch, MagicMock

_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from ml.predict import PredictionEngine, predict_from_student_data, batch_predict


class TestPredictionEngineInitialization:
    """Tests for PredictionEngine initialization"""

    def test_init_default_model_dir(self):
        """Default model dir is derived from file location"""
        engine = PredictionEngine()
        # Should point to .../Placement_Predictor/model/
        assert 'model' in engine.model_dir
        assert os.path.isabs(engine.model_dir)

    def test_init_custom_dir(self, temp_model_dir):
        """Custom model dir is accepted"""
        engine = PredictionEngine(model_dir=temp_model_dir)
        assert engine.model_dir == temp_model_dir

    def test_init_state(self):
        """Engine initializes with empty/unloaded state"""
        engine = PredictionEngine()
        assert engine.model is None
        assert engine.is_loaded is False
        assert engine.model_metadata is None
        assert engine.scaler is None
        assert engine.label_encoders is None
        assert engine.feature_columns is None


class TestPredictionEngineLoadModel:
    """Tests for load_model()"""

    def test_load_model_not_found_returns_false(self, tmp_path):
        """Loading from directory without model returns False"""
        engine = PredictionEngine(model_dir=str(tmp_path))
        result = engine.load_model()
        assert result is False
        assert engine.is_loaded is False

    def test_load_model_success(self, engineered_dataframe, temp_model_dir):
        """Loading a valid model sets is_loaded = True"""
        # First train and save a model
        from ml.train_model import ModelTrainer
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        trainer.save_model(temp_model_dir, feature_columns=X_train.columns.tolist())

        # Now try loading it
        engine = PredictionEngine(model_dir=temp_model_dir)
        result = engine.load_model()
        assert result is True
        assert engine.is_loaded is True
        assert engine.model is not None

    def test_load_model_loads_metadata(self, engineered_dataframe, temp_model_dir):
        """Loading model also loads model_metadata.json"""
        from ml.train_model import ModelTrainer
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        trainer.save_model(temp_model_dir)

        engine = PredictionEngine(model_dir=temp_model_dir)
        engine.load_model()
        assert engine.model_metadata is not None
        assert 'model_name' in engine.model_metadata
        assert 'accuracy' in engine.model_metadata


class TestPredictionEnginePrepareFeatures:
    """Tests for _prepare_features()"""

    def test_prepare_features_with_stored_columns(self, engineered_dataframe, temp_model_dir):
        """_prepare_features uses stored feature_columns"""
        from ml.train_model import ModelTrainer
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        trainer.save_model(temp_model_dir, feature_columns=X_train.columns.tolist())

        engine = PredictionEngine(model_dir=temp_model_dir)
        engine.load_model()

        # Prepare features from a small dict
        test_dict = {
            'cgpa': 8.5, 'tenth_percentage': 90.0, 'twelfth_percentage': 85.0,
            'communication_skill': 75, 'programming_skill': 80,
            'internships': 2, 'projects': 3, 'hackathons': 1, 'certifications': 2,
            'backlogs': 0, 'attendance': 85, 'aptitude_score': 75,
            'technical_score': 78, 'resume_score': 70,
            'department_encoded': 0
        }
        X = engine._prepare_features(pd.DataFrame([test_dict]))
        assert X is not None
        assert X.shape[1] == len(engine.feature_columns)
        # All values should be numeric
        assert X.dtypes.apply(lambda d: np.issubdtype(d, np.number)).all()

    def test_prepare_features_computes_derived(self, temp_model_dir):
        """_prepare_features computes derived features when stored columns are missing"""
        # Create a mock model with specific feature columns that include a derived feature
        engine = PredictionEngine(model_dir=temp_model_dir)
        engine.is_loaded = True
        engine.model = MagicMock()
        engine.feature_columns = ['cgpa', 'cgpa_programming_interaction', 'placement_readiness']

        test_dict = {
            'cgpa': 8.5, 'programming_skill': 80,
            'aptitude_score': 75, 'technical_score': 78,
            'communication_skill': 70, 'internships': 2, 'projects': 3,
            'certifications': 2, 'backlogs': 0, 'attendance': 85, 'resume_score': 70
        }
        X = engine._prepare_features(pd.DataFrame([test_dict]))
        assert X is not None
        assert X.shape[1] == 3
        assert not X.isnull().any().any()

    def test_prepare_features_fallback_no_columns(self, temp_model_dir):
        """Fallback path uses numeric columns when no stored feature_columns"""
        engine = PredictionEngine(model_dir=temp_model_dir)
        engine.is_loaded = True
        engine.model = MagicMock()

        df = pd.DataFrame({'a': [1, 2], 'b': [3.5, 4.2], 'c': ['x', 'y']})
        X = engine._prepare_features(df)
        assert X is not None
        # Should only pick numeric columns (a, b)
        assert 'a' in X.columns
        assert 'b' in X.columns
        assert 'c' not in X.columns


class TestPredictionEnginePredictSingle:
    """Tests for predict_single()"""

    def test_predict_single_not_loaded_returns_error(self, tmp_path):
        """Predicting without loaded model returns error result"""
        engine = PredictionEngine(model_dir=str(tmp_path))
        result = engine.predict_single({'cgpa': 8.0})
        assert result['status'] == 'error'
        assert result['prediction'] == -1

    def test_predict_single_returns_result(self, engineered_dataframe, temp_model_dir):
        """predict_single returns a valid result dict with a loaded model"""
        from ml.train_model import ModelTrainer
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        trainer.save_model(temp_model_dir, feature_columns=X_train.columns.tolist())

        engine = PredictionEngine(model_dir=temp_model_dir)
        engine.load_model()

        result = engine.predict_single({
            'cgpa': 8.5, 'department': 'Computer Science',
            'tenth_percentage': 90.0, 'twelfth_percentage': 85.0,
            'communication_skill': 75, 'programming_skill': 80,
            'internships': 2, 'projects': 3, 'hackathons': 1, 'certifications': 2,
            'backlogs': 0, 'attendance': 85, 'aptitude_score': 75,
            'technical_score': 78, 'resume_score': 70
        })
        assert result['status'] == 'success'
        assert result['prediction'] in [0, 1]
        assert 0 <= result['probability'] <= 100
        assert 0 <= result['confidence'] <= 100
        assert result['model_used'] is not None
        assert 'prediction_label' in result
        assert 'key_reasons' in result
        assert 'suggestions' in result

    def test_predict_result_keys(self, engineered_dataframe, temp_model_dir):
        """predict_single result contains all expected keys"""
        from ml.train_model import ModelTrainer
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        trainer.save_model(temp_model_dir, feature_columns=X_train.columns.tolist())

        engine = PredictionEngine(model_dir=temp_model_dir)
        engine.load_model()

        result = engine.predict_single({
            'cgpa': 7.5, 'department': 'Electronics',
            'tenth_percentage': 80.0, 'twelfth_percentage': 78.0,
            'communication_skill': 65, 'programming_skill': 60,
            'internships': 1, 'projects': 2, 'hackathons': 1, 'certifications': 1,
            'backlogs': 1, 'attendance': 75, 'aptitude_score': 65,
            'technical_score': 60, 'resume_score': 55
        })
        expected_keys = ['prediction', 'prediction_label', 'probability',
                         'confidence', 'confidence_level', 'model_used',
                         'key_reasons', 'suggestions', 'prediction_time', 'status']
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"

    def test_predict_with_various_thresholds(self, engineered_dataframe, temp_model_dir):
        """Predictions at different feature values still return valid results"""
        from ml.train_model import ModelTrainer
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        trainer.save_model(temp_model_dir, feature_columns=X_train.columns.tolist())

        engine = PredictionEngine(model_dir=temp_model_dir)
        engine.load_model()

        # Very weak student
        weak = engine.predict_single({
            'cgpa': 5.0, 'department': 'Mechanical',
            'tenth_percentage': 55.0, 'twelfth_percentage': 50.0,
            'communication_skill': 20, 'programming_skill': 15,
            'internships': 0, 'projects': 0, 'hackathons': 0, 'certifications': 0,
            'backlogs': 5, 'attendance': 50, 'aptitude_score': 20,
            'technical_score': 18, 'resume_score': 15
        })
        assert weak['status'] == 'success'
        assert 0 <= weak['probability'] <= 100
        assert len(weak['key_reasons']) > 0
        assert len(weak['suggestions']) > 0


class TestPredictionEngineBatchPrediction:
    """Tests for predict_batch()"""

    def test_batch_predict_returns_list(self, engineered_dataframe, temp_model_dir):
        """predict_batch returns a list of results"""
        from ml.train_model import ModelTrainer
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        trainer.save_model(temp_model_dir, feature_columns=X_train.columns.tolist())

        engine = PredictionEngine(model_dir=temp_model_dir)
        engine.load_model()

        # Create test batch
        test_df = pd.DataFrame([
            {'cgpa': 8.5, 'tenth_percentage': 90, 'twelfth_percentage': 85,
             'communication_skill': 75, 'programming_skill': 80,
             'internships': 2, 'projects': 3, 'hackathons': 1, 'certifications': 2,
             'backlogs': 0, 'attendance': 85, 'aptitude_score': 75,
             'technical_score': 78, 'resume_score': 70, 'name': 'Alice',
             'student_id': 'STU001', 'department': 'CS'},
            {'cgpa': 6.0, 'tenth_percentage': 65, 'twelfth_percentage': 60,
             'communication_skill': 35, 'programming_skill': 30,
             'internships': 0, 'projects': 1, 'hackathons': 0, 'certifications': 0,
             'backlogs': 3, 'attendance': 60, 'aptitude_score': 35,
             'technical_score': 30, 'resume_score': 25, 'name': 'Bob',
             'student_id': 'STU002', 'department': 'ME'}
        ])
        results = engine.predict_batch(test_df)
        assert isinstance(results, list)
        assert len(results) == 2
        for r in results:
            assert 'student_id' in r
            assert 'prediction' in r
            assert 'probability' in r
            assert 0 <= r['probability'] <= 100

    def test_batch_predict_empty_list(self, temp_model_dir):
        """Empty input returns empty list without error"""
        engine = PredictionEngine(model_dir=str(temp_model_dir))
        engine.is_loaded = True
        engine.model = MagicMock()
        results = engine.predict_batch(pd.DataFrame())
        assert results == []


class TestPredictionEngineComputeDerivedFeature:
    """Tests for _compute_derived_feature()"""

    def test_compute_cgpa_interaction(self):
        """cgpa_programming_interaction is computed correctly"""
        engine = PredictionEngine()
        df = pd.DataFrame({'cgpa': [8.0, 6.5], 'programming_skill': [80, 40]})
        result = engine._compute_derived_feature('cgpa_programming_interaction', df)
        assert result[0] == 8.0 * (80 / 100)
        assert result[1] == 6.5 * (40 / 100)

    def test_compute_academic_performance(self):
        """academic_performance_score averages cgpa(×10), 10th, 12th"""
        engine = PredictionEngine()
        df = pd.DataFrame({
            'cgpa': [8.0], 'tenth_percentage': [90.0], 'twelfth_percentage': [85.0]
        })
        result = engine._compute_derived_feature('academic_performance_score', df)
        expected = np.mean([80, 90, 85])
        assert result[0] == expected

    def test_compute_unknown_feature_returns_zero(self):
        """Unknown derived feature returns 0"""
        engine = PredictionEngine()
        df = pd.DataFrame({'cgpa': [8.0]})
        result = engine._compute_derived_feature('nonexistent_feature', df)
        assert result == 0


class TestPredictionEngineCalculateConfidence:
    """Tests for _calculate_confidence()"""

    def test_confidence_at_boundary(self):
        """At 50% probability, confidence should be 50"""
        engine = PredictionEngine()
        conf = engine._calculate_confidence(50.0, None)
        assert conf == 50.0

    def test_confidence_at_extreme(self):
        """At 100% probability, confidence should be 100"""
        engine = PredictionEngine()
        conf = engine._calculate_confidence(100.0, None)
        assert conf == 100.0

    def test_confidence_mid_range(self):
        """At 75% probability, confidence should be 75"""
        engine = PredictionEngine()
        conf = engine._calculate_confidence(75.0, None)
        assert conf == 75.0

    def test_confidence_never_below_50(self):
        """Confidence is always at least 50"""
        engine = PredictionEngine()
        conf = engine._calculate_confidence(50.0, None)
        assert conf >= 50


class TestPredictionEngineGetPredictionReasons:
    """Tests for _get_prediction_reasons()"""

    def test_reasons_for_high_performer(self, sample_student_dict):
        """High-performing student gets positive reasons"""
        engine = PredictionEngine()
        reasons = engine._get_prediction_reasons(sample_student_dict, 1, 90.0)
        assert len(reasons) > 0
        # High cgpa should trigger positive reason
        positive = [r for r in reasons if r.startswith("✅")]
        assert len(positive) > 0

    def test_reasons_for_low_performer(self, sample_student_dict_low_performer):
        """Low-performing student gets negative/warning reasons"""
        engine = PredictionEngine()
        reasons = engine._get_prediction_reasons(sample_student_dict_low_performer, 0, 20.0)
        assert len(reasons) > 0
        negative = [r for r in reasons if
                     r.startswith("❌") or r.startswith("⚠️") or r.startswith("💡")]
        assert len(negative) > 0

    def test_reasons_limited(self, sample_student_dict):
        """Reasons list should not exceed 8 items"""
        engine = PredictionEngine()
        reasons = engine._get_prediction_reasons(sample_student_dict, 1, 85.0)
        assert len(reasons) <= 8


class TestPredictionEngineGetImprovementSuggestions:
    """Tests for _get_improvement_suggestions()"""

    def test_suggestions_for_low_cgpa(self, sample_student_dict_low_performer):
        """Student with low cgpa gets improvement suggestions"""
        engine = PredictionEngine()
        suggestions = engine._get_improvement_suggestions(
            sample_student_dict_low_performer, 0, 20.0, ['Low CGPA']
        )
        # Should include CGPA improvement
        cgpa_suggestions = [s for s in suggestions if 'CGPA' in s or 'cgpa' in s.lower()]
        assert len(cgpa_suggestions) > 0

    def test_suggestions_not_empty(self, sample_student_dict):
        """All students get at least some suggestions"""
        engine = PredictionEngine()
        suggestions = engine._get_improvement_suggestions(
            sample_student_dict, 1, 80.0, []
        )
        assert len(suggestions) > 0

    def test_suggestions_limited(self, sample_student_dict_low_performer):
        """Suggestions list should not exceed 6 items"""
        engine = PredictionEngine()
        suggestions = engine._get_improvement_suggestions(
            sample_student_dict_low_performer, 0, 15.0, ['Many issues']
        )
        assert len(suggestions) <= 6

    def test_special_suggestions_for_not_placed(self, sample_student_dict_low_performer):
        """Students predicted as not placed get encouragement"""
        engine = PredictionEngine()
        suggestions = engine._get_improvement_suggestions(
            sample_student_dict_low_performer, 0, 20.0, ['Low CGPA']
        )
        encouragement = [s for s in suggestions if 'discouraged' in s or 'Start preparing' in s]
        assert len(encouragement) > 0


class TestPredictionEngineGetConfidenceLevel:
    """Tests for _get_confidence_level()"""

    def test_very_high(self):
        engine = PredictionEngine()
        assert engine._get_confidence_level(95) == "Very High"

    def test_high(self):
        engine = PredictionEngine()
        assert engine._get_confidence_level(80) == "High"

    def test_moderate(self):
        engine = PredictionEngine()
        assert engine._get_confidence_level(65) == "Moderate"

    def test_low(self):
        engine = PredictionEngine()
        assert engine._get_confidence_level(40) == "Low"

    def test_very_low(self):
        engine = PredictionEngine()
        assert engine._get_confidence_level(20) == "Very Low"


class TestPredictionEngineErrorResult:
    """Tests for _error_result()"""

    def test_error_result_structure(self):
        """Error result contains error keys and status"""
        engine = PredictionEngine()
        result = engine._error_result("Something went wrong")
        assert result['status'] == 'error'
        assert result['error_message'] == "Something went wrong"
        assert result['prediction'] == -1
        assert result['prediction_label'] == 'Error'


class TestPredictionEngineGetModelInfo:
    """Tests for get_model_info()"""

    def test_model_info_not_loaded(self):
        """Without loaded model, returns status message"""
        engine = PredictionEngine()
        info = engine.get_model_info()
        assert info == {'status': 'No model loaded'}

    def test_model_info_loaded(self, engineered_dataframe, temp_model_dir):
        """With loaded model, returns model details"""
        from ml.train_model import ModelTrainer
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        trainer.save_model(temp_model_dir)

        engine = PredictionEngine(model_dir=temp_model_dir)
        engine.load_model()
        info = engine.get_model_info()
        assert info['is_loaded'] is True
        assert 'model_name' in info
        assert 'model_type' in info


class TestConvenienceFunctions:
    """Tests for module-level convenience functions"""

    def test_predict_from_student_data_no_model(self, tmp_path):
        """predict_from_student_data returns error without model"""
        result = predict_from_student_data(
            {'cgpa': 8.0}, model_dir=str(tmp_path)
        )
        assert result['status'] == 'error'
        assert 'Failed to load model' in result.get('error_message', '')

    def test_batch_predict_no_model(self, tmp_path):
        """batch_predict returns empty list without model"""
        result = batch_predict(
            [{'cgpa': 8.0}], model_dir=str(tmp_path)
        )
        assert result == []

    def test_predict_from_student_data_with_model(self, engineered_dataframe, temp_model_dir):
        """predict_from_student_data returns valid result with loaded model"""
        from ml.train_model import ModelTrainer
        df, engineer = engineered_dataframe
        trainer = ModelTrainer()
        X_train, X_test, y_train, y_test, _ = engineer.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        trainer.train_all_models(X_train, y_train, X_test, y_test)
        trainer.save_model(temp_model_dir, feature_columns=X_train.columns.tolist())

        result = predict_from_student_data(
            {
                'cgpa': 8.5, 'department': 'CS',
                'tenth_percentage': 90, 'twelfth_percentage': 85,
                'communication_skill': 75, 'programming_skill': 80,
                'internships': 2, 'projects': 3, 'hackathons': 1, 'certifications': 2,
                'backlogs': 0, 'attendance': 85, 'aptitude_score': 75,
                'technical_score': 78, 'resume_score': 70
            },
            model_dir=temp_model_dir
        )
        assert result['status'] == 'success'
        assert result['prediction'] in [0, 1]
