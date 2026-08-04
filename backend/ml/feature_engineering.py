"""
Placement Predictor - Feature Engineering Module
Handles feature creation, selection, and transformation for ML models
"""

import pandas as pd
import numpy as np
from sklearn.feature_selection import SelectKBest, chi2, f_classif
from sklearn.model_selection import train_test_split
import json
import os
from datetime import datetime


class FeatureEngineer:
    """Feature engineering for placement prediction dataset"""

    def __init__(self):
        self.selected_features = []
        self.feature_importance = {}
        self.engineering_report = {}

    def create_interaction_features(self, df):
        """Create interaction features between important variables"""
        feature_log = {}

        # CGPA x Skill interactions
        if all(col in df.columns for col in ['cgpa', 'programming_skill']):
            df['cgpa_programming_interaction'] = df['cgpa'] * (df['programming_skill'] / 100)
            feature_log['cgpa_programming_interaction'] = 'CGPA × Programming Skill'

        if all(col in df.columns for col in ['cgpa', 'communication_skill']):
            df['cgpa_communication_interaction'] = df['cgpa'] * (df['communication_skill'] / 100)
            feature_log['cgpa_communication_interaction'] = 'CGPA × Communication Skill'

        # Academic performance score
        academic_cols = ['cgpa', 'tenth_percentage', 'twelfth_percentage']
        available_academic = [c for c in academic_cols if c in df.columns]
        if len(available_academic) >= 2:
            df['academic_performance_score'] = df[available_academic].mean(axis=1)
            feature_log['academic_performance_score'] = 'Average Academic Performance'

        # Technical competence score
        tech_cols = ['programming_skill', 'technical_score', 'aptitude_score']
        available_tech = [c for c in tech_cols if c in df.columns]
        if len(available_tech) >= 2:
            df['technical_competence_score'] = df[available_tech].mean(axis=1)
            feature_log['technical_competence_score'] = 'Average Technical Competence'

        # Experience score
        exp_cols = ['internships', 'projects', 'hackathons', 'certifications']
        available_exp = [c for c in exp_cols if c in df.columns]
        if available_exp:
            df['experience_score'] = df[available_exp].sum(axis=1)
            feature_log['experience_score'] = 'Total Experience Points'

        # Backlog penalty
        if 'backlogs' in df.columns:
            df['backlog_penalty'] = df['backlogs'] * (-2)
            feature_log['backlog_penalty'] = 'Backlog Penalty Score'

        # Attendance score (normalized)
        if 'attendance' in df.columns:
            df['attendance_score'] = df['attendance'] / 100.0
            feature_log['attendance_score'] = 'Normalized Attendance'

        # Resume quality score
        resume_cols = ['resume_score', 'projects', 'internships', 'certifications']
        available_resume = [c for c in resume_cols if c in df.columns]
        if len(available_resume) >= 2:
            df['resume_quality_score'] = (
                df['resume_score'] * 0.4 +
                (df['projects'] if 'projects' in df.columns else 0) * 0.2 +
                (df['internships'] if 'internships' in df.columns else 0) * 0.2 +
                (df['certifications'] if 'certifications' in df.columns else 0) * 0.2
            )
            feature_log['resume_quality_score'] = 'Weighted Resume Quality'

        self.engineering_report['interaction_features'] = feature_log
        return df

    def create_aggregate_features(self, df):
        """Create aggregate and composite features"""
        feature_log = {}

        # Overall placement readiness score (weighted combination)
        readiness_components = []

        if 'cgpa' in df.columns:
            df['cgpa_score'] = (df['cgpa'] / 10.0) * 100
            readiness_components.append(('cgpa_score', 0.20))
            feature_log['cgpa_score'] = 'CGPA Scaled to Percentage'

        if all(col in df.columns for col in ['aptitude_score', 'technical_score']):
            df['test_performance'] = (df['aptitude_score'] + df['technical_score']) / 2
            readiness_components.append(('test_performance', 0.15))
            feature_log['test_performance'] = 'Average Test Performance'

        if 'communication_skill' in df.columns:
            readiness_components.append(('communication_skill', 0.10))

        if 'programming_skill' in df.columns:
            readiness_components.append(('programming_skill', 0.15))

        if 'experience_score' in df.columns:
            max_exp = df['experience_score'].max()
            df['normalized_experience'] = (df['experience_score'] / max_exp * 100) if max_exp > 0 else 0
            readiness_components.append(('normalized_experience', 0.10))
            feature_log['normalized_experience'] = 'Normalized Experience Score'

        if 'resume_score' in df.columns:
            readiness_components.append(('resume_score', 0.10))

        if 'attendance' in df.columns:
            readiness_components.append(('attendance', 0.05))

        if 'backlogs' in df.columns:
            df['backlog_impact'] = (5 - df['backlogs'].clip(upper=5)) / 5.0 * 100
            readiness_components.append(('backlog_impact', 0.15))
            feature_log['backlog_impact'] = 'Backlog Impact Score'

        # Calculate composite readiness score
        if readiness_components:
            df['placement_readiness'] = sum(
                df[col] * weight for col, weight in readiness_components
                if col in df.columns
            )
            df['placement_readiness'] = df['placement_readiness'].clip(0, 100)
            feature_log['placement_readiness'] = 'Composite Placement Readiness Score'

        self.engineering_report['aggregate_features'] = feature_log
        return df

    def create_department_features(self, df):
        """Create department-specific features"""
        feature_log = {}

        if 'department' in df.columns:
            # Department placement rate (calculated from data)
            dept_stats = df.groupby('department').agg({
                'placement_status': ['mean', 'count']
            }) if 'placement_status' in df.columns else None

            if dept_stats is not None:
                dept_rates = dept_stats['placement_status']['mean'].to_dict()
                df['department_placement_rate'] = df['department'].map(dept_rates)
                feature_log['department_placement_rate'] = 'Historical Department Placement Rate'

                dept_counts = dept_stats['placement_status']['count'].to_dict()
                df['department_student_count'] = df['department'].map(dept_counts)
                feature_log['department_student_count'] = 'Students in Department'

        self.engineering_report['department_features'] = feature_log
        return df

    def select_best_features(self, X, y, k=15):
        """Select top k features using statistical tests"""
        selection_report = {}

        # Ensure all columns are numeric
        X_numeric = X.select_dtypes(include=[np.number])

        if X_numeric.shape[1] <= 2:
            self.selected_features = X_numeric.columns.tolist()
            selection_report['method'] = 'No selection needed'
            selection_report['selected_features'] = self.selected_features
            self.engineering_report['feature_selection'] = selection_report
            return X_numeric

        try:
            # Use ANOVA F-test for feature selection
            selector = SelectKBest(score_func=f_classif, k=min(k, X_numeric.shape[1]))
            selector.fit(X_numeric, y)

            # Get feature scores
            scores = pd.DataFrame({
                'feature': X_numeric.columns,
                'score': selector.scores_,
                'p_value': selector.pvalues_
            }).sort_values('score', ascending=False)

            # Select top features
            selected = scores.head(min(k, len(scores))).copy()
            self.selected_features = selected['feature'].tolist()
            self.feature_importance = dict(zip(selected['feature'], selected['score']))

            selection_report['method'] = 'ANOVA F-test (f_classif)'
            selection_report['total_features_considered'] = X_numeric.shape[1]
            selection_report['features_selected'] = len(self.selected_features)
            selection_report['top_features'] = scores.head(5).to_dict('records')
            selection_report['selected_features'] = self.selected_features

        except Exception as e:
            # Fallback: use all numeric features
            self.selected_features = X_numeric.columns.tolist()
            selection_report['method'] = f'Fallback (error: {str(e)})'
            selection_report['selected_features'] = self.selected_features

        self.engineering_report['feature_selection'] = selection_report
        return X_numeric[self.selected_features] if self.selected_features else X_numeric

    def prepare_ml_dataset(self, df, target_col='placement_status', test_size=0.2, random_state=42):
        """Complete feature engineering pipeline and prepare train/test split"""
        print("=" * 60)
        print("🔧 FEATURE ENGINEERING PIPELINE")
        print("=" * 60)

        # Step 1: Create interaction features
        print("\n🔄 Creating interaction features...")
        df = self.create_interaction_features(df)

        # Step 2: Create aggregate features
        print("\n🔄 Creating aggregate features...")
        df = self.create_aggregate_features(df)

        # Step 3: Create department features
        print("\n🔄 Creating department features...")
        df = self.create_department_features(df)

        # Step 4: Define feature columns (exclude target and non-feature columns)
        exclude_cols = [
            target_col, 'student_id', 'name', 'email', 'mentor_email',
            'company', 'package', 'department'
        ]
        
        # Also exclude original encoded columns that were used to create derived features
        feature_cols = [col for col in df.columns 
                       if col not in exclude_cols 
                       and col not in ['department_encoded']
                       and df[col].dtype in ['int64', 'float64']]

        X = df[feature_cols].copy()
        y = df[target_col] if target_col in df.columns else None

        # Step 5: Handle any remaining NaN or inf values
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(0)

        # Step 6: Select best features (if enough features)
        if X.shape[1] > 5 and y is not None:
            print(f"\n🔄 Selecting best features from {X.shape[1]} features...")
            X = self.select_best_features(X, y, k=min(20, X.shape[1]))
        else:
            self.selected_features = X.columns.tolist()

        # Step 7: Split into train/test sets
        if y is not None:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=y
            )
            print(f"\n✅ Dataset prepared successfully!")
            print(f"   Training samples: {X_train.shape[0]}")
            print(f"   Testing samples: {X_test.shape[0]}")
            print(f"   Features: {X_train.shape[1]}")
            print(f"   Target distribution (train): placed={y_train.sum()}, not_placed={(1-y_train).sum()}")
            
            # Store report
            self.engineering_report['dataset_stats'] = {
                'total_samples': len(df),
                'train_samples': X_train.shape[0],
                'test_samples': X_test.shape[0],
                'features': X_train.shape[1],
                'selected_features': self.selected_features
            }

            return X_train, X_test, y_train, y_test, df
        else:
            print(f"\n✅ Features prepared (no target column found)")
            return X, None, None, None, df

    def get_feature_importance_report(self, model=None, feature_names=None):
        """Get feature importance from trained model or from stored scores"""
        if model is not None and hasattr(model, 'feature_importances_') and feature_names:
            # For tree-based models
            importance = dict(zip(feature_names, model.feature_importances_))
        elif model is not None and hasattr(model, 'coef_') and feature_names:
            # For linear models
            importance = dict(zip(feature_names, np.abs(model.coef_[0])))
        else:
            importance = self.feature_importance

        # Sort by importance
        sorted_importance = dict(
            sorted(importance.items(), key=lambda x: x[1], reverse=True)
        )

        return sorted_importance

    def generate_engineering_report(self, output_path=None):
        """Generate and save feature engineering report"""
        if output_path is None:
            output_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'reports',
                f'feature_engineering_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(self.engineering_report, f, indent=2, default=str)

        return output_path
