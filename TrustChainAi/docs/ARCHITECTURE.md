# Architecture Deep Dive

## System Design Principles

1. **Separation of Concerns**: Auditor (I/O), Models (Logic), Dashboard (Presentation)
2. **Async-First**: Use asyncio for RPC calls to handle rate limiting
3. **Explainability Required**: Every prediction includes explanation tokens
4. **Fairness Monitoring**: Bias metrics computed continuously, not after deployment
5. **No Raw Code Logging**: Always sanitize or hash contract code in logs

## Component Deep Dive

### Auditor Layer (`src/auditor/`)

**Purpose**: Blockchain interaction and contract retrieval.

**Key Classes:**
- `ContractScanner`: Orchestrates Web3 calls and model invocation
- `RpcManager`: Rate-limited Ethereum RPC wrapper with retry logic
- `ContractFetcher`: Retrieves bytecode, ABI, transaction history

**Async Flow:**
```python
# Process 1000 contracts concurrently
tasks = [scanner.scan_contract(addr) for addr in addresses]
results = await asyncio.gather(*tasks)
```

**Rate Limiting Example:**
```python
# 100 RPC calls/sec max
rate_limiter = RateLimiter(calls_per_second=100)
async with rate_limiter:
    code = await web3.eth.get_code(address)
```

### Models Layer (`src/models/`)

**Purpose**: ML inference, clustering, fairness assessment.

**Data Flow:**
```
Raw Bytecode
    ↓
Tokenizer (HuggingFace)
    ↓
VulnerabilityDetector (Transformers)
    ↓ (vulnerabilities + risk_score)
RiskClusterer (PyTorch) → Groups by profile
    ↓
BiasDetector → Analyzes fairness
    ↓
Prediction + ExplanationResult
```

**VulnerabilityDetector**:
- Loads fine-tuned Transformers model
- Input: Solidity code tokens
- Output: List of detected vulnerabilities with confidence scores
- Pattern matching for: reentrancy, overflow, phishing

**RiskClusterer**:
- Unsupervised PyTorch clustering
- Groups contracts by: risk_score, vulnerability profile, code complexity
- Outputs: cluster assignment, distance to centroid

**BiasDetector**:
- Runs as post-processing step
- Input: List of Prediction objects
- Tracks: false positive rate by contract_type
- Flags: If FPR diff > 10% across types
- **Critical**: Only reports fairness stats after ≥50 samples per type

### Dashboard Layer (`src/dashboard/`)

**Purpose**: Interactive visualization and explainability UI.

**Key Files:**
- `app.py`: Main Streamlit entry point, session state management
- `pages/results.py`: Detection results, vulnerability list
- `pages/bias_metrics.py`: Fairness dashboard, FPR by contract type
- `components/explainer.py`: SHAP/LIME visualization
- `cache.py`: Prediction caching (SQLite, 7-day expiry)

**Streamlit Patterns:**
```python
@st.cache_data(ttl=3600)
def load_predictions():
    """Expensive operation cached for 1 hour"""
    return db.fetch_recent_predictions()

# Session state for form persistence
if 'contract_address' not in st.session_state:
    st.session_state.contract_address = ""
```

## Data Structures & Enums

### Prediction
```python
@dataclass
class Prediction:
    contract_address: str
    vulnerabilities: List[Vulnerability]
    risk_score: float  # 0.0-1.0
    contract_type: str  # "DEX", "Lending", "NFT", "Privacy", "Other"
    confidence: float  # 0.0-1.0
    explanation_tokens: List[str]  # For SHAP
    cluster_id: Optional[int]
```

### Vulnerability
```python
@dataclass
class Vulnerability:
    type: str  # "reentrancy", "overflow", "div_by_zero", "phishing_pattern"
    severity: str  # "critical", "high", "medium", "low"
    line_number: Optional[int]
    description: str
    confidence: float
```

### ContractType (Auto-Detection)
- **DEX**: Swap, liquidity pool, router patterns
- **Lending**: Collateral, borrow, interest logic
- **NFT**: mint, burn, transfer ERC721/ERC1155
- **Privacy**: Mixer, relayer, anonymity patterns
- **Other**: No clear classification

## External Integration Points

### Web3.py ↔ Ethereum RPC
```python
# Fetch bytecode
code = await web3.eth.get_code(checksummed_address)

# Fetch storage (for stateful analysis)
value = await web3.eth.get_storage_at(address, position, block)

# Rate limit: 100 calls/sec max
```

### Transformers ↔ Model Serving
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("data/models/tokenizer.json")
model = AutoModelForSequenceClassification.from_pretrained("data/models/vulnerability_detector_v1.pth")

# Batch inference
outputs = model(**tokenizer(bytecode, return_tensors="pt", max_length=512))
```

### SHAP ↔ Explainability
```python
import shap

explainer = shap.Explainer(model, tokenized_code)
shap_values = explainer(test_input)
# visualize in dashboard
```

## Error Handling & Resilience

### RPC Failures
```python
# Exponential backoff: 1s → 2s → 4s → 8s → fail
max_retries = 3
backoff_factor = 2
```

### Model Loading
```python
# Fallback to CPU if GPU unavailable
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
```

### Bias Detection
```python
# Only report fairness metrics after threshold samples
if samples_per_type < MIN_SAMPLES_PER_TYPE:
    return "Insufficient data for fairness assessment"
```

## Performance Considerations

| Operation | Typical Latency | Notes |
|-----------|-----------------|-------|
| Fetch bytecode (RPC) | 100-500ms | Rate limited to 100 calls/sec |
| Tokenize + inference | 50-200ms | GPU ≈10x faster than CPU |
| Clustering (100 contracts) | 200-500ms | PyTorch batch operation |
| SHAP explanation | 500ms-5s | Per-prediction, cacheable |
| Dashboard load | <2s | Streamlit caching essential |

---

See [../README.md](../README.md) for higher-level overview.
