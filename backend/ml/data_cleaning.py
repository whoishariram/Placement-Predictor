"""
Placement Predictor - Data Cleaning & Preprocessing Module
Handles missing values, duplicates, categorical encoding, and normalization
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
import os
import json
from datetime import datetime


class DataCleaner:
    """Data cleaning and preprocessing for placement dataset"""
    
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.cleaning_report = {}
        
    def load_dataset(self, filepath):
        """Load CSV dataset"""
        self.df = pd.read_csv(filepath)
        self.original_shape = self.df.shape
        return self.df
    
    def handle_missing_values(self):
        """Handle missing values in the dataset"""
        missing_before = self.df.isnull().sum().sum()
        report = {'missing_values_before': int(missing_before)}
        
        # Fill numeric columns with median
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            self.df[col].fillna(self.df[col].median(), inplace=True)
        
        # Fill categorical columns with mode
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            self.df[col].fillna(self.df[col].mode()[0] if not self.df[col].mode().empty else 'Unknown', inplace=True)
        
        missing_after = self.df.isnull().sum().sum()
        report['missing_values_after'] = int(missing_after)
        report['missing_values_filled'] = int(missing_before - missing_after)
        
        self.cleaning_report['missing_values'] = report
        return self.df
    
    def remove_duplicates(self):
        """Remove duplicate records"""
        duplicates_before = self.df.duplicated().sum()
        self.df.drop_duplicates(inplace=True)
        self.cleaning_report['duplicates'] = {
            'duplicates_found': int(duplicates_before),
            'duplicates_removed': int(duplicates_before)
        }
        return self.df
    
    def remove_invalid_entries(self):
        """Remove invalid entries (out of range values)"""
        invalid_counts = {}
        
        # CGPA validation (0-10)
        if 'cgpa' in self.df.columns:
            invalid = len(self.df[(self.df['cgpa'] < 0) | (self.df['cgpa'] > 10)])
            invalid_counts['cgpa'] = invalid
        
        # Percentage validation (0-100)
        for col in ['tenth_percentage', 'twelfth_percentage', 'attendance']:
            if col in self.df.columns:
                invalid = len(self.df[(self.df[col] < 0) | (self.df[col] > 100)])
                invalid_counts[col] = invalid
        
        # Score validation (0-100)
        for col in ['communication_skill', 'programming_skill', 'aptitude_score', 
                    'technical_score', 'resume_score']:
            if col in self.df.columns:
                invalid = len(self.df[(self.df[col] < 0) | (self.df[col] > 100)])
                invalid_counts[col] = invalid
        
        # Remove invalid entries
        for col, count in invalid_counts.items():
            if count > 0:
                self.df = self.df[(self.df[col] >= 0) & (self.df[col] <= (
                    10 if col == 'cgpa' else 100
                ))]
        
        self.cleaning_report['invalid_entries'] = invalid_counts
        return self.df
    
    def convert_categorical(self):
        """Convert categorical columns to numerical using Label Encoding"""
        categorical_cols = ['department', 'name', 'student_id']
        encoding_report = {}
        
        for col in categorical_cols:
            if col in self.df.columns:
                if col != 'student_id' and col != 'name':  # Keep student_id and name for reference
                    le = LabelEncoder()
                    self.df[f'{col}_encoded'] = le.fit_transform(self.df[col])
                    self.label_encoders[col] = le
                    encoding_report[col] = {
                        'unique_values': len(le.classes_),
                        'mapping': dict(zip(le.classes_, le.transform(le.classes_)))
                    }
        
        self.cleaning_report['categorical_encoding'] = encoding_report
        return self.df
    
    def normalize_features(self, feature_cols=None):
        """Normalize numerical features using StandardScaler"""
        if feature_cols is None:
            feature_cols = [
                'cgpa', 'tenth_percentage', 'twelfth_percentage',
                'communication_skill', 'programming_skill', 'internships',
                'projects', 'hackathons', 'certifications', 'backlogs',
                'attendance', 'aptitude_score', 'technical_score', 'resume_score'
            ]
        
        # Filter only available columns
        available_cols = [col for col in feature_cols if col in self.df.columns]
        self.feature_columns = available_cols
        
        if available_cols:
            self.df[available_cols] = self.scaler.fit_transform(self.df[available_cols])
            self.cleaning_report['normalization'] = {
                'features_normalized': available_cols,
                'scaler_mean': self.scaler.mean_.tolist() if hasattr(self.scaler, 'mean_') else [],
                'scaler_scale': self.scaler.scale_.tolist() if hasattr(self.scaler, 'scale_') else []
            }
        
        return self.df
    
    def prepare_features_target(self, target_col='placement_status'):
        """Prepare feature matrix X and target vector y"""
        # Define feature columns for ML
        feature_cols = [
            'department_encoded' if 'department_encoded' in self.df.columns else None,
            'cgpa', 'tenth_percentage', 'twelfth_percentage',
            'communication_skill', 'programming_skill',
            'internships', 'projects', 'hackathons', 'certifications',
            'backlogs', 'attendance', 'aptitude_score', 'technical_score',
            'resume_score'
        ]
        
        feature_cols = [col for col in feature_cols if col is not None and col in self.df.columns]
        self.feature_columns = feature_cols
        
        X = self.df[feature_cols]
        y = self.df[target_col] if target_col in self.df.columns else None
        
        return X, y
    
    def get_cleaning_summary(self):
        """Get a summary report of the cleaning process"""
        self.cleaning_report['original_shape'] = list(self.original_shape)
        self.cleaning_report['final_shape'] = list(self.df.shape)
        self.cleaning_report['rows_removed'] = int(self.original_shape[0] - self.df.shape[0])
        
        # Add basic statistics
        if 'cgpa' in self.df.columns:
            self.cleaning_report['statistics'] = {
                'cgpa_mean': float(self.df['cgpa'].mean()),
                'cgpa_std': float(self.df['cgpa'].std()),
                'placement_rate': float(self.df['placement_status'].mean() * 100) if 'placement_status' in self.df.columns else 0
            }
        
        return self.cleaning_report
    
    def clean_dataset(self, filepath):
        """Run the complete cleaning pipeline"""
        print("=" * 60)
        print("🧹 DATA CLEANING PIPELINE")
        print("=" * 60)
        
        # Load data
        print(f"\n📂 Loading dataset: {filepath}")
        df = self.load_dataset(filepath)
        print(f"   Original shape: {df.shape}")
        
        # Handle missing values
        print("\n🔄 Handling missing values...")
        self.handle_missing_values()
        
        # Remove duplicates
        print("\n🔄 Removing duplicates...")
        self.remove_duplicates()
        
        # Remove invalid entries
        print("\n🔄 Removing invalid entries...")
        self.remove_invalid_entries()
        
        # Convert categorical data
        print("\n🔄 Converting categorical data...")
        self.convert_categorical()
        
        # Normalize features
        print("\n🔄 Normalizing numerical features...")
        self.normalize_features()
        
        # Get summary
        summary = self.get_cleaning_summary()
        
        print(f"\n✅ Data cleaning complete!")
        print(f"   Final shape: {self.df.shape}")
        print(f"   Rows removed: {summary['rows_removed']}")
        
        if 'missing_values' in summary:
            print(f"   Missing values filled: {summary['missing_values'].get('missing_values_filled', 0)}")
        
        if 'duplicates' in summary:
            print(f"   Duplicates removed: {summary['duplicates']['duplicates_removed']}")
        
        return self.df, summary


def generate_cleaning_report(report, output_path=None):
    """Generate a formatted cleaning report"""
    if output_path is None:
        output_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'reports',
            f'cleaning_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    return output_path
