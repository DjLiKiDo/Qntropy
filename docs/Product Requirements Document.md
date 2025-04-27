# Qntropy: Cryptocurrency Tax Reporting System - Product Requirements Document (PRD)

**Version:** 1.0
**Date:** 27 de abril de 2025

## 1. Introduction

Qntropy is a desktop software application designed to help Spanish cryptocurrency investors accurately calculate and report their crypto-related taxes (IRPF). It addresses the challenge of fragmented transaction data from various exchanges and wallets, incomplete transaction history, and the complexities of applying Spanish tax regulations (FIFO cost basis, specific treatment of staking/airdrops) to crypto assets. The system imports transaction data (primarily via Cointracking.info CSV format), reconciles it, calculates cost basis and taxable events, and generates reports suitable for supporting Spanish tax declarations. A key feature is its ability to handle incomplete data by generating synthetic transactions to ensure balance consistency, while clearly documenting these adjustments for transparency.

## 2. Goals

*   **Accurate Tax Calculation:** Provide reliable calculation of capital gains/losses (*Ganancias y Pérdidas Patrimoniales*) and income (*Rendimientos del Capital Mobiliario*) from cryptocurrency transactions according to Spanish tax law (IRPF), specifically using the FIFO accounting method.
*   **Data Consolidation:** Aggregate transaction data from various sources, starting with the Cointracking.info CSV format.
*   **Handle Incomplete Data:** Implement mechanisms to detect and compensate for missing transaction history by generating auditable synthetic transactions (balancing deposits/adjustments) based on balance checks and optional user-provided final balances.
*   **User-Friendly Reporting:** Generate clear, understandable reports detailing taxable events, calculations, and adjustments, suitable for use when filing the Spanish *Declaración de la Renta*.
*   **Auditability:** Maintain transparency by logging all processing steps, data sources, price lookups, and generated synthetic transactions.
*   **Local Processing:** Ensure user privacy and data security by performing all calculations locally on the user's machine.

## 3. User Personas

*   **DIY Investor (Spain):** An individual resident in Spain who actively trades cryptocurrencies on multiple exchanges and potentially uses DeFi protocols (staking/lending). They need an accurate way to calculate their tax obligations for their annual IRPF declaration but may have incomplete records from past activities or closed exchanges.
*   **Accountant/Tax Advisor (Spain):** A professional assisting Spanish clients with their tax filings. They need a reliable tool to process their clients' complex crypto transaction histories and generate compliant tax figures and supporting documentation.

## 4. User Stories / Features

**Phase 1: Core Infrastructure & Import**

*   As a user, I want to import my transaction history using a CSV file exported from Cointracking.info, so that the system can process my trades.
*   As a user, I want the system to validate the imported CSV data for correct formatting and plausible values, so that I am alerted to potential issues early.
*   As a developer, I need a well-defined project structure, dependency management (virtual environments), and basic CI/CD setup, so that the project is maintainable and follows best practices.
*   As a developer, I need clear data models to represent transactions internally, so that data handling is consistent.

**Phase 2: Transaction Reconciliation**

*   As a user, I want the system to process my transactions chronologically per asset, so that it can track running balances accurately.
*   As a user, I want the system to detect when a withdrawal transaction would result in a negative balance (indicating missing history), so that this gap can be addressed.
*   As a user, I want the system to automatically generate a synthetic "Balancing Deposit" with zero cost basis when an insufficient balance is detected, so that processing can continue and the tax calculation remains conservative.
*   As a user, I want the option to provide my known final asset balances at a specific date (e.g., year-end), so that the system can compare its calculated balances and make final adjustments.
*   As a user, I want the system to generate synthetic "Consolidation Adjustment" transactions if the calculated final balances don't match my provided actual balances, so that the final state reflects reality.
*   As a user, I want all synthetic/adjustment transactions to be clearly marked and explained in logs and reports, so that I understand how the system handled data gaps.

**Phase 3: Cost Basis & Tax Calculation**

