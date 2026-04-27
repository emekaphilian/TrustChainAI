import os
from pathlib import Path

structure = [
    "data/raw/smart_contracts",
    "data/raw/vulnerability_samples",
    "data/raw/attack_patterns",
    "data/processed/cleaned_contracts",
    "data/processed/labeled_vulnerabilities",
    "data/processed/embeddings",
    "data/vector_db/faiss_index",
    "data/vector_db/pinecone_cache",
    "data/audit_logs",
    "agents/static_analysis",
    "agents/rag_agent",
    "agents/bias_agent",
    "agents/xai_agent",
    "agents/consensus_agent",
    "agents/trust_agent",
    "resources/swc_registry",
    "resources/owasp_top10",
    "resources/solidity_docs",
    "resources/openzeppelin_docs",
    "resources/consensys_guidelines",
    "resources/security_research_papers",
    "tests/unit_tests",
    "tests/integration_tests",
    "tests/adversarial_tests",
    "tests/bias_tests",
    "tests/hallucination_tests",
    "tests/regression_tests",
    "api",
    "frontend",
    "reports",
    "configs",
    "notebooks",
    "docs",
]

root = Path(__file__).resolve().parents[1]
for p in structure:
    d = root / p
    d.mkdir(parents=True, exist_ok=True)
print("Scaffold created or verified.")
