import logging
from pathlib import Path
from typing import Any, Dict, List

from app.agents.base import BaseAgent
from app.models.llm_service import LLMService
from app.models.verbalized_sampler import VerbalizedSampler
from app.orchestrator.state import AuditState
from app.rag.vector_store import PersistentVectorStore
from app.utils.trace_logger import log_agent_trace
import time

logger = logging.getLogger(__name__)


class LearningAgent(BaseAgent):
    """
    Self-improving agent that captures failures, updates RAG memory,
    and tracks reasoning diversity metrics.
    """

    name = "learning"

    def __init__(
        self,
        llm_service: LLMService | None = None,
        vector_store: PersistentVectorStore | None = None,
        num_samples: int = 3,
    ) -> None:
        self.llm_service = llm_service or LLMService()
        if vector_store is None:
            root = Path(__file__).resolve().parents[3]
            db_path = root / "data" / "vector_db" / "knowledge_store.json"
            self.vector_store = PersistentVectorStore(db_path)
        else:
            self.vector_store = vector_store
        self.num_samples = num_samples

    def run(self, state: AuditState) -> Dict[str, Any]:
        start_time = time.time()
        learning_events: List[str] = []
        low_confidence_agents: List[str] = []
        consensus_scores: Dict[str, int] = {}

        for agent_name in ["analysis", "review", "ethics"]:
            agent_output = state.get(agent_name, {})
            consensus_output = state.get(f"{agent_name}_consensus", {})
            confidence = float(agent_output.get("confidence", 1.0))
            consensus_count = len(consensus_output.get("vulnerabilities", []))
            consensus_scores[agent_name] = consensus_count

            if confidence < 0.7:
                low_confidence_agents.append(agent_name)
                learning_events.append(f"low_confidence_in_{agent_name}")

        if state.get("review", {}).get("discrepancies"):
            learning_events.append("agent_disagreement")

        feedback_cases: List[Dict[str, Any]] = []
        for agent_name in low_confidence_agents:
            agent_output = state.get(agent_name, {})
            case = {
                "agent": agent_name,
                "reasoning": agent_output.get("reasoning", ""),
                "vulnerabilities": agent_output.get("vulnerabilities", []),
                "confidence": agent_output.get("confidence", 0.0),
                "discrepancies": state.get("review", {}).get("discrepancies", []),
            }
            feedback_cases.append(case)

        num_samples = max(1, int(state.get("num_samples", self.num_samples)))
        sampler = VerbalizedSampler(self.llm_service, num_samples=num_samples)
        for case in feedback_cases:
            self.vector_store.add_learning_case(case)
            prompt = (
                "You are a LearningAgent improving the AI smart contract auditor. "
                "Review this low-confidence case and suggest improvements for model or prompt. "
                f"Reasoning: {case['reasoning']} "
                f"Vulnerabilities: {case['vulnerabilities']} "
                f"Discrepancies: {case['discrepancies']} "
                "Return keys: suggested_fix, improved_prompt, confidence_estimate."
            )
            responses = sampler.generate(prompt)
            best = sampler.select_best(
                responses,
                scoring_fn=lambda r: float(r.get("confidence_estimate", r.get("confidence", 0.0))),
            )
            case["improvement"] = best

        logger.info("LearningAgent completed with events: %s", learning_events)
        output = {
            "learning": {
                "status": "learning_complete",
                "events_count": len(learning_events),
            },
            "learning_events": learning_events,
            "consensus_scores": consensus_scores,
            "feedback_cases": feedback_cases,
            "feedback": {"stored_case_count": len(feedback_cases)},
            "timeline": ["learning_agent completed"],
        }
        avg_conf = 0.0
        if feedback_cases:
            avg_conf = sum(float(case.get("confidence", 0.0)) for case in feedback_cases) / len(feedback_cases)
        log_agent_trace(
            agent_name="learning",
            input_data={
                "learning_events_seed": learning_events,
                "low_confidence_agents": low_confidence_agents,
                "num_samples": num_samples,
            },
            output_data=output,
            confidence=avg_conf,
            latency_ms=int((time.time() - start_time) * 1000),
        )
        return output

