"""
Placement Predictor - Model Training Module
Trains multiple ML models, compares accuracy, and saves the best model
"""

import pandas as pd
import numpy as np
import os
import sys
import json
import pickle
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add project root to path for reliable imports
_this_file = os.path.abspath(__file__)
_backend_dir = os.path.dirname(os.path.dirname(_this_file))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

# Scikit-Learn Models
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

# Model Evaluation
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)

# Model Persistence
import joblib

# Cross Validation
from sklearn.model_selection import cross_val_score, StratifiedKFold


class ModelTrainer:
    """Train and evaluate multiple ML models for placement prediction"""

    def __init__(self):
        self.models = {}
        self.trained_models = {}
        self.results = {}
        self.best_model = None
        self.best_model_name = None
        self.best_accuracy = 0
        self.training_report = {}

        # Define models to train
        self.model_definitions = {
            'Logistic Regression': LogisticRegression(
                max_iter=2000,
                random_state=42,
                C=1.0,
                solver='lbfgs',
                class_weight='balanced'
            ),
            'Random Forest': RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=10,
                min_samples_leaf=4,
                random_state=42,
                class_weight='balanced',
                n_jobs=-1
            ),
            'Decision Tree': DecisionTreeClassifier(
                max_depth=10,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=42,
                class_weight='balanced'
            ),
            'Support Vector Machine': SVC(
                kernel='rbf',
                C=1.0,
                gamma='scale',
                probability=True,
                random_state=42,
                class_weight='balanced'
            ),
            'Gradient Boosting': GradientBoostingClassifier(
                n_estimators=150,
                max_depth=5,
                learning_rate=0.1,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=42
            ),
            'K-Nearest Neighbors': KNeighborsClassifier(
                n_neighbors=7,
                weights='distance',
                metric='minkowski',
                n_jobs=-1
            )
        }

    def train_model(self, model_name, model, X_train, y_train):
        """Train a single model"""
        print(f"   Training {model_name}...", end=' ')
        try:
            model.fit(X_train, y_train)
            print("✅ Done")
            return model
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
            return None

    def evaluate_model(self, model_name, model, X_train, y_train, X_test, y_test):
        """Evaluate a trained model on multiple metrics"""
        # Predictions
        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

        # Probabilities for AUC
        try:
            y_train_prob = model.predict_proba(X_train)[:, 1]
            y_test_prob = model.predict_proba(X_test)[:, 1]
            train_auc = roc_auc_score(y_train, y_train_prob)
            test_auc = roc_auc_score(y_test, y_test_prob)
        except Exception:
            y_train_prob = None
            y_test_prob = None
            train_auc = 0
            test_auc = 0

        # Training metrics
        train_accuracy = accuracy_score(y_train, y_train_pred)
        train_precision = precision_score(y_train, y_train_pred, zero_division=0)
        train_recall = recall_score(y_train, y_train_pred, zero_division=0)
        train_f1 = f1_score(y_train, y_train_pred, zero_division=0)

        # Testing metrics
        test_accuracy = accuracy_score(y_test, y_test_pred)
        test_precision = precision_score(y_test, y_test_pred, zero_division=0)
        test_recall = recall_score(y_test, y_test_pred, zero_division=0)
        test_f1 = f1_score(y_test, y_test_pred, zero_division=0)

        # Confusion matrix
        cm = confusion_matrix(y_test, y_test_pred)

        # Cross-validation score
        try:
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy')
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
        except Exception:
            cv_scores = []
            cv_mean = 0
            cv_std = 0

        # Overfit detection
        overfit_gap = train_accuracy - test_accuracy
        is_overfitting = overfit_gap > 0.15

        results = {
            'model_name': model_name,
            'train_accuracy': round(train_accuracy * 100, 2),
            'test_accuracy': round(test_accuracy * 100, 2),
            'train_precision': round(train_precision * 100, 2),
            'test_precision': round(test_precision * 100, 2),
            'train_recall': round(train_recall * 100, 2),
            'test_recall': round(test_recall * 100, 2),
            'train_f1': round(train_f1 * 100, 2),
            'test_f1': round(test_f1 * 100, 2),
            'train_auc': round(train_auc * 100, 2),
            'test_auc': round(test_auc * 100, 2),
            'cv_mean': round(cv_mean * 100, 2),
            'cv_std': round(cv_std * 100, 2),
            'overfit_gap': round(overfit_gap * 100, 2),
            'is_overfitting': is_overfitting,
            'confusion_matrix': cm.tolist(),
            'y_test_prob': y_test_prob.tolist() if y_test_prob is not None else None
        }

        return results

    def train_all_models(self, X_train, y_train, X_test, y_test):
        """Train and evaluate all defined models"""
        print("\n" + "=" * 60)
        print("🤖 MODEL TRAINING PIPELINE")
        print("=" * 60)

        print(f"\n📊 Dataset Statistics:")
        print(f"   Training samples: {X_train.shape[0]}")
        print(f"   Testing samples: {X_test.shape[0]}")
        print(f"   Features: {X_train.shape[1]}")
        print(f"   Target: placed={y_train.sum()}, not_placed={(1-y_train).sum()}")

        print(f"\n{'='*60}")
        print(f"🚀 Training {len(self.model_definitions)} Models")
        print(f"{'='*60}\n")

        for model_name, model in self.model_definitions.items():
            print(f"\n{'─'*50}")
            print(f"📌 {model_name}")
            print(f"{'─'*50}")

            # Train
            trained = self.train_model(model_name, model, X_train, y_train)
            if trained is None:
                continue

            # Store trained model
            self.trained_models[model_name] = trained

            # Evaluate
            results = self.evaluate_model(
                model_name, trained, X_train, y_train, X_test, y_test
            )
            self.results[model_name] = results

            # Display results
            print(f"\n   📈 Performance:")
            print(f"      Train Accuracy: {results['train_accuracy']}%")
            print(f"      Test Accuracy:  {results['test_accuracy']}%")
            print(f"      Precision:      {results['test_precision']}%")
            print(f"      Recall:         {results['test_recall']}%")
            print(f"      F1-Score:       {results['test_f1']}%")
            print(f"      AUC-ROC:        {results['test_auc']}%")
            print(f"      CV Score:       {results['cv_mean']}% ± {results['cv_std']}%")

            if results['is_overfitting']:
                print(f"      ⚠️  Overfitting detected (gap: {results['overfit_gap']}%)")
            else:
                print(f"      ✅ Good generalization (gap: {results['overfit_gap']}%)")

            # Confusion matrix
            cm = results['confusion_matrix']
            print(f"\n   📋 Confusion Matrix:")
            print(f"      TN={cm[0][0]}  FP={cm[0][1]}")
            print(f"      FN={cm[1][0]}  TP={cm[1][1]}")

            # Track best model (based on test accuracy with overfit penalty)
            score = results['test_accuracy']
            if results['is_overfitting']:
                score *= 0.8  # Penalize overfitting models

            if score > self.best_accuracy:
                self.best_accuracy = score
                self.best_model = trained
                self.best_model_name = model_name
                print(f"      ⭐ Current best model!")

        return self.results

    def display_leaderboard(self):
        """Display model comparison leaderboard"""
        if not self.results:
            print("No models trained yet.")
            return

        print("\n" + "=" * 80)
        print("🏆 MODEL COMPARISON LEADERBOARD")
        print("=" * 80)
        print(f"{'Model':<25} {'Test Acc':<10} {'Precision':<10} {'Recall':<10} {'F1':<10} {'AUC':<10} {'CV Mean':<10}")
        print("-" * 80)

        # Sort by test accuracy
        sorted_models = sorted(
            self.results.items(),
            key=lambda x: x[1]['test_accuracy'],
            reverse=True
        )

        rank = 1
        for model_name, results in sorted_models:
            marker = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
            print(f"{marker} {model_name:<22} {results['test_accuracy']:<8.2f}% "
                  f"{results['test_precision']:<8.2f}% {results['test_recall']:<8.2f}% "
                  f"{results['test_f1']:<8.2f}% {results['test_auc']:<8.2f}% "
                  f"{results['cv_mean']:<8.2f}%")
            rank += 1

        print("=" * 80)
        print(f"\n✅ Best Model: {self.best_model_name}")
        print(f"   Test Accuracy: {self.results[self.best_model_name]['test_accuracy']}%")
        print(f"   Test F1-Score: {self.results[self.best_model_name]['test_f1']}%")

    def save_model(self, model_dir, scaler=None, label_encoders=None, feature_columns=None):
        """Save the best model and associated objects using Joblib"""
        if self.best_model is None:
            print("❌ No best model to save. Train models first.")
            return None

        os.makedirs(model_dir, exist_ok=True)

        # Save model
        model_path = os.path.join(model_dir, 'best_model.pkl')
        joblib.dump(self.best_model, model_path)
        print(f"✅ Model saved: {model_path}")

        # Save model metadata
        metadata = {
            'model_name': self.best_model_name,
            'accuracy': self.results[self.best_model_name]['test_accuracy'],
            'precision': self.results[self.best_model_name]['test_precision'],
            'recall': self.results[self.best_model_name]['test_recall'],
            'f1_score': self.results[self.best_model_name]['test_f1'],
            'auc_roc': self.results[self.best_model_name]['test_auc'],
            'trained_at': datetime.now().isoformat(),
            'features_count': len(feature_columns) if feature_columns else 0
        }

        metadata_path = os.path.join(model_dir, 'model_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Metadata saved: {metadata_path}")

        # Save all trained models for ensemble
        all_models_path = os.path.join(model_dir, 'all_models.pkl')
        joblib.dump(self.trained_models, all_models_path)
        print(f"✅ All models saved: {all_models_path}")

        # Save training report
        self.generate_training_report(model_dir)

        # Save scaler if provided
        if scaler is not None:
            scaler_path = os.path.join(model_dir, 'scaler.pkl')
            joblib.dump(scaler, scaler_path)
            print(f"✅ Scaler saved: {scaler_path}")

        # Save label encoders if provided
        if label_encoders is not None:
            encoder_path = os.path.join(model_dir, 'label_encoders.pkl')
            joblib.dump(label_encoders, encoder_path)
            print(f"✅ Label encoders saved: {encoder_path}")

        # Save feature columns
        if feature_columns is not None:
            features_path = os.path.join(model_dir, 'feature_columns.pkl')
            joblib.dump(feature_columns, features_path)
            print(f"✅ Feature columns saved: {features_path}")

        return model_path

    def generate_training_report(self, output_dir=None):
        """Generate comprehensive training report"""
        if output_dir is None:
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'reports'
            )

        os.makedirs(output_dir, exist_ok=True)

        report = {
            'training_time': datetime.now().isoformat(),
            'best_model': self.best_model_name,
            'best_model_accuracy': self.results[self.best_model_name]['test_accuracy'] if self.best_model_name else 0,
            'models_trained': len(self.trained_models),
            'model_comparison': {
                name: {
                    'test_accuracy': r['test_accuracy'],
                    'test_precision': r['test_precision'],
                    'test_recall': r['test_recall'],
                    'test_f1': r['test_f1'],
                    'test_auc': r['test_auc'],
                    'cv_mean': r['cv_mean'],
                    'is_overfitting': r['is_overfitting']
                }
                for name, r in self.results.items()
            },
            'leaderboard': [
                {
                    'rank': i + 1,
                    'model': name,
                    'accuracy': r['test_accuracy']
                }
                for i, (name, r) in enumerate(
                    sorted(self.results.items(),
                           key=lambda x: x[1]['test_accuracy'],
                           reverse=True)
                )
            ]
        }

        report_path = os.path.join(output_dir, f'training_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"✅ Training report saved: {report_path}")
        return report_path

    def get_model_feature_importance(self, model_name=None):
        """Get feature importance from a trained model"""
        if model_name is None:
            model_name = self.best_model_name

        if model_name not in self.trained_models:
            return None

        model = self.trained_models[model_name]

        # Check if model supports feature importance
        if hasattr(model, 'feature_importances_'):
            return model.feature_importances_
        elif hasattr(model, 'coef_'):
            return np.abs(model.coef_[0])
        else:
            return None

    def get_training_summary(self):
        """Get a concise summary of training results"""
        if not self.results:
            return "No models trained yet."

        summary = {
            'best_model': self.best_model_name,
            'best_accuracy': self.best_accuracy,
            'models_evaluated': len(self.results),
            'all_results': {
                name: {
                    'test_accuracy': r['test_accuracy'],
                    'test_f1': r['test_f1'],
                    'is_overfitting': r['is_overfitting']
                }
                for name, r in self.results.items()
            }
        }

        return summary


def train_and_save_model(dataset_path=None, model_dir=None, config=None):
    """
    Complete training pipeline: load data, engineer features, train models, save best model

    Args:
        dataset_path: Path to the CSV dataset
        model_dir: Directory to save the model
        config: Configuration object with model parameters

    Returns:
        Tuple of (ModelTrainer, FeatureEngineer)
    """
    from ml.data_cleaning import DataCleaner
    from ml.feature_engineering import FeatureEngineer

    if config is None:
        # Default config using project-relative paths
        BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/
        PROJECT_ROOT = os.path.dirname(BASE)  # Placement_Predictor/

        class DefaultConfig:
            DATASET_DIR = os.path.join(PROJECT_ROOT, 'dataset')
            STUDENT_CSV_PATH = os.path.join(DATASET_DIR, 'student_data.csv')
            MODEL_DIR = os.path.join(PROJECT_ROOT, 'model')
            MODEL_TEST_SIZE = 0.2
            MODEL_RANDOM_STATE = 42

        config = DefaultConfig()

    if dataset_path is None:
        dataset_path = config.STUDENT_CSV_PATH

    if model_dir is None:
        model_dir = config.MODEL_DIR

    print("\n" + "🚀" * 20)
    print("🚀  PLACEMENT PREDICTOR - ML PIPELINE  🚀")
    print("🚀" * 20 + "\n")

    # Step 1: Check if dataset exists
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found at: {dataset_path}")
        print("   Please generate the dataset first using generate_dataset.py")
        return None, None

    # Step 2: Clean data
    print("\n📦 Step 1: Loading and Cleaning Data")
    cleaner = DataCleaner()
    df, cleaning_report = cleaner.clean_dataset(dataset_path)

    # Step 3: Feature engineering
    print("\n📦 Step 2: Feature Engineering")
    engineer = FeatureEngineer()
    X_train, X_test, y_train, y_test, df_engineered = engineer.prepare_ml_dataset(
        df,
        target_col='placement_status',
        test_size=config.MODEL_TEST_SIZE,
        random_state=config.MODEL_RANDOM_STATE
    )

    # Step 4: Train models
    print("\n📦 Step 3: Training ML Models")
    trainer = ModelTrainer()
    trainer.train_all_models(X_train, y_train, X_test, y_test)

    # Step 5: Display leaderboard
    trainer.display_leaderboard()

    # Guard: check if any model trained successfully
    if trainer.best_model is None:
        print("\n❌ No models trained successfully. Cannot save model.")
        return None, None

    # Step 6: Save the best model
    print(f"\n📦 Step 4: Saving Best Model ({trainer.best_model_name})")
    trainer.save_model(
        model_dir=model_dir,
        scaler=cleaner.scaler if hasattr(cleaner, 'scaler') else None,
        label_encoders=cleaner.label_encoders if hasattr(cleaner, 'label_encoders') else None,
        feature_columns=X_train.columns.tolist()
    )

    # Step 7: Save feature engineering report
    engineer.generate_engineering_report()

    print("\n" + "=" * 60)
    print("🎉 ML PIPELINE COMPLETE!")
    print("=" * 60)
    print(f"\n🏆 Best Model: {trainer.best_model_name}")
    print(f"📊 Test Accuracy: {trainer.results[trainer.best_model_name]['test_accuracy']}%")
    print(f"📁 Model saved at: {model_dir}")

    return trainer, engineer


if __name__ == '__main__':
    train_and_save_model()
