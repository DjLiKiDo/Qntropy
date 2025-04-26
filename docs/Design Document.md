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

Qntropy is a software solution designed to consolidate cryptocurrency portfolios and generate accurate tax reports. The system imports transaction data from CSV files (currently focusing on Binance exchange data), reconciles all operations with final balances, and produces detailed fiscal reports compliant with tax regulations.

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
- Import transaction CSV files following the standard format provided by Cointracking.info
- Normalize data into a standard internal format
- Validate data integrity and completeness
- Support for future expansion to other exchanges/sources

### 3.2 Transaction Reconciliation

#### 3.2.1 Detecting Missing Transactions
- Process transactions chronologically
- Track running balances for each cryptocurrency
- Identify operations where balance is insufficient
- Generate adjustment operations to balance accounts
- Flag these synthetic operations for auditability

#### 3.2.2 Balance Consolidation
- Import final balances for each cryptocurrency from exchange
- Calculate theoretical balances based on processed transactions
- Compute discrepancies between actual and calculated balances
- Generate balancing operations to reconcile differences
- Flag these adjustment operations appropriately

### 3.3 Cost Basis Calculation
- For each transaction, determine entry and exit currencies
- Obtain market prices in EUR at transaction time using:
  - Historical price APIs
  - Price reference database
  - Calculated cross-rates when direct rates unavailable
- Calculate the cost basis for each position
- Implement different cost accounting methods (FIFO, LIFO, average cost)

## 4. Tax Calculation Logic

### 4.1 Taxable Events Identification
- Classify each transaction type (buy, sell, trade, transfer, staking, etc.)
- Determine which transactions constitute taxable events
- Calculate holding period for each position
- Apply appropriate tax treatment based on holding period

### 4.2 Gain/Loss Calculation
For each taxable event:
- Calculate proceeds (sale amount in EUR)
- Determine cost basis (purchase amount in EUR)
- Compute gain/loss (proceeds - cost basis)
- Classify as short-term or long-term based on holding period

### 4.3 Special Situations
- Handle staking rewards and income
- Account for airdrops and forks
- Process liquidations and margin trading
- Manage transaction fees and their tax treatment

## 5. Reporting Features

### 5.1 Tax Reports
- Annual summary of taxable events
- Detailed transaction lists with gain/loss calculations
- Form-specific outputs for tax filing
- Capital gains summary report

### 5.2 Portfolio Analytics
- Portfolio composition and historical value
- Performance metrics and unrealized gains
- Cost basis by asset
- Transaction activity summary

### 5.3 Audit Support
- Complete transaction audit trail
- Reconciliation reports
- Flagged transaction report (missing/adjusted entries)
- Data provenance tracking

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