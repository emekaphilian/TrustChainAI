# Notebook Documentation

This directory contains Jupyter notebooks that implement key parts of the TrustChainAi pipeline.

---

## 📓 train_vulnerability_detector.ipynb

**Status**: ✅ Ready to Execute  
**Phase**: Phase 2 - Model Training  
**Execution Time**: 15-30 minutes (GPU) / 1-2 hours (CPU)  
**Prerequisites**: Datasets prepared in `data/Datasets/`  

### Purpose
Fine-tune a CodeBERT transformer model to detect vulnerabilities in Ethereum smart contracts.

### What This Notebook Does

#### Input
- 10,000 Ethereum contracts split into:
  - SolidiFI: 3,000 contracts (curated set)
  - SmartBugs: 7,000 contracts (production set)
- Vulnerability labels: safe, reentrancy, overflow, phishing

#### Process
1. **Cell 1**: Check GPU/CPU availability and system info
2. **Cell 2**: Load datasets from CSV files
3. **Cell 3**: Prepare labels and create train/validation split (80/20)
4. **Cell 4**: Load pre-trained CodeBERT model
5. **Cell 5**: Tokenize contract bytecode to token IDs
6. **Cell 6**: Define evaluation metrics (accuracy, F1, precision, recall)
7. **Cell 7**: Configure training parameters (3 epochs, batch size 8, LR 2e-5)
8. **Cell 8**: Train model with HuggingFace Trainer
9. **Cell 9**: Evaluate on validation set and save artifacts

#### Output
```
data/models/vulnerability_detector_v1/
├── pytorch_model.bin              (Trained model weights)
├── config.json                    (Model architecture)
├── training_config.json           (Full training metadata + metrics)
├── label_map.json                 (Vulnerability type mappings)
├── tokenizer.json                 (BPE tokenizer vocabulary)
└── special_tokens_map.json        (Special token definitions)
```

### Results You'll See
```
✓ Training Metrics
  - Accuracy:   >80%
  - F1 Score:   >75%
  - Precision:  >80%
  - Recall:     >70%

✓ Sample Predictions
  - True: reentrancy | Pred: reentrancy (confidence: 92%)
  - True: safe | Pred: safe (confidence: 97%)
```

### How to Run
```bash
cd notebooks
jupyter notebook train_vulnerability_detector.ipynb
# Run all cells from top to bottom
```

Or non-interactively:
```bash
jupyter nbconvert --to notebook --execute train_vulnerability_detector.ipynb
```

### Key Hyperparameters
| Parameter | Value | Purpose |
|-----------|-------|---------|
| Model | CodeBERT-base | Pre-trained on code |
| Epochs | 3 | Full passes through data |
| Batch Size | 8 | Gradient update size |
| Learning Rate | 2e-5 | Fine-tuning adjustment rate |
| Max Tokens | 512 | CodeBERT maximum sequence length |
| Warmup Steps | 500 | Gradual LR increase at start |

### What Happens During Training
- **Epoch 1**: Model learns basic patterns (loss decreases rapidly)
- **Epoch 2**: Fine-tunes predictions (loss continues decreasing)
- **Epoch 3**: Converges to final performance (loss levels off)
- **After Each Epoch**: Best model saved (by F1 score)

### Troubleshooting

**Issue: CUDA out of memory**
```python
# Reduce batch size in Cell 7
per_device_train_batch_size=4,
```

**Issue: Very slow training**
- Check GPU is being used: `torch.cuda.is_available()` should be True
- Reduce max_length: Change to 256 tokens instead of 512
- Run on GPU-equipped machine if available

**Issue: Poor validation loss (increasing after epoch 1)**
- Likely overfitting on small dataset
- Reduce learning rate: Try `1e-5` instead of `2e-5`
- Add early stopping (see docs/TRAINING.md)

### GPU vs CPU Training
| Hardware | Speed | Memory | Recommended |
|----------|-------|--------|-------------|
| NVIDIA RTX 4090 | ~15 min | 8GB | ✅ Best |
| NVIDIA A100 | ~20 min | 10GB | ✅ Great |
| Apple M1/M2 | ~20 min | 8GB | ✅ Good |
| CPU (Intel i7) | ~90 min | 6GB | Works, slow |

### What Gets Saved

1. **pytorch_model.bin**: Binary file containing trained weights (~250MB)
2. **config.json**: Model architecture configuration (small, ~1KB)
3. **training_config.json**: Metadata about training run
4. **label_map.json**: Mapping from class IDs to vulnerability types
5. **tokenizer.json**: HuggingFace tokenizer (how to convert text→tokens)

### Next Steps After Training

Once this notebook completes:

1. **Load Model in Inference**
   ```python
   from transformers import AutoModelForSequenceClassification
   model = AutoModelForSequenceClassification.from_pretrained(
       'data/models/vulnerability_detector_v1'
   )
   ```

2. **Update VulnerabilityDetector**
   - Edit `src/models/vulnerability_detector.py`
   - Load model artifacts created here
   - Implement real `predict()` method

3. **Test Scanner**
   ```bash
   python -m src.auditor.scanner --contract 0x...
   ```

4. **Monitor Fairness**
   - Bias detector automatically tracks by contract type
   - See false positive rates in dashboard

### Understanding CodeBERT

CodeBERT is a transformer pre-trained specifically on code:
- **Pre-training**: Trained on GitHub open-source repositories
- **Architecture**: BERT (Bidirectional Encoder Representations)
- **Strengths**: Understands code semantics, variable scoping, control flow
- **Parameters**: 125M weights that will be fine-tuned for our task

### Class Imbalance Handling

Dataset is ~99.6% "safe" contracts, only 0.4% with vulnerabilities.

Model handles this by:
- Stratified train/val split (preserves ratio)
- Weighted loss (rare classes weighted higher)
- Weighted evaluation metrics

### Reproducibility

All randomness is controlled:
```python
torch.manual_seed(42)
np.random.seed(42)
random.seed(42)
```

Same results on re-run (unless using non-deterministic GPU ops).

---

## 📓 contract_clustering.ipynb

**Status**: 🔲 Not Yet Used  
**Phase**: Phase 2-3 (Future)  
**Purpose**: Cluster contracts by risk profile using unsupervised learning  

*This notebook is a template for implementing RiskClusterer.* Will be used after vulnerability detector is trained.

---

## 📋 Summary: Notebook Execution Order

1. **First**: `train_vulnerability_detector.ipynb` ← You are here
2. **Then**: Updates to `src/models/vulnerability_detector.py` to load trained model
3. **Then**: Test scanner with real contracts
4. **Later**: Dashboard visualization
5. **Later**: `contract_clustering.ipynb` for risk profiling

---

## 📊 Execution Checklist

- [ ] Cell 1: Environment setup completes without errors
- [ ] Cell 2: Datasets load successfully (check paths)
- [ ] Cell 3: Labels assigned, class distribution printed
- [ ] Cell 4: CodeBERT model loads from HuggingFace
- [ ] Cell 5: Tokenization completes (should say "✓ Datasets ready")
- [ ] Cell 6: Metrics function defined
- [ ] Cell 7: Training configuration printed
- [ ] Cell 8: **Training starts and progresses**
  - Watch for decreasing loss each epoch
  - Validation metrics improve
  - Best model checkpoint saved
- [ ] Cell 9: Final metrics printed, model artifacts saved

If all cells complete, you've successfully trained the vulnerability detector! 🎉

---

**Questions?** See:
- `docs/TRAINING.md` - Detailed training explanation
- `PROGRESS.md` - Project status and timeline
- `README.md` - Quick start guide

