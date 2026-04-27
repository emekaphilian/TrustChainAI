# Contributing to TrustChainAi

We welcome contributions! Please follow these guidelines.

## Development Setup

```bash
git clone https://github.com/yourusername/trustchainai.git
cd trustchainai
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Code Standards

### Style & Formatting
- **Black**: Format with `black src/ tests/ --line-length=100`
- **Flake8**: Lint with `flake8 src/ tests/`
- **Type Hints**: All functions must have type hints
- **Docstrings**: Google-style for all public methods/classes

### Example Function
```python
def validate_contract_address(address: str) -> bool:
    """Validates Ethereum contract address format.
    
    Args:
        address: Hex string, optionally with 0x prefix.
        
    Returns:
        True if valid checksummed address, False otherwise.
        
    Raises:
        ValueError: If address is not a valid Ethereum address.
    """
    if not address.startswith('0x'):
        address = '0x' + address
    
    return Web3.is_address(address)
```

## Testing

```bash
# Run all tests with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_auditor.py -v

# Run with specific test pattern
pytest tests/ -k "test_bias_detection" -v
```

**Critical Coverage Areas:**
- `src/auditor/`: Mock Web3 calls, handle address validation
- `src/models/`: Test inference, bias computation with synthetic data
- `src/dashboard/`: Streamlit component rendering
- `src/utils/`: RPC error handling, rate limiting

## Git Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit with clear messages: `git commit -m "Add bias detection for DEX contracts"`
3. Push: `git push origin feature/your-feature`
4. Create Pull Request with description linking to issue
5. Ensure CI passes before merge

## Pull Request Checklist

- [ ] Code passes `black`, `flake8`, `mypy`
- [ ] All tests pass: `pytest --cov=src`
- [ ] Added tests for new functionality
- [ ] Updated docstrings if modifying public APIs
- [ ] Updated `docs/` if adding major features
- [ ] Bias implications reviewed (if adding new detectors)

## Reporting Issues

Include:
1. **Minimal reproduction**: Code snippet or contract address
2. **Expected behavior**: What should happen
3. **Actual behavior**: What's happening
4. **Environment**: Python version, OS, dependencies

## Maintainers

- Lead: [Your Name] (@github-username)
- Ethics Review: [Team Member]
- DevOps: [Team Member]

---

**Questions?** Open an issue or check existing discussions.
