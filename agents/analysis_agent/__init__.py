from app.agents.base import BaseAgent
from app.models.llm_service import LLMService
from app.orchestrator.state import AuditState
from app.utils.trace_logger import log_agent_trace
from src.models.vulnerability_detector import VulnerabilityDetector
import time


class AnalysisAgent(BaseAgent):
    name = "analysis"

    def __init__(self) -> None:
        self.detector = VulnerabilityDetector()
        self.llm_service = LLMService()

    def run(self, state: AuditState) -> dict:
        start_time = time.time()
        contract_code = state.get("contract_code")
        contract_address = state.get("contract_address") or "unknown"
        if not contract_code:
            output = {
                "analysis": {"warning": "No source code provided", "risk_score": 0.0},
                "timeline": ["analysis_agent skipped"],
            }
            log_agent_trace(
                agent_name="analysis",
                input_data={"contract_address": contract_address, "has_contract_code": False},
                output_data=output,
                confidence=0.0,
                latency_ms=int((time.time() - start_time) * 1000),
            )
            return output
        # Use detector when available; fall back to lightweight heuristic if model integration fails.
        try:
            prediction = self.detector.predict(contract_code, contract_address)
            analysis = {
                "risk_score": float(getattr(prediction, "risk_score", 0.0)),
                "confidence": float(getattr(prediction, "confidence", 0.6)),
                "vulnerabilities": [
                    getattr(v, "type", str(v)) for v in getattr(prediction, "vulnerabilities", [])
                ],
            }
        except Exception as exc:
            lowered = contract_code.lower()
            heuristic_vulns = []
            if ".call(" in lowered or "call.value" in lowered:
                heuristic_vulns.append("reentrancy")
            if "tx.origin" in lowered:
                heuristic_vulns.append("phishing_pattern")
            if "+=" in lowered and "uint" in lowered:
                heuristic_vulns.append("overflow")
            analysis = {
                "risk_score": 0.45 if heuristic_vulns else 0.15,
                "confidence": 0.55,
                "vulnerabilities": heuristic_vulns,
                "warning": f"detector_fallback:{exc.__class__.__name__}",
            }
        prompt = (
            "You are a smart contract security expert. Analyze this Solidity-like code and return "
            "JSON with keys: reasoning, vulnerabilities, confidence. Code:\n"
            f"{contract_code[:3000]}"
        )
        num_samples = max(1, int(state.get("num_samples", 3)))
        best, consensus = self.llm_service.verbalized_sample(prompt, num_samples=num_samples)
        llm_vulns = [
            vuln.get("type", "unknown")
            for vuln in best.get("vulnerabilities", [])
            if isinstance(vuln, dict)
        ]
        analysis["vulnerabilities"] = sorted(set(analysis["vulnerabilities"] + llm_vulns))
        analysis["reasoning"] = best.get("reasoning", "")
        analysis["confidence"] = max(float(analysis["confidence"]), float(best.get("confidence", 0.0)))
        output = {
            "analysis": analysis,
            "analysis_consensus": consensus,
            "timeline": ["analysis_agent completed"],
        }
        log_agent_trace(
            agent_name="analysis",
            input_data={"prompt": prompt, "contract_address": contract_address, "num_samples": num_samples},
            output_data={"best": best, "consensus": consensus, "analysis": analysis},
            confidence=float(analysis.get("confidence", 0.0)),
            latency_ms=int((time.time() - start_time) * 1000),
        )
        return output

