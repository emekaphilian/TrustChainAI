"""Script to download and prepare SolidiFI + SmartBugs datasets for training."""

import os
import json
import csv
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def clone_repository(repo_url: str, target_dir: str, force: bool = False) -> bool:
    """Clone a GitHub repository.
    
    Args:
        repo_url: GitHub repository URL
        target_dir: Target directory for clone
        force: Force re-clone if directory exists
        
    Returns:
        True if successful
    """
    target_path = Path(target_dir)
    
    if target_path.exists() and force:
        logger.info(f"Removing existing {target_dir}")
        subprocess.run(['git', 'stash'], cwd=target_dir, capture_output=True)
        subprocess.run(['git', 'pull'], cwd=target_dir, capture_output=True)
        return True
    elif target_path.exists():
        logger.info(f"Directory {target_dir} already exists, skipping clone")
        return True
    
    logger.info(f"Cloning {repo_url} to {target_dir}")
    result = subprocess.run(
        ['git', 'clone', repo_url, str(target_path)],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        logger.error(f"Failed to clone: {result.stderr}")
        return False
    
    logger.info(f"Successfully cloned to {target_dir}")
    return True


def parse_solidifi_contracts(solidifi_dir: str) -> List[Tuple[str, str]]:
    """Parse SolidiFI (smartbugs-curated) contracts and labels.
    
    Args:
        solidifi_dir: Path to smartbugs-curated/contracts directory
        
    Returns:
        List of (contract_code, vulnerability_type) tuples
    """
    logger.info(f"Parsing SolidiFI contracts from {solidifi_dir}")
    contracts = []
    solidifi_path = Path(solidifi_dir)
    
    if not solidifi_path.exists():
        logger.warning(f"SolidiFI directory not found: {solidifi_dir}")
        return contracts
    
    # Look for JSON metadata files with vulnerability info
    for json_file in solidifi_path.glob("**/*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Extract code (source or bytecode)
            code = data.get('source_code') or data.get('bytecode') or ""
            if not code:
                # Try to find .sol file paired with JSON
                sol_file = json_file.with_suffix('.sol')
                if sol_file.exists():
                    with open(sol_file, 'r', encoding='utf-8') as f:
                        code = f.read()
            
            # Extract vulnerability type from metadata
            vulns = data.get('vulnerabilities', [])
            vuln_type = 'safe' if not vulns else vulns[0].lower()
            
            # Normalize vulnerability names
            if 'reentr' in vuln_type.lower():
                vuln_type = 'reentrancy'
            elif 'overflow' in vuln_type.lower() or 'underflow' in vuln_type.lower():
                vuln_type = 'overflow'
            elif 'phishing' in vuln_type.lower() or 'honeypot' in vuln_type.lower():
                vuln_type = 'phishing'
            else:
                vuln_type = 'other'
            
            if code and len(code) > 10:  # Only include non-empty code
                contracts.append((code, vuln_type))
                
        except (json.JSONDecodeError, KeyError, UnicodeDecodeError) as e:
            logger.debug(f"Error parsing {json_file}: {e}")
            continue
    
    logger.info(f"Parsed {len(contracts)} SolidiFI contracts")
    return contracts


def parse_smartbugs_contracts(smartbugs_dir: str, max_contracts: int = 5000) -> List[Tuple[str, str]]:
    """Parse SmartBugs contracts and labels.
    
    Args:
        smartbugs_dir: Path to smartbugs/contracts directory
        max_contracts: Maximum contracts to include (for manageable dataset size)
        
    Returns:
        List of (contract_code, vulnerability_type) tuples
    """
    logger.info(f"Parsing SmartBugs contracts from {smartbugs_dir}")
    contracts = []
    smartbugs_path = Path(smartbugs_dir)
    
    if not smartbugs_path.exists():
        logger.warning(f"SmartBugs directory not found: {smartbugs_dir}")
        return contracts
    
    # SmartBugs organizes by vulnerability type in subdirectories
    vuln_types = {
        'reentrancy': ['reentrancy'],
        'overflow': ['arithmetic', 'overflow'],
        'phishing': ['phishing'],
        'honeypot': ['honeypot'],
        'access_control': ['access_control'],
        'safe': ['safe']
    }
    
    contract_count = 0
    
    for base_vuln, patterns in vuln_types.items():
        for pattern in patterns:
            vuln_dir = smartbugs_path / pattern
            
            if not vuln_dir.exists():
                continue
            
            # Find all .sol files in this vulnerability subdirectory
            for sol_file in vuln_dir.glob("**/*.sol"):
                if contract_count >= max_contracts:
                    break
                    
                try:
                    with open(sol_file, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    if len(code) > 10:  # Only include non-empty code
                        contracts.append((code, base_vuln))
                        contract_count += 1
                        
                except UnicodeDecodeError:
                    logger.debug(f"Skipping binary file: {sol_file}")
                    continue
            
            if contract_count >= max_contracts:
                break
    
    logger.info(f"Parsed {len(contracts)} SmartBugs contracts")
    return contracts


def save_to_csv(contracts: List[Tuple[str, str]], output_path: str) -> None:
    """Save contracts to CSV file.
    
    Args:
        contracts: List of (code, vulnerability_type) tuples
        output_path: Output CSV file path
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Saving {len(contracts)} contracts to {output_path}")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['code', 'vulnerability_type'])
        
        for code, vuln_type in contracts:
            # Clean code: remove newlines for CSV compatibility, keep code intact
            code_clean = code.replace('\n', ' ').replace('\r', ' ')
            writer.writerow([code_clean, vuln_type])
    
    logger.info(f"Successfully saved to {output_path}")


def main():
    """Download and prepare datasets."""
    project_root = Path(__file__).parent.parent
    data_dir = project_root / 'data' / 'Datasets'
    temp_dir = project_root / 'data' / 'tmp_repos'
    
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("TrustChainAi Dataset Preparation")
    logger.info("=" * 60)
    
    # Download SolidiFI (smartbugs-curated)
    solidifi_repo_dir = temp_dir / 'smartbugs-curated'
    if clone_repository(
        'https://github.com/smartbugs/smartbugs-curated.git',
        str(solidifi_repo_dir)
    ):
        solidifi_contracts = parse_solidifi_contracts(str(solidifi_repo_dir / 'contracts'))
        save_to_csv(
            solidifi_contracts,
            str(data_dir / 'SolidiFI' / 'dataset.csv')
        )
    
    # Download SmartBugs
    smartbugs_repo_dir = temp_dir / 'smartbugs'
    if clone_repository(
        'https://github.com/smartbugs/smartbugs.git',
        str(smartbugs_repo_dir)
    ):
        smartbugs_contracts = parse_smartbugs_contracts(str(smartbugs_repo_dir / 'contracts'))
        save_to_csv(
            smartbugs_contracts,
            str(data_dir / 'SmartBugs' / 'dataset.csv')
        )
    
    logger.info("=" * 60)
    logger.info("Dataset preparation complete!")
    logger.info(f"SolidiFI: {data_dir / 'SolidiFI' / 'dataset.csv'}")
    logger.info(f"SmartBugs: {data_dir / 'SmartBugs' / 'dataset.csv'}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
