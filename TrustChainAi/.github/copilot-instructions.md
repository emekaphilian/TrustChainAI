# TrustChainAi Copilot Instructions

AI coding agents working on TrustChainAi should understand this architecture, conventions, and workflows to contribute effectively. Focus on the overlap between ML security and AI ethics.

## 🏗️ Architecture Overview

**Three-Tier Design:**
1. **Auditor (Blockchain Layer)**: `src/auditor/` - Retrieves contract code via Web3.py with multi-RPC fallback, invokes LLM scanning
2. **Models (ML Layer)**: `src/models/` - In-process Transformers inference, PyTorch clustering, lightweight bias detection per-scan
3. **Dashboard (UI Layer)**: `src/dashboard/` - Streamlit app exposing results + per-prediction SHAP/LIME explainability

**Data Flow:**
```
Ethereum RPC (Infura → Alchemy fallback) → Web3.py retrieval → Auditor (scanner) → Transformers (vulnerability detection)
                                                                                    ↓
                                                            Models (clustering + bias detection on every scan)
                                                                                    ↓
                                                            Dashboard (visualization + fairness metrics)
                                                                                    ↓
                                                       SHAP/LIME (per-prediction explanation)
```

**Why This Structure:** Separates concerns - auditor handles blockchain I/O with resilience, models encapsulate ML logic in-process, dashboard is presentation layer. Easy to test and deploy each independently.

**Portfolio Strategy:**
- **Bias Detection**: Runs on every scan (not batch-only) to showcase fairness integration. Lightweight (FPR per contract type + SHAP importances).
- **Model Serving**: In-process Python (no TorchServe/FastAPI yet) for simplicity. Future docs mention microservices as "scalable extension."
- **Deployment**: Docker + local Kubernetes (kind/minikube) for demo. Cloud-ready architecture but credits-free.
- **RPC Resilience**: Multi-provider fallback (Infura → Alchemy) shows reliability thinking.

## 📦 Key Modules & Patterns

### Auditor Module (`src/auditor/`)
- **Purpose**: Interface with Ethereum via multi-RPC provider fallback, retrieve contracts, orchestrate scans
- **Key Class**: `ContractScanner` - orchestrates multi-RPC calls and passes contracts to models
- **Pattern**: Synchronous scanning with batching, RPC calls use fallback (Infura → Alchemy)
- **Example**: `auditor/scanner.py` should validate contract addresses before web3 calls
- **Resilience**: If primary RPC fails, automatically tries secondary provider (see `RpcManager.get_code_with_fallback()`)

### Models Module (`src/models/`)
- **Purpose**: ML inference - vulnerability detection, clustering, fairness assessment
- **VulnerabilityDetector**: Uses fine-tuned Transformers to detect patterns (reentrancy, overflow, phishing)
- **RiskClusterer**: Unsupervised clustering (PyTorch) groups contracts by risk profile
- **BiasDetector**: Runs on every scan, analyzes false positive distributions by contract type (FPR metric)
- **Model Serving**: In-process Python (Transformers loaded directly), no external ML service needed
- **Pattern**: All models inherit `BaseModel` (in `src/models/base.py`) with `.predict()` and `.explain()` methods
- **Critical Invariant**: Bias detection runs *after* vulnerability detection to assess fairness; lightweight (SHAP importance + FPR tracking)

### Dashboard (`src/dashboard/`)
- **Purpose**: Interactive Streamlit UI for results, explainability, bias metrics
- **Structure**: `app.py` (main entry), `pages/` (multi-page app), `components/` (reusable widgets)
- **Pattern**: Streamlit session state holds cached model predictions to avoid re-running expensive inference
- **SHAP Integration**: `components/explainer.py` generates per-prediction explanations
- **Ethics Display**: `pages/bias_metrics.py` shows fairness metrics - false positive rate by contract type

### Utils (`src/utils/`)
- **web3_helper.py**: Wrapper around Web3.py - address validation, ABI fetching, multi-RPC fallback with retry logic
- **logging.py**: Structured logging with audit trail (who ran scan, what contracts, when, why flags)
- **config.py**: Centralized config (model paths, RPC endpoints, thresholds) - source from `.env`

