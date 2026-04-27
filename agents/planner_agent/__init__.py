from app.agents.base import BaseAgent
from app.orchestrator.state import AuditState


class PlannerAgent(BaseAgent):
    name = "planner"

    def run(self, state: AuditState) -> dict:
        plan = {
            "steps": ["research", "analysis", "static_analysis", "cluster", "review", "ethics"],
            "priority": "high" if state.get("contract_address") else "normal",
        }
        return {"plan": plan, "timeline": ["planner_agent completed"]}

