"""Structured logging with audit trail."""

import logging
import json
from datetime import datetime
from typing import Any, Dict


class AuditLogger:
    """Logs all auditing decisions with full context."""
    
    def __init__(self, log_file: str = "logs/audit.log"):
        """Initialize audit logger.
        
        Args:
            log_file: Path to audit log file.
        """
        self.logger = logging.getLogger("audit")
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_scan(self, contract_address: str, vulns_found: int, 
                 risk_score: float, contract_type: str, model_version: str):
        """Log contract scan completion.
        
        Args:
            contract_address: Address scanned.
            vulns_found: Count of vulnerabilities detected.
            risk_score: Risk score (0.0-1.0).
            contract_type: Inferred type (DEX, Lending, etc.).
            model_version: Model version used.
        """
        event = {
            "event": "contract_scan",
            "contract": contract_address,
            "vulnerabilities": vulns_found,
            "risk_score": risk_score,
            "contract_type": contract_type,
            "model_version": model_version,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info(json.dumps(event))
    
    def log_bias_alert(self, detector_type: str, affected_type: str, 
                       fpr_diff: float, threshold: float):
        """Log fairness/bias alert.
        
        Args:
            detector_type: Name of detector (e.g., "reentrancy").
            affected_type: Contract type with bias (DEX, Lending, etc.).
            fpr_diff: False positive rate difference.
            threshold: Configured threshold.
        """
        event = {
            "event": "bias_alert",
            "detector": detector_type,
            "affected_type": affected_type,
            "fpr_difference": fpr_diff,
            "threshold": threshold,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.warning(json.dumps(event))
    
    def log_error(self, error_type: str, context: Dict[str, Any]):
        """Log error with context (never raw contract code).
        
        Args:
            error_type: Type of error.
            context: Error context (no sensitive data).
        """
        event = {
            "event": "error",
            "type": error_type,
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.error(json.dumps(event))


# Global instance
audit_logger = AuditLogger()
