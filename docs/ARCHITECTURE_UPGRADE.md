# TrustChainAI — High-Level System Architecture (Upgrade)

This document captures the proposed high-level system architecture and production-ready folder structure for TrustChainAI. It expands the existing design into a clear, interview-ready architecture and calls out crucial test types (including adversarial tests for prompt attacks).

---

## Overview — TrustChainAI Flow

User Uploads Solidity Contract
        ↓
Preprocessing Layer
        ↓
Static Analysis Agent
        ↓
RAG Grounding Agent
        ↓
Bias Detection Agent
        ↓
Explainability Agent
        ↓
Consensus Agent
        ↓
Trustworthiness Scoring Engine
        ↓
Governance Report Generator
        ↓
Dashboard + PDF Export

This pipeline emphasizes reproducible, auditable decisions and strong grounding for any LLM-derived findings.

---

## Production-Level Folder Structure (recommended)

TrustChainAI/
│
├── data/
│
├── agents/
│
├── resources/
│
├── tests/
│
├── api/
│
├── frontend/
│
├── reports/
│
├── configs/
│
├── notebooks/
│
├── docs/
│
├── scripts/
│
├── requirements.txt
├── docker-compose.yml
├── README.md
└── .env.example

The structure above keeps ML/data, agent logic, and operational artifacts clearly separated for audits and demos.

---

## 1. DATA/ — Purpose & Layout

Purpose: store datasets, intermediate artifacts, and vectorized knowledge used by the RAG and evaluation pipelines.

data/
│
├── raw/
│   ├── smart_contracts/
│   ├── vulnerability_samples/
│   └── attack_patterns/
│
├── processed/
│   ├── cleaned_contracts/
│   ├── labeled_vulnerabilities/
│   └── embeddings/
│
├── vector_db/
│   ├── faiss_index/
│   └── pinecone_cache/
│
└── audit_logs/

Notes:
- Keep raw immutable; any cleaning produces new snapshot under `processed/` with provenance metadata.
- Store vector DB artifacts separately and include a small `manifest.json` describing indexing parameters.

---

## 2. AGENTS/ — Core Brain

High-level layout for agents; each agent folder contains a clear API, unit tests, and a lightweight CLI for local runs.

agents/
│
├── static_analysis/
│   ├── slither_agent.py
│   ├── mythril_agent.py
│   └── vulnerability_mapper.py
│
├── rag_agent/
│   ├── retriever.py
│   ├── vector_search.py
│   └── evidence_grounding.py
│
├── bias_agent/
│   ├── fairness_checker.py
│   ├── bias_metrics.py
│   └── severity_bias_detector.py
│
├── xai_agent/
│   ├── explanation_engine.py
│   ├── exploit_trace.py
│   └── confidence_scorer.py
│
├── consensus_agent/
│   ├── decision_engine.py
│   └── verdict_generator.py
│
└── trust_agent/
    ├── trust_score.py
    └── governance_scoring.py

Notes:
- Each agent implements `process(input) -> structured_result` and emits an audit record.
- Agents communicate via typed messages (dataclasses or pydantic models) so orchestration is lightweight and testable.

---

## 3. RESOURCES/ — External Knowledge + Standards

resources/
│
├── swc_registry/
├── owasp_top10/
├── solidity_docs/
├── openzeppelin_docs/
├── consensys_guidelines/
└── security_research_papers/

Notes:
- These resources are the canonical sources for the RAG layer; track versioned snapshots and citation metadata.

---

## 4. TESTS/ — Critical for Senior-Level Signal

tests/
│
├── unit_tests/
├── integration_tests/
├── adversarial_tests/
├── bias_tests/
├── hallucination_tests/
└── regression_tests/

Adversarial testing (REQUIRED):
- Add tests for prompt attacks, instruction injection, data poisoning, and model-misleading evidence in RAG retrieval.
- Include automation to run adversarial scenarios against the entire pipeline (static analysis outputs → RAG → LLM prompts → final scoring).

Bias and hallucination tests:
- Bias tests should assert false-positive rate parity across contract types when enough samples exist.
- Hallucination tests validate RAG grounding coverage and penalize unsupported assertions in generated reports.

---

## Governance & Auditability (cross-cutting)

- Every agent must produce an `audit_record` with input hash, timestamp, agent version, model/tokenizer hashes, and deterministic evidence references (RAG doc ids or vector ids).
- The `audit_logs/` folder in `data/` must store these records and be queryable for each governance report.

---

## Additional Notes & Next Steps

1. Add `ARCHITECTURE_UPGRADE.md` (this file) to `docs/` (done).
2. If you want, I can scaffold the directory tree and create lightweight starter files for each agent and test suite.
3. I strongly recommend adding an automated `scripts/scaffold_structure.py` or a Makefile to create this layout in any new repo clone.

---

## Why this wins interviews

- Clear separation of concerns (data, agents, resources, tests).
- Explicit adversarial testing and bias measurement demonstrates security-first thinking.
- Auditability / provenance baked in (audit logs + version hashes).
- Scalable RAG + vector DB design with explicit grounding sources.

---

Prepared on: 2026-04-27
