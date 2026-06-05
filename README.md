# TrustChainAI

**AI-Powered Smart Contract Security & Audit Intelligence**

[![Status](https://img.shields.io/badge/Status-Active%20Development-F59E0B?style=flat-square)]()
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org)
[![HuggingFace](https://img.shields.io/badge/🤗%20HuggingFace-Model-FFD21F?style=flat-square)](https://huggingface.co/emekaphilian)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)

[**Live Demo**](https://huggingface.co/spaces/emekaphilian/trustchainai) · [**Model**](https://huggingface.co/emekaphilian) · [**Architecture Docs**](docs/ARCHITECTURE.md) · [**Ethics Framework**](docs/ETHICS.md)

---

## Overview

Professional smart contract audits cost **$10,000–$50,000** per engagement and take weeks. In 2023, over **$1.8 billion** was lost to smart contract exploits — vulnerabilities that pattern-matching tools could partially detect, but no system existed to do so *accessibly*, *transparently*, or *fairly* at scale.

TrustChainAI closes that gap. It is a **continuously learning audit intelligence system** that goes beyond static detection into reasoning, memory, and governance — designed first for African and emerging-market Web3 ecosystems where audit access is near zero, and built to scale to any team deploying Solidity contracts.

Where traditional tools (Slither, Mythril) stop at rule-based classification, TrustChainAI adds:

- **Memory** — learns from past audits via persistent case retrieval
- **Knowledge grounding** — enriches predictions with the SWC vulnerability ontology
- **Explainability** — produces traceable, context-aware reasoning per finding
- **Governance** — bias-aware scoring with a full audit trail

---

## Architecture

```
                    ┌──────────────────────────┐
                    │       Orchestrator        │
                    └──────────┬────────────────┘
                               │
       ┌───────────────────────┼──────────────────────┐
       ▼                       ▼                      ▼
┌─────────────┐     ┌──────────────────┐    ┌──────────────────┐
│  Detection  │     │ Knowledge Layer  │    │  Memory Layer    │
│  Agent      │     │ (SWC Registry)   │    │ (Case Retrieval) │
│  CodeBERT   │     │ Exploit KB       │    │ Similarity Index │
└──────┬──────┘     └────────┬─────────┘    └────────┬─────────┘
       │                     │                        │
       └─────────────┬───────┴────────────────────────┘
                     ▼
        ┌────────────────────────────────┐
        │        Explainer Agent         │
        │  Memory + Knowledge XAI        │
        └──────────────┬─────────────────┘
                       ▼
        ┌────────────────────────────────┐
        │      Ethics / Bias Layer       │
        │  Fairness + Risk Calibration   │
        └──────────────┬─────────────────┘
                       ▼
        ┌────────────────────────────────┐
        │       Reporting Agent          │
        │  Structured Audit Report       │
        └──────────────┬─────────────────┘
                       ▼
        ┌────────────────────────────────┐
        │    Streamlit UI + FastAPI      │
        └────────────────────────────────┘
```

**End-to-end pipeline:**

1. Submit a Solidity contract, bytecode, or on-chain address
2. Detection agent classifies vulnerability risk (CodeBERT, 14 classes)
3. Knowledge layer maps findings to the SWC exploit registry
4. Memory system retrieves similar historical audit cases
5. Explainer generates context-aware reasoning over steps 2–4
6. Ethics layer applies bias-aware risk calibration
7. Reporting agent produces a structured audit output
8. Dashboard visualizes findings, traces, memory matches, and fairness indicators

---

## Core Modules

### Detection Engine
CodeBERT-based classifier covering 14 vulnerability classes, with a hybrid ML + heuristic fallback for edge cases.

### Knowledge Grounding (Stage 2.4)
SWC registry mapping, exploit pattern library, and security ontology enrichment. Every finding is anchored to a standardized vulnerability taxonomy.

### Memory System (Stages 2.1–2.3)
Persistent JSONL audit memory with fingerprint-based similarity retrieval. The system learns from completed audits via post-audit writeback.

### Explainability Engine
Memory- and knowledge-conditioned reasoning with confidence calibration and a fully traceable decision flow per prediction.

### Ethics & Governance Layer
Bias-aware audit scoring, risk calibration safeguards, per-prediction transparency enforcement, and a full audit trail. Built to align with responsible AI and regulatory-grade audit standards.

### Analyst Dashboard
A Streamlit interface with modules for contract analysis, detection output, memory similarity, SWC mapping, ethics indicators, risk/severity scoring, and full report export.

**Example panel outputs:**

```
# Detection
Vulnerability: Reentrancy  |  Severity: Critical  |  Confidence: 0.93

# Memory
DAO Hack            Similarity: 0.87
Parity Wallet       Similarity: 0.79

# Knowledge
SWC-107 → Reentrancy
Mitigation: checks-effects-interactions pattern
Exploit vector: external call before state update
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| ML Model | CodeBERT (HuggingFace) |
| Framework | PyTorch |
| Memory | JSONL + Similarity Index |
| Knowledge | SWC Registry |
| Explainability | Memory + Knowledge Conditioning |
| Ethics | Bias + Risk Calibration Engine |
| Backend | Python + FastAPI |
| UI | Streamlit + Plotly |
| Deployment | Docker + HuggingFace Spaces |

---

## Roadmap

### ✅ Completed
- Multi-agent orchestration
- CodeBERT detection engine
- Persistent memory system
- SWC knowledge grounding
- XAI explainability engine
- Streamlit UI framework

### 🔵 Model Optimization
- Calibration tuning
- Precision/recall optimization
- Adversarial robustness testing

### 🟣 UI Enhancement
- Advanced analytics dashboard
- Contract diff viewer
- Real-time streaming updates

### 🟠 API Productization
- FastAPI production endpoints
- Auth + rate limiting

### 🔴 Deployment
- Docker production packaging
- HuggingFace Spaces deployment
- CI/CD automation pipeline

---

## Reliability

50+ unit and integration tests covering memory validation, knowledge registry consistency, deterministic pipeline execution, and end-to-end system correctness.

---

## Author

**Emeka Philian Ogbonna** — AI Systems Engineer · Cybersecurity ML · Multi-Agent Architect

[![GitHub](https://img.shields.io/badge/GitHub-emekaphilian-181717?style=flat-square&logo=github)](https://github.com/emekaphilian)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-emeka--ogbonna-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/emeka-ogbonna-24064a179/)
[![HuggingFace](https://img.shields.io/badge/🤗%20HuggingFace-emekaphilians-FFD21F?style=flat-square)](https://huggingface.co/emekaphilians)

---

*If this project helps or interests you, consider starring the repository.*