*   As a user, I want the system to fetch historical cryptocurrency prices in EUR for the dates of my transactions, so that cost basis and proceeds can be calculated accurately.
*   As a user, I want the system to use a reliable price source (e.g., CoinGecko API) and cache prices, so that calculations are consistent and API usage is minimized.
*   As a user, I want the system to calculate the cost basis (*Valor de Adquisición*) for my disposed assets using the FIFO method, as required by Spanish tax law.
*   As a user, I want the system to correctly account for transaction fees (adding acquisition fees to cost basis, deducting disposal fees from proceeds).
*   As a user, I want the system to identify taxable events according to Spanish regulations (sales to fiat, crypto-to-crypto swaps, staking rewards, airdrops upon disposal).
*   As a user, I want the system to calculate capital gains/losses (*Ganancias y Pérdidas Patrimoniales*) for relevant disposals in EUR.
*   As a user, I want the system to calculate income (*Rendimientos del Capital Mobiliario*) from staking/lending rewards in EUR, based on the market value at the time of receipt.
*   As a user, I want the system to correctly treat airdrops (zero cost basis, gain realized on disposal) according to common Spanish tax interpretations.
*   As a user, I want the system to understand that transfers between my own wallets are not taxable events.

**Phase 4: Reporting**

*   As a user, I want to generate a Capital Gains/Losses report summarizing taxable events for my IRPF declaration (*Base Imponible del Ahorro*).
*   As a user, I want to generate an Income report summarizing staking/lending rewards for my IRPF declaration (*Base Imponible del Ahorro*).
*   As a user, I want a detailed transaction list showing all original and processed transactions, including cost basis, proceeds, gain/loss calculations, and flags for synthetic entries, for audit purposes.
*   As a user, I want to export these reports, potentially as CSV files, so I can use them for my tax filing or provide them to my accountant.
*   As a user, I want an audit report detailing the reconciliation process, including detected discrepancies and generated synthetic transactions.

## 5. Functional Requirements

### 5.1 Data Import
*   FR1.1: The system MUST support importing transaction data from CSV files adhering to the Cointracking.info "Trade Table (Full)" format.
*   FR1.2: The importer MUST parse required fields: Type, Buy Amount, Buy Currency, Sell Amount, Sell Currency, Fee Amount, Fee Currency, Exchange, Trade Group, Comment, Date.
*   FR1.3: The importer MUST convert imported data into a standardized internal `Transaction` model.
*   FR1.4: The importer MUST perform basic validation: check for missing required columns, validate date formats, check for numeric values in amount/fee columns.
*   FR1.5: The importer MUST log errors or warnings for invalid rows or data inconsistencies found during import.

### 5.2 Reconciliation Engine
*   FR2.1: The system MUST process transactions chronologically for each asset.
*   FR2.2: The system MUST maintain a running balance for each asset held by the user.
*   FR2.3: The system MUST detect insufficient balance situations prior to processing an outflow (sell, withdrawal, fee).
*   FR2.4: Upon detecting insufficient balance, the system MUST generate a synthetic "Balancing Deposit" transaction immediately preceding the problematic transaction.
*   FR2.5: The synthetic "Balancing Deposit" MUST have a cost basis of zero EUR.
*   FR2.6: The system MUST allow optional input of final asset balances provided by the user for a specific date.
*   FR2.7: The system MUST compare calculated final balances against user-provided balances (if supplied).
*   FR2.8: If discrepancies exist between calculated and provided final balances, the system MUST generate synthetic "Consolidation Adjustment" transactions (deposit or withdrawal) to align the balances.
*   FR2.9: All generated synthetic transactions MUST be clearly identifiable (e.g., via a specific type or note).

### 5.3 Pricing Engine
*   FR3.1: The system MUST fetch historical market prices for cryptocurrencies against EUR.
*   FR3.2: The system MUST use a configurable external API (default: CoinGecko or similar reliable source) for price data.
*   FR3.3: The system MUST implement caching for fetched prices to minimize API calls.
*   FR3.4: The system MUST handle cases where direct EUR prices are unavailable by attempting cross-rate calculations (e.g., ASSET -> USD -> EUR).
*   FR3.5: The system MUST define a fallback mechanism (e.g., log warning, use nearest available price, potentially allow user input in future) if price data cannot be obtained for a specific asset/time.

### 5.4 Tax Calculation Engine (Spain - IRPF)
*   FR4.1: The system MUST identify taxable events based on transaction types according to Spanish tax law:
    *   Capital Gains/Losses: Sale for fiat, Crypto-to-crypto swap.
    *   Income (Rendimientos del Capital Mobiliario): Staking rewards, Lending interest.
    *   Airdrops: Taxable as capital gain upon disposal (zero cost basis).
