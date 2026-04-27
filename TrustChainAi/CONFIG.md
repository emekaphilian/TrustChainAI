# Project Configuration

## Environment Variables

```bash
# Blockchain RPC
WEB3_RPC_ENDPOINT=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
WEB3_RATE_LIMIT=100  # RPC calls per second

# Model Configuration
MODEL_PATH=data/models/vulnerability_detector_v1.pth
TOKENIZER_PATH=data/models/tokenizer.json
DEVICE=cuda  # or 'cpu'
BATCH_SIZE=32

# Bias Detection
FAIRNESS_THRESHOLD=0.10  # Flag if false positive rate diff > 10%
MIN_SAMPLES_PER_TYPE=50  # Minimum samples before reporting fairness metrics

# Dashboard
STREAMLIT_PORT=8501
CACHE_EXPIRY_DAYS=7

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/trustchainai.log
AUDIT_LOG_FILE=logs/audit.log
```

See `.env.example` for all available options.

## Configuration Files

- `config/models.yaml` - Model paths, versions, hyperparameters
- `config/thresholds.yaml` - Risk scoring thresholds, severity cutoffs
- `config/blockchain.yaml` - RPC endpoints, contract type heuristics
