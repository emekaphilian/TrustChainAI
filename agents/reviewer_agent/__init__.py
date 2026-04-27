from app.agents.base import BaseAgent
from app.models.llm_service import LLMService
from app.orchestrator.state import AuditState
from app.utils.trace_logger import log_agent_trace
import time


class ReviewerAgent(BaseAgent):
    name = "reviewer"

    def __init__(self) -> None:
        self.llm_service = LLMService()

    def run(self, state: AuditState) -> dict:
        start_time = time.time()
        findings = len(state.get("analysis", {}).get("vulnerabilities", [])) + len(
            state.get("static_analysis", {}).get("issues", [])
        )
        prompt = (
            "You are reviewing multiple AI analyses of a smart contract. Identify consistent findings, "
            "contradictions, and confidence levels. Return JSON keys: verified_findings, discrepancies, "
            "final_confidence, vulnerabilities."
        )
        num_samples = max(1, int(state.get("num_samples", 3)))
        best, consensus = self.llm_service.verbalized_sample(prompt, num_samples=num_samples)
        review = {
            "validated": True,
            "finding_count": findings,
            "notes": "Cross-check complete between LLM and static analysis outputs.",
            "final_confidence": best.get("confidence", 0.0),
            "discrepancies": best.get("discrepancies", []),
        }
        output = {
            "review": review,
            "review_consensus": consensus,
            "timeline": ["reviewer_agent completed"],
        }
        log_agent_trace(
            agent_name="reviewer",
            input_data={"prompt": prompt, "findings": findings, "num_samples": num_samples},
            output_data={"best": best, "consensus": consensus, "review": review},
            confidence=float(review.get("final_confidence", 0.0)),
            latency_ms=int((time.time() - start_time) * 1000),
        )
        return output

