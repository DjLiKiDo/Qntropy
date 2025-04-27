"""Integration tests for the Cointracking importer."""

import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from qntropy.importers.cointracking import CointrackingImporter
from qntropy.models.transaction import TransactionType


@pytest.fixture
def sample_csv_path():
    """Return the path to the sample CSV fixture."""
    return Path(__file__).parent.parent / "fixtures" / "cointracking_sample.csv"


class TestCointrackingIntegration:
    """Integration tests for importing Cointracking CSV files."""

    def test_import_sample_file(self, sample_csv_path):
        """Test importing the sample fixture CSV file."""
        # Ensure the fixture file exists
        assert sample_csv_path.exists(), f"Sample CSV fixture not found at {sample_csv_path}"
        
        # Import the file
        importer = CointrackingImporter()
        transactions = importer.import_file(sample_csv_path)
        
        # Check that all transactions were imported
        assert len(transactions) == 7, "Should import all 7 transactions from the sample file"
        
        # Verify transaction types
        transaction_types = [tx.transaction_type for tx in transactions]
        assert TransactionType.TRADE in transaction_types
        assert TransactionType.DEPOSIT in transaction_types
        assert TransactionType.WITHDRAWAL in transaction_types
        assert TransactionType.STAKING_REWARD in transaction_types
        assert TransactionType.BUY in transaction_types
        assert TransactionType.SELL in transaction_types
        assert TransactionType.TRANSFER in transaction_types
        
        # Verify some specific transactions
        buy_tx = next(tx for tx in transactions if tx.transaction_type == TransactionType.BUY)
        assert buy_tx.asset_in.asset.symbol == "ETH"
        assert buy_tx.asset_in.amount == Decimal("1")
        assert buy_tx.asset_out.asset.symbol == "EUR"
        assert buy_tx.asset_out.amount == Decimal("1800")
        assert buy_tx.fee.asset.symbol == "EUR"
        assert buy_tx.fee.amount == Decimal("2.5")
        assert buy_tx.exchange == "Coinbase"
        
        staking_tx = next(tx for tx in transactions if tx.transaction_type == TransactionType.STAKING_REWARD)
        assert staking_tx.asset_in.asset.symbol == "DOT"
        assert staking_tx.asset_in.amount == Decimal("10")
        assert staking_tx.fee.asset.symbol == "DOT"
        assert staking_tx.fee.amount == Decimal("0.1")
        assert staking_tx.exchange == "Kraken"
        assert "Monthly rewards" in staking_tx.notes

    def test_import_to_json(self, sample_csv_path, tmp_path):
        """Test importing and saving to JSON via the CLI."""
        from qntropy.cli.main import import_cointracking
        
        # Define output path for the JSON file
        output_path = tmp_path / "transactions.json"
        
        # Run the import command
        imported_transactions = import_cointracking(sample_csv_path, output_path)
        
        # Check that the transactions were returned
        assert len(imported_transactions) == 7
        
        # Check that the JSON file was created
        assert output_path.exists()
        
        # Check the JSON file content
        import json
        with open(output_path) as f:
            data = json.load(f)
        
        assert len(data) == 7
        assert "timestamp" in data[0]
        assert "transaction_type" in data[0]
        
        # Check that a specific transaction was saved correctly
        trade_tx = next(tx for tx in data if tx["transaction_type"] == "Trade")
        assert trade_tx["asset_in"]["asset"]["symbol"] == "BTC"
        assert trade_tx["asset_out"]["asset"]["symbol"] == "EUR"