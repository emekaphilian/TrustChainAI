from app.agents.base import BaseAgent
from app.models.llm_service import LLMService
from app.orchestrator.state import AuditState
from app.utils.trace_logger import log_agent_trace
from src.models.bias_detector import BiasDetector
import time


class EthicsAgent(BaseAgent):
    name = "ethics"

    def __init__(self) -> None:
        self.bias_detector = BiasDetector()
        self.llm_service = LLMService()

        # 🔥 Frameworks (NEW - for compliance scoring)
        self.frameworks = {
            "SWC": "Smart Contract Weakness Classification",
            "OWASP": "Smart Contract Top 10",
            "ISO27001": "Security Principles",
            "IEEE": "Ethically Aligned Design"
        }

    def run(self, state: AuditState) -> dict:
        start_time = time.time()

        # -----------------------------
        # INPUT STATE (UNCHANGED)
        # -----------------------------
        analysis = state.get("analysis", [])
        review = state.get("review", {})
        num_samples = max(1, int(state.get("num_samples", 3)))
        use_rag = state.get("use_rag", False)

        # -----------------------------
        # 🔍 RAG TRANSPARENCY LAYER (NEW)
        # -----------------------------
        rag_sources = []
        rag_summary = ""
        rag_context = ""

        if use_rag:
            try:
                # Lazy import to avoid breaking system if RAG not configured
                from app.rag.retriever import Retriever

                retriever = Retriever()
                rag_results = retriever.retrieve(
                    query=str(analysis),
                    top_k=5
                )

                rag_sources = [
                    {
                        "title": r.get("title", "Unknown"),
                        "score": round(r.get("score", 0), 3),
                        "snippet": r.get("content", "")[:200]
                    }
                    for r in rag_results
                ]

                rag_context = "\n".join([r["snippet"] for r in rag_sources])

                rag_summary = f"{len(rag_sources)} sources retrieved for grounding."

            except Exception as e:
                rag_summary = f"RAG retrieval failed: {str(e)}"

        # -----------------------------
        # 🧠 VERBALIZED SAMPLING PROMPT (UPGRADED)
        # -----------------------------
        prompt = f"""
Evaluate the outputs of the analysis and review agents.

Analysis:
{analysis}

Review:
{review}

Use these frameworks:
- SWC Registry
- OWASP Smart Contract Top 10
- ISO/IEC 27001
- IEEE Ethics Guidelines

Use this retrieved knowledge if available:
{rag_context}

Tasks:
1. Identify ethical and security violations
2. Map violations to frameworks
3. Detect bias in reasoning
4. Estimate compliance per framework (0–1)
5. Assign an overall ethics score (0–100)

Return STRICT JSON:
{{
    "bias_detected": true/false,
    "bias_type": "...",
    "violations": [
        {{
            "issue": "...",
            "severity": "Low|Medium|High|Critical",
            "framework": "SWC|OWASP|ISO|IEEE"
        }}
    ],
    "framework_alignment": {{
        "SWC": 0-1,
        "OWASP": 0-1,
        "ISO27001": 0-1,
        "IEEE": 0-1
    }},
    "ethics_score": 0-100,
    "recommendations": [...],
    "confidence": 0-1
}}
"""

        # -----------------------------
        # 🔁 VERBALIZED SAMPLING (UNCHANGED CORE)
        # -----------------------------
        best, consensus = self.llm_service.verbalized_sample(
            prompt,
            num_samples=num_samples
        )

        # -----------------------------
        # 🧠 SYSTEM BIAS DETECTION (NEW)
        # -----------------------------
        discrepancies = state.get("review_consensus", {}).get("discrepancies", [])

        system_bias = {
            "detected": False,
            "type": None
        }

        if consensus.get("agreement_rate", 1) < 0.6:
            system_bias = {"detected": True, "type": "Low agreement (agent conflict)"}

        elif len(discrepancies) > 2:
            system_bias = {"detected": True, "type": "High agent disagreement"}

        elif consensus.get("confidence_spread", 0) > 0.5:
            system_bias = {"detected": True, "type": "High confidence variance"}

        # -----------------------------
        # 📊 ETHICS SCORING (NEW)
        # -----------------------------
        violations = best.get("violations", [])

        severity_weights = {
            "Low": 5,
            "Medium": 10,
            "High": 20,
            "Critical": 30
        }

        penalty = sum(
            severity_weights.get(v.get("severity", "Low"), 5)
            for v in violations
        )

        ethics_score = max(0, 100 - penalty)

        # -----------------------------
        # 📏 COMPLIANCE SCORING (NEW)
        # -----------------------------
        framework_alignment = best.get("framework_alignment", {})

        compliance_scores = {
            fw: round(framework_alignment.get(fw, 0) * 100, 2)
            for fw in self.frameworks.keys()
        }

        avg_compliance = round(
            sum(compliance_scores.values()) / len(compliance_scores),
            2
        )

        # -----------------------------
        # 🧠 FINAL ETHICS OBJECT (EXTENDED)
        # -----------------------------
        ethics = {
            # ORIGINAL (unchanged behavior)
            "bias_check": "enabled",
            "status": "flagged" if best.get("bias_detected") else "pass",
            "explainability_ready": bool(state.get("analysis")),
            "violations": violations,
            "recommendations": best.get("recommendations", []),
            "confidence": best.get("confidence", 0.0),

            # 🔥 NEW FIELDS
            "bias_detected": best.get("bias_detected", False),
            "bias_type": best.get("bias_type"),
            "system_bias": system_bias,
            "ethics_score": ethics_score,
            "compliance_scores": compliance_scores,
            "avg_compliance": avg_compliance,
        }

        # -----------------------------
        # 📦 FINAL OUTPUT (EXTENDED)
        # -----------------------------
        output = {
            "ethics": ethics,
            "ethics_consensus": consensus,
            "frameworks_used": list(self.frameworks.keys()),

            # 🔥 RAG TRANSPARENCY
            "rag_enabled": use_rag,
            "rag_sources": rag_sources,
            "rag_summary": rag_summary,

            "timeline": ["ethics_agent completed"],
        }

        # -----------------------------
        # 🧾 TRACE LOGGING (UNCHANGED)
        # -----------------------------
        log_agent_trace(
            agent_name="ethics",
            input_data={
                "prompt": prompt,
                "num_samples": num_samples,
                "use_rag": use_rag
            },
            output_data={
                "best": best,
                "consensus": consensus,
                "ethics": ethics,
                "rag_sources": rag_sources
            },
            confidence=float(ethics.get("confidence", 0.0)),
            latency_ms=int((time.time() - start_time) * 1000),
        )

        return output