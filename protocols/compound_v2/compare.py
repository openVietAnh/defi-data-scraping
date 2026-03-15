"""Compare Compound V2 TVL/liquidity data between subgraph and DeFiLlama.

Reads:  compound_info.csv, compound-defillama.csv
Writes: diff.txt
"""

import csv
from pathlib import Path

BASE = Path(__file__).parent


def main():
    dates = []
    graph = {}
    with open(BASE / "compound_info.csv", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for item in reader:
            graph[item[1]] = (int(item[0]), float(item[3]) - float(item[2]))
            dates.append(item[1])

    llama = {}
    with open(BASE / "compound-defillama.csv", newline="") as f:
        reader = csv.reader(f)
        for _ in range(5):
            next(reader)
        for item in reader:
            try:
                llama[item[1]] = (int(item[2]), float(item[5]))
            except (ValueError, IndexError):
                pass

    diffs = []
    for date in dates:
        if date in llama:
            diffs.append((date, graph[date][0] - llama[date][0],
                          graph[date][1] - llama[date][1]))
        else:
            diffs.append((date, 0, 0))

    print("Max difference:", max(diffs, key=lambda x: x[1]))
    out_path = BASE / "diff.txt"
    out_path.write_text(
        "".join(f"{d},{g},{l}\n" for d, g, l in diffs)
    )
    print(f"Wrote diff to {out_path}")


if __name__ == "__main__":
    main()
