"""Type definitions for TrustChainAi models and predictions."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Vulnerability:
    """Represents a detected vulnerability in a smart contract."""
    type: str  # "reentrancy", "overflow", "phishing_pattern", etc.
    severity: str  # "critical", "high", "medium", "low"
    line_number: Optional[int]  # Line number if available (None for bytecode)
    description: str  # Human-readable description


@dataclass
class Prediction:
    """Complete prediction result from model analysis."""
    contract_address: str
    vulnerabilities: List[Vulnerability]
    risk_score: float  # 0.0-1.0 overall risk
    contract_type: str  # "DEX", "Lending", "NFT", "Privacy", "Other"
    confidence: float  # 0.0-1.0 model confidence
    explanation_tokens: List[str]  # Tokens for SHAP explanation
    model_version: str  # Version identifier for the model used