"""Process user-level data: count depositors/borrowers per block and compute HHI.

Note: countDepositors and countBorrowers fetch live data from the subgraph
and therefore act as both fetchers and processors.

Usage:
    python -m src.processors.users --task count_depositors --token DAI
    python -m src.processors.users --task count_borrowers  --token DAI
    python -m src.processors.users --task calc_hhi         --token DAI
    python -m src.processors.users --task user_count       --token DAI
"""

import argparse
import csv
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import (
    TOKENS, RESERVE_IDS, AAVE_LEGACY_URL, PROCESSED_DIR,
    COLLECTION_START_TIMESTAMP,
)
from src.fetchers.base import subgraph_post
from src.utils.csv_io import write_csv


# ---------------------------------------------------------------------------
# Count depositors per block
# ---------------------------------------------------------------------------

def count_depositors(token: str, blocks_path: Path, out_path: Path) -> None:
    """Count unique depositors for each block by querying userReserves."""
    reserve_id = RESERVE_IDS[token]
    records = []

    with open(blocks_path) as f:
        blocks = [line.strip() for line in f if line.strip()]

    total = len(blocks)
    for i, block in enumerate(blocks):
        user_funds = set()
        last_balance = None
        last_time = datetime.datetime.now()

        while True:
            extra = (f'scaledATokenBalance_lte: "{last_balance}"'
                     if last_balance else "")
            query = f"""
            {{
                userReserves(
                    first: 1000,
                    block: {{number: {block}}},
                    where: {{
                        reserve: "{reserve_id}",
                        scaledATokenBalance_gt: 0,
                        {extra}
                    }},
                    orderBy: scaledATokenBalance,
                    orderDirection: desc
                ) {{
                    user {{ id }}
                    scaledATokenBalance
                }}
            }}
            """
            result = subgraph_post(AAVE_LEGACY_URL, query)
            if result is None:
                continue

            output = result.get("data", {}).get("userReserves", [])
            # Skip records already added (cursor-based dedup)
            start = 0
            while start < len(output) and output[start]["user"]["id"] in user_funds:
                start += 1
            if start == len(output):
                break
            for item in output[start:]:
                user_funds.add(item["user"]["id"])
            last_balance = output[-1]["scaledATokenBalance"]

        records.append({"block": block, "HHI": 0, "depositers": len(user_funds)})
        elapsed = (datetime.datetime.now() - last_time).total_seconds()
        print(f"[depositors] {token} block {block}: {len(user_funds)} users "
              f"({(i + 1) / total * 100:.1f}%) ({elapsed:.1f}s)")

    write_csv(out_path, ["block", "HHI", "depositers"], records)
    print(f"[count_depositors] {token}: {len(records)} blocks → {out_path}")


# ---------------------------------------------------------------------------
# Count borrowers per block
# ---------------------------------------------------------------------------

def count_borrowers(token: str, blocks_path: Path, out_path: Path) -> None:
    """Count unique borrowers for each block by querying userReserves."""
    reserve_id = RESERVE_IDS[token]
    records = []

    with open(blocks_path) as f:
        blocks = [line.strip() for line in f if line.strip()]

    total = len(blocks)
    for i, block in enumerate(blocks):
        user_debts = set()
        last_debt = None

        while True:
            extra = f'currentTotalDebt_lte: "{last_debt}"' if last_debt else ""
            query = f"""
            {{
                userReserves(
                    first: 1000,
                    block: {{number: {block}}},
                    where: {{
                        reserve: "{reserve_id}",
                        currentTotalDebt_gt: 0,
                        {extra}
                    }},
                    orderBy: currentTotalDebt,
                    orderDirection: desc
                ) {{
                    user {{ id }}
                    currentTotalDebt
                }}
            }}
            """
            result = subgraph_post(AAVE_LEGACY_URL, query)
            if result is None:
                continue

            output = result.get("data", {}).get("userReserves", [])
            start = 0
            while start < len(output) and output[start]["user"]["id"] in user_debts:
                start += 1
            if start == len(output):
                break
            for item in output[start:]:
                user_debts.add(item["user"]["id"])
            last_debt = output[-1]["currentTotalDebt"]

        records.append({"block": block, "borrowers": len(user_debts)})
        print(f"[borrowers] {token} block {block}: {len(user_debts)} borrowers "
              f"({(i + 1) / total * 100:.1f}%)")

    write_csv(out_path, ["block", "borrowers"], records)
    print(f"[count_borrowers] {token}: {len(records)} blocks → {out_path}")


