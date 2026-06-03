"""
TrustChainAI — Full Dataset Pipeline
=====================================
Merges contracts from:
  1. SmartBugs Curated  (https://github.com/smartbugs/smartbugs-curated)
  2. SolidiFI Benchmark (https://github.com/smartbugs/SolidiFI-benchmark)
  3. DeFiHackLabs       (https://github.com/SunWeb3Sec/DeFiHackLabs)
  4. Not-So-Smart Contracts / Trail of Bits (https://github.com/crytic/not-so-smart-contracts)

Output:
  data/processed/train.csv
  data/processed/val.csv
  data/processed/test.csv
  data/processed/dataset_stats.json

Label Schema (14 classes matching TrustChainAI vulnerability table):
  0  safe
  1  reentrancy
  2  integer_overflow
  3  access_control
  4  tx_origin_phishing
  5  dos_gas
  6  unchecked_call
  7  front_running_mev
  8  timestamp_dependence
  9  proxy_storage_collision
  10 flash_loan_oracle
  11 flash_loan_single_block
  12 misnamed_constructor
  13 other

Usage:
  python prepare_datasets.py [--output_dir data/processed] [--seed 42]
  python prepare_datasets.py --skip_clone   # if repos already cloned
  python prepare_datasets.py --synthetic_aug 500  # add N synthetic samples per rare class
"""

import os
import re
import json
import glob
import shutil
import random
import argparse
import subprocess
import hashlib
from pathlib import Path
from collections import Counter, defaultdict
from typing import Optional

import pandas as pd
from sklearn.model_selection import train_test_split

# ── Config ────────────────────────────────────────────────────────────────────

REPOS = {
    "smartbugs":   "https://github.com/smartbugs/smartbugs-curated.git",
    "solidifi":    "https://github.com/smartbugs/SolidiFI-benchmark.git",
    "defihack":    "https://github.com/SunWeb3Sec/DeFiHackLabs.git",
    "notsosmarts": "https://github.com/crytic/not-so-smart-contracts.git",
}

CLONE_DIR = Path("data/raw_repos")
OUTPUT_DIR = Path("data/processed")
MAX_TOKEN_LEN = 512  # chars proxy for 512 tokens

# Label constants
LABELS = {
    "safe":                     0,
    "reentrancy":               1,
    "integer_overflow":         2,
    "access_control":           3,
    "tx_origin_phishing":       4,
    "dos_gas":                  5,
    "unchecked_call":           6,
    "front_running_mev":        7,
    "timestamp_dependence":     8,
    "proxy_storage_collision":  9,
    "flash_loan_oracle":        10,
    "flash_loan_single_block":  11,
    "misnamed_constructor":     12,
    "other":                    13,
}

# ── SmartBugs label mapping ────────────────────────────────────────────────────
# SmartBugs folder names → our label IDs

SMARTBUGS_MAP = {
    "reentrancy":          "reentrancy",
    "arithmetic":          "integer_overflow",
    "access_control":      "access_control",
    "unchecked_low_level_calls": "unchecked_call",
    "denial_of_service":   "dos_gas",
    "bad_randomness":      "timestamp_dependence",
    "front_running":       "front_running_mev",
    "time_manipulation":   "timestamp_dependence",
    "short_addresses":     "other",
    "other":               "other",
    "safe":                "safe",
}

# SolidiFI uses numbered bug types in directory names
SOLIDIFI_MAP = {
    "reentrancy":          "reentrancy",
    "overflow":            "integer_overflow",
    "underflow":           "integer_overflow",
    "tod":                 "front_running_mev",
    "tx.origin":           "tx_origin_phishing",
    "unhandled-exceptions": "unchecked_call",
    "integer-overflow":    "integer_overflow",
}

# DeFiHackLabs src/ subdir keyword → our label
DEFIHACK_MAP = {
    "reentrancy":       "reentrancy",
    "flashloan":        "flash_loan_oracle",
    "flash_loan":       "flash_loan_oracle",
    "oracle":           "flash_loan_oracle",
    "overflow":         "integer_overflow",
    "access":           "access_control",
    "frontrun":         "front_running_mev",
}

# Trail of Bits: folder names
NOTSO_MAP = {
    "reentrancy":              "reentrancy",
    "integer-overflow":        "integer_overflow",
    "unprotected-functions":   "access_control",
    "tx.origin":               "tx_origin_phishing",
    "denial-of-service":       "dos_gas",
    "unchecked-return-value":  "unchecked_call",
    "assert-violation":        "other",
    "suicidal":                "access_control",
    "variable-shadowing":      "other",
}


# ── Utilities ─────────────────────────────────────────────────────────────────

def run(cmd: str, cwd: Optional[Path] = None) -> int:
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    return result.returncode


