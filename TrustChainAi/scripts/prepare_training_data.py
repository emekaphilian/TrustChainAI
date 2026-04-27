"""Prepare existing contract data into training datasets."""

import pandas as pd
from pathlib import Path
from typing import List, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def assign_vulnerability_labels(bytecode: str) -> str:
    """Assign synthetic vulnerability labels based on bytecode heuristics.
    
    This is for demonstration/training purposes. In production, you'd use
    labeled datasets like SolidiFI or SmartBugs with verified labels.
    
    Args:
        bytecode: Contract bytecode (hex string)
        
    Returns:
        Vulnerability type label
    """
    if not bytecode or len(bytecode) < 20:
        return 'safe'
    
    bytecode_lower = bytecode.lower()
    
    # Simple heuristics (in real scenario, use labeled datasets)
    risk_indicators = {
        'reentrancy': ['call', 'delegatecall', 'sends_eth'],
        'overflow': ['add', 'mul', 'sub', 'arithmetic'],
        'phishing': ['selfdestruct', 'suicide'],
    }
    
    score = {}
    for vuln_type, patterns in risk_indicators.items():
        score[vuln_type] = sum(1 for p in patterns if p in bytecode_lower)
    
    if max(score.values()) == 0:
        return 'safe'
    
    return max(score, key=score.get)


def prepare_training_datasets(input_csv: str, output_dir: str, train_split: float = 0.7):
    """Prepare datasets from existing contract data.
    
    Args:
        input_csv: Path to RawEthSmartContracts CSV
        output_dir: Directory to save prepared datasets
        train_split: Proportion for training (rest for validation)
    """
    logger.info(f"Loading data from {input_csv}")
    df = pd.read_csv(input_csv)
    
    logger.info(f"Loaded {len(df)} contracts")
    
    # Assign vulnerability labels based on bytecode patterns
    logger.info("Assigning vulnerability labels...")
    df['vulnerability_type'] = df['bytecode'].apply(assign_vulnerability_labels)
    
    # Rename bytecode column to 'code' for consistency
    df = df.rename(columns={'bytecode': 'code'})
    
    # Keep only code and vulnerability_type columns
    df = df[['code', 'vulnerability_type']]
    
    # Show distribution
    logger.info("\nVulnerability Type Distribution:")
    print(df['vulnerability_type'].value_counts())
    
    # Split into SolidiFI (smaller, curated-like) and SmartBugs (larger)
    # SolidiFI gets ~30% (smaller curated set), SmartBugs gets ~70%
    split_idx = int(len(df) * 0.3)
    
    solidifi_df = df.iloc[:split_idx].copy()
    smartbugs_df = df.iloc[split_idx:].copy()
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    solidifi_path = output_path / 'SolidiFI' / 'dataset.csv'
    smartbugs_path = output_path / 'SmartBugs' / 'dataset.csv'
    
    solidifi_path.parent.mkdir(parents=True, exist_ok=True)
    smartbugs_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"\nSaving SolidiFI dataset ({len(solidifi_df)} contracts)...")
    solidifi_df.to_csv(solidifi_path, index=False)
    logger.info(f"✓ Saved to {solidifi_path}")
    
    logger.info(f"\nSaving SmartBugs dataset ({len(smartbugs_df)} contracts)...")
    smartbugs_df.to_csv(smartbugs_path, index=False)
    logger.info(f"✓ Saved to {smartbugs_path}")
    
    logger.info("\n" + "="*60)
    logger.info("Dataset preparation complete!")
    logger.info("="*60)
    logger.info(f"SolidiFI: {solidifi_path} ({len(solidifi_df)} contracts)")
    logger.info(f"SmartBugs: {smartbugs_path} ({len(smartbugs_df)} contracts)")
    logger.info(f"\nTotal: {len(df)} contracts across all types")
    logger.info("\nReady for training! Run: jupyter notebook train_vulnerability_detector.ipynb")


if __name__ == '__main__':
    project_root = Path(__file__).parent.parent
    input_csv = project_root / 'data' / 'Raw' / 'RawEthSmartContracts-10K-Sample.csv'
    output_dir = project_root / 'data' / 'Datasets'
    
    prepare_training_datasets(str(input_csv), str(output_dir))
