"""Base model class for all ML models in TrustChainAi."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class ExplanationResult:
    """Result from model explanation (SHAP/LIME)."""
    feature_importance: List[tuple]  # (token, importance_score)
    explanation_text: str
    visualization_data: Optional[Any] = None


@dataclass
class Prediction:
    """Standard prediction output from any model."""
    contract_address: str
    risk_score: float
    confidence: float
    explanation_tokens: List[str]
    model_version: str


class BaseModel(ABC):
    """Abstract base class for all TrustChainAi models."""
    
    def __init__(self, model_config: dict):
        """Initialize model with config.
        
        Args:
            model_config: Dict with 'model_path', 'device', etc.
        """
        self.config = model_config
        self.model = None
        self._load_model()
    
    @abstractmethod
    def _load_model(self) -> None:
        """Load model from disk. Implement in subclass."""
        pass
    
    @abstractmethod
    def predict(self, input_data: Any) -> Prediction:
        """Generate prediction.
        
        Args:
            input_data: Contract bytecode, code tokens, or embedding.
            
        Returns:
            Prediction with risk_score and confidence.
        """
        pass
    
    @abstractmethod
    def explain(self, prediction: Prediction) -> ExplanationResult:
        """Generate SHAP/LIME explanation for prediction.
        
        Args:
            prediction: Output from predict().
            
        Returns:
            ExplanationResult with feature importance.
        """
        pass
    
    def batch_predict(self, inputs: List[Any]) -> List[Prediction]:
        """Batch prediction (default: loop, override for efficiency).
        
        Args:
            inputs: List of contract data.
            
        Returns:
            List of Predictions.
        """
        return [self.predict(inp) for inp in inputs]
