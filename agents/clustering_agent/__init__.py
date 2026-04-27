from app.agents.base import BaseAgent
from app.orchestrator.state import AuditState


class ClusteringAgent(BaseAgent):
    name = "clustering"

    def run(self, state: AuditState) -> dict:
        risk = float(state.get("analysis", {}).get("risk_score", 0.0))
        bucket = "critical" if risk > 0.8 else "high" if risk > 0.5 else "medium" if risk > 0.2 else "low"
        return {"clusters": {"risk_cluster": bucket}, "timeline": ["clustering_agent completed"]}

