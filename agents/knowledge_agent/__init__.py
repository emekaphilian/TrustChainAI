from app.agents.base import BaseAgent
from app.orchestrator.state import AuditState
from app.rag.retriever import retrieve_context, seed_default_knowledge


class KnowledgeAgent(BaseAgent):
    name = "knowledge"

    def run(self, state: AuditState) -> dict:
        if not state.get("use_rag", True):
            return {
                "research": {"rag_context": [], "rag_enabled": False},
                "timeline": ["knowledge_agent skipped (rag disabled)"],
            }
        seed_default_knowledge()
        query = state.get("contract_code") or state.get("contract_address") or "smart contract audit"
        return {
            "research": {"rag_context": retrieve_context(query), "rag_enabled": True},
            "timeline": ["knowledge_agent completed"],
        }

