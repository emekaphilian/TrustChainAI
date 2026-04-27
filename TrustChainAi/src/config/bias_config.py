"""Bias detection configuration and fairness monitoring."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class BiasDetectionConfig:
    """Configuration for per-scan fairness monitoring."""
    
    # Enable bias detection on every scan
    enabled: bool = True
    
    # Minimum samples before reporting fairness metrics
    min_samples_per_type: int = 50
    
    # False positive rate difference threshold (alert if exceeded)
    fpr_alert_threshold: float = 0.10  # 10% difference
    
    # Contract types to track separately
    contract_types: List[str] = None
    
    # Metrics to compute
    metrics: List[str] = None
    
    def __post_init__(self):
        """Set defaults for list fields."""
        if self.contract_types is None:
            self.contract_types = [
                "DEX",
                "Lending",
                "NFT",
                "Privacy",
                "Other"
            ]
        
        if self.metrics is None:
            self.metrics = [
                "false_positive_rate",
                "false_negative_rate",
                "precision_by_type",
                "recall_by_type",
                "prediction_count_by_type"
            ]


# Global bias detection configuration
# This runs on EVERY scan, making fairness monitoring built-in
BIAS_DETECTION = BiasDetectionConfig(
    enabled=True,
    min_samples_per_type=50,
    fpr_alert_threshold=0.10,
)

# Fairness metrics baseline (computed post-training)
# These are used to detect model drift in production
FAIRNESS_BASELINE = {
    "false_positive_rate_by_type": {
        "DEX": 0.05,  # Example baseline (compute actual after training)
        "Lending": 0.07,
        "NFT": 0.08,
        "Privacy": 0.10,
        "Other": 0.06,
    },
    "sample_counts": {
        "DEX": 100,
        "Lending": 150,
        "NFT": 80,
        "Privacy": 60,
        "Other": 110,
    }
}

# SHAP configuration for per-prediction explanations
SHAP_CONFIG = {
    "enabled": True,
    "background_samples": 100,  # Number of samples for SHAP background
    "max_display_features": 10,  # Top 10 features in explanation
    "cache_explanations": True,  # Cache SHAP values for faster dashboard loads
}

# Logging configuration for bias events
BIAS_LOGGING = {
    "log_predictions": True,  # Log all predictions for fairness analysis
    "log_file": "logs/bias_decisions.json",
    "alert_on_drift": True,  # Alert if model fairness drifts from baseline
    "drift_threshold": 0.15,  # Alert if FPR change > 15% from baseline
}