### Config (`src/config/`)
- **rpc_config.py**: RPC provider configuration with fallback chain (Infura → Alchemy)
- **model_config.py**: Model hyperparameters and dataset sources (SolidiFI, SmartBugs, Mythril)
- **bias_config.py**: Fairness monitoring configuration for per-scan bias detection

## 🔄 Critical Development Workflows

### Running the Full Pipeline
```bash
# 1. Scan specific contract
python -m src.auditor.scanner --contract 0xABC123 --model-path data/models/detector.pth

# 2. Launch dashboard (displays cached results)
streamlit run src/dashboard/app.py

# 3. View bias metrics in dashboard -> Bias Analytics tab
```

### Model Training/Fine-tuning
- Training scripts in `scripts/train_vulnerability_detector.py`
- **Primary Datasets**: SolidiFI + SmartBugs (well-known academic datasets for smart contract vulnerabilities)
- **Synthetic Augmentation**: Use Mythril locally to generate symbolic execution traces for contract samples
- Output: `data/models/detector.pth` + tokenizer
- **Important**: Update `src/models/config.yaml` with new model metrics (accuracy, false positive rate by type)

### Adding a New Vulnerability Pattern
1. New detector class in `src/models/detectors/` inheriting `BaseDetector`
2. Update `RiskAssessment` enum in `src/models/enums.py`
3. Wire into `VulnerabilityDetector.detect()` pipeline
4. Add test case in `tests/test_detectors.py`
5. Bias checker automatically tracks this detector's fairness

### Bias Analysis
- Run: `python -m src.models.bias_analyzer --results-file results.json`
- Outputs: false positive rate by contract type, statistical fairness metrics
- Flag: If false positive rate diff >10% across types → alert in dashboard

## 🎯 Code Conventions & Patterns

### Python Style
- Black formatting (80 char line length)
- Type hints required for function signatures
- Docstrings: Google style (see `src/auditor/scanner.py` example)

### Architectural Decisions & Rationale

**1. Bias Detection (Per-Scan)**
- Runs lightweight fairness checks on every contract scan (not batch-only)
- Portfolio advantage: Fairness as first-class feature, not afterthought
- Metrics: FPR by contract type, SHAP feature importance per prediction
- Config: `src/config/bias_config.py`

**2. Model Serving (In-Process)**
- Models loaded directly in Python (no TorchServe/FastAPI required)
- Simplifies demo and iteration; faster feedback loop
- Future: Document microservices as scalable extension
- Base class: `src/models/base.py` with `.predict()` and `.explain()` methods

**3. Datasets (SolidiFI + SmartBugs + Mythril)**
- Academic benchmarks ensure research credibility
- Mythril augmentation shows initiative and understanding of formal methods
- Config: `src/config/model_config.py` documents sources and citations
- Setup: See `docs/DATASETS.md` for download and preparation

**4. RPC Resilience (Multi-Provider Fallback)**
- Try Infura first, fall back to Alchemy (easily extensible)
- Demonstrates production reliability thinking
- Implementation: `src/utils/web3_helper.py` RpcManager class
- Config: `src/config/rpc_config.py` provider definitions

**5. Deployment (Docker + Local Kubernetes)**
- Demo on local cluster (kind/minikube) with zero cloud costs
- Manifests work unchanged on AWS/GCP/Azure (provider-agnostic)
- Setup: `docs/KUBERNETES.md` for local deployment instructions
- Portfolio message: Understands orchestration and cloud-ready architecture

**→ See `docs/PORTFOLIO_STRATEGY.md` for detailed rationale and interview talking points**

### ML Model Pattern
```python
class MyModel(BaseModel):
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model = self._load_model()
    
    def predict(self, input_data) -> Prediction:
        """Return Prediction with confidence & explanation_tokens"""
        pass
    
    def explain(self, prediction: Prediction) -> ExplanationResult:
        """Return SHAP/LIME explanation"""
        pass
```

### Async Contract Processing
- Use `asyncio` for batch RPC calls to avoid blocking
- Rate-limit to 100 RPC calls/sec per endpoint specs
- Log all RPC failures with retry logic

### Bias Tracking
- Every prediction includes `contract_type` field (flagged by heuristics: DEX, Lending, NFT, etc.)
- BiasDetector stores prediction samples per type
- False positive rate computed after ≥100 samples per type

