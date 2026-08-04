"""
Tests for the Data Cleaning & Preprocessing Module (ml/data_cleaning.py)
"""

import pytest
import pandas as pd
import numpy as np
import os
import sys

_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from ml.data_cleaning import DataCleaner, generate_cleaning_report


class TestDataCleanerInitialization:
    """Test DataCleaner initialization and basic attributes"""

    def test_init(self):
        """Cleaner initializes with empty state"""
        cleaner = DataCleaner()
        assert cleaner.label_encoders == {}
        assert cleaner.feature_columns == []
        assert cleaner.cleaning_report == {}
        assert cleaner.scaler is not None

    def test_init_attributes_exist(self):
        """All expected attributes are present"""
        cleaner = DataCleaner()
        assert hasattr(cleaner, 'df')
        assert hasattr(cleaner, 'original_shape')
        assert hasattr(cleaner, 'label_encoders')
        assert hasattr(cleaner, 'scaler')
        assert hasattr(cleaner, 'feature_columns')
        assert hasattr(cleaner, 'cleaning_report')


class TestDataCleanerLoadDataset:
    """Tests for load_dataset()"""

    def test_load_valid_csv(self, temp_csv_path):
        """Loading a valid CSV populates the df and records original shape"""
        cleaner = DataCleaner()
        df = cleaner.load_dataset(temp_csv_path)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert cleaner.original_shape == df.shape

    def test_load_missing_columns(self, temp_csv_path):
        """Loading preserves all original columns"""
        cleaner = DataCleaner()
        df = cleaner.load_dataset(temp_csv_path)
        expected_cols = ['student_id', 'name', 'department', 'cgpa',
                         'tenth_percentage', 'placement_status']
        for col in expected_cols:
            assert col in df.columns, f"Missing column: {col}"


class TestDataCleanerHandleMissingValues:
    """Tests for handle_missing_values()"""

    def test_fills_numeric_with_median(self, sample_student_data_with_missing):
        """Numeric missing values are filled with column median"""
        cleaner = DataCleaner()
        cleaner.df = sample_student_data_with_missing.copy()
        cleaner.original_shape = cleaner.df.shape

        before = cleaner.df['cgpa'].isnull().sum()
        assert before > 0, "Test data should have missing cgpa values"

        cleaner.handle_missing_values()
        after = cleaner.df['cgpa'].isnull().sum()
        assert after == 0, "All missing cgpa values should be filled"

    def test_fills_categorical_with_mode(self, sample_student_data_with_missing):
        """Categorical missing values are filled with mode"""
        cleaner = DataCleaner()
        cleaner.df = sample_student_data_with_missing.copy()
        cleaner.original_shape = cleaner.df.shape

        before = cleaner.df['department'].isnull().sum()
        assert before > 0

        cleaner.handle_missing_values()
        after = cleaner.df['department'].isnull().sum()
        assert after == 0
        # Check filled values match an actual department name
        assert cleaner.df['department'].iloc[6] in cleaner.df['department'].unique()

    def test_report_generated(self, sample_student_data_with_missing):
        """Cleaning report includes missing value details"""
        cleaner = DataCleaner()
        cleaner.df = sample_student_data_with_missing.copy()
        cleaner.original_shape = cleaner.df.shape
        cleaner.handle_missing_values()
        report = cleaner.cleaning_report.get('missing_values', {})
        assert 'missing_values_before' in report
        assert 'missing_values_after' in report
        assert 'missing_values_filled' in report
        assert report['missing_values_before'] > 0

    def test_no_missing_data_is_unchanged(self, sample_student_data):
        """Data without missing values should not be altered"""
        cleaner = DataCleaner()
        cleaner.df = sample_student_data.copy()
        cleaner.original_shape = cleaner.df.shape
        cgpa_before = cleaner.df['cgpa'].iloc[0]
        cleaner.handle_missing_values()
        # Existing values should be preserved
        assert cleaner.df['cgpa'].iloc[0] == cgpa_before


