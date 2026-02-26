import argparse
import sys
import logging
from decimal import Decimal
from pathlib import Path

from src.config_loader import load_tax_config
from src.loader.csv_loader import CSVLoader
from src.engine.reference_service import ReferenceDataService
from src.engine.fifo_engine import FifoEngine
from src.engine.tax_calculator import TaxCalculator
from src.reporter.excel_reporter import ExcelReporter
from src.reporter.pdf_reporter import PDFReporter


# -------------------------------------------------------
# Logging Configuration
# -------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# -------------------------------------------------------
# Reporter Factory (extensible)
# -------------------------------------------------------
REPORTERS = {
    "excel": ExcelReporter,
    "pdf": PDFReporter,
}


# -------------------------------------------------------
# Safe money formatting (no float conversion)
# -------------------------------------------------------
def format_money(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.01')):,.2f}"


# -------------------------------------------------------
# Argument Parsing
# -------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="TaxEngine — Foreign Equity Tax Calculation Engine"
    )

    parser.add_argument(
        "--trades",
        required=True,
        help="Path to trade history file (CSV or Excel)",
    )

    parser.add_argument(
        "--rates",
        default="examples/tcmb_rates.csv",
        help="Path to FX rate file (default: examples/tcmb_rates.csv)",
    )

    parser.add_argument(
        "--wpi",
        default="examples/tuik_wpi.csv",
        help="Path to WPI index file (default: examples/tuik_wpi.csv)",
    )

    parser.add_argument(
        "--config",
        default="config/tax_config_2025.yaml",
        help="Path to tax configuration file",
    )

    parser.add_argument(
        "--format",
        choices=REPORTERS.keys(),
        required=True,
        help="Report format",
    )

    parser.add_argument(
        "--output",
        default=None,
        help="Output filename (default: auto-generated)",
    )

    return parser.parse_args()


def print_banner():
    print("""
┌─────────────────────────────────────────┐
│  ████████╗ █████╗ ██╗  ██╗              │
│     ██╔══╝██╔══██╗╚██╗██╔╝              │
│     ██║   ███████║ ╚███╔╝  ENGINE       │
│     ██║   ██╔══██║ ██╔██╗               │
│     ██║   ██║  ██║██╔╝ ██╗              │
│     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝  v0.9.2      │
└─────────────────────────────────────────┘
  Foreign Equity Tax Calculator 
""")


# -------------------------------------------------------
# Main Execution
# -------------------------------------------------------
def main():
    print_banner()
    args = parse_args()

    # Validate critical file paths early
    for path_arg in [args.trades, args.rates, args.wpi, args.config]:
        if not Path(path_arg).exists():
            logger.error(f"File not found: {path_arg}")
            sys.exit(1)

    # --- Step 1: Load config ---
    logger.info("Loading tax configuration...")
    try:
        config = load_tax_config(args.config)
        logger.info(f"Fiscal year: {config['fiscal_year']} ✓")
    except Exception as e:
        logger.error(f"Failed to load configuration — {e}")
        sys.exit(1)

    # --- Step 2: Load trades ---
    logger.info("Loading trade history...")
    try:
        loader = CSVLoader()
        trades = loader.load(args.trades)
        logger.info(f"{len(trades)} trades loaded ✓")
    except Exception as e:
        logger.error(f"Trade loading failed — {e}")
        sys.exit(1)

    # --- Step 3: Load reference data ---
    logger.info("Loading reference data (FX & WPI)...")
    try:
        rds = ReferenceDataService(
            rates_path=args.rates,
            wpi_path=args.wpi,
        )
        logger.info("Reference data loaded ✓")
    except Exception as e:
        logger.error(f"Reference data loading failed — {e}")
        sys.exit(1)

    # --- Step 4: Process & report ---
    logger.info("Calculating tax and generating report...")
    try:
        engine = FifoEngine(rds, config)
        records = engine.process(trades)

        calculator = TaxCalculator(config)
        summary = calculator.calculate(records)

        # Output filename
        if args.output:
            output_path = args.output
        else:
            extension = "xlsx" if args.format == "excel" else "pdf"
            output_path = f"vergi_raporu_{config['fiscal_year']}.{extension}"

        reporter_class = REPORTERS[args.format]
        reporter = reporter_class()

        path = reporter.generate(summary, records, output_path)

        logger.info("Report successfully generated ✓")

    except Exception as e:
        logger.error(f"Processing failed — {e}")
        sys.exit(1)

    # --- Final Summary ---
    print("\n" + "=" * 50)
    print(f"  TaxEngine — {config['fiscal_year']} Summary")
    print("=" * 50)
    print(f"  Total Gain   : {format_money(summary['total_gain_tl']):>15} TL")
    print(f"  Total Loss   : {format_money(summary['total_loss_tl']):>15} TL")
    print(f"  Net Gain     : {format_money(summary['net_gain_tl']):>15} TL")
    print(f"  Taxable Base : {format_money(summary['taxable_base_tl']):>15} TL")
    print(f"  Estimated Tax: {format_money(summary['estimated_tax_tl']):>15} TL")
    print("=" * 50)
    print(f"\n  Report saved to: {path}\n")
    print("Advisory only. Consult a tax professional for official filing.\n")


if __name__ == "__main__":
    main()