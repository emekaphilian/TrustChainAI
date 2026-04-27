# 🚀 Quick Reference: What to Do Next

**Current Status**: Phase 2 Ready to Execute  
**Next Action**: Train the Vulnerability Detector Model  
**Time Required**: 15-30 minutes (GPU) / 1-2 hours (CPU)

---

## ⚡ Quick Start Checklist

### ✅ Pre-Training Verification (5 min)

```bash
# 1. Verify datasets exist
ls -la data/Datasets/SolidiFI/dataset.csv
ls -la data/Datasets/SmartBugs/dataset.csv
# Should show files ~5-10MB each

# 2. Verify Python environment
python -c "import torch; print('PyTorch:', torch.__version__); print('GPU:', torch.cuda.is_available())"
python -c "import transformers; print('Transformers:', transformers.__version__)"

# 3. Verify notebook exists
ls -la notebooks/train_vulnerability_detector.ipynb
# Should show recent modification date
```

### 🎯 Execute Training (20-60 min depending on GPU)

```bash
# Method 1: Interactive (recommended - see progress)
cd notebooks
jupyter notebook train_vulnerability_detector.ipynb
# Click "Run All" or Shift+Enter on each cell

# Method 2: Automated (no visualization)
cd notebooks
jupyter nbconvert --to notebook --execute train_vulnerability_detector.ipynb
```

### ✅ Post-Training Verification (5 min)

```bash
# 1. Verify model artifacts were created
ls -la data/models/vulnerability_detector_v1/
# Should show: pytorch_model.bin, config.json, label_map.json, tokenizer.json, etc.

# 2. Check training results
cat data/models/vulnerability_detector_v1/training_config.json | grep -A 5 "training_results"
# Should show: accuracy >80%, f1 >75%

# 3. Note the metrics for your report
```

---

## 📊 What You're About to Do

### Training Process (9 Notebook Cells)

| Cell | Time | What It Does |
|------|------|-------------|
| 1 | 30s | Check GPU, print system info |
| 2 | 5s | Load 10K contracts from CSV |
| 3 | 10s | Map labels, create train/val split |
| 4 | 30s | Load CodeBERT model from HuggingFace |
| 5 | 2min | Tokenize all contracts |
| 6 | 5s | Define evaluation metrics |
| 7 | 5s | Configure training parameters |
| 8 | 15-25min | **MAIN TRAINING** (watch loss decrease) |
| 9 | 2min | Evaluate and save model artifacts |

**Total: 15-30 min (GPU) / 1-2h (CPU)**

### What Gets Produced

```
data/models/vulnerability_detector_v1/
│
├── pytorch_model.bin (250MB)
│   └─ The actual trained model weights
│
├── config.json (1KB)
│   └─ Model architecture and parameters
│
├── training_config.json (5KB)
│   └─ Full training metadata + final metrics
│
├── label_map.json (1KB)
│   └─ Maps class IDs to vulnerability types
│      Example: {
│        "0": "safe",
│        "1": "reentrancy",
│        "2": "overflow",
│        "3": "phishing"
│      }
│
└─ tokenizer files
   └─ JSON, vocab, special tokens
```

---

## 📈 Expected Results

After training completes, you'll see something like:

```
============================================================
STEP 8: TRAINING CONFIGURATION
============================================================
Epochs: 3
Batch size: 8
Learning rate: 2e-5
Output directory: data/models/checkpoints

Estimated training steps: 3000
  Steps per epoch: 1000
  Epochs: 3

✓ Trainer ready

============================================================
STARTING TRAINING
============================================================
Training 8000 contracts on 4 vulnerability classes

[Training Output - watch loss decrease]
Epoch 1/3 [========!              ] loss=0.523 (progress bar)
Epoch 2/3 [==================!    ] loss=0.234
Epoch 3/3 [====================!  ] loss=0.156

============================================================
STEP 7: FINAL EVALUATION & MODEL SAVING
============================================================

✓ Final Metrics (VALIDATION SET)
  accuracy             98.50%
  f1                   85.30%
  precision            87.20%
  recall               83.50%

✓ Saving model to data/models/vulnerability_detector_v1/
  ├─ pytorch_model.bin (weights)
  ├─ config.json (architecture)
  ├─ training_config.json (metadata)
  └─ label_map.json (vulnerability types)

✓ Training Complete!
```

---

## 🔥 If Something Goes Wrong

### Error: "Datasets not found"
```bash
# Re-run dataset preparation
python scripts/prepare_training_data.py
```

### Error: "CUDA out of memory"
```python
# Edit cell 8, reduce batch size:
per_device_train_batch_size=4,  # was 8
per_device_eval_batch_size=4,   # was 8
```

### Error: "Model loading failed"
```bash
# Check internet connection (downloads from HuggingFace)
python -c "from transformers import AutoModel; m = AutoModel.from_pretrained('microsoft/codebert-base')"
```

### Issue: Training is very slow
- Confirm GPU is being used: Cell 1 should show GPU name
- If CPU only: This is normal (~1-2 hours), use GPU machine if possible
- Reduce max_length in cells 5 & 7 from 512 to 256 for speed test

---

## 📚 Documentation Reference

| Question | Document | Section |
|----------|----------|---------|
| How does training work? | docs/TRAINING.md | "Training Process" |
| What's in each cell? | notebooks/README.md | "Cell Overview" |
| What's my overall progress? | PROGRESS.md | "Phase-by-Phase Breakdown" |
| What's the project status? | PROJECT_STATUS.md | "Accomplishments" |
| How do I fix errors? | docs/TRAINING.md | "Troubleshooting" |

---

## ⏱️ Timeline

| Time | Event |
|------|-------|
| Right Now | You are here - ready to execute |
| Next 15-30 min | Execute training notebook |
| After training | Model artifacts created |
| Week 4 (4-6 hrs) | Integrate model into scanner |
| Week 5 (6-8 hrs) | Build Streamlit dashboard |
| Week 6 (4-6 hrs) | Testing & Docker |
| Week 7 (3-4 hrs) | Kubernetes deployment |

**MVP Ready By**: March 20, 2026

---

## 🎓 Key Takeaway

You have:
1. ✅ 10,000 Ethereum contracts prepared
2. ✅ Training notebook with comprehensive comments
3. ✅ All dependencies installed
4. ✅ Clear documentation

**Now you just need to execute the notebook and wait for training to finish.** 

After training, you'll have a trained model that can detect smart contract vulnerabilities. This is the core of your entire project!

---

## 🔗 Related Documents

- **Full Training Guide**: docs/TRAINING.md (250+ lines of detailed explanation)
- **Notebook Guide**: notebooks/README.md (what each cell does)
- **Project Status**: PROJECT_STATUS.md (complete accomplishments)
- **Progress Tracker**: PROGRESS.md (phase-by-phase breakdown)

---

**Ready to train? Open `notebooks/train_vulnerability_detector.ipynb` and run all cells! 🚀**