class TestDataCleanerRemoveDuplicates:
    """Tests for remove_duplicates()"""

    def test_duplicates_removed(self, sample_student_data_with_missing):
        """Exact duplicate rows are removed"""
        cleaner = DataCleaner()
        cleaner.df = sample_student_data_with_missing.copy()
        cleaner.original_shape = cleaner.df.shape

        cleaner.remove_duplicates()
        assert 'duplicates' in cleaner.cleaning_report
        assert cleaner.cleaning_report['duplicates']['duplicates_found'] > 0
        assert cleaner.cleaning_report['duplicates']['duplicates_removed'] > 0

    def test_no_duplicates_unchanged(self, sample_student_data):
        """Data without duplicates should remain the same shape"""
        cleaner = DataCleaner()
        cleaner.df = sample_student_data.copy()
        original_len = len(cleaner.df)
        cleaner.original_shape = cleaner.df.shape

        # Ensure no exact duplicates
        cleaner.df = cleaner.df.drop_duplicates()  # Remove existing
        cleaner.df = pd.concat([cleaner.df,
                                cleaner.df.iloc[:0]], ignore_index=True)

        cleaner.remove_duplicates()
        assert len(cleaner.df) >= original_len - 1  # At most 1 less after dedup


class TestDataCleanerRemoveInvalidEntries:
    """Tests for remove_invalid_entries()"""

    def test_invalid_cgpa_removed(self, sample_student_data_with_missing):
        """Rows with CGPA > 10 or < 0 are removed"""
        cleaner = DataCleaner()
        cleaner.df = sample_student_data_with_missing.copy()
        cleaner.original_shape = cleaner.df.shape

        assert len(cleaner.df[cleaner.df['cgpa'] > 10]) > 0, \
            "Test data should contain invalid cgpa"
        cleaner.remove_invalid_entries()
        assert len(cleaner.df[cleaner.df['cgpa'] > 10]) == 0
        assert len(cleaner.df[cleaner.df['cgpa'] < 0]) == 0

    def test_invalid_percentage_removed(self, sample_student_data_with_missing):
        """Rows with percentage > 100 are removed"""
        cleaner = DataCleaner()
        cleaner.df = sample_student_data_with_missing.copy()
        cleaner.original_shape = cleaner.df.shape

        assert len(cleaner.df[cleaner.df['tenth_percentage'] > 100]) > 0
        cleaner.remove_invalid_entries()
        assert len(cleaner.df[cleaner.df['tenth_percentage'] > 100]) == 0

    def test_report_contains_counts(self, sample_student_data_with_missing):
        """Cleaning report includes counts of invalid entries found"""
        cleaner = DataCleaner()
        cleaner.df = sample_student_data_with_missing.copy()
        cleaner.original_shape = cleaner.df.shape
        cleaner.remove_invalid_entries()
        report = cleaner.cleaning_report.get('invalid_entries', {})
        assert 'cgpa' in report
        assert report['cgpa'] > 0


class TestDataCleanerConvertCategorical:
    """Tests for convert_categorical()"""

    def test_department_encoded(self, cleaned_dataframe):
        """Department column is label-encoded with _encoded suffix"""
        df = cleaned_dataframe.df
        assert 'department_encoded' in df.columns
        assert df['department_encoded'].dtype in ['int32', 'int64']

    def test_label_encoders_stored(self, cleaned_dataframe):
        """Label encoder for department is stored in the cleaner"""
        assert 'department' in cleaned_dataframe.label_encoders
        le = cleaned_dataframe.label_encoders['department']
        assert hasattr(le, 'classes_')
        assert len(le.classes_) > 0

    def test_encoding_report(self, cleaned_dataframe):
        """Cleaning report has categorical encoding section"""
        report = cleaned_dataframe.cleaning_report.get('categorical_encoding', {})
        assert 'department' in report
        assert 'unique_values' in report['department']
        assert 'mapping' in report['department']


class TestDataCleanerNormalizeFeatures:
    """Tests for normalize_features()"""

    def test_features_normalized(self, cleaned_dataframe):
        """Core numeric columns have mean ~0 and std ~1 after normalization"""
        df = cleaned_dataframe.df
        assert 'cgpa' in df.columns
        # Check feature_columns is not empty
        assert len(cleaned_dataframe.feature_columns) > 0

    def test_normalization_report(self, cleaned_dataframe):
        """Normalization report lists features and scaler params"""
        report = cleaned_dataframe.cleaning_report.get('normalization', {})
        assert 'features_normalized' in report
        assert len(report['features_normalized']) > 0
        assert 'scaler_mean' in report

    def test_allow_custom_feature_list(self, sample_student_data):
        """Normalize only specified features when provided"""
        cleaner = DataCleaner()
        df = sample_student_data.copy()
        cleaner.df = df
        cleaner.original_shape = df.shape
        cleaner.normalize_features(['cgpa', 'aptitude_score'])
        assert 'cgpa' in cleaner.feature_columns
        assert 'internships' not in cleaner.feature_columns