# ---------------------------------------------------------------------------
# Compute Herfindahl-Hirschman Index (HHI) per block
# ---------------------------------------------------------------------------

def _hhi(fund_values: dict) -> float:
    """Compute the HHI concentration index from a dict of user → balance."""
    total = sum(fund_values.values())
    if total == 0:
        return 0.0
    return sum((v / total * 100) ** 2 for v in fund_values.values())


def calc_hhi(token: str, blocks_path: Path, out_path: Path) -> None:
    """Compute the HHI concentration index for each block."""
    reserve_id = RESERVE_IDS[token]
    records = []

    with open(blocks_path) as f:
        blocks = [line.strip() for line in f if line.strip()]

    total = len(blocks)
    for i, block in enumerate(blocks):
        user_funds = {}
        last_balance = None

        while True:
            extra = f'scaledATokenBalance_lte: "{last_balance}"' if last_balance else ""
            query = f"""
            {{
                userReserves(
                    first: 1000,
                    block: {{number: {block}}},
                    where: {{
                        reserve: "{reserve_id}",
                        scaledATokenBalance_gt: 0,
                        {extra}
                    }},
                    orderBy: scaledATokenBalance,
                    orderDirection: desc
                ) {{
                    user {{ id }}
                    scaledATokenBalance
                }}
            }}
            """
            result = subgraph_post(AAVE_LEGACY_URL, query)
            if result is None:
                continue

            output = result.get("data", {}).get("userReserves", [])
            start = 0
            while start < len(output) and output[start]["user"]["id"] in user_funds:
                start += 1
            if start == len(output):
                break
            for item in output[start:]:
                user_funds[item["user"]["id"]] = float(item["scaledATokenBalance"])
            last_balance = output[-1]["scaledATokenBalance"]

        hhi = _hhi(user_funds)
        records.append({"block": block, "HHI": hhi})
        print(f"[hhi] {token} block {block}: HHI={hhi:.2f} ({(i + 1) / total * 100:.1f}%)")

    write_csv(out_path, ["block", "HHI"], records)
    print(f"[calc_hhi] {token}: {len(records)} blocks → {out_path}")


# ---------------------------------------------------------------------------
# Build token user count time-series from transaction data
# ---------------------------------------------------------------------------

def build_user_count(token: str, token_tx_path: Path, out_path: Path) -> None:
    """Count cumulative unique users at each transaction timestamp."""
    user_addresses = set()
    records = []

    with open(token_tx_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            user_addresses.add(row[2])  # user column
            records.append({"timestamp": row[-1], "userCount": len(user_addresses)})

    write_csv(out_path, ["timestamp", "userCount"], records)
    print(f"[user_count] {token}: {len(records)} rows → {out_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Process user-level DeFi data")
    parser.add_argument("--task", required=True,
                        choices=["count_depositors", "count_borrowers",
                                 "calc_hhi", "user_count"],
                        help="Task to run")
    parser.add_argument("--token", required=True, choices=TOKENS,
                        help="Token to process")
    parser.add_argument("--blocks", type=Path,
                        help="Path to block numbers file (default: data/raw/<token>_blocks.txt)")
    args = parser.parse_args()

    token = args.token
    blocks_path = args.blocks or (PROCESSED_DIR.parent / "raw" / "reserve_info" / f"{token}_blocks.txt")
    depositors_dir = PROCESSED_DIR / "depositors"
    borrowers_dir = PROCESSED_DIR / "borrowers"
    hhi_dir = PROCESSED_DIR / "hhi"
    user_count_dir = PROCESSED_DIR / "token_user_count"

    for d in (depositors_dir, borrowers_dir, hhi_dir, user_count_dir):
        d.mkdir(parents=True, exist_ok=True)

    if args.task == "count_depositors":
        count_depositors(token, blocks_path,
                         out_path=depositors_dir / f"{token}_depositers.csv")

    elif args.task == "count_borrowers":
        count_borrowers(token, blocks_path,
                        out_path=borrowers_dir / f"{token}_borrowers.csv")

    elif args.task == "calc_hhi":
        calc_hhi(token, blocks_path,
                 out_path=hhi_dir / f"{token}_HHI.csv")

    elif args.task == "user_count":
        token_tx_path = PROCESSED_DIR / "token_transactions" / f"{token}.csv"
        build_user_count(token, token_tx_path,
                         out_path=user_count_dir / f"{token}.csv")


if __name__ == "__main__":
    main()
