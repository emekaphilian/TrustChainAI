from app.agents.base import BaseAgent
from app.orchestrator.state import AuditState
from app.tools.slither_tool import run_static_analysis


class StaticAgent(BaseAgent):
    name = "static"

    def run(self, state: AuditState) -> dict:
        return {
            "static_analysis": run_static_analysis(state.get("contract_code") or ""),
            "timeline": ["static_agent completed"],
        }