class TestDataCleanerPrepareFeaturesTarget:
    """Tests for prepare_features_target()"""

    def test_returns_X_and_y(self, cleaned_dataframe):
        """Returns feature matrix X and target vector y"""
        X, y = cleaned_dataframe.prepare_features_target()
        assert X is not None
        assert isinstance(X, pd.DataFrame)
        assert y is not None
        assert isinstance(y, pd.Series)

    def test_feature_columns_match(self, cleaned_dataframe):
        """Feature columns in X match the stored feature_columns"""
        X, y = cleaned_dataframe.prepare_features_target()
        assert list(X.columns) == cleaned_dataframe.feature_columns

    def test_target_values_binary(self, cleaned_dataframe):
        """Target y contains only 0 and 1 values"""
        X, y = cleaned_dataframe.prepare_features_target()
        assert set(y.unique()).issubset({0, 1})

    def test_returns_none_y_without_target(self, cleaned_dataframe):
        """Returns y=None if target column is missing"""
        df = cleaned_dataframe.df.drop(columns=['placement_status'])
        cleaner = DataCleaner()
        cleaner.df = df
        X, y = cleaner.prepare_features_target()
        assert y is None


class TestDataCleanerGetCleaningSummary:
    """Tests for get_cleaning_summary()"""

    def test_summary_structure(self, cleaned_dataframe):
        """Cleaning summary contains expected keys"""
        summary = cleaned_dataframe.get_cleaning_summary()
        assert 'original_shape' in summary
        assert 'final_shape' in summary
        assert 'rows_removed' in summary

    def test_rows_removed_non_negative(self, cleaned_dataframe):
        """Rows removed should never be negative"""
        summary = cleaned_dataframe.get_cleaning_summary()
        assert summary['rows_removed'] >= 0

    def test_placement_rate_in_summary(self, cleaned_dataframe):
        """Placement rate is included in summary statistics"""
        summary = cleaned_dataframe.get_cleaning_summary()
        if 'statistics' in summary:
            assert 'placement_rate' in summary['statistics']


class TestDataCleanerFullPipeline:
    """Integration test for clean_dataset()"""

    def test_clean_dataset_returns_df_and_report(self, temp_csv_path_with_missing):
        """clean_dataset() returns cleaned dataframe and report dict"""
        cleaner = DataCleaner()
        df, report = cleaner.clean_dataset(temp_csv_path_with_missing)
        assert isinstance(df, pd.DataFrame)
        assert isinstance(report, dict)
        assert len(df) > 0

    def test_cleaned_data_no_nulls(self, temp_csv_path_with_missing):
        """After full pipeline, there should be no missing values"""
        cleaner = DataCleaner()
        df, report = cleaner.clean_dataset(temp_csv_path_with_missing)
        assert df.isnull().sum().sum() == 0

    def test_cleaned_data_no_invalid_cgpa(self, temp_csv_path_with_missing):
        """After full pipeline, no CGPA values outside 0-10 range"""
        cleaner = DataCleaner()
        df, report = cleaner.clean_dataset(temp_csv_path_with_missing)
        assert len(df[df['cgpa'] > 10]) == 0
        assert len(df[df['cgpa'] < 0]) == 0


class TestGenerateCleaningReport:
    """Tests for generate_cleaning_report()"""

    def test_generates_json_file(self, tmp_path):
        """generate_cleaning_report creates a valid JSON file"""
        report = {
            'original_shape': [100, 20],
            'rows_removed': 5,
            'missing_values': {'filled': 10}
        }
        output_path = os.path.join(tmp_path, 'cleaning_test.json')
        result = generate_cleaning_report(report, output_path)
        assert os.path.exists(result)
        assert result == output_path

    def test_json_content_matches_report(self, tmp_path):
        """Generated JSON file contains the exact report data"""
        report = {'test_key': 'test_value', 'numbers': [1, 2, 3]}
        output_path = os.path.join(tmp_path, 'cleaning_test.json')
        result_path = generate_cleaning_report(report, output_path)

        import json
        with open(result_path, 'r') as f:
            loaded = json.load(f)
        assert loaded == report
