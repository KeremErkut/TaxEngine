# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### [0.9.0] - Planned 
#### Added
- **CLI Polish:** User-facing error messages and progress indicators in Turkish.
- **Demo Dataset:** Sample CSV file representing a realistic investor transaction history.
- **README:** Three-step setup and run guide for PoC presentation.

### [0.8.0] - Planned 
#### Added
- **Cross-Validation:** Manual verification of engine outputs against GIB sample tax declarations.
- **Unit Tests — FIFO:** Edge case coverage for partial lot matching, multi-year positions, and zero-gain years.
- **Unit Tests — Tax Calculator:** Threshold boundary tests for the 10% WPI indexing rule.

### [0.7.0] - Planned 
#### Added
- **Excel Reporter:** `excel_reporter.py` — Annual Tax Summary and Transaction Audit List in `.xlsx` format.
- **PDF Reporter:** `pdf_reporter.py` — Formatted compliance report for tax authority submission.
- **Session Termination:** All in-memory data cleared automatically upon process exit via Python garbage collection.

---

### [0.6.0] - 2026-02-21 
#### Added
- **ReferenceDataService:** `reference_service.py` — In-memory loader for CBRT (TCMB) FX rates and TURKSTAT (TÜİK) WPI indices with date-based lookup.
- **FIFO Engine:** `fifo_engine.py` — Chronological lot matching algorithm with partial fill support.
- **Tax Calculator:** `tax_calculator.py` — GVK 80-81 compliant indexing logic with 10% WPI threshold enforcement.

### [0.5.0] - 2026-02-21
#### Added
- **DataSource Interface:** `loader/base.py` — Abstract base class for future data source adapters.
- **CSV Loader:** `loader/csv_loader.py` — CSV/Excel ingestion with date normalization and schema validation.
- **Sample Dataset:** `examples/sample_trades.csv` — Mock dataset for testing.

### [0.4.0] - 2026-02-19
#### Added
- **Project Skeleton:** Modular folder structure (`models/`, `engine/`, `loader/`, `reporter/`, `config/`, `tests/`).
- **Trade Model:** `models/trade.py` — Pydantic model with `TradeType` enum and field-level validation.
- **FifoLot Model:** `models/fifo_lot.py` — Pydantic model with `is_depleted()` and `consume()` methods.
- **GainRecord Model:** `models/gain_record.py` — Pydantic model with `audit_note` for calculation transparency.
- **Tax Config:** `config/tax_config_2025.yaml` — Externalized income tax brackets, WPI threshold, and exemption limits for fiscal year 2025.
- **Config Loader:** `src/config_loader.py` — Decimal-safe YAML parser to prevent floating-point precision errors in tax calculations.

## [0.3.0] - 2026-02-18
#### Added
- **Software Design Specification (SDS):** Finalized technical blueprint for TaxEngine v0.3.0.
- **Architecture Strategy:** Established a **Modular Monolith** design to balance PoC speed with future microservice readiness.
- **Data Dictionary:** Defined structured objects for `Trade`, `FifoLot`, and `GainRecord` using high-precision Decimal types.
- **Sequence Diagrams:** Documented detailed interaction flows for Data Ingestion (UC1), Tax Calculation (UC2), and Report Generation (UC3).
- **Tax Logic & Algorithms:** Formalized FIFO matching logic and WPI-based cost indexing formulas in accordance with GVK Articles 80-81.
- **Design Tradeoffs:** Documented decisions on stateless RAM processing for maximum data privacy and CLI-first interaction.

## [0.2.0] - 2026-02-15
#### Added
- Comprehensive Software Requirements Specification (SRS) in English.
- Logical Data Model (ERD) for tax entities.
- Feature Tree & Sequence Diagram for PoC scope definition.
- Project versioning and structure established.

## [0.1.0] - 2026-02-12
#### Added
- Initial project concept and legal framework research.
- Basic SRS structure and purpose definition.

---

# References
[1] IEEE Std 830-1998 "IEEE Recommended Practice for Software Requirements Specifications"