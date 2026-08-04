"""
Placement Predictor - Prediction Engine Module
Loads the trained model and makes predictions with probability, confidence, and explanations
"""

import pandas as pd
import numpy as np
import os
import json
import joblib
import warnings
warnings.filterwarnings('ignore')

from datetime import datetime


class PredictionEngine:
    """Prediction engine for loading and using trained ML models"""

    def __init__(self, model_dir=None):
        """
        Initialize prediction engine

        Args:
            model_dir: Directory containing saved model files
        """
        self.model = None
        self.model_name = None
        self.model_metadata = None
        self.scaler = None
        self.label_encoders = None
        self.feature_columns = None
        self.is_loaded = False

        if model_dir is None:
            # From backend/ml/predict.py -> backend/ -> Placement_Predictor/ -> model/
            _base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_dir = os.path.join(os.path.dirname(_base), 'model')
        self.model_dir = model_dir

    def load_model(self, model_dir=None):
        """
        Load the saved model and associated objects

        Returns:
            bool: True if model loaded successfully
        """
        if model_dir is not None:
            self.model_dir = model_dir

        try:
            # Load best model
            model_path = os.path.join(self.model_dir, 'best_model.pkl')
            if not os.path.exists(model_path):
                print(f"❌ Model not found at: {model_path}")
                return False

            self.model = joblib.load(model_path)
            print(f"✅ Model loaded from: {model_path}")

            # Load model metadata
            metadata_path = os.path.join(self.model_dir, 'model_metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    self.model_metadata = json.load(f)
                self.model_name = self.model_metadata.get('model_name', 'Unknown')
                print(f"   Model: {self.model_name}")
                print(f"   Accuracy: {self.model_metadata.get('accuracy', 'N/A')}%")
            else:
                self.model_name = type(self.model).__name__

            # Load scaler
            scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
                print(f"✅ Scaler loaded")

            # Load label encoders
            encoder_path = os.path.join(self.model_dir, 'label_encoders.pkl')
            if os.path.exists(encoder_path):
                self.label_encoders = joblib.load(encoder_path)
                print(f"✅ Label encoders loaded")

            # Load feature columns
            features_path = os.path.join(self.model_dir, 'feature_columns.pkl')
            if os.path.exists(features_path):
                self.feature_columns = joblib.load(features_path)
                print(f"✅ Feature columns loaded ({len(self.feature_columns)} features)")

            self.is_loaded = True
            return True

        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
            return False

    def predict_single(self, student_data):
        """
        Predict placement for a single student

        Args:
            student_data: Dict or DataFrame row with student features

        Returns:
            Dict with prediction results
        """
        if not self.is_loaded:
            if not self.load_model():
                return self._error_result("Model not loaded")

        try:
            # Convert to DataFrame if dict
            if isinstance(student_data, dict):
                df = pd.DataFrame([student_data])
            else:
                df = student_data.copy()

            # Extract and prepare features
            X = self._prepare_features(df)

            if X is None or len(X) == 0:
                return self._error_result("Feature preparation failed")

            # Make prediction
            prediction = int(self.model.predict(X)[0])
            probability = float(self.model.predict_proba(X)[0][1]) * 100

            # Calculate confidence
            confidence = self._calculate_confidence(probability, X)

            # Get reasons influencing prediction
            reasons = self._get_prediction_reasons(student_data, prediction, probability)

            # Get suggestions for improvement
            suggestions = self._get_improvement_suggestions(
                student_data, prediction, probability, reasons
            )

            result = {
                'prediction': prediction,
                'prediction_label': 'Placed 🎉' if prediction == 1 else 'Not Placed ❌',
                'probability': round(probability, 2),
                'confidence': round(confidence, 2),
                'confidence_level': self._get_confidence_level(confidence),
                'model_used': self.model_name,
                'key_reasons': reasons,
                'suggestions': suggestions,
                'prediction_time': datetime.now().isoformat(),
                'status': 'success'
            }

            return result

        except Exception as e:
            return self._error_result(f"Prediction error: {str(e)}")

    def predict_batch(self, students_df):
        """
        Predict placement for multiple students

        Args:
            students_df: DataFrame with student features

        Returns:
            List of prediction results
        """
        if not self.is_loaded:
            if not self.load_model():
                return []

        try:
            X = self._prepare_features(students_df)
            if X is None:
                return []

            predictions = self.model.predict(X)
            probabilities = self.model.predict_proba(X)[:, 1] * 100

            results = []
            for i in range(len(students_df)):
                student = students_df.iloc[i].to_dict()
                pred = int(predictions[i])
                prob = float(probabilities[i])
                confidence = self._calculate_confidence(prob, X.iloc[i:i+1])

                results.append({
                    'student_id': student.get('student_id', f'STU{i:04d}'),
                    'name': student.get('name', 'Unknown'),
                    'prediction': pred,
                    'prediction_label': 'Placed 🎉' if pred == 1 else 'Not Placed ❌',
                    'probability': round(prob, 2),
                    'confidence': round(confidence, 2),
                    'department': student.get('department', ''),
                    'cgpa': student.get('cgpa', 0)
                })

            return results

        except Exception as e:
            print(f"❌ Batch prediction error: {str(e)}")
            return []

    def _prepare_features(self, df):
        """
        Prepare feature matrix for prediction

        Ensures the DataFrame has the same features the model was trained on
        """
        # If feature columns are stored, use them
        if self.feature_columns:
            # Create DataFrame with all required features
            X = pd.DataFrame(index=df.index)

            for col in self.feature_columns:
                if col in df.columns:
                    X[col] = df[col].values
                else:
                    # Check if it's a derived feature we can compute
                    X[col] = self._compute_derived_feature(col, df)

            # Fill any remaining NaN values
            X = X.fillna(0)

            # Ensure correct data types
            X = X.astype(float)

            # Handle infinities
            X = X.replace([np.inf, -np.inf], 0)

            return X

        # Fallback: use all numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        # Remove target and ID columns if present
        exclude = ['placement_status', 'student_id_encoded']
        feature_cols = [c for c in numeric_cols if c not in exclude]

        if not feature_cols:
            return None

        return df[feature_cols].fillna(0)

    def _compute_derived_feature(self, feature_name, df):
        """
        Compute a derived feature if possible

        This reconstructs features created during feature engineering
        """
        feature_map = {
            'cgpa_programming_interaction': lambda d: (
                d.get('cgpa', 0) * (d.get('programming_skill', 0) / 100)
            ),
            'cgpa_communication_interaction': lambda d: (
                d.get('cgpa', 0) * (d.get('communication_skill', 0) / 100)
            ),
            'academic_performance_score': lambda d: np.mean([
                d.get('cgpa', 0) * 10, d.get('tenth_percentage', 0),
                d.get('twelfth_percentage', 0)
            ]),
            'technical_competence_score': lambda d: np.mean([
                d.get('programming_skill', 0),
                d.get('technical_score', 0),
                d.get('aptitude_score', 0)
            ]),
            'experience_score': lambda d: sum([
                d.get('internships', 0), d.get('projects', 0),
                d.get('hackathons', 0), d.get('certifications', 0)
            ]),
            'backlog_penalty': lambda d: d.get('backlogs', 0) * (-2),
            'attendance_score': lambda d: d.get('attendance', 0) / 100.0,
            'cgpa_score': lambda d: (d.get('cgpa', 0) / 10.0) * 100,
            'test_performance': lambda d: np.mean([
                d.get('aptitude_score', 0), d.get('technical_score', 0)
            ]),
            'placement_readiness': lambda d: self._compute_readiness(d),
            'backlog_impact': lambda d: (5 - min(d.get('backlogs', 0), 5)) / 5.0 * 100,
        }

        if feature_name in feature_map:
            # Apply to each row
            results = []
            for _, row in df.iterrows():
                try:
                    val = feature_map[feature_name](row.to_dict())
                    results.append(float(val) if not np.isnan(val) else 0)
                except Exception:
                    results.append(0)
            return results

        return 0

    def _compute_readiness(self, d):
        """Compute composite placement readiness score"""
        score = 0
        if 'cgpa' in d:
            score += (d['cgpa'] / 10.0) * 20
        if 'aptitude_score' in d:
            score += d['aptitude_score'] * 0.10
        if 'technical_score' in d:
            score += d['technical_score'] * 0.10
        if 'communication_skill' in d:
            score += d['communication_skill'] * 0.10
        if 'programming_skill' in d:
            score += d['programming_skill'] * 0.15
        if 'internships' in d:
            score += min(d['internships'], 4) * 5
        if 'projects' in d:
            score += min(d['projects'], 4) * 3
        if 'certifications' in d:
            score += d['certifications'] * 3
        if 'resume_score' in d:
            score += d['resume_score'] * 0.10
        if 'backlogs' in d:
            score -= d['backlogs'] * 8
        if 'attendance' in d:
            score += ((d['attendance'] - 50) / 50.0) * 3
        return max(0, min(100, score))

    def _calculate_confidence(self, probability, X):
        """
        Calculate prediction confidence based on:
        - How far probability is from decision boundary (0.5)
        - Model certainty (probability calibration)
        """
        # Distance from boundary (0-50 range)
        boundary_distance = abs(probability - 50)

        # Map boundary distance (0..50) to confidence (50..100)
        # At boundary (dist=0): confidence=50 (uncertain)
        # At extremes (dist=50): confidence=100 (very certain)
        confidence = 50 + boundary_distance

        return confidence

    def _get_prediction_reasons(self, student_data, prediction, probability):
        """
        Generate human-readable reasons for the prediction

        Analyzes which features most influenced the prediction
        """
        reasons = []

        if isinstance(student_data, dict):
            data = student_data
        else:
            data = student_data.to_dict() if hasattr(student_data, 'to_dict') else {}

        # CGPA analysis
        cgpa = data.get('cgpa', 0)
        if cgpa >= 8.5:
            reasons.append("✅ Excellent CGPA (above 8.5) - Strong academic foundation")
        elif cgpa >= 7.0:
            reasons.append("✅ Good CGPA (above 7.0) - Solid academic performance")
        elif cgpa >= 6.0:
            reasons.append("⚠️ Average CGPA (6.0-7.0) - Room for academic improvement")
        else:
            reasons.append("❌ Low CGPA (below 6.0) - Major area for improvement")

        # Programming skill
        prog_skill = data.get('programming_skill', 0)
        if prog_skill >= 80:
            reasons.append("✅ Strong programming skills - Industry-ready")
        elif prog_skill >= 60:
            reasons.append("✅ Good programming foundation")
        elif prog_skill >= 40:
            reasons.append("⚠️ Average programming skills - Needs improvement")
        else:
            reasons.append("❌ Weak programming skills - Critical area to work on")

        # Communication skill
        comm_skill = data.get('communication_skill', 0)
        if comm_skill >= 70:
            reasons.append("✅ Good communication skills")
        else:
            reasons.append("⚠️ Communication skills need improvement")

        # Internships
        internships = data.get('internships', 0)
        if internships >= 2:
            reasons.append(f"✅ {internships} internships - Valuable industry exposure")
        elif internships == 1:
            reasons.append("✅ 1 internship completed")
        else:
            reasons.append("❌ No internships - Consider gaining practical experience")

        # Projects
        projects = data.get('projects', 0)
        if projects >= 3:
            reasons.append(f"✅ {projects} projects - Strong practical experience")
        elif projects >= 1:
            reasons.append(f"✅ {projects} project(s) completed")
        else:
            reasons.append("❌ No projects - Build a project portfolio")

        # Technical score
        tech_score = data.get('technical_score', 0)
        if tech_score >= 75:
            reasons.append("✅ Strong technical skills")
        elif tech_score >= 50:
            reasons.append("✅ Satisfactory technical ability")
        else:
            reasons.append("⚠️ Technical skills need strengthening")

        # Aptitude score
        aptitude = data.get('aptitude_score', 0)
        if aptitude >= 70:
            reasons.append("✅ Good aptitude - Strong problem-solving")
        else:
            reasons.append("⚠️ Practice aptitude questions regularly")

        # Backlogs
        backlogs = data.get('backlogs', 0)
        if backlogs > 0:
            reasons.append(f"❌ {backlogs} backlog(s) - Clear pending backlogs")
        else:
            reasons.append("✅ No backlogs - Clean academic record")

        # Certifications
        certs = data.get('certifications', 0)
        if certs >= 2:
            reasons.append(f"✅ {certs} certifications - Industry recognized skills")
        elif certs >= 1:
            reasons.append("✅ Has relevant certifications")
        else:
            reasons.append("💡 No certifications - Consider getting certified")

        # Resume score
        resume = data.get('resume_score', 0)
        if resume >= 70:
            reasons.append("✅ Strong resume - Well presented profile")
        elif resume >= 50:
            reasons.append("✅ Decent resume score")
        else:
            reasons.append("⚠️ Resume needs improvement - Highlight your achievements")

        # Attendance
        attendance = data.get('attendance', 0)
        if attendance < 75:
            reasons.append("⚠️ Low attendance - Maintain at least 75% attendance")

        # Limit to top reasons
        if len(reasons) > 8:
            # Prioritize negative reasons and high-impact positive ones
            negative = [r for r in reasons if r.startswith("❌") or r.startswith("⚠️")]
            positive = [r for r in reasons if r.startswith("✅")]
            neutral = [r for r in reasons if r.startswith("💡")]

            # Take all negative, top positive, some neutral
            reasons = negative + positive[:4] + neutral[:1]

        return reasons

    def _get_improvement_suggestions(self, student_data, prediction, probability, reasons):
        """
        Generate actionable improvement suggestions based on student's weak areas
        """
        suggestions = []

        if isinstance(student_data, dict):
            data = student_data
        else:
            data = student_data.to_dict() if hasattr(student_data, 'to_dict') else {}

        # CGPA improvement
        cgpa = data.get('cgpa', 0)
        if cgpa < 7.0:
            suggestions.append("📚 Focus on improving CGPA - Attend extra classes and seek help from professors")

        # Programming skill
        prog = data.get('programming_skill', 0)
        if prog < 60:
            suggestions.append("💻 Practice coding daily on platforms like LeetCode, HackerRank, and CodeChef")
        if prog < 40:
            suggestions.append("📖 Enroll in programming fundamentals course (Python/Java recommended)")

        # Communication
        comm = data.get('communication_skill', 0)
        if comm < 60:
            suggestions.append("🎯 Improve communication skills - Practice mock interviews and group discussions")

        # Internships
        if data.get('internships', 0) < 1:
            suggestions.append("🏢 Apply for internships on platforms like Internshala, LinkedIn, and company career pages")

        # Projects
        if data.get('projects', 0) < 2:
            suggestions.append("🛠️ Build 2-3 strong projects showcasing your skills (full-stack, ML, or domain-specific)")

        # Technical score
        if data.get('technical_score', 0) < 60:
            suggestions.append("📘 Strengthen technical fundamentals - Focus on DSA, DBMS, OS, and Computer Networks")

        # Aptitude
        if data.get('aptitude_score', 0) < 60:
            suggestions.append("🧮 Practice aptitude questions daily - Use Indiabix, PrepInsta, and placement preparation books")

        # Backlogs
        if data.get('backlogs', 0) > 0:
            suggestions.append("⚠️ Prioritize clearing all backlogs at the earliest opportunity")

        # Certifications
        if data.get('certifications', 0) < 2:
            suggestions.append("🎓 Earn relevant certifications (AWS, Google Cloud, Microsoft, etc.) from Coursera or Udemy")

        # Resume
        if data.get('resume_score', 0) < 50:
            suggestions.append("📄 Improve resume - Use ATS-friendly format, quantify achievements, and highlight relevant skills")

        # Attendance
        if data.get('attendance', 0) < 75:
            suggestions.append("📋 Maintain minimum 75% attendance - Some companies have attendance eligibility criteria")

        # Special suggestions based on prediction
        if prediction == 0:
            suggestions.append("🎯 Don't be discouraged! Start preparing early with a structured plan covering aptitude, technical, and soft skills")
            suggestions.append("🤝 Connect with placed seniors and participate in campus placement preparation groups")

        if probability < 40:
            suggestions.append("🚀 Create a 3-month intensive preparation plan focusing on your weakest areas first")

        if prediction == 1 and probability >= 80:
            suggestions.append("🌟 Great profile! Focus on dream companies and prepare for advanced technical interviews")

        # Limit suggestions
        if len(suggestions) > 6:
            suggestions = suggestions[:6]

        return suggestions

    def _get_confidence_level(self, confidence):
        """Get confidence level label"""
        if confidence >= 90:
            return "Very High"
        elif confidence >= 75:
            return "High"
        elif confidence >= 55:
            return "Moderate"
        elif confidence >= 35:
            return "Low"
        else:
            return "Very Low"

    def _error_result(self, message):
        """Return error result"""
        return {
            'prediction': -1,
            'prediction_label': 'Error',
            'probability': 0,
            'confidence': 0,
            'confidence_level': 'N/A',
            'model_used': None,
            'key_reasons': [],
            'suggestions': [message],
            'prediction_time': datetime.now().isoformat(),
            'status': 'error',
            'error_message': message
        }

    def get_model_info(self):
        """Get information about the loaded model"""
        if not self.is_loaded:
            return {'status': 'No model loaded'}

        info = {
            'model_name': self.model_name,
            'model_type': type(self.model).__name__,
            'is_loaded': True,
        }

        if self.model_metadata:
            info.update({
                'accuracy': self.model_metadata.get('accuracy'),
                'f1_score': self.model_metadata.get('f1_score'),
                'precision': self.model_metadata.get('precision'),
                'recall': self.model_metadata.get('recall'),
                'trained_at': self.model_metadata.get('trained_at'),
                'features_count': self.model_metadata.get('features_count')
            })

        if self.feature_columns:
            info['features'] = self.feature_columns

        return info


def predict_from_student_data(student_data, model_dir=None):
    """
    Convenience function to predict placement for a student

    Args:
        student_data: Dict with student features
        model_dir: Directory containing saved model

    Returns:
        Dict with prediction results
    """
    engine = PredictionEngine(model_dir)
    if not engine.load_model():
        return engine._error_result("Failed to load model")
    return engine.predict_single(student_data)


def batch_predict(students_data, model_dir=None):
    """
    Convenience function to predict placement for multiple students

    Args:
        students_data: List of dicts or DataFrame with student features
        model_dir: Directory containing saved model

    Returns:
        List of prediction results
    """
    engine = PredictionEngine(model_dir)
    if not engine.load_model():
        return []

    if isinstance(students_data, list):
        students_data = pd.DataFrame(students_data)

    return engine.predict_batch(students_data)


if __name__ == '__main__':
    # Test prediction engine
    print("=" * 60)
    print("🔮 PREDICTION ENGINE TEST")
    print("=" * 60)

    # Load model
    engine = PredictionEngine()
    if engine.load_model():
        print("\n✅ Model loaded successfully!")
        print(f"   Model: {engine.get_model_info().get('model_name', 'Unknown')}")

        # Sample student for testing
        test_student = {
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

        print(f"\n🔮 Testing prediction for: {test_student['name']}")
        result = engine.predict_single(test_student)

        print(f"\n{'='*60}")
        print(f"📊 PREDICTION RESULT")
        print(f"{'='*60}")
        print(f"   Result: {result['prediction_label']}")
        print(f"   Probability: {result['probability']}%")
        print(f"   Confidence: {result['confidence']}% ({result['confidence_level']})")
        print(f"   Model: {result['model_used']}")

        if result.get('key_reasons'):
            print(f"\n   📋 Key Reasons:")
            for reason in result['key_reasons']:
                print(f"      • {reason}")

        if result.get('suggestions'):
            print(f"\n   💡 Improvement Suggestions:")
            for suggestion in result['suggestions']:
                print(f"      • {suggestion}")

        print(f"\n{'='*60}")
    else:
        print("\n❌ Model not found. Train the model first using train_model.py")
