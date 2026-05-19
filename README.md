# TrustChainAI 🔐

<div align="center">

**AI-Powered Smart Contract Auditor with Ethics Dashboard**

*Combining LLM vulnerability detection, explainable AI, and fairness monitoring to make blockchain security trustworthy — and accessible.*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org)
[![HuggingFace](https://img.shields.io/badge/🤗%20Hugging%20Face-Model-FFD21F?style=flat-square)](https://huggingface.co/emekaphilian)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active%20Development-F59E0B?style=flat-square)]()

[**Live Demo**](https://huggingface.co/spaces/emekaphilian/trustchainai) · [**Model on Hugging Face**](https://huggingface.co/emekaphilian) · [**Architecture Docs**](docs/ARCHITECTURE.md) · [**Ethics Framework**](docs/ETHICS.md)

</div>

---

## Why This Exists

Professional smart contract audits cost **$10,000–$50,000** per engagement and take weeks. In 2023 alone, over **$1.8 billion** was lost to smart contract exploits — with DeFi protocols on EVM-compatible chains bearing the majority of losses. The DAO hack (2016), Parity Wallet exploit (2017), and BatchOverflow attack (2018) all share a common thread: vulnerabilities that pattern-matching tools could partially detect, but no system existed to do so *accessibly*, *transparently*, or *fairly* at scale.

TrustChainAI is built to close that gap — starting with African and emerging-market Web3 ecosystems where audit access is near zero, and scaling to any team deploying Solidity contracts who needs automated, explainable, bias-aware security analysis.

---

## What It Does

TrustChainAI is an enterprise-grade smart contract security platform with four core capabilities:

**1. Vulnerability Detection**
Fine-tuned CodeBERT (microsoft/codebert-base) classifies Solidity contracts across 14 vulnerability categories in real time. Detects both well-known patterns (reentrancy, overflow) and advanced attack vectors (flash loan manipulation, MEV exposure, proxy storage collisions).

**2. Risk Clustering**
Unsupervised PyTorch clustering groups contracts by risk profile — enabling batch portfolio analysis and anomaly identification without manual review of every contract.

**3. Explainable AI**
Every prediction is accompanied by SHAP token-level attributions and LIME explanations, showing exactly *which lines of code* drove the classification. This is not a black box.

**4. Ethics & Bias Monitoring**
A live Streamlit dashboard tracks false positive rates broken down by contract type, monitors model fairness metrics across audit sessions, and maintains a complete audit trail — aligned with EU AI Act transparency requirements and responsible AI principles.

---

## Architecture

```
                        ┌─────────────────────────────────────┐
                        │           TrustChainAI               │
                        │        Orchestrator Agent            │
                        └──────────────┬──────────────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
   ┌──────────▼──────────┐  ┌─────────▼────────┐  ┌──────────▼──────────┐
   │   Detection Agent   │  │  Intel / RAG      │  │   Ethics Agent      │
   │                     │  │  Grounding Agent  │  │                     │
   │  CodeBERT fine-tune │  │                   │  │  BiasDetector       │
   │  14-class classify  │  │  Retrieval-aug.   │  │  FPR by contract    │
   │  Heuristic fallback │  │  vulnerability KB │  │  Fairness metrics   │
   └──────────┬──────────┘  └─────────┬────────┘  └──────────┬──────────┘
              │                        │                        │
              └────────────────────────┼────────────────────────┘
                                       │
                        ┌──────────────▼──────────────┐
                        │      Explainer Agent         │
                        │  SHAP · LIME · Token attr.   │
                        └──────────────┬───────────────┘
                                       │
                        ┌──────────────▼──────────────┐
                        │     Reporting Agent          │
                        │  GenAI plain-English summary │
                        │  Regulatory audit trail      │
                        └──────────────┬───────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                                                  │
   ┌──────────▼──────────┐                         ┌───────────▼──────────┐
   │   Streamlit         │                         │   REST API           │
   │   Ethics Dashboard  │                         │   FastAPI endpoints  │
   │   Bias metrics      │                         │   Programmatic scans │
   │   SHAP viz          │                         │   Webhook support    │
   └─────────────────────┘                         └──────────────────────┘
```

**Data flow:** Contract input (source/bytecode/address) → Orchestrator → parallel Detection + RAG grounding → Explainer → Ethics check → Report generation → Dashboard / API response.

---

## Vulnerability Detection Coverage

| Category | Vulnerability | Severity | Detection Method |
|----------|--------------|----------|-----------------|
| **Reentrancy** | Classic reentrancy (DAO-style) | 🔴 Critical | CodeBERT + pattern |
| **Arithmetic** | Integer overflow / underflow | 🔴 Critical | CodeBERT + heuristic |
| **Access Control** | Unprotected `selfdestruct` | 🔴 Critical | CodeBERT + AST |
| **Access Control** | Broken ownership / `setOwner` | 🔴 Critical | CodeBERT + pattern |
| **Phishing** | `tx.origin` authentication | 🟠 High | CodeBERT + pattern |
| **DoS** | Unbounded loop gas exhaustion | 🟠 High | Heuristic + CodeBERT |
| **Call Safety** | Unchecked external call return | 🟡 Medium | Pattern + CodeBERT |
| **MEV** | Front-running / TOD exposure | 🟡 Medium | CodeBERT |
| **Randomness** | Block timestamp dependence | 🟡 Medium | Pattern |
| **Upgradability** | Proxy storage collision | 🟡 Medium | CodeBERT + AST |
| **Flash Loans** | Price oracle manipulation | 🟠 High | CodeBERT |
| **Flash Loans** | Single-block liquidity attack | 🟠 High | CodeBERT |
| **Constructor** | Misnamed constructor bug | 🔴 Critical | Pattern |
| **Control** | Safe contract (baseline) | ✅ Low | Full pipeline |

---

## Real-World Benchmark Contracts

The system is evaluated against historically significant exploits as ground truth:

| Contract | Incident | Year | Loss | Expected Detection |
|----------|----------|------|------|--------------------|
| SimpleDAO | [The DAO Hack](https://www.coindesk.com/learn/the-dao-hack-explained/) | 2016 | $60M | Reentrancy · Critical |
| ParityWallet | [Parity Wallet Exploit](https://blog.openzeppelin.com/on-the-parity-wallet-multisig-hack-405a8c12e8f7) | 2017 | $30M | Access Control · Critical |
| BatchOverflow | BEC Token Hack | 2018 | $900M | Integer Overflow · Critical |
| Rubixi | Constructor Bug | 2016 | — | Ownership Takeover · Critical |

Plus adversarial/obfuscated variants and a 2,000-contract synthetic dataset for robustness benchmarking.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **LLM Core** | CodeBERT (microsoft/codebert-base) | Fine-tuned vulnerability classifier |
| **ML Framework** | PyTorch 2.x | Training, clustering, inference |
| **Feature Engineering** | scikit-learn | Preprocessing, evaluation |
| **Blockchain** | Web3.py | Ethereum RPC, bytecode retrieval |
| **Static Analysis** | Slither, Mythril | Heuristic fallback + validation |
| **Explainability** | SHAP, LIME | Per-prediction token attribution |
| **Orchestration** | LangGraph | Multi-agent workflow management |
| **Dashboard** | Streamlit | Ethics monitoring UI |
| **API** | FastAPI | Programmatic access |
| **Caching** | SQLite | Prediction + explanation cache |
| **Deployment** | Docker, Kubernetes | Containerised production deployment |
| **Experiment Tracking** | Hugging Face Hub | Model versioning + public demo |

---

## Quick Start

### Prerequisites
- Python 3.10+
- PyTorch (GPU recommended; CPU fallback supported)
- Docker & Docker Compose (optional)

### 1. Clone and set up environment

```bash
git clone https://github.com/emekaphilian/TrustChainAI.git
cd TrustChainAI

python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Prepare datasets

```bash
python scripts/prepare_datasets.py
```

### 3. Train the vulnerability detector

```bash
# Opens notebook with full CodeBERT fine-tuning pipeline
jupyter notebook notebooks/train_vulnerability_detector.ipynb

# Or run headlessly (GPU recommended, ~20 min)
python -m jupyter nbconvert --to notebook --execute \
  notebooks/train_vulnerability_detector.ipynb \
  --ExecutePreprocessor.timeout=6000
```

Model artifacts saved to `data/models/vulnerability_detector_v1/`.

### 4. Run a scan

```bash
# Scan a single contract by Ethereum address
python pipelines/audit_pipeline.py \
  --address 0xYOUR_CONTRACT_ADDRESS \
  --output data/processed/scan_results.json

# Or scan a local Solidity file
python pipelines/audit_pipeline.py \
  --file contracts/ReentrancyVulnerable.sol
```

### 5. Launch the Ethics Dashboard

```bash
streamlit run app/main.py --server.port 8501
# Visit http://localhost:8501
```

### Docker (all-in-one)

```bash
docker-compose up --build
# Dashboard: http://localhost:8501
# API:       http://localhost:8000
```

---

## Training Details

| Parameter | Value |
|-----------|-------|
| Base model | microsoft/codebert-base |
| Dataset size | 10,000 Ethereum contracts |
| Train / val split | 80% / 20% |
| Classes | 4 (safe, reentrancy, overflow, phishing) |
| Max token length | 512 |
| Batch size | 8 |
| Epochs | 3 |
| Learning rate | 2e-5 |
| Optimizer | AdamW (weight decay 0.01) |
| Hardware | CUDA GPU / CPU fallback |

Dataset sourced from BigQuery public Ethereum dataset (block-range sampled to stay within free-tier quotas), SolidiFI (3,000 contracts), and SmartBugs (7,000 contracts).

---

## Project Structure

```
TrustChainAI/
├── agents/                     # Multi-agent business logic
│   ├── base.py                 # BaseAgent class
│   ├── detection_agent.py      # Vulnerability detection orchestration
│   ├── ethics_agent.py         # Bias monitoring and fairness checks
│   ├── explainer_agent.py      # SHAP/LIME explanation generation
│   ├── reporting_agent.py      # GenAI incident summaries
│   └── clustering_agent.py     # Risk profile clustering
├── app/
│   └── main.py                 # Streamlit dashboard entry point
├── api/
│   └── main.py                 # FastAPI REST service
├── data/
│   ├── Datasets/               # Raw + processed contract datasets
│   ├── models/                 # Trained model artifacts
│   ├── benchmark/              # Historical exploit contracts
│   └── synthetic/              # Generated training contracts
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ETHICS.md
│   ├── TRAINING.md
│   └── KUBERNETES.md
├── infra/                      # Slither, Mythril static analyzers
├── notebooks/
│   └── train_vulnerability_detector.ipynb
├── pipelines/
│   └── audit_pipeline.py       # End-to-end scan orchestration
├── scripts/
│   ├── prepare_datasets.py
│   ├── generate_dataset.py     # Synthetic contract generator
│   └── evaluate_benchmark.py
├── src/
│   ├── auditor/                # Contract scanning engine
│   ├── models/                 # ML model classes
│   └── utils/                  # Web3 helpers, RPC manager
├── tests/                      # Unit + integration tests
├── kubernetes/                 # K8s deployment manifests
├── docker-compose.yml
└── requirements.txt
```

---

## Development Roadmap

| Phase | Component | Status |
|-------|-----------|--------|
| 1 | Architecture, base classes, config framework | ✅ Complete |
| 1 | Documentation (ARCHITECTURE, ETHICS, API) | ✅ Complete |
| 2 | Dataset preparation (10K contracts) | ✅ Complete |
| 2 | Training notebook (CodeBERT fine-tuning) | ✅ Complete |
| 2 | Model training execution + Hugging Face publish | 🔄 In Progress |
| 3 | VulnerabilityDetector integration + predict() | ⏳ Next |
| 3 | SHAP/LIME explainability per prediction | ⏳ Planned |
| 3 | Scanner → Detector → BiasDetector pipeline | ⏳ Planned |
| 4 | Streamlit Ethics Dashboard (full build) | ⏳ Planned |
| 4 | Multi-agent LangGraph orchestration | ⏳ Planned |
| 5 | Full test suite (unit + integration) | ⏳ Planned |
| 6 | Docker + Kubernetes production deployment | ⏳ Planned |
| 6 | Hugging Face Spaces public demo | ⏳ Planned |

---

## Ethics & Fairness

TrustChainAI treats fairness as a first-class engineering concern, not an afterthought.

- **Bias detection** — false positive rates are computed and surfaced per contract type after every audit session (minimum 50 samples per category for statistical validity)
- **Explainability** — every prediction includes SHAP token-level attribution so analysts can verify the model's reasoning
- **Audit trail** — all decisions are logged with timestamps, confidence scores, and model version for regulatory compliance
- **EU AI Act alignment** — transparency and human oversight mechanisms built in by design
- **Human-in-the-loop** — high-stakes predictions (Critical severity) are flagged for human analyst review

---

## Target Use Cases

- **DeFi protocols** — Pre-deployment security audit at a fraction of traditional audit cost
- **African & emerging-market Web3 startups** — Audit access where traditional firms don't operate
- **Security researchers** — Benchmark platform for comparing detection approaches (Slither vs ML vs hybrid)
- **Compliance teams** — Automated audit trail generation for regulatory reporting
- **Smart contract developers** — Real-time feedback during development

---

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas actively seeking contribution:
- Additional Solidity vulnerability test cases
- Dataset expansion (new contract sources)
- Dashboard UI components
- Non-English language support for GenAI reporting

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**Emeka Philian**
AI/ML Engineer · Cybersecurity Specialist · Builder

[![GitHub](https://img.shields.io/badge/GitHub-emekaphilian-181717?style=flat-square&logo=github)](https://github.com/emekaphilian)
[![Hugging Face](https://img.shields.io/badge/🤗%20Hugging%20Face-emekaphilian-FFD21F?style=flat-square)](https://huggingface.co/philian)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat-square&logo=linkedin)](https://linkedin.com/in/emekaogbonna)

---

<div align="center">

*"Most smart contract auditors cost more than most Web3 startups can afford.*
*TrustChainAI is building the infrastructure to change that."*

⭐ Star this repo if you find it useful — it helps with visibility.

</div>

