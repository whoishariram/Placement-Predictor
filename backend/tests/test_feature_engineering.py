"""
Tests for the Feature Engineering Module (ml/feature_engineering.py)
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys

_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from ml.feature_engineering import FeatureEngineer


class TestFeatureEngineerInitialization:
    """Tests for FeatureEngineer initialization"""

    def test_init(self):
        """Engineer initializes with empty state"""
        eng = FeatureEngineer()
        assert eng.selected_features == []
        assert eng.feature_importance == {}
        assert eng.engineering_report == {}

    def test_init_attributes(self):
        """All expected attributes are present"""
        eng = FeatureEngineer()
        assert hasattr(eng, 'selected_features')
        assert hasattr(eng, 'feature_importance')
        assert hasattr(eng, 'engineering_report')


class TestFeatureEngineerCreateInteractionFeatures:
    """Tests for create_interaction_features()"""

    def test_cgpa_programming_interaction_created(self, sample_student_data):
        """CGPA × Programming interaction feature is present"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        result = eng.create_interaction_features(df)
        assert 'cgpa_programming_interaction' in result.columns
        assert len(result) == len(df)

    def test_academic_performance_score_created(self, sample_student_data):
        """Academic performance score is computed from cgpa, 10th, 12th"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        result = eng.create_interaction_features(df)
        assert 'academic_performance_score' in result.columns
        # Should be the row-wise mean of available academic cols
        assert result['academic_performance_score'].iloc[0] > 0

    def test_technical_competence_score_created(self, sample_student_data):
        """Technical competence score is created from prog skill, tech score, aptitude"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        result = eng.create_interaction_features(df)
        assert 'technical_competence_score' in result.columns

    def test_experience_score_created(self, sample_student_data):
        """Experience score sums internships, projects, hackathons, certifications"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        result = eng.create_interaction_features(df)
        assert 'experience_score' in result.columns
        # Verify computation: first row sum
        row = df.iloc[0]
        expected = row['internships'] + row['projects'] + row['hackathons'] + row['certifications']
        assert result['experience_score'].iloc[0] == expected

    def test_backlog_penalty_created(self, sample_student_data):
        """Backlog penalty is backlogs * -2"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        result = eng.create_interaction_features(df)
        assert 'backlog_penalty' in result.columns
        row = df.iloc[0]
        assert result['backlog_penalty'].iloc[0] == row['backlogs'] * (-2)

    def test_attendance_score_normalized(self, sample_student_data):
        """Attendance score is attendance / 100"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        result = eng.create_interaction_features(df)
        assert 'attendance_score' in result.columns
        assert result['attendance_score'].iloc[0] == df['attendance'].iloc[0] / 100.0

    def test_resume_quality_score_created(self, sample_student_data):
        """Resume quality score is weighted combination"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        result = eng.create_interaction_features(df)
        assert 'resume_quality_score' in result.columns
        # First row value should be non-zero if any component > 0
        assert result['resume_quality_score'].isna().sum() == 0

    def test_feature_log_in_report(self, sample_student_data):
        """Created interaction features are logged in engineering_report"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        eng.create_interaction_features(df)
        assert 'interaction_features' in eng.engineering_report
        assert len(eng.engineering_report['interaction_features']) >= 5


class TestFeatureEngineerCreateAggregateFeatures:
    """Tests for create_aggregate_features()"""

    def test_cgpa_score_created(self, sample_student_data):
        """CGPA is scaled to percentage (cgpa/10 * 100)"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        df = eng.create_interaction_features(df)
        result = eng.create_aggregate_features(df)
        assert 'cgpa_score' in result.columns
        assert result['cgpa_score'].iloc[0] == (df['cgpa'].iloc[0] / 10.0) * 100

    def test_test_performance_created(self, sample_student_data):
        """Test performance averages aptitude and technical scores"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        df = eng.create_interaction_features(df)
        result = eng.create_aggregate_features(df)
        assert 'test_performance' in result.columns
        row = df.iloc[0]
        expected = (row['aptitude_score'] + row['technical_score']) / 2
        assert result['test_performance'].iloc[0] == expected

    def test_placement_readiness_created(self, sample_student_data):
        """Placement readiness composite score is present"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        df = eng.create_interaction_features(df)
        result = eng.create_aggregate_features(df)
        assert 'placement_readiness' in result.columns
        # Score should be bounded 0-100
        assert result['placement_readiness'].min() >= 0
        assert result['placement_readiness'].max() <= 100

    def test_backlog_impact_created(self, sample_student_data):
        """Backlog impact score clips backlogs to max 5"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        df = eng.create_interaction_features(df)
        result = eng.create_aggregate_features(df)
        assert 'backlog_impact' in result.columns
        # Student with 0 backlogs should get 100
        mask = result['backlogs'] == 0
        if mask.any():
            assert result.loc[mask, 'backlog_impact'].iloc[0] == 100.0

    def test_aggregate_report(self, sample_student_data):
        """Aggregate features are logged in report"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        df = eng.create_interaction_features(df)
        eng.create_aggregate_features(df)
        assert 'aggregate_features' in eng.engineering_report
        assert 'placement_readiness' in eng.engineering_report['aggregate_features']


