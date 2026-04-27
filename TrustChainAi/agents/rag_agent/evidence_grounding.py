"""Evidence grounding utilities for RAG outputs."""

def ground_evidence(retrieved_docs: list) -> dict:
    return {"grounded": [], "docs": retrieved_docs}
