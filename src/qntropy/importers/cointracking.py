"""Importer for Cointracking.info CSV files."""

import csv
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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

    def __init__(self) -> None:
        """Initialize the importer."""
        # Add configuration options here if needed

    def import_file(self, file_path: Path) -> List[Transaction]:
        """
        Import transactions from a Cointracking.info CSV file.
        
        Args:
            file_path: Path to the CSV file.
            
        Returns:
            List of Transaction objects.
            
        Raises:
            CSVFormatException: If the CSV file is malformed or missing required columns.
            DataValidationException: If the data in the CSV file is invalid.
        """
        logger.info(f"Importing transactions from {file_path}")
        
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
            for idx, row in df.iterrows():
                try:
                    transaction = self._parse_row(row, file_path.name, idx + 2)  # +2 because idx is 0-based and there's a header row
                    transactions.append(transaction)
                except Exception as e:
                    logger.warning(f"Error parsing row {idx + 2}: {e}")
                    # Continue with next row instead of failing completely
            
            logger.info(f"Successfully imported {len(transactions)} transactions from {file_path}")
            return transactions
            
        except pd.errors.EmptyDataError:
            raise CSVFormatException(f"The CSV file {file_path} is empty")
        except pd.errors.ParserError:
            raise CSVFormatException(f"Error parsing CSV file {file_path}")
        except Exception as e:
            raise CSVFormatException(f"Unexpected error reading CSV file {file_path}: {str(e)}")

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
            # Parse date - optimized for Python 3.11
            date_str = row["Date"]
            timestamp = self._parse_date(date_str)

            # Determine transaction type
            ct_type = row["Type"]
            if ct_type in self.TRANSACTION_TYPE_MAPPING:
                transaction_type = self.TRANSACTION_TYPE_MAPPING[ct_type]
            elif ct_type == "Buy":
                transaction_type = TransactionType.BUY
            elif ct_type == "Sell":
                transaction_type = TransactionType.SELL
            else:
                # Fallback for unknown types
                if pd.notna(row["Buy Amount"]) and float(row["Buy Amount"]) > 0:
                    transaction_type = TransactionType.BUY
                elif pd.notna(row["Sell Amount"]) and float(row["Sell Amount"]) > 0:
                    transaction_type = TransactionType.SELL
                else:
                    logger.warning(f"Unknown transaction type: {ct_type}, defaulting to TRADE")
                    transaction_type = TransactionType.TRADE

            # Parse buy (incoming) asset
            asset_in = None
            if pd.notna(row["Buy Amount"]) and pd.notna(row["Buy Currency"]) and float(row["Buy Amount"]) > 0:
                buy_amount = self._parse_decimal(row["Buy Amount"], "Buy Amount")
                buy_currency = row["Buy Currency"].strip()
                asset_in = AssetAmount(
                    asset=Asset(symbol=buy_currency),
                    amount=buy_amount
                )

            # Parse sell (outgoing) asset
            asset_out = None
            if pd.notna(row["Sell Amount"]) and pd.notna(row["Sell Currency"]) and float(row["Sell Amount"]) > 0:
                sell_amount = self._parse_decimal(row["Sell Amount"], "Sell Amount")
                sell_currency = row["Sell Currency"].strip()
                asset_out = AssetAmount(
                    asset=Asset(symbol=sell_currency),
                    amount=sell_amount
                )

            # Parse fee
            fee = None
            if pd.notna(row["Fee"]) and pd.notna(row["Fee Currency"]) and float(row["Fee"]) > 0:
                fee_amount = self._parse_decimal(row["Fee"], "Fee")
                fee_currency = row["Fee Currency"].strip()
                fee = AssetAmount(
                    asset=Asset(symbol=fee_currency),
                    amount=fee_amount
                )

            # Create the transaction
            return Transaction(
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

        except DataValidationException:
            # Re-raise validation exceptions without modification
            raise
        except Exception as e:
            # Convert other exceptions to DataValidationException
            raise DataValidationException(f"Error parsing row: {str(e)}")

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
            
            decimal_value = Decimal(str(value))
            if decimal_value < 0:
                raise DataValidationException(f"{field_name} cannot be negative: {value}")
            return decimal_value
        except InvalidOperation:
            raise DataValidationException(f"Invalid {field_name} value: {value}")