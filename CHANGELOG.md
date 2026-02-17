# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### [0.4.0] - Planned
#### Added
- **Base Engine Implementation:** Core Python logic for financial processing.
- **Data Models:** Development of `Trade` and `FifoLot` classes with Pydantic validation.
- **Core FIFO Algorithm:** Implementation of the initial matching logic for sell transactions.
- **Mock Data Generator:** A utility to create sample CSV files for testing the base engine.

## [0.3.0] - 2026-02-18
#### Added
- **Design Tradeoffs:** Documented decisions on stateless RAM processing for maximum data privacy and CLI-first interaction.
- **Software Design Specification (SDS):** Finalized technical blueprint for TaxEngine.
- **Architecture Strategy:** Established a **Modular Monolith** design to balance PoC speed with future microservice readiness.
- **Data Dictionary:** Defined structured objects for `Trade`, `FifoLot`, and `GainRecord` using high-precision Decimal types.
- **Sequence Diagrams:** Documented detailed interaction flows for Data Ingestion (UC1), Tax Calculation (UC2), and Report Generation (UC3).
- **Tax Logic & Algorithms:** Formalized FIFO matching logic and WPI-based cost indexing formulas in accordance with GVK 80-81.
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
- [cite_start]Basic SRS structure and purpose definition[cite: 1].

# References
[1] IEEE Std 830-1998 "IEEE Recommended Practice for Software Requirements Specifications"