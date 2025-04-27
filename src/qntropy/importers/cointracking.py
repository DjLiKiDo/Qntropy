"""Importer for Cointracking.info CSV files."""

import csv
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

import pandas as pd

from qntropy.models.transaction import (
    Asset,
    AssetAmount,
    Transaction,
    TransactionType,
)
from qntropy.utils.exceptions import CSVFormatException, DataValidationException

logger = logging.getLogger(__name__)


class CointrackingImporter:
    """Importer for Cointracking.info CSV files."""

    # Mapping from Cointracking.info transaction types to our internal types
    TRANSACTION_TYPE_MAPPING = {
        "Trade": TransactionType.TRADE,
        "Deposit": TransactionType.DEPOSIT,
        "Withdrawal": TransactionType.WITHDRAWAL,
        "Staking": TransactionType.STAKING_REWARD,
        "Interest": TransactionType.INTEREST,
        "Airdrop": TransactionType.AIRDROP,
        "Mining": TransactionType.MINING,
        "Transfer": TransactionType.TRANSFER,
        "Buy": TransactionType.BUY,
        "Sell": TransactionType.SELL,
    }

    # Mapping CSV column names from CoinTracking to our expected names
    COLUMN_MAPPING = {
        "Cur.": "Buy Currency",
        "Cur..1": "Sell Currency",
        "Cur..2": "Fee Currency",
        "Buy": "Buy Amount",
        "Sell": "Sell Amount"
    }

    # Required columns in the CSV file
    REQUIRED_COLUMNS = [
        "Type", 
        "Buy Amount", 
        "Buy Currency", 
        "Sell Amount", 
        "Sell Currency", 
        "Fee", 
        "Fee Currency", 
        "Exchange", 
        "Group", 
        "Comment", 
        "Date"
    ]

    # Date formats supported by Cointracking.info
    DATE_FORMATS = [
        "%Y-%m-%d %H:%M:%S",  # 2023-01-15 14:30:25
        "%d.%m.%Y %H:%M",     # 15.01.2023 14:30
        "%Y-%m-%dT%H:%M:%S",  # 2023-01-15T14:30:25
        "%d/%m/%Y %H:%M:%S",  # 15/01/2023 14:30:25
        "%d-%m-%Y %H:%M:%S",  # 15-01-2023 14:30:25
    ]

    def __init__(self, skip_invalid_rows: bool = False) -> None:
        """
        Initialize the importer.
        
        Args:
            skip_invalid_rows: If True, skip invalid rows instead of failing the entire import.
        """
        self.skip_invalid_rows = skip_invalid_rows

    def import_file(self, file_path: Path) -> List[Transaction]:
        """
        Import transactions from a Cointracking.info CSV file.
        
        Args:
            file_path: Path to the CSV file.
            
        Returns:
            List of Transaction objects.
            
        Raises:
            CSVFormatException: If the CSV file is malformed or missing required columns.
            DataValidationException: If the data in the CSV file is invalid and skip_invalid_rows is False.
        """
        logger.info(f"Importing transactions from {file_path}")
        
        if not file_path.exists():
            raise CSVFormatException(f"File not found: {file_path}")
            
        try:
            # Use pandas to read the CSV file
            df = pd.read_csv(file_path)
            
            # Rename columns based on the mapping
            df_columns = list(df.columns)
            for csv_col, expected_col in self.COLUMN_MAPPING.items():
                if csv_col in df_columns and expected_col not in df_columns:
                    df = df.rename(columns={csv_col: expected_col})
            
            # Check if required columns exist in the DataFrame
            missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
            if missing_columns:
                raise CSVFormatException(
                    f"Missing required columns in CSV: {', '.join(missing_columns)}"
                )
            
            # Convert DataFrame rows to Transaction objects
            transactions = []
            invalid_rows = []
            
            for idx, row in df.iterrows():
                # Parse row
                line_number = idx + 2  # +2 because idx is 0-based and there's a header row
                try:
                    # Apply additional data cleaning
                    row = self._clean_row_data(row)
                    
                    # Validate row has the minimal required data
                    self._validate_row_basic_requirements(row)
                    
                    transaction = self._parse_row(row, file_path.name, line_number)
                    transactions.append(transaction)
                except Exception as e:
                    # Record error information
                    error_msg = f"Error in row {line_number}: {str(e)}"
                    invalid_rows.append((line_number, error_msg))
                    
                    if not self.skip_invalid_rows:
                        if isinstance(e, DataValidationException):
                            raise DataValidationException(error_msg) from e
                        else:
                            raise DataValidationException(f"Unexpected error processing row {line_number}: {str(e)}") from e
                    else:
                        # Log the error but continue processing
                        logger.warning(error_msg)
            
            # Report on the import results
            if invalid_rows:
                logger.warning(f"Skipped {len(invalid_rows)} invalid rows during import")
                for line, error in invalid_rows:
                    logger.debug(f"  Line {line}: {error}")
            
            logger.info(f"Successfully imported {len(transactions)} transactions from {file_path}")
            
            if len(transactions) == 0 and len(invalid_rows) > 0:
                logger.error("No valid transactions were found in the file")
                raise DataValidationException(f"No valid transactions found in {file_path}. All {len(invalid_rows)} rows had validation errors.")
                
            return transactions
            
        except pd.errors.EmptyDataError:
            raise CSVFormatException(f"The CSV file {file_path} is empty")
        except pd.errors.ParserError:
            raise CSVFormatException(f"Error parsing CSV file {file_path}")
        except Exception as e:
            if isinstance(e, (CSVFormatException, DataValidationException)):
                # Re-raise the exception without modifying it
                raise
            else:
                # Convert other exceptions to CSVFormatException
                raise CSVFormatException(f"Unexpected error reading CSV file {file_path}: {str(e)}")
    
    def _clean_row_data(self, row: pd.Series) -> pd.Series:
        """
        Clean and normalize row data before parsing.
        
        Args:
            row: Pandas Series representing a row from the CSV.
            
        Returns:
            Cleaned row data.
        """
        # Create a copy to avoid modifying the original DataFrame
        cleaned_row = row.copy()
        
        # Strip whitespace from string columns
        for col in cleaned_row.index:
            if isinstance(cleaned_row[col], str):
                cleaned_row[col] = cleaned_row[col].strip()
        
        return cleaned_row
    
    def _validate_row_basic_requirements(self, row: pd.Series) -> None:
        """
        Validate that a row meets basic requirements before detailed parsing.
        
        Args:
            row: Pandas Series representing a row from the CSV.
            
        Raises:
            DataValidationException: If the row doesn't meet basic requirements.
        """
        # Check that the row has a valid type
        if pd.isna(row["Type"]) or not row["Type"]:
            raise DataValidationException("Transaction type is missing")
        
        # Check that the row has at least one valid asset (buy or sell)
        has_buy = pd.notna(row["Buy Amount"]) and pd.notna(row["Buy Currency"]) and self._is_positive_number(row["Buy Amount"])
        has_sell = pd.notna(row["Sell Amount"]) and pd.notna(row["Sell Currency"]) and self._is_positive_number(row["Sell Amount"])
        
        if not (has_buy or has_sell):
            raise DataValidationException("Transaction must have at least one valid asset (buy or sell)")
            
        # Check transaction type consistency with data
        self._validate_transaction_type_consistency(row)

    def _is_positive_number(self, value) -> bool:
        """
        Check if a value represents a positive number.
        
        Args:
            value: Value to check.
            
        Returns:
            True if the value is a positive number, False otherwise.
        """
        try:
            # Replace comma with dot for decimal separator if it's a string
            if isinstance(value, str):
                value = value.replace(',', '.')
            
            num_value = float(value)
            return num_value > 0
        except (ValueError, TypeError):
            return False
    
    def _validate_transaction_type_consistency(self, row: pd.Series) -> None:
        """
        Validate that the transaction type is consistent with the data in the row.
        
        Args:
            row: Pandas Series representing a row from the CSV.
            
        Raises:
            DataValidationException: If the transaction type is inconsistent with the data.
        """
        ct_type = row["Type"]
        has_buy = pd.notna(row["Buy Amount"]) and pd.notna(row["Buy Currency"]) and self._is_positive_number(row["Buy Amount"])
        has_sell = pd.notna(row["Sell Amount"]) and pd.notna(row["Sell Currency"]) and self._is_positive_number(row["Sell Amount"])
        
        # Type-specific validations
        if ct_type == "Buy" and not has_buy:
            raise DataValidationException("Buy transaction must have valid buy amount and currency")
        elif ct_type == "Sell" and not has_sell:
            raise DataValidationException("Sell transaction must have valid sell amount and currency")
        elif ct_type == "Trade" and not (has_buy and has_sell):
            raise DataValidationException("Trade transaction must have both valid buy and sell data")
        elif ct_type in ["Deposit", "Staking", "Interest", "Airdrop", "Mining"] and not has_buy:
            raise DataValidationException(f"{ct_type} transaction must have valid buy amount and currency")
        elif ct_type == "Withdrawal" and not has_sell:
            raise DataValidationException("Withdrawal transaction must have valid sell amount and currency")

    def _parse_row(self, row: pd.Series, source_file: str, line_number: int) -> Transaction:
        """
        Parse a row from the CSV file into a Transaction object.
        
        Args:
            row: Pandas Series representing a row from the CSV.
            source_file: Name of the source file.
            line_number: Line number in the source file.
            
        Returns:
            Transaction object.
            
        Raises:
            DataValidationException: If the data in the row is invalid.
        """
        try:
            # Parse date
            date_str = row["Date"]
            timestamp = self._parse_date(date_str)

            # Determine transaction type
            ct_type = row["Type"]
            transaction_type = self._determine_transaction_type(ct_type, row)

            # Parse buy (incoming) asset
            asset_in = None
            if pd.notna(row["Buy Amount"]) and pd.notna(row["Buy Currency"]) and self._is_positive_number(row["Buy Amount"]):
                buy_amount = self._parse_decimal(row["Buy Amount"], "Buy Amount")
                buy_currency = row["Buy Currency"].strip()
                asset_in = AssetAmount(
                    asset=Asset(symbol=buy_currency),
                    amount=buy_amount
                )

            # Parse sell (outgoing) asset
            asset_out = None
            if pd.notna(row["Sell Amount"]) and pd.notna(row["Sell Currency"]) and self._is_positive_number(row["Sell Amount"]):
                sell_amount = self._parse_decimal(row["Sell Amount"], "Sell Amount")
                sell_currency = row["Sell Currency"].strip()
                asset_out = AssetAmount(
                    asset=Asset(symbol=sell_currency),
                    amount=sell_amount
                )

            # Parse fee
            fee = None
            if pd.notna(row["Fee"]) and pd.notna(row["Fee Currency"]) and self._is_positive_number(row["Fee"]):
                fee_amount = self._parse_decimal(row["Fee"], "Fee")
                fee_currency = row["Fee Currency"].strip()
                fee = AssetAmount(
                    asset=Asset(symbol=fee_currency),
                    amount=fee_amount
                )

            # Create the transaction
            transaction = Transaction(
                timestamp=timestamp,
                transaction_type=transaction_type,
                asset_in=asset_in,
                asset_out=asset_out,
                fee=fee,
                exchange=row["Exchange"] if pd.notna(row["Exchange"]) else None,
                trade_group=row["Group"] if pd.notna(row["Group"]) else None,
                notes=row["Comment"] if pd.notna(row["Comment"]) else None,
                source_file=source_file,
                source_line=line_number
            )
            
            # Final validation of the transaction
            self._validate_created_transaction(transaction)
            
            return transaction

        except DataValidationException:
            # Re-raise validation exceptions without modification
            raise
        except Exception as e:
            # Convert other exceptions to DataValidationException
            raise DataValidationException(f"Error parsing row: {str(e)}")
            
    def _determine_transaction_type(self, ct_type: str, row: pd.Series) -> TransactionType:
        """
        Determine the transaction type based on the Cointracking type and row data.
        
        Args:
            ct_type: Cointracking transaction type.
            row: Row data.
            
        Returns:
            Determined TransactionType.
        """
        # Direct mapping if available
        if ct_type in self.TRANSACTION_TYPE_MAPPING:
            return self.TRANSACTION_TYPE_MAPPING[ct_type]
        
        # Fallback logic for unknown types
        has_buy = pd.notna(row["Buy Amount"]) and self._is_positive_number(row["Buy Amount"])
        has_sell = pd.notna(row["Sell Amount"]) and self._is_positive_number(row["Sell Amount"])
        
        if has_buy and has_sell:
            logger.warning(f"Unknown transaction type: {ct_type}, defaulting to TRADE")
            return TransactionType.TRADE
        elif has_buy:
            logger.warning(f"Unknown transaction type: {ct_type}, defaulting to BUY")
            return TransactionType.BUY
        elif has_sell:
            logger.warning(f"Unknown transaction type: {ct_type}, defaulting to SELL")
            return TransactionType.SELL
        else:
            # This shouldn't happen due to prior validation, but just in case
            logger.warning(f"Unknown transaction type with no clear assets: {ct_type}, defaulting to TRADE")
            return TransactionType.TRADE

    def _validate_created_transaction(self, transaction: Transaction) -> None:
        """
        Validate that a created transaction is logically consistent.
        
        Args:
            transaction: Transaction to validate.
            
        Raises:
            DataValidationException: If the transaction is not valid.
        """
        # Validate that the transaction has the right assets for its type
        if transaction.transaction_type in [TransactionType.BUY, TransactionType.DEPOSIT, TransactionType.STAKING_REWARD,
                                          TransactionType.INTEREST, TransactionType.AIRDROP, TransactionType.MINING] and not transaction.asset_in:
            raise DataValidationException(f"{transaction.transaction_type.value} transaction must have an incoming asset")
            
        if transaction.transaction_type in [TransactionType.SELL, TransactionType.WITHDRAWAL] and not transaction.asset_out:
            raise DataValidationException(f"{transaction.transaction_type.value} transaction must have an outgoing asset")
            
        if transaction.transaction_type == TransactionType.TRADE and (not transaction.asset_in or not transaction.asset_out):
            raise DataValidationException("Trade transaction must have both incoming and outgoing assets")

    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse a date string into a datetime object.
        
        Args:
            date_str: Date string to parse.
            
        Returns:
            Parsed datetime object.
            
        Raises:
            DataValidationException: If the date string cannot be parsed.
        """
        if not date_str or not isinstance(date_str, str):
            raise DataValidationException(f"Invalid date string: {date_str}")
        
        # Strip whitespace
        date_str = date_str.strip()
        
        format_errors = []
        
        # Try each format in order
        for fmt in self.DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError as e:
                # In Python 3.11, ValueError has better error messages
                format_errors.append(f"Format {fmt}: {str(e)}")
                continue
        
        # If we get here, none of the formats worked
        error_msg = "Could not parse date string. Tried the following formats:\n"
        error_msg += "\n".join(format_errors)
        raise DataValidationException(f"Invalid date format '{date_str}': {error_msg}")

    def _parse_decimal(self, value: str, field_name: str) -> Decimal:
        """
        Parse a string value into a Decimal, with validation.
        
        Args:
            value: String value to parse.
            field_name: Name of the field for error reporting.
            
        Returns:
            Decimal value.
            
        Raises:
            DataValidationException: If the value cannot be parsed as a Decimal.
        """
        try:
            # Replace comma with dot for decimal separator
            if isinstance(value, str):
                value = value.replace(',', '.')
                
                # Remove whitespace
                value = value.strip()
                
                # Handle European number formats with space as thousand separator
                value = value.replace(' ', '')
            
            decimal_value = Decimal(str(value))
            if decimal_value < 0:
                raise DataValidationException(f"{field_name} cannot be negative: {value}")
            return decimal_value
        except InvalidOperation:
            raise DataValidationException(f"Invalid {field_name} value: {value}")