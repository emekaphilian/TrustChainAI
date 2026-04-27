"""Model configuration including dataset sources and training parameters."""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class DatasetSource:
    """Reference to a training dataset."""
    name: str
    description: str
    source_url: str
    paper_citation: str
    samples: int
    vulnerability_types: List[str]


# Core academic datasets
DATASET_SOLIDIFI = DatasetSource(
    name="SolidiFI",
    description="Large-scale dataset of real smart contracts with vulnerability labels",
    source_url="https://github.com/smartbugs/smartbugs-curated",
    paper_citation="Ferreira et al., SolidiFI: Solidity Fuzzing Harness Integrated",
    samples=47,  # Curated subset
    vulnerability_types=["reentrancy", "overflow", "underflow", "delegatecall", "timestamp"]
)

DATASET_SMARTBUGS = DatasetSource(
    name="SmartBugs",
    description="Academic benchmark for smart contract vulnerability detection",
    source_url="https://github.com/smartbugs/smartbugs",
    paper_citation="Chinen et al., SmartBugs: A Smart Contract Benchmark for Software Testing and Analysis",
    samples=47000,
    vulnerability_types=["reentrancy", "overflow", "underflow", "delegatecall", "timestamp", "gas"]
)

# Synthetic augmentation via Mythril
SYNTHETIC_MYTHRIL = DatasetSource(
    name="Mythril Augmentation",
    description="Symbolic execution traces generated locally to augment real contract samples",
    source_url="https://github.com/ConsenSys/mythril",
    paper_citation="Mueller et al., Mythril: Ethereum Smart Contract Semantics-Based Symbolic Execution",
    samples=1000,  # Approximate synthetic samples per training run
    vulnerability_types=["reentrancy", "overflow", "underflow", "delegatecall", "assertion_failure"]
)

# Recommended training pipeline
TRAINING_DATASETS = [DATASET_SOLIDIFI, DATASET_SMARTBUGS]
AUGMENTATION_DATASETS = [SYNTHETIC_MYTHRIL]

# Model configuration
MODEL_CONFIG = {
    "model_name": "distilbert-base-uncased",
    "tokenizer_max_length": 512,
    "batch_size": 32,
    "learning_rate": 2e-5,
    "num_epochs": 3,
    "warmup_steps": 500,
    "weight_decay": 0.01,
    "device": "cuda",  # Override with 'cpu' if no GPU
    "output_dir": "data/models",
    "model_file": "vulnerability_detector_v1.pth",
    "tokenizer_file": "tokenizer.json",
}

# Vulnerability types supported
VULNERABILITY_TYPES = [
    "reentrancy",
    "overflow",
    "underflow",
    "delegatecall",
    "timestamp_manipulation",
    "gas_limit",
    "phishing_pattern",
    "access_control",
    "division_by_zero",
]

# Severity levels
SEVERITY_LEVELS = {
    "critical": 0.9,  # Risk score threshold
    "high": 0.7,
    "medium": 0.5,
    "low": 0.3,
}
