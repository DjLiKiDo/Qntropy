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
  - requests (for external API interactions, e.g., price fetching)
- **Architecture**: Modular design following SOLID principles
- **Data Storage**: 
  - CSV files for input data.
  - **Processed Data**: Initially, processed data (reconciled transactions, calculated basis, etc.) will be stored in CSV files within the `data/output/` directory. This allows for a simpler initial implementation. A database solution (e.g., SQLite or PostgreSQL) will be considered for future enhancements to handle larger datasets and more complex queries more efficiently.

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
│       ├── external_apis/  # Clients for external services (e.g., price APIs)
│       ├── utils/
│       └── cli/          # Typer/Click entry point
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── config/               # .env, settings.toml (opcional)
├── data/
│   ├── input/   (gitignored) # Source CSV files (e.g., Cointracking exports)
│   └── output/  (gitignored) # Generated CSV files with processed data and reports
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
    - The cost basis of this synthetic deposit requires careful consideration. Options include:
      - Zero cost basis (most conservative, maximizes potential gain later).
      - Estimated cost basis based on market price at that time (requires price fetching, potentially less conservative).
      - User-provided estimate (requires user interaction).
    - **Initial Implementation:** The initial implementation **will use a zero cost basis** for these synthetic deposits. This is the most conservative approach from a tax perspective, as it assumes the highest possible capital gain when the asset associated with this synthetic deposit is eventually disposed of. Future enhancements might allow for alternative methods or user overrides.
  - **Final Balance Adjustments:** Discrepancies found during final balance consolidation (3.2.2) also result in synthetic transactions. These adjust the final state to match known reality.
- **Auditability:** All generated synthetic transactions must be clearly flagged (e.g., in a 'notes' field or a dedicated flag) and included in audit reports, explaining *why* they were created (e.g., "Synthetic deposit (zero cost basis) created due to insufficient balance for withdrawal on YYYY-MM-DD", "Final balance adjustment based on user input"). This transparency is crucial for understanding the tax report's basis.

## 4. Tax Calculation Logic

**Target Jurisdiction: Spain**

The initial implementation will focus on calculating cryptocurrency taxes according to Spanish regulations (IRPF - Impuesto sobre la Renta de las Personas Físicas). All calculations and reporting will be based on the rules applicable in Spain, with amounts expressed in EUR.

### 4.1 Taxable Events Identification
- Define a mapping from Cointracking.info transaction types (and internal types) to taxable event categories under Spanish law.
- **Primary Taxable Events (Capital Gains/Losses - *Ganancias y Pérdidas Patrimoniales*):**
    - Sale of cryptocurrency for fiat currency (e.g., BTC -> EUR).
    - Exchange of one cryptocurrency for another (e.g., BTC -> ETH). These "swaps" are considered disposals of the first asset and acquisitions of the second.
- **Income Events (*Rendimientos del Capital Mobiliario* or other income types):**
    - Staking rewards, interest earned from lending crypto.
    - Airdrops (treatment can vary, often considered a capital gain with zero acquisition cost upon disposal, but specific guidance should be monitored).
- **Non-Taxable Events (Generally):**
    - Buying cryptocurrency with fiat.
    - Transfers between own wallets/exchanges (*Permutas*).
- **Holding Period:** Determine the holding period for each disposed asset lot. In Spain, gains/losses are classified based on whether the asset was held for **more than 12 months** (long-term, integrated into the *Base Imponible del Ahorro*) or **12 months or less** (short-term, also integrated into the *Base Imponible del Ahorro*). *Note: Historically, short-term gains went to the general base, but recent changes integrate both into the savings base.*

### 4.2 Gain/Loss Calculation
For each taxable disposal event (*Ganancia o Pérdida Patrimonial*):
- Calculate **Proceeds (*Valor de Transmisión*)**: Amount of asset received * market price in EUR at transaction time. For crypto-to-crypto swaps, this is the fair market value in EUR of the crypto received.
- Determine **Cost Basis (*Valor de Adquisición*)**: Cost basis of the specific lot(s) being disposed of (calculated in 3.3 using FIFO, as it's the method mandated by Spanish tax authorities - *Dirección General de Tributos*) in EUR. This includes the purchase price and associated non-deductible acquisition costs (e.g., purchase fees).
- Compute **Gain/Loss**: Proceeds - Cost Basis.
- Factor in **Fees**:
    - Acquisition fees (e.g., trading fees paid when buying) are added to the Cost Basis.
    - Disposal fees (e.g., trading fees paid when selling/swapping) are deducted from the Proceeds.
- Aggregate gains/losses. In Spain, all capital gains/losses from crypto (both short and long-term) are integrated into the *Base Imponible del Ahorro* and taxed at progressive rates (e.g., 19% up to €6,000, 21% from €6,000 to €50,000, etc. - rates subject to change). Net losses can potentially offset other capital gains within the savings base, subject to limitations.

### 4.3 Special Situations
- **Staking Rewards/Interest**: Generally treated as *Rendimientos del Capital Mobiliario* (Income from Movable Capital) in Spain. Taxable upon receipt, valued at the market price in EUR at that time. This income is integrated into the *Base Imponible del Ahorro*. The received crypto forms a new lot with a cost basis equal to the income recognized.
- **Airdrops/Forks**: Spanish tax authorities often consider these as generating a capital gain upon disposal, with an acquisition value (cost basis) of zero. The full proceeds (less disposal fees) become the taxable gain, integrated into the *Base Imponible del Ahorro*.
- **Transfers (Internal)**: Transfers between an individual's own accounts or wallets (*permutas*) are not taxable events in Spain. However, associated transaction fees (e.g., network fees) might not be directly deductible but could potentially be factored into the cost basis or proceeds of a later taxable event if directly related. Accurate tracking is vital for reconciliation.
- **Margin Trading/Liquidations**: Complex. Liquidations trigger standard capital gain/loss calculations. Margin interest paid might not be deductible. Defer detailed handling unless specifically required.
- **Transaction Fees**: As detailed in 4.2, acquisition fees increase cost basis, and disposal fees decrease proceeds. Network fees for non-taxable transfers are generally not directly deductible against income or gains.

## 5. Reporting Features

### 5.1 Tax Reports
- **Capital Gains Report (*Ganancias y Pérdidas Patrimoniales*)**: Summary of gains and losses integrated into the *Base Imponible del Ahorro*, potentially distinguishing between acquisition dates for informational purposes, aggregated by asset. Essential for the *Declaración de la Renta* (IRPF).
- **Income Report (*Rendimientos del Capital Mobiliario*)**: Summary of income from staking, lending, etc., also integrated into the *Base Imponible del Ahorro*.
- **Detailed Transaction List**: Chronological list of all transactions, including calculated cost basis (*Valor de Adquisición*), proceeds (*Valor de Transmisión*), gain/loss for taxable events, and flags for synthetic/adjusted entries. Crucial for audit and supporting the IRPF declaration.
- **Form-Specific Data (Future)**: Output data formatted to assist filling specific sections of the Spanish *Declaración de la Renta* (IRPF). Data might also be relevant for *Modelo 721* (informative declaration of virtual currencies held abroad), although Qntropy focuses on calculating gains/income, not just reporting holdings.

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
- [ ] Create CSV importers for Cointracking.info format
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