def clone_repos(skip: bool = False):
    CLONE_DIR.mkdir(parents=True, exist_ok=True)
    for name, url in REPOS.items():
        dest = CLONE_DIR / name
        if dest.exists():
            if skip:
                print(f"  [skip] {name} already exists.")
                continue
            print(f"  Updating {name}...")
            run("git pull --depth=1", cwd=dest)
        else:
            print(f"  Cloning {name}...")
            run(f"git clone --depth=1 {url} {dest}")


def truncate_source(src: str, max_chars: int = MAX_TOKEN_LEN * 4) -> str:
    """Keep up to max_chars of contract source (roughly 512 tokens)."""
    return src[:max_chars]


def normalize_label(raw: str) -> str:
    raw = raw.lower().strip().replace("-", "_").replace(" ", "_")
    if raw in LABELS:
        return raw
    return "other"


def file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def load_sol_file(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8", errors="ignore").strip()
    except Exception:
        return None


# ── Source loaders ────────────────────────────────────────────────────────────

def load_smartbugs(records: list):
    base = CLONE_DIR / "smartbugs" / "dataset"
    if not base.exists():
        print("  [warn] SmartBugs dataset/ not found, skipping.")
        return

    for vuln_dir in sorted(base.iterdir()):
        if not vuln_dir.is_dir():
            continue
        raw_label = vuln_dir.name.lower()
        label = normalize_label(SMARTBUGS_MAP.get(raw_label, "other"))

        for sol_file in vuln_dir.rglob("*.sol"):
            src = load_sol_file(sol_file)
            if not src:
                continue
            records.append({
                "source":   "smartbugs",
                "filename": sol_file.name,
                "label":    label,
                "label_id": LABELS[label],
                "code":     truncate_source(src),
            })

    print(f"  [smartbugs] loaded {sum(1 for r in records if r['source']=='smartbugs')} contracts")


def load_solidifi(records: list):
    base = CLONE_DIR / "solidifi"
    if not base.exists():
        print("  [warn] SolidiFI not found, skipping.")
        return

    before = len(records)
    for sol_file in base.rglob("*.sol"):
        parts = [p.lower() for p in sol_file.parts]
        label = "other"
        for keyword, mapped in SOLIDIFI_MAP.items():
            if any(keyword in p for p in parts):
                label = mapped
                break

        src = load_sol_file(sol_file)
        if not src:
            continue
        records.append({
            "source":   "solidifi",
            "filename": sol_file.name,
            "label":    label,
            "label_id": LABELS[label],
            "code":     truncate_source(src),
        })

    print(f"  [solidifi] loaded {len(records) - before} contracts")


def load_defihack(records: list):
    """
    DeFiHackLabs keeps PoC contracts under src/test/.
    We infer label from subdirectory name / filename keywords.
    """
    base = CLONE_DIR / "defihack" / "src" / "test"
    if not base.exists():
        base = CLONE_DIR / "defihack" / "src"
    if not base.exists():
        print("  [warn] DeFiHackLabs src not found, skipping.")
        return

    before = len(records)
    for sol_file in base.rglob("*.sol"):
        label = "other"
        haystack = (str(sol_file).lower() + " " + sol_file.stem.lower())
        for keyword, mapped in DEFIHACK_MAP.items():
            if keyword in haystack:
                label = mapped
                break

        src = load_sol_file(sol_file)
        if not src:
            continue
        records.append({
            "source":   "defihack",
            "filename": sol_file.name,
            "label":    label,
            "label_id": LABELS[label],
            "code":     truncate_source(src),
        })

    print(f"  [defihack] loaded {len(records) - before} contracts")


def load_notsosmarts(records: list):
    base = CLONE_DIR / "notsosmarts"
    if not base.exists():
        print("  [warn] not-so-smart-contracts not found, skipping.")
        return

    before = len(records)
    for vuln_dir in sorted(base.iterdir()):
        if not vuln_dir.is_dir() or vuln_dir.name.startswith("."):
            continue
        raw = vuln_dir.name.lower()
        label = normalize_label(NOTSO_MAP.get(raw, "other"))

        for sol_file in vuln_dir.rglob("*.sol"):
            src = load_sol_file(sol_file)
            if not src:
                continue
            records.append({
                "source":   "notsosmarts",
                "filename": sol_file.name,
                "label":    label,
                "label_id": LABELS[label],
                "code":     truncate_source(src),
            })

    print(f"  [notsosmarts] loaded {len(records) - before} contracts")


# ── Synthetic augmentation for rare classes ───────────────────────────────────

SYNTHETIC_TEMPLATES = {
    "flash_loan_oracle": """
pragma solidity ^0.8.0;
interface IFlashLoan {{ function flashLoan(uint amount) external; }}
interface IOracle {{ function getPrice() external view returns (uint); }}
contract FlashLoanOracleAttack {{
    IFlashLoan lender;
    IOracle oracle;
    constructor(address _l, address _o) {{ lender = IFlashLoan(_l); oracle = IOracle(_o); }}
    function attack(uint amount) external {{
        lender.flashLoan(amount);
        // Manipulate oracle price here
        uint price = oracle.getPrice();
    }}
    receive() external payable {{}}
}}
""",
    "flash_loan_single_block": """
pragma solidity ^0.8.0;
interface IERC20 {{ function transfer(address to, uint amount) external returns (bool); }}
interface IPool {{ function borrow(uint amount) external; function repay(uint amount) external; }}
contract SingleBlockFlashAttack {{
    IPool pool;
    IERC20 token;
    constructor(address _pool, address _token) {{ pool = IPool(_pool); token = IERC20(_token); }}
    function execute(uint amount) external {{
        pool.borrow(amount);           // borrow in same block
        // exploit logic
        pool.repay(amount);            // repay in same block
    }}
}}
""",
    "proxy_storage_collision": """
pragma solidity ^0.8.0;
contract Proxy {{
    address public implementation;   // slot 0 — collides with logic contract state
    address public admin;            // slot 1
    fallback() external payable {{
        address impl = implementation;
        assembly {{
            calldatacopy(0, 0, calldatasize())
            let result := delegatecall(gas(), impl, 0, calldatasize(), 0, 0)
            returndatacopy(0, 0, returndatasize())
            switch result
            case 0 {{ revert(0, returndatasize()) }}
            default {{ return(0, returndatasize()) }}
        }}
    }}
}}
contract LogicV1 {{
    address public owner;            // slot 0 — overwrites Proxy.implementation!
    function setOwner(address _o) public {{ owner = _o; }}
}}
""",
    "misnamed_constructor": """
pragma solidity ^0.4.22;
contract MisnamedConstructor {{
    address public owner;
    function MisnamedConstructor() public {{   // old-style constructor — anyone can call
        owner = msg.sender;
    }}
    function withdraw() public {{
        require(msg.sender == owner);
        msg.sender.transfer(address(this).balance);
    }}
    function() public payable {{}}
}}
""",
    "front_running_mev": """
pragma solidity ^0.8.0;
contract FrontRunnable {{
    mapping(address => uint) public commitments;
    function commit(bytes32 hash) external payable {{
        commitments[msg.sender] = block.number;  // visible in mempool
    }}
    function reveal(uint secret) external {{
        require(commitments[msg.sender] != 0);
        // attacker can frontrun with same secret
        _reward(msg.sender, secret);
    }}
    function _reward(address to, uint amt) internal {{}}
}}
""",
    "timestamp_dependence": """
pragma solidity ^0.8.0;
contract TimestampLottery {{
    uint public jackpot;
    function enter() external payable {{ jackpot += msg.value; }}
    function pickWinner() external {{
        require(block.timestamp % 15 == 0, "not lucky time");  // miner-manipulable
        payable(msg.sender).transfer(jackpot);
        jackpot = 0;
    }}
}}
""",
}


def generate_synthetic(records: list, n_per_class: int, seed: int = 42):
    rng = random.Random(seed)
    before = len(records)
    for label, template in SYNTHETIC_TEMPLATES.items():
        for i in range(n_per_class):
            # Minor variation: inject a random comment to avoid exact duplicates
            variation = template.strip() + f"\n// variant_{i}_{rng.randint(1000,9999)}"
            records.append({
                "source":   "synthetic",
                "filename": f"synthetic_{label}_{i}.sol",
                "label":    label,
                "label_id": LABELS[label],
                "code":     truncate_source(variation),
            })
    print(f"  [synthetic] generated {len(records) - before} augmentation contracts")


# ── Deduplication ─────────────────────────────────────────────────────────────

def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact-code duplicates, keeping first occurrence."""
    before = len(df)
    df["_hash"] = df["code"].apply(lambda c: hashlib.md5(c.encode()).hexdigest())
    df = df.drop_duplicates(subset="_hash").drop(columns="_hash")
    print(f"  [dedup] removed {before - len(df)} duplicates → {len(df)} unique contracts")
    return df


# ── Splitting ─────────────────────────────────────────────────────────────────

def split_dataset(df: pd.DataFrame, seed: int = 42):
    """
    Stratified 70 / 15 / 15 split.
    Falls back to random split for classes with < 3 samples.
    """
    # Separate tiny classes that can't be stratified
    counts = df["label"].value_counts()
    tiny_labels = counts[counts < 3].index.tolist()
    tiny_df = df[df["label"].isin(tiny_labels)]
    main_df = df[~df["label"].isin(tiny_labels)]

    if len(main_df) == 0:
        # Edge case: everything is tiny
        train = df.sample(frac=0.7, random_state=seed)
        rest  = df.drop(train.index)
        val   = rest.sample(frac=0.5, random_state=seed)
        test  = rest.drop(val.index)
        return train, val, test

    train, temp = train_test_split(main_df, test_size=0.30, stratify=main_df["label"], random_state=seed)
    val,   test = train_test_split(temp,    test_size=0.50, stratify=temp["label"],    random_state=seed)

    # Append tiny samples to train
    train = pd.concat([train, tiny_df], ignore_index=True)

    return train, val, test


# ── Stats ──────────────────────────────────────────────────────────────────────

def print_stats(df: pd.DataFrame, split_name: str):
    counts = df["label"].value_counts().to_dict()
    print(f"\n  [{split_name}] {len(df)} total")
    for label, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * min(count // 10, 40)
        print(f"    {label:<30} {count:>5}  {bar}")


def save_stats(train: pd.DataFrame, val: pd.DataFrame, test: pd.DataFrame, output_dir: Path):
    def counts(df):
        return df["label"].value_counts().to_dict()

    stats = {
        "total": len(train) + len(val) + len(test),
        "train": {"count": len(train), "label_distribution": counts(train)},
        "val":   {"count": len(val),   "label_distribution": counts(val)},
        "test":  {"count": len(test),  "label_distribution": counts(test)},
        "sources": (
            pd.concat([train, val, test])["source"].value_counts().to_dict()
        ),
        "labels": LABELS,
    }
    path = output_dir / "dataset_stats.json"
    path.write_text(json.dumps(stats, indent=2))
    print(f"\n  Stats saved → {path}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="TrustChainAI dataset pipeline")
    parser.add_argument("--output_dir",    default="data/processed", help="Where to save CSVs")
    parser.add_argument("--clone_dir",     default="data/raw_repos",  help="Where to clone repos")
    parser.add_argument("--skip_clone",    action="store_true",       help="Skip git clone/pull")
    parser.add_argument("--synthetic_aug", type=int, default=0,       help="Synthetic samples per rare class (0=off)")
    parser.add_argument("--seed",          type=int, default=42)
    args = parser.parse_args()

    global CLONE_DIR, OUTPUT_DIR
    CLONE_DIR  = Path(args.clone_dir)
    OUTPUT_DIR = Path(args.output_dir)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\n═══════════════════════════════════════════")
    print("  TrustChainAI — Dataset Pipeline")
    print("═══════════════════════════════════════════\n")

    # 1. Clone / update repos
    print("▶ Step 1: Fetching source repos...")
    clone_repos(skip=args.skip_clone)

    # 2. Load all sources
    print("\n▶ Step 2: Loading contracts...")
    records = []
    load_smartbugs(records)
    load_solidifi(records)
    load_defihack(records)
    load_notsosmarts(records)

    if not records:
        print("\n[ERROR] No contracts loaded. Check that repos cloned successfully.")
        return

    # 3. Synthetic augmentation
    if args.synthetic_aug > 0:
        print(f"\n▶ Step 3: Synthetic augmentation ({args.synthetic_aug} samples/rare class)...")
        generate_synthetic(records, n_per_class=args.synthetic_aug, seed=args.seed)
    else:
        print("\n▶ Step 3: Skipping synthetic augmentation (use --synthetic_aug N to enable)")

    # 4. Build DataFrame + deduplicate
    print("\n▶ Step 4: Deduplication...")
    df = pd.DataFrame(records)
    df = deduplicate(df)

    # 5. Split
    print("\n▶ Step 5: Train / val / test split (70/15/15, stratified)...")
    train, val, test = split_dataset(df, seed=args.seed)

    print_stats(train, "train")
    print_stats(val,   "val")
    print_stats(test,  "test")

    # 6. Save
    print("\n▶ Step 6: Saving datasets...")
    train.to_csv(OUTPUT_DIR / "train.csv", index=False)
    val.to_csv(  OUTPUT_DIR / "val.csv",   index=False)
    test.to_csv( OUTPUT_DIR / "test.csv",  index=False)
    save_stats(train, val, test, OUTPUT_DIR)

    print(f"\n✅ Done! Files written to {OUTPUT_DIR}/")
    print(f"   train.csv  ({len(train)} rows)")
    print(f"   val.csv    ({len(val)} rows)")
    print(f"   test.csv   ({len(test)} rows)")
    print(f"   dataset_stats.json\n")
    print("  Next step → open notebooks/train_vulnerability_detector.ipynb")
    print("              and point DATA_DIR to:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