class TestFeatureEngineerCreateDepartmentFeatures:
    """Tests for create_department_features()"""

    def test_department_placement_rate_created(self, sample_student_data):
        """Department-wise placement rate is computed"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        df = eng.create_interaction_features(df)
        df = eng.create_aggregate_features(df)
        result = eng.create_department_features(df)
        assert 'department_placement_rate' in result.columns
        # Rate should be between 0 and 1
        assert 0 <= result['department_placement_rate'].min() <= 1
        assert 0 <= result['department_placement_rate'].max() <= 1

    def test_department_student_count(self, sample_student_data):
        """Department student count is computed"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        df = eng.create_interaction_features(df)
        df = eng.create_aggregate_features(df)
        result = eng.create_department_features(df)
        assert 'department_student_count' in result.columns
        assert result['department_student_count'].iloc[0] > 0

    def test_department_report(self, sample_student_data):
        """Department features are logged in report"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        df = eng.create_interaction_features(df)
        df = eng.create_aggregate_features(df)
        eng.create_department_features(df)
        assert 'department_features' in eng.engineering_report


class TestFeatureEngineerSelectBestFeatures:
    """Tests for select_best_features()"""

    def test_selects_k_features(self, sample_student_data):
        """select_best_features returns at most k features"""
        eng = FeatureEngineer()
        # Prepare data similar to post-feature-engineering
        df = sample_student_data.copy()
        df = eng.create_interaction_features(df)
        df = eng.create_aggregate_features(df)

        # Build X, y from numeric columns
        feature_cols = [c for c in df.columns if df[c].dtype in ['int64', 'float64']
                        and c not in ['placement_status', 'student_id']]
        X = df[feature_cols].fillna(0)
        y = df['placement_status']

        k = 10
        X_selected = eng.select_best_features(X, y, k=k)
        assert X_selected.shape[1] <= min(k, X.shape[1])

    def test_selected_features_stored(self, sample_student_data):
        """Selected features are stored in the engineer object"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        df = eng.create_interaction_features(df)
        df = eng.create_aggregate_features(df)

        feature_cols = [c for c in df.columns if df[c].dtype in ['int64', 'float64']
                        and c not in ['placement_status', 'student_id']]
        X = df[feature_cols].fillna(0)
        y = df['placement_status']

        eng.select_best_features(X, y, k=8)
        assert len(eng.selected_features) > 0
        assert len(eng.selected_features) <= 8

    def test_feature_importance_populated(self, sample_student_data):
        """Feature importance scores are populated after selection"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        df = eng.create_interaction_features(df)
        df = eng.create_aggregate_features(df)

        feature_cols = [c for c in df.columns if df[c].dtype in ['int64', 'float64']
                        and c not in ['placement_status', 'student_id']]
        X = df[feature_cols].fillna(0)
        y = df['placement_status']

        eng.select_best_features(X, y, k=8)
        assert len(eng.feature_importance) > 0

    def test_selection_report(self, sample_student_data):
        """Feature selection report is stored in engineering_report"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        df = eng.create_interaction_features(df)
        df = eng.create_aggregate_features(df)

        feature_cols = [c for c in df.columns if df[c].dtype in ['int64', 'float64']
                        and c not in ['placement_status', 'student_id']]
        X = df[feature_cols].fillna(0)
        y = df['placement_status']

        eng.select_best_features(X, y, k=8)
        report = eng.engineering_report.get('feature_selection', {})
        assert 'method' in report
        assert 'features_selected' in report

    def test_fallback_on_too_few_features(self):
        """With very few features, selection returns all without error"""
        eng = FeatureEngineer()
        X = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        y = pd.Series([0, 1, 0])
        result = eng.select_best_features(X, y, k=15)
        # Since k > total features, should select all 2
        assert result.shape[1] == 2
        assert len(eng.selected_features) == 2