## 🧪 Testing Strategy

**Directory**: `tests/` mirrors `src/`
- `test_auditor.py`: Mock Web3.py, test scanner logic
- `test_models.py`: Load small model checkpoint, test inference pipeline
- `test_dashboard.py`: Streamlit testing via `streamlit.testing.v1`
- Run: `pytest --cov=src tests/`

**Critical Tests:**
- Bias detector catches fairness issues (test with synthetic imbalanced data)
- Scanner handles invalid addresses gracefully
- Dashboard updates when new results arrive

## 📊 Key Data Structures

### Prediction (from `src/models/types.py`)
```python
@dataclass
class Prediction:
    contract_address: str
    vulnerabilities: List[Vulnerability]  # List of detected issues
    risk_score: float  # 0-1
    contract_type: str  # Inferred: DEX, Lending, etc.
    confidence: float
    explanation_tokens: List[str]  # For SHAP
```

### Vulnerability
```python
@dataclass
class Vulnerability:
    type: str  # "reentrancy", "overflow", "phishing_pattern"
    severity: str  # "critical", "high", "medium", "low"
    line_number: Optional[int]  # If available
    description: str
```

## 🔌 Integration Points

### Web3.py → RPC
- Endpoint config: `WEB3_RPC_ENDPOINT` (primary) and `WEB3_RPC_FALLBACK` (secondary) env vars
- Primary: Infura `https://mainnet.infura.io/v3/YOUR_KEY`
- Fallback: Alchemy `https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY`
- Queries: `eth_getCode()` for contract bytecode, `eth_getStorageAt()` for state
- Retry Logic: If primary fails, automatically try fallback. Max 3 retries with exponential backoff (1s → 2s → 4s)
- Caching: Store recently fetched contracts in SQLite to reduce RPC calls (cache expiry: 24h)

### Transformers → Model Inference
- Model hosted: `data/models/vulnerability_detector_v1.pth`
- Tokenizer: `data/models/tokenizer.json` (HuggingFace format)
- Inference device: GPU if available, CPU fallback
- Batch size: 32 (tunable in config)

### Streamlit ↔ Cache
- Results cached in `data/cache/predictions.db` (SQLite)
- Expiry: 7 days (configurable)
- Invalidate on model version change

## ⚠️ Common Pitfalls & How to Avoid

1. **Infinite retries on RPC failures**: Set max_retries=3, exponential backoff (1s → 8s)
2. **Logging raw contract code**: Always sanitize logs, only store code hashes
3. **Bias detector with too few samples**: Skip fairness metrics until ≥50 samples per type
4. **Dashboard slowness**: Use Streamlit `@st.cache_data` on expensive operations, set TTL
5. **Model drift**: Retrain detector quarterly on new vulnerability datasets, compare metrics

## 🚀 Deployment Checklist

- [ ] All tests pass: `pytest --cov=src tests/`
- [ ] Black + mypy pass: `black src/ && mypy src/`
- [ ] Docker build succeeds: `docker build -t trustchainai:latest .`
- [ ] K8s manifests validated: `kubectl apply --dry-run=client -f kubernetes/`
- [ ] Environment variables documented in `.env.example`
- [ ] Model artifacts versioned in `data/models/` with README
- [ ] Bias metrics baseline recorded (for future regression detection)
- [ ] Local K8s demo tested: `kind create cluster && kubectl apply -f kubernetes/ && kubectl port-forward svc/trustchainai-dashboard 8501:80`

## 📚 Key Files to Review First

1. [docs/PORTFOLIO_STRATEGY.md](../docs/PORTFOLIO_STRATEGY.md) - **KEY**: Explains "why" behind every architectural decision
2. [README.md](../README.md) - Project overview
3. [src/auditor/scanner.py](../src/auditor/scanner.py) - Entry point
4. [src/models/vulnerability_detector.py](../src/models/vulnerability_detector.py) - Core ML
5. [src/models/bias_detector.py](../src/models/bias_detector.py) - Ethics logic
6. [src/dashboard/app.py](../src/dashboard/app.py) - UI structure

---

**Last Updated**: March 2026 | **Maintainers**: [Your Team]
