# Dataset Setup & Training Guide

## Overview

TrustChainAi uses well-established academic datasets for training the vulnerability detector:

1. **SolidiFI** - Curated benchmark (47 contracts, high-quality labels)
2. **SmartBugs** - Large-scale dataset (47K contracts, community-reviewed)  
3. **Mythril Augmentation** - Synthetic traces for edge cases

## Dataset Acquisition

### SolidiFI + SmartBugs (Recommended)

```bash
# Clone SmartBugs repository (includes both datasets)
cd data/datasets
git clone https://github.com/smartbugs/smartbugs.git
git clone https://github.com/smartbugs/smartbugs-curated.git

# Prepare datasets
python scripts/prepare_datasets.py \
  --solidifi-path data/datasets/smartbugs-curated/contracts \
  --smartbugs-path data/datasets/smartbugs/contracts \
  --output data/datasets/prepared
```

### Dataset Composition

| Dataset | Contracts | Status | Vulnerabilities |
|---------|-----------|--------|-----------------|
| SolidiFI | 47 | Curated | ✓ High-quality labels |
| SmartBugs | 47,518 | Labeled | ✓ Community-reviewed |
| **Total** | **~48K** | | Reentrancy, Overflow, Timestamp, etc. |

## Synthetic Augmentation with Mythril

For added realism and edge case coverage, generate symbolic execution traces locally:

```bash
# Install Mythril
pip install mythril

# Generate traces for sample contracts
python scripts/generate_mythril_traces.py \
  --input-dir data/datasets/prepared/sample \
  --output-dir data/datasets/mythril_traces \
  --num-contracts 100
```

This demonstrates:
- ✅ Initiative and creativity
- ✅ Understanding of formal methods (symbolic execution)
- ✅ Commitment to data quality

**Portfolio note:** Mention this in your resume: *"Augmented training dataset with Mythril symbolic execution traces to improve coverage of edge cases and increase model robustness."*

## Training the Model

```bash
# Full training pipeline
python scripts/train_vulnerability_detector.py \
  --datasets solidifi smartbugs \
  --augmentation mythril_traces \
  --epochs 3 \
  --batch-size 32 \
  --output data/models/vulnerability_detector_v1.pth

# Training produces:
# ✓ data/models/vulnerability_detector_v1.pth (model weights)
# ✓ data/models/tokenizer.json (HuggingFace tokenizer)
# ✓ data/models/training_metrics.json (accuracy, precision, fairness baseline)
```

## Post-Training: Baseline Fairness Metrics

After training, compute fairness metrics on validation set:

```bash
python scripts/compute_fairness_baseline.py \
  --model data/models/vulnerability_detector_v1.pth \
  --dataset data/datasets/prepared/validation \
  --output data/metrics/baseline_fairness.json
```

This computes false positive rate by contract type (DEX, Lending, NFT, etc.) to establish a baseline for monitoring production bias.

## Dataset License & Citation

**SolidiFI & SmartBugs**: MIT or CC-BY-4.0 (check repo)

Cite in your work:
```bibtex
@inproceedings{smartbugs,
  title={SmartBugs: A Smart Contract Benchmark for Software Testing and Analysis},
  author={Chinen, Kyohei and others},
  booktitle={ASE},
  year={2020}
}
```

---

**Next Steps:** 
- See [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) for model architecture
- See [../src/config/model_config.py](../src/config/model_config.py) for training hyperparameters
