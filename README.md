# defi-data-scraping

Scrapes and processes on-chain DeFi data from **AAVE V2** (and Compound, Euler, MakerDAO for comparison).
Produces 5-minute and hourly market snapshots — total deposits, borrow/deposit rates, utilization, user counts, HHI concentration index — as CSV files for client delivery.

## Project structure

```
defi-data-scraping/
├── config.py               # Shared config: tokens, API endpoints, data paths
├── requirements.txt
├── .env.example
│
├── src/
│   ├── fetchers/           # Pull raw data from The Graph / Alchemy
│   │   ├── base.py         # HTTP retry helper (exponential backoff)
│   │   ├── transactions.py # All AAVE V2 transaction types
│   │   ├── reserve_info.py # Block-level reserve state (rates, TVL)
│   │   ├── prices.py       # Token prices in ETH + USD/ETH rate
│   │   └── hash_to_block.py# Resolve tx hashes → block numbers (Alchemy)
│   │
│   ├── processors/         # Transform raw CSVs into clean data
│   │   ├── reserve.py      # Decimal conversion, APY calc, price/user merge
│   │   ├── transactions.py # Type classification, per-token filtering, dedup
│   │   ├── prices.py       # Merge, sort, interpolate, convert to USD
│   │   └── users.py        # Count depositors/borrowers, compute HHI
│   │
│   ├── aggregators/        # Build final output files
│   │   ├── timeseries.py   # Forward-fill snapshots at 5-min or 1-hour intervals
│   │   └── averages.py     # Daily averages from 5-min data
│   │
│   └── utils/
│       └── csv_io.py       # Shared CSV read/write helpers
│
├── notebooks/              # Jupyter notebooks for interactive exploration
├── protocols/              # Secondary protocol comparison scripts
│   ├── aave/               # AAVE protocol-level metrics (TVL, fees, market cap)
│   ├── aave_daily/         # AAVE daily aggregates
│   ├── compound/           # Compound protocol-level metrics
│   ├── compound_subgraph/  # Compound V2 DAI subgraph
│   ├── compound_v2/        # Compound V2 data + DeFiLlama comparison
│   ├── euler/              # Euler protocol daily data
│   └── maker_dao/          # MakerDAO protocol data
│
├── data/                   # Runtime data (gitignored)
│   ├── raw/                # Direct API output
│   ├── processed/          # After processor stages
│   └── output/             # Final CSVs for clients (5min/, 1hour/, daily/)
│
└── tests/
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and fill in API_KEY and ALCHEMY_URL
```

## Data pipeline

The final output is in `data/output/5min/<TOKEN>.csv` (5-minute market snapshots).

Run each stage in order, or use `--stage all` where available.

### Step 1 — Fetch transactions

```bash
# Fetch all AAVE V2 transaction types
python -m src.fetchers.transactions --type all

# Or fetch a single type with a custom time window
python -m src.fetchers.transactions --type borrow --start 1654016400 --end 1659286703
```

Outputs → `data/raw/transactions/`

### Step 2 — Classify and split transactions by token

```bash
python -m src.processors.transactions --stage all
```

Stages:
1. `sort` — sort all raw transaction files by timestamp
2. `classify` — match each `allTransaction` row to its specific type
3. `filter_by_token` — split into per-token files (DAI, WBTC, WETH, USDC, USDT)
4. `dedup_hashes` — deduplicate transaction hashes per token

Outputs → `data/processed/transactions/`, `data/processed/token_transactions/`, `data/processed/hash_to_block/`

### Step 3 — Resolve hashes to block numbers

```bash
python -m src.fetchers.hash_to_block
```

Requires `ALCHEMY_URL` in `.env`.
Output → `data/processed/hash_to_block/all.csv`

### Step 4 — Fetch reserve state per block

```bash
python -m src.fetchers.reserve_info --token DAI
# Repeat for each token
```

Requires a file of block numbers at `data/raw/reserve_info/<TOKEN>.txt`.
Output → `data/raw/reserve_info/<TOKEN>_info.csv`

### Step 5 — Fetch token prices

```bash
# Token price in ETH (for DAI, WBTC, USDC, USDT)
python -m src.fetchers.prices --type token_eth --token DAI

# USD/ETH price
python -m src.fetchers.prices --type usd_eth
```

Outputs → `data/raw/prices/`

### Step 6 — Process prices

```bash
python -m src.processors.prices --stage all
```

Stages: merge raw chunk files → sort + dedup → interpolate missing → convert to USD → derive WETH price.
Outputs → `data/processed/prices/`

### Step 7 — Count depositors, borrowers, and compute HHI

```bash
python -m src.processors.users --task count_depositors --token DAI
python -m src.processors.users --task count_borrowers  --token DAI
python -m src.processors.users --task calc_hhi         --token DAI
python -m src.processors.users --task user_count       --token DAI
# Repeat for each token
```

Outputs → `data/processed/depositors/`, `data/processed/borrowers/`, `data/processed/hhi/`, `data/processed/token_user_count/`

### Step 8 — Process reserve info

```bash
python -m src.processors.reserve --stage all
```

Stages:
1. `process_raw` — decimal conversion + APY calculation from raw subgraph data
2. `calc_market_size` — multiply total deposits by USD price (TVL in USD)
3. `merge_user_data` — attach userCount, HHI, depositors, borrowers per block
4. `add_prices` — append USD price column for the final full-info file

Outputs → `data/processed/reserve_info/`

### Step 9 — Generate time-series snapshots

```bash
# 5-minute snapshots (default)
python -m src.aggregators.timeseries --interval 5

# 1-hour snapshots
python -m src.aggregators.timeseries --interval 60
```

Output → `data/output/5min/<TOKEN>.csv` and `data/output/1hour/<TOKEN>.csv`

### Step 10 — Compute daily averages

```bash
python -m src.aggregators.averages
```

Output → `data/output/daily/<TOKEN>_average.csv`

---

## Data dependency graph

```
raw transactions
    └─ classify → allTransactionType.csv
         └─ filter_by_token → token_transactions/<TOKEN>.csv
              └─ dedup_hashes → hash_to_block/<TOKEN>_filtered.csv
                   └─ hash_to_block → all.csv

raw reserve_info/<TOKEN>_info.csv
    └─ process_raw → <TOKEN>_processed_info.csv
         └─ calc_market_size (needs <TOKEN>-usd-price.csv) → <TOKEN>_TLV_USD.csv
              └─ merge_user_data (needs userCount, HHI, depositors, borrowers) → <TOKEN>_info.csv
                   └─ add_prices (needs <TOKEN>-usd-price.csv) → <TOKEN>_full_info.csv
                        └─ timeseries → data/output/5min/<TOKEN>.csv
                             └─ averages → data/output/daily/<TOKEN>_average.csv
```

## Supported tokens

| Symbol | Decimals |
|--------|----------|
| DAI    | 18       |
| WBTC   | 8        |
| WETH   | 18       |
| USDC   | 6        |
| USDT   | 6        |

## Environment variables

| Variable      | Description                                              |
|---------------|----------------------------------------------------------|
| `API_KEY`     | The Graph API key (gateway-arbitrum.network.thegraph.com)|
| `ALCHEMY_URL` | Alchemy ETH mainnet node URL (for hash → block lookup)   |

## License

MIT © Viet Anh Tran
