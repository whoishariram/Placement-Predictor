"""
Placement Predictor - Model Explainability Module
Feature importance, prediction confidence, top factors, and explainable AI

Provides:
- Feature importance analysis (built-in and permutation-based)
- Prediction confidence scoring
- Top factors influencing placement prediction
- Human-readable explanations
"""

import numpy as np
import pandas as pd
import json
import os
from datetime import datetime


class ModelExplainer:
    """
    Model explainability and feature importance analysis

    Generates human-readable explanations for ML predictions
    including feature importance, top factors, and confidence scores
    """

    def __init__(self, model=None, feature_names=None):
        """
        Initialize the explainer

        Args:
            model: Trained ML model with predict_proba
            feature_names: List of feature column names
        """
        self.model = model
        self.feature_names = feature_names or []
        self._importance_cache = None

    def get_feature_importance(self):
        """
        Get feature importance from the model

        Returns:
            Dict mapping feature names to importance scores, sorted descending
        """
        if self._importance_cache is not None:
            return self._importance_cache

        if self.model is None:
            return {}

        importance = None

        # Tree-based models (Random Forest, Gradient Boosting, Decision Tree)
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_

        # Linear models (Logistic Regression, SVM with linear kernel)
        elif hasattr(self.model, 'coef_'):
            coef = self.model.coef_
            if coef.ndim > 1:
                importance = np.abs(coef[0])
            else:
                importance = np.abs(coef)

        if importance is not None and self.feature_names:
            # Create dict and sort by importance
            importance_dict = dict(zip(
                self.feature_names[:len(importance)],
                importance
            ))
            sorted_dict = dict(
                sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
            )
            self._importance_cache = sorted_dict
            return sorted_dict

        return {}

    def get_top_features(self, n=5):
        """
        Get top N most important features

        Args:
            n: Number of top features to return

        Returns:
            List of (feature_name, importance_score) tuples
        """
        importance = self.get_feature_importance()
        if not importance:
            return []

        top_features = list(importance.items())[:n]
        return top_features

    def explain_prediction(self, student_data, prediction, probability):
        """
        Generate human-readable explanation for a prediction

        Args:
            student_data: Dict or DataFrame row with student features
            prediction: 0 (Not Placed) or 1 (Placed)
            probability: Prediction probability (0-100)

        Returns:
            Dict with explanation details
        """
        if isinstance(student_data, dict):
            data = student_data
        else:
            data = student_data.to_dict() if hasattr(student_data, 'to_dict') else {}

        # Get top contributing factors
        importance = self.get_feature_importance()
        if not importance:
            return self._rule_based_explanation(data, prediction, probability)

        # Calculate contribution of each feature
        contributions = self._calculate_feature_contributions(data, importance)

        # Determine which features pushed toward placed vs not-placed
        positive_factors = []
        negative_factors = []

        for feature, contribution in contributions:
            if contribution > 0:
                positive_factors.append({
                    'feature': feature,
                    'contribution': round(contribution, 2),
                    'current_value': data.get(feature, 'N/A')
                })
            else:
                negative_factors.append({
                    'feature': feature,
                    'contribution': round(contribution, 2),
                    'current_value': data.get(feature, 'N/A')
                })

        # Sort by absolute contribution
        positive_factors.sort(key=lambda x: abs(x['contribution']), reverse=True)
        negative_factors.sort(key=lambda x: abs(x['contribution']), reverse=True)

        explanation = {
            'prediction': 'Placed 🎉' if prediction == 1 else 'Not Placed ❌',
            'probability': round(probability, 2),
            'confidence': self._calculate_confidence(probability),
            'confidence_level': self._get_confidence_level(probability),
            'top_positive_factors': positive_factors[:5],
            'top_negative_factors': negative_factors[:5],
            'feature_importance': {
                feat: round(imp, 4)
                for feat, imp in list(importance.items())[:10]
            },
            'summary': self._generate_summary(
                data, prediction, probability,
                positive_factors[:3], negative_factors[:3]
            )
        }

        return explanation

    def _calculate_feature_contributions(self, data, importance):
        """
        Calculate how each feature value contributed to the prediction

        Uses feature importance scores and compares actual values to thresholds
        """
        contributions = []
        thresholds = self._get_feature_thresholds()

        for feature, imp in importance.items():
            if feature in data:
                value = data[feature]
                threshold = thresholds.get(feature, 0.5)

                try:
                    value = float(value) if value is not None else 0
                except (ValueError, TypeError):
                    continue

                # Normalize value to comparable scale
                normalized = self._normalize_feature(feature, value)

                # Contribution = importance * (normalized_value - threshold)
                contribution = imp * (normalized - threshold)
                contributions.append((feature, contribution))

        # Normalize contributions
        if contributions:
            max_abs = max(abs(c) for _, c in contributions) or 1
            contributions = [(f, c / max_abs) for f, c in contributions]

        return sorted(contributions, key=lambda x: abs(x[1]), reverse=True)

    def _get_feature_thresholds(self):
        """Get reasonable thresholds for each feature"""
        return {
            'cgpa': 0.6, 'tenth_percentage': 0.6, 'twelfth_percentage': 0.6,
            'communication_skill': 0.5, 'programming_skill': 0.5,
            'internships': 0.3, 'projects': 0.3, 'hackathons': 0.2,
            'certifications': 0.2, 'backlogs': 0.8, 'attendance': 0.6,
            'aptitude_score': 0.5, 'technical_score': 0.5, 'resume_score': 0.5
        }

    def _normalize_feature(self, feature, value):
        """Normalize a feature value to 0-1 range"""
        ranges = {
            'cgpa': (0, 10), 'tenth_percentage': (0, 100),
            'twelfth_percentage': (0, 100), 'communication_skill': (0, 100),
            'programming_skill': (0, 100), 'internships': (0, 10),
            'projects': (0, 10), 'hackathons': (0, 10),
            'certifications': (0, 10), 'backlogs': (0, 10),
            'attendance': (0, 100), 'aptitude_score': (0, 100),
            'technical_score': (0, 100), 'resume_score': (0, 100)
        }

        if feature in ranges:
            min_val, max_val = ranges[feature]
            if max_val > min_val:
                return max(0, min(1, (value - min_val) / (max_val - min_val)))
        return 0.5

    def _calculate_confidence(self, probability):
        """
        Calculate prediction confidence based on distance from decision boundary

        Args:
            probability: Prediction probability (0-100)

        Returns:
            Confidence score (0-100)
        """
        # Distance from 50% boundary (0-50 range mapped to 50-100)
        boundary_distance = abs(probability - 50)
        confidence = 50 + boundary_distance
        return min(100, max(0, confidence))

    def _get_confidence_level(self, probability):
        """Get confidence level description"""
        boundary_distance = abs(probability - 50)
        if boundary_distance > 40:
            return "Very High"
        elif boundary_distance > 25:
            return "High"
        elif boundary_distance > 15:
            return "Moderate"
        elif boundary_distance > 5:
            return "Low"
        else:
            return "Very Low (Borderline)"

    def _rule_based_explanation(self, data, prediction, probability):
        """Fallback rule-based explanation when model isn't available"""
        reasons = []

        cgpa = float(data.get('cgpa', 0) or 0)
        prog = float(data.get('programming_skill', 0) or 0)
        backlogs = int(data.get('backlogs', 0) or 0)

        if cgpa >= 8.0:
            reasons.append({"factor": "CGPA", "impact": "positive", "detail": f"CGPA of {cgpa} is excellent"})
        elif cgpa >= 6.0:
            reasons.append({"factor": "CGPA", "impact": "neutral", "detail": f"CGPA of {cgpa} is average"})
        else:
            reasons.append({"factor": "CGPA", "impact": "negative", "detail": f"CGPA of {cgpa} needs improvement"})

        if prog >= 70:
            reasons.append({"factor": "Programming", "impact": "positive", "detail": "Strong programming skills"})
        elif prog < 40:
            reasons.append({"factor": "Programming", "impact": "negative", "detail": "Programming skills need improvement"})

        if backlogs > 0:
            reasons.append({"factor": "Backlogs", "impact": "negative", "detail": f"{backlogs} backlog(s) to clear"})

        return {
            'prediction': 'Placed 🎉' if prediction == 1 else 'Not Placed ❌',
            'probability': round(probability, 2),
            'confidence': self._calculate_confidence(probability),
            'confidence_level': self._get_confidence_level(probability),
            'rule_based_reasons': reasons,
            'summary': f"Rule-based analysis: {len(reasons)} factors evaluated."
        }

    def _generate_summary(self, data, prediction, probability,
                          positive_factors, negative_factors):
        """Generate a concise natural-language summary"""
        parts = []

        if prediction == 1:
            parts.append(f"The student is predicted to be PLACED with {probability:.0f}% probability.")
        else:
            parts.append(f"The student is predicted to NOT BE PLACED with {100-probability:.0f}% uncertainty.")

        if positive_factors:
            top_pos = positive_factors[0]['feature'].replace('_', ' ').title()
            parts.append(f"Strong area: {top_pos}.")

        if negative_factors:
            top_neg = negative_factors[0]['feature'].replace('_', ' ').title()
            parts.append(f"Area for improvement: {top_neg}.")

        return ' '.join(parts)

    def generate_explainability_report(self, output_path=None):
        """Generate a full explainability report as JSON"""
        importance = self.get_feature_importance()
        top_features = self.get_top_features(10)

        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'model_type': type(self.model).__name__ if self.model else 'Not loaded',
            'total_features': len(self.feature_names),
            'feature_importance': {
                feat: round(imp, 4)
                for feat, imp in importance.items()
            },
            'top_features': [
                {'feature': feat, 'importance': round(imp, 4)}
                for feat, imp in top_features
            ],
            'interpretation_guide': {
                'high_importance': 'Features with higher scores have more influence on predictions',
                'positive_contribution': 'Higher feature values increase placement probability',
                'negative_contribution': 'Lower feature values increase placement probability'
            }
        }

        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)

        return report
