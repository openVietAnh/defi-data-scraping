"""Process raw AAVE V2 transaction CSVs through the classification pipeline.

Pipeline stages (run in order):
    1. sort             — sort allTransaction.csv and per-type files by timestamp
    2. classify         — classify each transaction with its type
    3. filter_by_token  — split classified transactions into per-token files
    4. dedup_hashes     — remove duplicate transaction hashes per token

Usage:
    python -m src.processors.transactions --stage sort
    python -m src.processors.transactions --stage all
"""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import TOKENS, TRANSACTION_TYPES, PROCESSED_DIR, RAW_DIR
from src.utils.csv_io import write_csv


# ---------------------------------------------------------------------------
# Stage 1: Sort by timestamp
# ---------------------------------------------------------------------------

# Column index of the transaction ID (matches allTransaction id) per type.
# These indices reflect the column order produced by the fetchers.
TYPE_ID_INDEX = {
    "borrow":                       4,
    "deposit":                      2,
    "flashLoan":                    1,
    "liquidationCall":              2,
    "redeemUnderlying":             1,
    "repay":                        1,
    "swap":                         2,
    "usageAsCollateral":            1,
    "rebalanceStableBorrowRate":    1,
}

# Column index of the reserve symbol per type
TYPE_TOKEN_INDEX = {
    "borrow":                       5,
    "deposit":                      3,
    "flashLoan":                    3,
    "liquidationCall":              6,
    "redeemUnderlying":             3,
    "repay":                        4,
    "swap":                         4,
    "usageAsCollateral":            3,
    "rebalanceStableBorrowRate":    3,
}


def _sort_csv_by_timestamp(path: Path) -> None:
    """Sort a CSV file in-place by its 'timestamp' column."""
    if not path.exists():
        print(f"[sort] Skipping missing file: {path}")
        return
    with open(path, newline="") as f:
        reader = csv.reader(f)
        keys = next(reader)
        rows = list(reader)
    rows.sort(key=lambda x: x[keys.index("timestamp")])
    write_csv(path, keys, [{keys[i]: row[i] for i in range(len(keys))} for row in rows])
    print(f"[sort] {path.name}: sorted {len(rows)} rows")


def sort_all(raw_dir: Path) -> None:
    """Sort allTransaction.csv and each transaction-type CSV by timestamp."""
    _sort_csv_by_timestamp(raw_dir / "transactions" / "allTransaction.csv")
    for tx_type in TRANSACTION_TYPES:
        _sort_csv_by_timestamp(raw_dir / "transactions" / f"{tx_type}.csv")


# ---------------------------------------------------------------------------
# Stage 2: Classify each allTransaction row with its type
# ---------------------------------------------------------------------------

def classify_transactions(raw_dir: Path, out_dir: Path) -> None:
    """Build allTransactionType.csv by matching allTransaction ids to typed files."""
    type_map = {}
    for tx_type in TRANSACTION_TYPES:
        path = raw_dir / "transactions" / f"{tx_type}.csv"
        if not path.exists():
            continue
        id_col = TYPE_ID_INDEX.get(tx_type, 0)
        with open(path, newline="") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if row:
                    type_map[row[id_col]] = tx_type

    classified = []
    missing = []
    keys = ["id", "pool", "user", "timestamp"]

    all_tx_path = raw_dir / "transactions" / "allTransaction.csv"
    with open(all_tx_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            entry = {keys[i]: row[i] for i in range(len(keys))}
            tx_type = type_map.get(row[0])
            if tx_type:
                entry["type"] = tx_type
                classified.append(entry)
            else:
                missing.append(entry)

    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(out_dir / "allTransactionType.csv",
              ["id", "type", "user", "pool", "timestamp"], classified)
    write_csv(out_dir / "missing_type.csv",
              ["id", "user", "pool", "timestamp"], missing)
    print(f"[classify] {len(classified)} classified, {len(missing)} missing type")


# ---------------------------------------------------------------------------
# Stage 3: Filter classified transactions into per-token files
# ---------------------------------------------------------------------------

def filter_by_token(raw_dir: Path, out_dir: Path) -> None:
    """Split allTransactionType.csv into one CSV per token."""
    hash_to_token = {}
    for tx_type in TRANSACTION_TYPES:
        path = raw_dir / "transactions" / f"{tx_type}.csv"
        if not path.exists():
            continue
        id_col = TYPE_ID_INDEX.get(tx_type, 0)
        token_col = TYPE_TOKEN_INDEX.get(tx_type, 3)
        with open(path, newline="") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if row:
                    hash_to_token[row[id_col]] = row[token_col]

    token_transactions = {token: [] for token in TOKENS}
    keys = ["id", "type", "user", "pool", "timestamp"]

    classified_path = out_dir / "allTransactionType.csv"
    with open(classified_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            token = hash_to_token.get(row[0])
            if token in TOKENS:
                token_transactions[token].append({keys[i]: row[i] for i in range(len(keys))})

    token_dir = out_dir / "token_transactions"
    token_dir.mkdir(parents=True, exist_ok=True)
    for token, records in token_transactions.items():
        write_csv(token_dir / f"{token}.csv", keys, records)
        print(f"[filter_by_token] {token}: {len(records)} transactions")


# ---------------------------------------------------------------------------
# Stage 4: Deduplicate transaction hashes per token
# ---------------------------------------------------------------------------

def dedup_hashes(out_dir: Path) -> None:
    """Write per-token deduplicated hash files (used by hash_to_block fetcher)."""
    token_dir = out_dir / "token_transactions"
    hash_dir = out_dir / "hash_to_block"
    hash_dir.mkdir(parents=True, exist_ok=True)

    for token in TOKENS:
        path = token_dir / f"{token}.csv"
        if not path.exists():
            continue
        seen = set()
        hashes = []
        with open(path, newline="") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                tx_hash = row[0].split(":")[2] if ":" in row[0] else row[0]
                if tx_hash not in seen:
                    seen.add(tx_hash)
                    hashes.append(tx_hash)

        out_path = hash_dir / f"{token}_filtered.csv"
        out_path.write_text("hash\n" + "\n".join(hashes))
        print(f"[dedup_hashes] {token}: {len(hashes)} unique hashes")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Process AAVE V2 transaction data")
    parser.add_argument("--stage", required=True,
                        choices=["sort", "classify", "filter_by_token", "dedup_hashes", "all"],
                        help="Processing stage to run")
    args = parser.parse_args()

    if args.stage in ("sort", "all"):
        sort_all(RAW_DIR)
    if args.stage in ("classify", "all"):
        classify_transactions(RAW_DIR, PROCESSED_DIR)
    if args.stage in ("filter_by_token", "all"):
        filter_by_token(RAW_DIR, PROCESSED_DIR)
    if args.stage in ("dedup_hashes", "all"):
        dedup_hashes(PROCESSED_DIR)


if __name__ == "__main__":
    main()
