"""Bias detector for monitoring fairness in vulnerability predictions."""

import logging
from typing import Dict, List
from collections import defaultdict

from src.models.types import Prediction
from src.utils.logging import audit_logger
from src.config.bias_config import BIAS_DETECTION

logger = logging.getLogger(__name__)


class BiasDetector:
    """Monitors fairness in vulnerability detection across contract types."""

    def __init__(self):
        """Initialize bias detector with configuration."""
        self.config = BIAS_DETECTION
        self.prediction_counts: Dict[str, int] = defaultdict(int)
        self.false_positive_counts: Dict[str, int] = defaultdict(int)

        # In production, load baseline from data/metrics/baseline_fairness.json
        self.baseline_fpr = {
            "DEX": 0.05,
            "Lending": 0.07,
            "NFT": 0.08,
            "Privacy": 0.10,
            "Other": 0.06,
        }

        logger.info("BiasDetector initialized (per-scan monitoring enabled)")

    def analyze_prediction(self, prediction: Prediction) -> None:
        """Analyze a single prediction for bias patterns.

        Args:
            prediction: Prediction result to analyze
        """
        if not self.config.enabled:
            return

        contract_type = prediction.contract_type
        self.prediction_counts[contract_type] += 1

        # Check for false positive (high risk score but no critical vulns)
        is_false_positive = (
            prediction.risk_score > 0.5 and
            not any(v.severity == "critical" for v in prediction.vulnerabilities)
        )

        if is_false_positive:
            self.false_positive_counts[contract_type] += 1

        # Check if we have enough samples to compute fairness metrics
        if self.prediction_counts[contract_type] >= self.config.min_samples_per_type:
            self._check_fairness_alerts(contract_type)

    def _check_fairness_alerts(self, contract_type: str) -> None:
        """Check for fairness violations and log alerts.

        Args:
            contract_type: Contract type to check
        """
        total_predictions = self.prediction_counts[contract_type]
        false_positives = self.false_positive_counts[contract_type]

        if total_predictions == 0:
            return

        current_fpr = false_positives / total_predictions

        # Check against baseline
        baseline_fpr = self.baseline_fpr.get(contract_type, 0.05)
        fpr_diff = abs(current_fpr - baseline_fpr)

        if fpr_diff > self.config.fpr_alert_threshold:
            # Log bias alert
            audit_logger.log_bias_alert(
                detector_type="vulnerability_detector",
                affected_type=contract_type,
                fpr_diff=fpr_diff,
                threshold=self.config.fpr_alert_threshold
            )

            logger.warning(
                f"Bias alert: {contract_type} FPR ({current_fpr:.3f}) differs from "
                f"baseline ({baseline_fpr:.3f}) by {fpr_diff:.3f} > {self.config.fpr_alert_threshold}"
            )

    def get_fairness_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get current fairness metrics for all contract types.

        Returns:
            Dict mapping contract types to fairness metrics
        """
        metrics = {}

        for contract_type in self.config.contract_types:
            total = self.prediction_counts[contract_type]
            fp = self.false_positive_counts[contract_type]

            if total >= self.config.min_samples_per_type:
                metrics[contract_type] = {
                    "false_positive_rate": fp / total,
                    "total_predictions": total,
                    "false_positives": fp,
                    "precision": (total - fp) / total if total > 0 else 0.0
                }
            else:
                metrics[contract_type] = {
                    "insufficient_samples": True,
                    "total_predictions": total
                }

        return metrics

    def reset_metrics(self) -> None:
        """Reset all fairness metrics (for testing/debugging)."""
        self.prediction_counts.clear()
        self.false_positive_counts.clear()
        logger.info("Bias metrics reset")