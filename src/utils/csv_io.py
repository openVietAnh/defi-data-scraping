"""Reusable CSV read/write helpers used across all pipeline stages."""

import csv
from pathlib import Path


def read_csv(path: Path) -> tuple:
    """Read a CSV file and return (headers, rows).

    Returns:
        headers: list of column name strings
        rows: list of lists of string values (one per data row)
    """
    with open(path, newline="") as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)
    return headers, rows


def write_csv(path: Path, fieldnames: list, rows) -> None:
    """Write an iterable of dicts to a CSV file.

    Creates parent directories automatically if they don't exist.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
