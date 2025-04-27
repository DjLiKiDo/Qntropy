"""Unit tests for the Cointracking importer."""

from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from qntropy.importers.cointracking import CointrackingImporter
from qntropy.models.transaction import Asset, TransactionType
from qntropy.utils.exceptions import CSVFormatException, DataValidationException


class TestCointrackingImporter:
    """Tests for the CointrackingImporter class."""

    def test_import_file_success(self, tmp_path):
        """Test successful import of a valid CSV file."""
        # Create a test CSV file
        csv_content = """Type,Buy Amount,Buy Currency,Sell Amount,Sell Currency,Fee,Fee Currency,Exchange,Group,Comment,Date
Trade,0.5,BTC,7500,EUR,5,EUR,Binance,Trading,,2023-01-15 14:30:25
Deposit,1000,EUR,,,,,Binance,Funding,Initial deposit,2023-01-10 09:15:00
"""
        csv_file = tmp_path / "test_valid.csv"
        csv_file.write_text(csv_content)
        
        # Import the file
        importer = CointrackingImporter()
        transactions = importer.import_file(csv_file)
        
        # Check that the correct number of transactions were imported
        assert len(transactions) == 2
        
        # Check the trade transaction
        trade_tx = transactions[0]
        assert trade_tx.transaction_type == TransactionType.TRADE
        assert trade_tx.asset_in.asset.symbol == "BTC"
        assert trade_tx.asset_in.amount == Decimal("0.5")
        assert trade_tx.asset_out.asset.symbol == "EUR"
        assert trade_tx.asset_out.amount == Decimal("7500")
        assert trade_tx.fee.asset.symbol == "EUR"
        assert trade_tx.fee.amount == Decimal("5")
        assert trade_tx.exchange == "Binance"
        
        # Check the deposit transaction
        deposit_tx = transactions[1]
        assert deposit_tx.transaction_type == TransactionType.DEPOSIT
        assert deposit_tx.asset_in.asset.symbol == "EUR"
        assert deposit_tx.asset_in.amount == Decimal("1000")
        assert deposit_tx.asset_out is None
        assert deposit_tx.fee is None
        assert deposit_tx.exchange == "Binance"
        assert deposit_tx.notes == "Initial deposit"

    def test_import_file_missing_columns(self, tmp_path):
        """Test import with missing columns."""
        # Create a test CSV file with missing columns
        csv_content = """Type,Buy Amount,Buy Currency,Sell Amount,Sell Currency,Exchange,Date
Trade,0.5,BTC,7500,EUR,Binance,2023-01-15 14:30:25
"""
        csv_file = tmp_path / "test_missing_columns.csv"
        csv_file.write_text(csv_content)
        
        # Import the file
        importer = CointrackingImporter()
        with pytest.raises(CSVFormatException) as excinfo:
            importer.import_file(csv_file)
        
        # Check the error message
        assert "Missing required columns" in str(excinfo.value)

    def test_import_file_invalid_date(self, tmp_path):
        """Test import with invalid date format."""
        # Create a test CSV file with invalid date
        csv_content = """Type,Buy Amount,Buy Currency,Sell Amount,Sell Currency,Fee,Fee Currency,Exchange,Group,Comment,Date
Trade,0.5,BTC,7500,EUR,5,EUR,Binance,Trading,,invalid-date
"""
        csv_file = tmp_path / "test_invalid_date.csv"
        csv_file.write_text(csv_content)
        
        # Import the file
        importer = CointrackingImporter()
        # The importer should continue with the next row, but log a warning
        transactions = importer.import_file(csv_file)
        assert len(transactions) == 0

    def test_import_file_invalid_amount(self, tmp_path):
        """Test import with invalid amount values."""
        # Create a test CSV file with invalid amount
        csv_content = """Type,Buy Amount,Buy Currency,Sell Amount,Sell Currency,Fee,Fee Currency,Exchange,Group,Comment,Date
Trade,not-a-number,BTC,7500,EUR,5,EUR,Binance,Trading,,2023-01-15 14:30:25
"""
        csv_file = tmp_path / "test_invalid_amount.csv"
        csv_file.write_text(csv_content)
        
        # Import the file
        importer = CointrackingImporter()
        # The importer should continue with the next row, but log a warning
        transactions = importer.import_file(csv_file)
        assert len(transactions) == 0

    def test_import_file_empty_file(self, tmp_path):
        """Test import with an empty CSV file."""
        # Create an empty CSV file
        csv_file = tmp_path / "test_empty.csv"
        csv_file.write_text("")
        
        # Import the file
        importer = CointrackingImporter()
        with pytest.raises(CSVFormatException) as excinfo:
            importer.import_file(csv_file)
        
        # Check the error message
        assert "is empty" in str(excinfo.value)

    def test_parse_decimal(self):
        """Test decimal parsing with various formats."""
        importer = CointrackingImporter()
        
        # Test valid decimal values
        assert importer._parse_decimal("123.45", "Test") == Decimal("123.45")
        assert importer._parse_decimal("123,45", "Test") == Decimal("123.45")
        assert importer._parse_decimal("0", "Test") == Decimal("0")
        
        # Test invalid decimal values
        with pytest.raises(DataValidationException):
            importer._parse_decimal("-1", "Test")  # Negative values not allowed
            
        with pytest.raises(DataValidationException):
            importer._parse_decimal("not-a-number", "Test")

    def test_transaction_type_mapping(self):
        """Test mapping of Cointracking transaction types to internal types."""
        importer = CointrackingImporter()
        
        # Test known mappings
        assert importer.TRANSACTION_TYPE_MAPPING["Trade"] == TransactionType.TRADE
        assert importer.TRANSACTION_TYPE_MAPPING["Deposit"] == TransactionType.DEPOSIT
        assert importer.TRANSACTION_TYPE_MAPPING["Withdrawal"] == TransactionType.WITHDRAWAL
        assert importer.TRANSACTION_TYPE_MAPPING["Staking"] == TransactionType.STAKING_REWARD