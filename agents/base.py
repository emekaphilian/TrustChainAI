"""Base interfaces for audit agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from app.orchestrator.state import AuditState


class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    def run(self, state: AuditState) -> Dict[str, Any]:
        raise NotImplementedError

