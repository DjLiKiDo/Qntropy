# Qntropy: Cryptocurrency Tax Reporting System - Design Document

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Architecture and Technical Design](#2-architecture-and-technical-design)
   1. [Technical Stack](#21-technical-stack)
   2. [Directory Structure](#22-directory-structure)
   3. [Project Foundation](#23-project-foundation)
      1. [Project Bootstrapping](#231-project-bootstrapping)
      2. [Error Handling Strategy](#232-error-handling-strategy)
      3. [Logging Infrastructure](#233-logging-infrastructure)
      4. [Configuration Management](#234-configuration-management)
      5. [Common Utilities](#235-common-utilities)
3. [Core Functionality](#3-core-functionality)
   1. [Data Import](#31-data-import)
   2. [Transaction Reconciliation](#32-transaction-reconciliation)
      1. [Detecting Missing Transactions](#321-detecting-missing-transactions)
      2. [Balance Consolidation](#322-balance-consolidation)
   3. [Cost Basis Calculation](#33-cost-basis-calculation)
   4. [Handling Incomplete Data History](#34-handling-incomplete-data-history)
4. [Tax Calculation Logic](#4-tax-calculation-logic)
   1. [Taxable Events Identification](#41-taxable-events-identification)
   2. [Gain/Loss Calculation](#42-gainloss-calculation)
   3. [Special Situations](#43-special-situations)
5. [Reporting Features](#5-reporting-features)
   1. [Tax Reports](#51-tax-reports)
   2. [Portfolio Analytics](#52-portfolio-analytics)
   3. [Audit Support](#53-audit-support)
6. [Implementation Plan](#6-implementation-plan)
   1. [Phase 1: Core Infrastructure](#61-phase-1-core-infrastructure-weeks-1-2)
   2. [Phase 2: Transaction Reconciliation](#62-phase-2-transaction-reconciliation-weeks-3-4)
   3. [Phase 3: Cost and Tax Calculation](#63-phase-3-cost-and-tax-calculation-weeks-5-7)
   4. [Phase 4: Reporting](#64-phase-4-reporting-weeks-8-10)
7. [Future Enhancements](#7-future-enhancements)
   1. [Additional Data Sources](#71-additional-data-sources)
   2. [Advanced Features](#72-advanced-features)
8. [Technical Requirements](#8-technical-requirements)
   1. [Performance Considerations](#81-performance-considerations)
   2. [Security and Privacy](#82-security-and-privacy)
   3. [Testing Strategy](#83-testing-strategy)

## 1. Executive Summary

Qntropy is a software solution designed to consolidate cryptocurrency portfolios and generate accurate tax reports. The system imports transaction data primarily from CSV files formatted by Cointracking.info (which can include data from exchanges like Binance), reconciles all known operations against final balances, and generates synthetic transactions where necessary to account for incomplete data history (e.g., from lost exchange records). The goal is to produce detailed fiscal reports compliant with tax regulations, even with partial data.

This design document outlines the architecture, core functionality, implementation plan, and technical requirements for building the Qntropy system.

## 2. Architecture and Technical Design

### 2.1 Technical Stack
- **Language**: Python 3.10+ with type hints
- **Core Libraries**: 
  - pandas (for data processing)
  - pytest (for testing)
  - requests (for API interactions)
- **Architecture**: Modular design following SOLID principles
- **Data Storage**: 
  - CSV files for input
  - SQLite/CSV for processed data

### 2.2 Directory Structure
```
qntropy/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── src/
│   └── qntropy/
│       ├── importers/
│       ├── models/
│       ├── reconciliation/
│       ├── tax/
│       ├── api/
│       ├── utils/
│       └── cli/          # Typer/Click entry point
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── config/               # .env, settings.toml (opcional)
├── data/
│   ├── input/   (gitignored)
│   └── output/  (gitignored)
├── docs/
└── tools/                # scripts puntuales

```

### 2.3 Project Foundation

#### 2.3.1 Project Bootstrapping
- Initialize project with Poetry for dependency management
- Create standardized directory structure following the layout in section 2.2
- Set up Git repository with appropriate .gitignore file
- Configure pre-commit hooks for code quality checks
- Implement CI/CD pipeline with GitHub Actions
- Configure development tools:
  - ruff for linting
  - mypy for static type checking
  - black for code formatting
  - pytest for test execution

#### 2.3.2 Error Handling Strategy
- Define custom exception hierarchy:
  ```
  QntropyBaseException
  ├── ImporterException
  │   ├── CSVFormatException
  │   └── DataValidationException
  ├── ReconciliationException
  │   ├── InsufficientBalanceException
  │   └── UnreconcilableTransactionException
  ├── TaxCalculationException
  │   └── MissingPriceDataException
  └── ConfigurationException
  ```
- Implement error handling patterns:
  - Use context managers for resource management
  - Apply early returns to reduce nesting
  - Catch specific exceptions, not general ones
  - Log exceptions with appropriate context
  - Surface user-friendly error messages

#### 2.3.3 Logging Infrastructure
- Configure hierarchical loggers:
  - Root logger for application-wide events
  - Component-specific loggers (importer, reconciliation, tax)
- Implement log levels consistently:
  - DEBUG: Detailed information for developers
  - INFO: Normal application flow
  - WARNING: Non-critical issues
  - ERROR: Failures that allow continued operation
  - CRITICAL: Application-threatening issues
- Set up rotating file handlers with configurable retention
- Create separate logging for audit trail of financial calculations
- Ensure PII and sensitive financial data are never logged

#### 2.3.4 Configuration Management
- Implement layered configuration:
  - Default values in code
  - Configuration files (YAML/TOML)
  - Environment variables
  - Command-line arguments
- Create models for configuration settings with validation
- Support different environments (development, testing, production)
- Secure storage for API keys and sensitive settings

#### 2.3.5 Common Utilities
- Implement CSV safety tools to prevent formula injection
- Create data validation helpers for common operations
- Develop monetary and currency handling utilities
- Build date/time manipulation functions for timezone handling
- Design reusable data transformation patterns

## 3. Core Functionality

### 3.1 Data Import
- Implement a primary importer for CSV files generated by Cointracking.info. This format serves as the standard input.
- Normalize imported data into a consistent internal `Transaction` model (e.g., timestamp, transaction_type, asset_in, amount_in, asset_out, amount_out, fee_asset, fee_amount, exchange, notes).
- Perform initial data validation: check for required columns, correct data types, and plausible values.
- Explicitly handle and log potential data gaps or inconsistencies identified during import.

### 3.2 Transaction Reconciliation

#### 3.2.1 Detecting Missing Transactions
- Process transactions chronologically, grouped by asset.
- Maintain a running balance for each asset.
- When processing a withdrawal or trade (outflow), check if the calculated running balance is sufficient.
- If the balance is insufficient, flag this discrepancy. This often indicates missing deposit or trade history *prior* to the current transaction. The system will need to generate a synthetic "balancing deposit" transaction to proceed (see section 3.4).
- Log these detected insufficiencies clearly, pointing to the likely period of missing data.

#### 3.2.2 Balance Consolidation
- Optionally allow the user to provide final known balances for assets at a specific point in time (e.g., end of the tax year) via a separate file or input.
- After processing all known transactions, compare the calculated final balances against the user-provided actual balances.
- If discrepancies exist, generate final balancing adjustment transactions (deposits or withdrawals) to match the provided actual balances.
- Clearly label these adjustments as "Consolidation Adjustment" and log them for auditability. This helps align the calculated state with reality, especially when historical data is incomplete.

### 3.3 Cost Basis Calculation
- For each disposal transaction (sell, trade out), determine the cost basis of the disposed asset.
- Fetch historical market prices in the reporting currency (e.g., EUR) at the time of each relevant transaction (acquisition and disposal).
  - Prioritize reliable historical price APIs (e.g., CoinGecko, CoinMarketCap, specialized providers).
  - Implement caching for fetched prices to reduce API calls and costs.
  - Handle cases where direct EUR rates are unavailable by calculating cross-rates (e.g., BTC -> USD -> EUR).
  - Define fallback strategies if price data is missing (e.g., user input, nearest available price with warning).
- Implement selectable cost accounting methods, starting with FIFO (First-In, First-Out) as it's common, but allowing for future expansion (LIFO, HIFO, Average Cost).
- Accurately account for transaction fees as part of the cost basis or proceeds, according to tax regulations.

### 3.4 Handling Incomplete Data History
- **Problem:** Users may have lost transaction records from defunct exchanges or old wallets, leading to gaps in their transaction history. This manifests as insufficient balances when processing known withdrawals or discrepancies in final balances.
- **Solution Strategy:** The reconciliation process (3.2.1 and 3.2.2) is designed to mitigate this.
  - **Synthetic Deposits:** When an insufficient balance is detected (3.2.1), the system will generate a synthetic "Balancing Deposit" transaction immediately before the problematic withdrawal. This deposit will bring the balance up to the required amount.
    - The cost basis of this synthetic deposit will need careful consideration. Options include:
      - Zero cost basis (most conservative, maximizes potential gain later).
      - Estimated cost basis based on market price at that time (requires price fetching, potentially less conservative).
      - User-provided estimate (requires user interaction).
    - *Initial implementation likely uses zero cost basis for simplicity and conservatism.*
  - **Final Balance Adjustments:** Discrepancies found during final balance consolidation (3.2.2) also result in synthetic transactions. These adjust the final state to match known reality.
- **Auditability:** All generated synthetic transactions must be clearly flagged (e.g., in a 'notes' field or a dedicated flag) and included in audit reports, explaining *why* they were created (e.g., "Synthetic deposit created due to insufficient balance for withdrawal on YYYY-MM-DD", "Final balance adjustment based on user input"). This transparency is crucial for understanding the tax report's basis.

## 4. Tax Calculation Logic

### 4.1 Taxable Events Identification
- Define a mapping from Cointracking.info transaction types (and internal types) to taxable event categories (e.g., buy, sell, trade, staking reward, fee, transfer).
- Identify disposals (sell, trade where the asset is the 'out' currency) as primary taxable events triggering gain/loss calculation.
- Identify income events (staking rewards, airdrops classified as income).
- Determine the holding period for each disposed asset lot based on the acquisition date (from actual or synthetic transactions) and disposal date. Classify as short-term or long-term based on regulatory thresholds (e.g., 1 year).

### 4.2 Gain/Loss Calculation
For each taxable disposal event:
- Calculate **Proceeds**: Amount of asset received * market price in EUR at transaction time.
- Determine **Cost Basis**: Cost basis of the specific lot(s) being disposed of (calculated in 3.3 using FIFO/etc.) in EUR.
- Compute **Gain/Loss**: Proceeds - Cost Basis.
- Factor in **Fees**: Adjust proceeds or cost basis based on how fees are treated (e.g., selling fees reduce proceeds, buying fees add to cost basis).
- Aggregate gains/losses, categorized by short-term and long-term.

### 4.3 Special Situations
- **Staking Rewards/Interest**: Treat as income at the time received, valued at the market price in EUR. These rewards then form a new lot with a cost basis equal to the income recognized.
- **Airdrops/Forks**: Treatment varies by jurisdiction. May be income upon receipt or have a zero cost basis until sold. Implement based on target jurisdiction rules (initially, potentially zero cost basis).
- **Transfers (Internal)**: Generally not taxable events, but fees associated might be deductible or capitalized depending on context. Track transfers accurately for balance reconciliation.
- **Margin Trading/Liquidations**: More complex; defer to future enhancements unless specifically required initially. Mark these transactions if identifiable.
- **Transaction Fees**: Ensure consistent handling (add to basis on acquisition, deduct from proceeds on disposal, or potentially expense if related to income generation like staking).

## 5. Reporting Features

### 5.1 Tax Reports
- **Capital Gains Report**: Summary of short-term and long-term capital gains/losses, aggregated by asset.
- **Income Report**: Summary of income from staking, airdrops, etc.
- **Detailed Transaction List**: Chronological list of all transactions, including calculated cost basis, proceeds, gain/loss for taxable events, and flags for synthetic/adjusted entries. Essential for audit.
- **Form-Specific Data (Future)**: Output data formatted to assist filling specific tax forms (e.g., Form 8949 for US, specific schedules for other countries).

### 5.2 Portfolio Analytics (Optional/Future)
- Current portfolio holdings and value (requires real-time price fetching).
- Historical portfolio value chart.
- Unrealized gains/losses summary.
- Performance metrics (ROI).

### 5.3 Audit Support
- **Reconciliation Report**: Details discrepancies found and adjustments made (synthetic transactions generated during insufficient balance checks and final consolidation).
- **Complete Transaction Log**: Export of all processed transactions, including original data and calculated values (basis, proceeds, gain/loss).
- **Price Source Log**: Record of which price sources and values were used for calculations.
- **Data Provenance**: Clear indication of the source file for each transaction.

## 6. Implementation Plan

### 6.1 Phase 1: Core Infrastructure (Weeks 1-2)
- [ ] Set up project structure and repository
- [ ] Configure development environment (virtual env, dependencies)
- [ ] Implement data models for transactions
- [ ] Create CSV importers for Binance format
- [ ] Develop basic validation for imported data
- [ ] Write unit tests for core components

### 6.2 Phase 2: Transaction Reconciliation (Weeks 3-4)
- [ ] Develop balance tracking system
- [ ] Implement missing transaction detection algorithm
- [ ] Create balance consolidation logic
- [ ] Build adjustment transaction generator
- [ ] Test with sample datasets

### 6.3 Phase 3: Cost and Tax Calculation (Weeks 5-7)
- [ ] Integrate with price data sources
- [ ] Implement cost basis calculation modules
- [ ] Develop tax event identification logic
- [ ] Create gain/loss calculation engine
- [ ] Implement different accounting methods (FIFO/LIFO)
- [ ] Build comprehensive test suite for tax calculations

### 6.4 Phase 4: Reporting (Weeks 8-10)
- [ ] Design report templates
- [ ] Create tax report generators
- [ ] Implement transaction audit trail
- [ ] Develop data visualization components
- [ ] Build export functionality for various formats
- [ ] Complete end-to-end testing

## 7. Future Enhancements

### 7.1 Additional Data Sources
- Support for other exchanges beyond Binance
- Wallet transaction imports
- Blockchain transaction scanning

### 7.2 Advanced Features
- Tax-loss harvesting recommendations
- Scenario planning for tax optimization
- Multi-country tax support
- Integration with tax filing software

## 8. Technical Requirements

### 8.1 Performance Considerations
- Efficient processing of large transaction volumes
- Optimization for memory usage with large datasets
- Incremental processing support

### 8.2 Security and Privacy
- Secure handling of financial data
- Local processing to maintain privacy
- No transmission of sensitive information

### 8.3 Testing Strategy
- Comprehensive unit tests for tax calculations
- Integration tests for data import/export
- Example datasets for validation