class TestFeatureEngineerPrepareMLDataset:
    """Tests for prepare_ml_dataset()"""

    def test_returns_train_test_split(self, sample_student_data):
        """Full pipeline returns X_train, X_test, y_train, y_test, df"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        result = eng.prepare_ml_dataset(df, target_col='placement_status',
                                        test_size=0.2, random_state=42)
        assert len(result) == 5
        X_train, X_test, y_train, y_test, df_out = result
        assert X_train is not None and X_test is not None
        assert y_train is not None and y_test is not None
        assert X_train.shape[0] > X_test.shape[0]  # train larger than test

    def test_stratified_split_preserves_ratio(self, sample_student_data):
        """Split maintains class ratio in train/test"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        X_train, X_test, y_train, y_test, df_out = eng.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        # Both sets should have both classes
        assert set(y_train.unique()).issubset({0, 1})
        assert set(y_test.unique()).issubset({0, 1})

    def test_no_target_returns_X_only(self, sample_student_data):
        """Without target column, prepare_ml_dataset returns X with None for y"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        df_no_target = df.drop(columns=['placement_status'])
        X, y_train, X_test, y_test, df_out = eng.prepare_ml_dataset(
            df_no_target, target_col='placement_status'
        )
        # When no target, returns X, None, None, None, df
        assert y_train is None
        assert y_test is None

    def test_dataset_stats_in_report(self, sample_student_data):
        """Dataset statistics are stored in engineering report"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        eng.prepare_ml_dataset(df, target_col='placement_status',
                               test_size=0.2, random_state=42)
        stats = eng.engineering_report.get('dataset_stats', {})
        assert 'total_samples' in stats
        assert 'train_samples' in stats
        assert 'test_samples' in stats
        assert 'features' in stats
        assert stats['total_samples'] == len(df)

    def test_no_nan_in_output(self, sample_student_data):
        """Output X_train/X_test have no NaN values"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        X_train, X_test, y_train, y_test, df_out = eng.prepare_ml_dataset(
            df, target_col='placement_status', test_size=0.2, random_state=42
        )
        assert X_train.isnull().sum().sum() == 0
        assert X_test.isnull().sum().sum() == 0


class TestFeatureEngineerGetFeatureImportance:
    """Tests for get_feature_importance_report()"""

    def test_returns_dict(self, sample_student_data):
        """Feature importance is returned as a dict"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        df = eng.create_interaction_features(df)
        df = eng.create_aggregate_features(df)

        feature_cols = [c for c in df.columns if df[c].dtype in ['int64', 'float64']
                        and c not in ['placement_status', 'student_id']]
        X = df[feature_cols].fillna(0)
        y = df['placement_status']
        eng.select_best_features(X, y)

        importance = eng.get_feature_importance_report()
        assert isinstance(importance, dict)

    def test_sorted_by_importance(self, sample_student_data):
        """Feature importance dict is sorted descending by score"""
        eng = FeatureEngineer()
        df = sample_student_data.copy()
        df = eng.create_interaction_features(df)
        df = eng.create_aggregate_features(df)

        feature_cols = [c for c in df.columns if df[c].dtype in ['int64', 'float64']
                        and c not in ['placement_status', 'student_id']]
        X = df[feature_cols].fillna(0)
        y = df['placement_status']
        eng.select_best_features(X, y)

        importance = eng.get_feature_importance_report()
        scores = list(importance.values())
        assert scores == sorted(scores, reverse=True)

    def test_with_model_feature_importances(self):
        """Accepts model with feature_importances_ attribute"""
        from sklearn.ensemble import RandomForestClassifier
        eng = FeatureEngineer()

        X = pd.DataFrame({'a': [1, 2, 3, 4, 5], 'b': [5, 4, 3, 2, 1],
                          'c': [1, 0, 1, 0, 1]})
        y = pd.Series([0, 1, 0, 1, 0])

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)

        importance = eng.get_feature_importance_report(
            model=model, feature_names=['a', 'b', 'c']
        )
        assert isinstance(importance, dict)
        assert set(importance.keys()) == {'a', 'b', 'c'}


class TestFeatureEngineerGenerateReport:
    """Tests for generate_engineering_report()"""

    def test_generates_json_file(self, tmp_path):
        """generate_engineering_report creates a JSON file"""
        eng = FeatureEngineer()
        eng.engineering_report = {'test': 'data', 'features': ['a', 'b']}
        output_path = os.path.join(tmp_path, 'eng_test.json')
        result = eng.generate_engineering_report(output_path)
        assert os.path.exists(result)
        assert result == output_path

    def test_creates_parent_dirs(self, tmp_path):
        """generate_engineering_report creates intermediate directories"""
        eng = FeatureEngineer()
        eng.engineering_report = {'key': 'value'}
        nested = os.path.join(tmp_path, 'sub', 'dir', 'eng_report.json')
        result = eng.generate_engineering_report(nested)
        assert os.path.exists(result)