*   FR4.2: The system MUST identify non-taxable events: Buy with fiat, Transfers between own wallets.
*   FR4.3: The system MUST calculate the cost basis (*Valor de Adquisición*) for disposed assets using the FIFO method.
*   FR4.4: The cost basis calculation MUST include acquisition fees paid in EUR equivalent at the time of acquisition.
*   FR4.5: The system MUST calculate proceeds (*Valor de Transmisión*) in EUR based on the market value at the time of disposal.
*   FR4.6: The proceeds calculation MUST deduct disposal fees paid in EUR equivalent at the time of disposal.
*   FR4.7: The system MUST calculate the capital gain or loss (Proceeds - Cost Basis) in EUR for each disposal.
*   FR4.8: The system MUST calculate income from staking/lending based on the EUR market value at the time of receipt. The received asset forms a new lot with this value as its cost basis.
*   FR4.9: The system MUST determine the holding period for disposed assets (<= 12 months or > 12 months) for informational purposes (though both integrate into the *Base Imponible del Ahorro* in Spain).

### 5.5 Reporting
*   FR5.1: The system MUST generate a summary report of total Capital Gains and Losses, aggregated per tax year, suitable for the *Base Imponible del Ahorro* section of the IRPF.
*   FR5.2: The system MUST generate a summary report of total Income (*Rendimientos del Capital Mobiliario*), aggregated per tax year, suitable for the *Base Imponible del Ahorro* section of the IRPF.
*   FR5.3: The system MUST generate a detailed transaction report including:
    *   Original transaction details.
    *   Timestamp, Type, Assets involved, Amounts, Fees.
    *   Calculated Cost Basis (EUR).
    *   Calculated Proceeds (EUR).
    *   Calculated Gain/Loss (EUR).
    *   Flags/Notes indicating synthetic or adjusted transactions.
    *   Price source/value used.
*   FR5.4: The system MUST generate a Reconciliation/Audit report detailing:
    *   Detected insufficient balance events.
    *   Generated "Balancing Deposit" transactions.
    *   Final balance comparison (if user provided balances).
    *   Generated "Consolidation Adjustment" transactions.
*   FR5.5: The system MUST allow exporting generated reports to CSV format.

## 6. Non-Functional Requirements

*   **NFR1 (Performance):** The system should process a typical user's transaction history (e.g., several thousand transactions) within a reasonable timeframe (e.g., under 5 minutes) on standard desktop hardware.
*   **NFR2 (Accuracy):** Financial calculations (cost basis, gains/losses, income) must be accurate to a standard level of precision (e.g., 2 decimal places for EUR values, sufficient precision for crypto amounts). Calculations must strictly adhere to the specified tax logic (FIFO for Spain).
*   **NFR3 (Security/Privacy):** All user data (CSV files, calculated results) must be processed and stored locally on the user's machine. No sensitive financial data should be transmitted externally, except for anonymized requests to price APIs. API keys for price services should be configurable and stored securely if applicable.
*   **NFR4 (Usability):** The application should be usable via a Command Line Interface (CLI) initially. Error messages should be clear and guide the user towards resolving issues (e.g., formatting errors in CSV, missing price data).
*   **NFR5 (Maintainability):** The codebase must follow SOLID principles, include type hints, be well-documented, and have comprehensive test coverage (unit and integration tests). It should adhere to standard Python linting (ruff) and formatting (black) rules.
*   **NFR6 (Auditability):** All generated reports and logs must provide sufficient detail to trace calculations back to the source transactions and applied rules, including any synthetic adjustments made.
*   **NFR7 (Configuration):** Key parameters like the price API endpoint, API keys (if needed), and potentially fallback strategies should be configurable (e.g., via config file or environment variables).

## 7. Future Considerations / Out of Scope for v1.0

*   Graphical User Interface (GUI).
*   Direct API integration with exchanges/wallets.
*   Support for other cost basis methods (LIFO, HIFO, Average Cost).
*   Support for tax jurisdictions other than Spain.
*   Advanced tax optimization features (tax-loss harvesting).
*   Handling complex DeFi interactions (liquidity pools, complex derivatives) beyond simple staking/lending.
*   Detailed handling of margin trading specifics (interest payments, liquidations beyond standard gain/loss).
*   Generating specific tax forms (e.g., pre-filling Modelo 721 or IRPF sections).
*   Portfolio analytics features (charts, ROI).
*   Database backend (will use CSV output initially).

## 8. Release Criteria

*   All functional requirements for Phase 1-4 are implemented.
*   Comprehensive unit and integration tests pass, covering core logic, reconciliation, tax calculations (FIFO), and reporting for Spanish regulations.
*   Successful processing of representative test datasets, including cases with missing history requiring synthetic transactions.
*   Generated reports are verified for accuracy against manual calculations for test cases.
*   Core non-functional requirements (Performance on test data, Accuracy, Security/Privacy, Auditability) are met.
*   Basic documentation (README) explaining installation, usage, and limitations is available.
