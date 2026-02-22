# TaxEngine

A proof-of-concept tax calculation engine for foreign equity transactions,
compliant with Turkish income tax law 

Built as a demonstration of production-grade software engineering practices
for brokerage firm evaluation.

---

## Requirements

- Python 3.9+
- pip

---

## Installation
```bash
git clone https://github.com/your-username/TaxEngine.git
cd TaxEngine
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

---

## Usage
```bash
taxengine --trades <path> --format <excel|pdf> [options]
```

**Required arguments:**

| Argument | Description |
|----------|-------------|
| `--trades` | Path to trade history file (CSV or Excel) |
| `--format` | Report format: `excel` or `pdf` |

**Optional arguments:**

| Argument | Default | Description |
|----------|---------|-------------|
| `--rates` | `examples/tcmb_rates.csv` | CBRT FX rate file |
| `--wpi` | `examples/tuik_wpi.csv` | TURKSTAT WPI index file |
| `--config` | `config/tax_config_2025.yaml` | Tax configuration file |
| `--output` | Auto-generated | Output file name |

**Example:**
```bash
taxengine --trades examples/sample_trades.csv --format excel
taxengine --trades examples/sample_trades.csv --format pdf --output my_report.pdf
```
---

---

## Input File Format

Trade history CSV must contain the following columns:

| Column | Type | Example |
|--------|------|---------|
| `trade_date` | YYYY-MM-DD | `2024-03-15` |
| `ticker` | String | `AAPL` |
| `trade_type` | BUY / SELL | `BUY` |
| `quantity` | Decimal | `10` |
| `price_fc` | Decimal | `150.50` |
| `currency` | String | `USD` |

---

## Running Tests
```bash
pytest tests/ -v
```

---

## Project Structure
```
TaxEngine/
├── config/
│   └── tax_config_2025.yaml    # Tax brackets, WPI threshold, exemption limits
├── examples/
│   ├── sample_trades.csv       # Mock trade history (test data only)
│   ├── tcmb_rates.csv          # Mock CBRT FX rates (test data only)
│   └── tuik_wpi.csv            # Mock TURKSTAT WPI indices (test data only)
├── src/
│   ├── main.py                 # CLI entry point
│   ├── config_loader.py        # Decimal-safe YAML loader
│   ├── models/                 # Pydantic data models
│   ├── loader/                 # Data ingestion layer
│   ├── engine/                 # Business logic layer
│   └── reporter/               # Report generation layer
└── tests/
    ├── conftest.py
    └── engine/
        ├── test_fifo.py
        └── test_tax_calculator.py
```

---

## Disclaimer

This tool is for informational purposes only and does not constitute
official tax advice. Consult a certified tax professional (mali müşavir)
before filing your tax declaration.

## Example Data Disclaimer

The CSV files provided in the `examples/` directory are mock datasets
created for testing and demonstration purposes.

They do not represent official CBRT (TCMB) or TURKSTAT (TÜİK) data
and must not be used for real-world tax filings.

---

## Technical Notes

- All monetary calculations use Python `Decimal` — no floating point arithmetic.
- FIFO lot matching follows chronological ordering.
- WPI indexing applied when inflation ratio exceeds 10% threshold.
- Tax brackets configurable via `tax_config_2025.yaml` without code changes.