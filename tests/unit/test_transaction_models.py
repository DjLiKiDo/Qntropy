"""Unit tests for transaction models."""

from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from qntropy.models.transaction import (
    Asset,
    AssetAmount,
    Transaction,
    TransactionType,
)


class TestAsset:
    """Tests for the Asset model."""

    def test_asset_creation(self):
        """Test creating an Asset with valid data."""
        asset = Asset(symbol="BTC")
        assert asset.symbol == "BTC"
        assert asset.name is None

        asset_with_name = Asset(symbol="BTC", name="Bitcoin")
        assert asset_with_name.symbol == "BTC"
        assert asset_with_name.name == "Bitcoin"

    def test_asset_string_representation(self):
        """Test the string representation of an Asset."""
        asset = Asset(symbol="ETH", name="Ethereum")
        assert str(asset) == "ETH"


class TestAssetAmount:
    """Tests for the AssetAmount model."""

    def test_asset_amount_creation(self):
        """Test creating an AssetAmount with valid data."""
        asset = Asset(symbol="BTC")
        asset_amount = AssetAmount(asset=asset, amount=Decimal("1.5"))
        assert asset_amount.asset.symbol == "BTC"
        assert asset_amount.amount == Decimal("1.5")

    def test_asset_amount_string_representation(self):
        """Test the string representation of an AssetAmount."""
        asset = Asset(symbol="ETH")
        asset_amount = AssetAmount(asset=asset, amount=Decimal("2.75"))
        assert str(asset_amount) == "2.75 ETH"

    def test_scientific_notation_display(self):
        """Test that scientific notation is displayed as decimal."""
        asset = Asset(symbol="BTC")
        # Test very small number (scientific notation)
        small_amount = AssetAmount(asset=asset, amount=Decimal("1e-7"))
        assert str(small_amount) == "0.0000001 BTC"
        
        # Test very large number
        large_amount = AssetAmount(asset=asset, amount=Decimal("1e6"))
        assert str(large_amount) == "1000000 BTC"
        
        # Test number with trailing zeros
        trailing_zeros = AssetAmount(asset=asset, amount=Decimal("1.500000"))
        assert str(trailing_zeros) == "1.5 BTC"
        
        # Test whole number
        whole_number = AssetAmount(asset=asset, amount=Decimal("5.0"))
        assert str(whole_number) == "5 BTC"

    def test_asset_amount_validation(self):
        """Test validation of AssetAmount."""
        asset = Asset(symbol="BTC")
        
        # Test with valid amount
        AssetAmount(asset=asset, amount=Decimal("0"))
        AssetAmount(asset=asset, amount=Decimal("1.23456789"))
        
        # Test with invalid amount
        with pytest.raises(ValidationError):
            AssetAmount(asset=asset, amount=Decimal("-1"))

    def test_scientific_notation_precision(self):
        """Test that scientific notation maintains calculation precision."""
        asset = Asset(symbol="BTC")
        
        # Create amounts with scientific notation
        small_amount1 = AssetAmount(asset=asset, amount=Decimal("1e-7"))
        small_amount2 = AssetAmount(asset=asset, amount=Decimal("2e-7"))
        
        # Verify display formatting
        assert str(small_amount1) == "0.0000001 BTC"
        assert str(small_amount2) == "0.0000002 BTC"
        
        # Verify precision in calculations is maintained
        sum_amount = small_amount1.amount + small_amount2.amount
        assert sum_amount == Decimal("3e-7")
        
        # Test multiplication precision
        mult_result = small_amount1.amount * Decimal("1000000")
        assert mult_result == Decimal("0.1")
        
        # Test division precision
        div_result = small_amount1.amount / Decimal("0.0000001")
        assert div_result == Decimal("1")
        
        # Test complex calculation with mixed scales
        complex_calc = (small_amount1.amount * Decimal("1e6")) / Decimal("10") + small_amount2.amount
        assert complex_calc == Decimal("0.0100002")


class TestTransaction:
    """Tests for the Transaction model."""

    def test_buy_transaction_creation(self):
        """Test creating a Buy transaction."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        asset_in = AssetAmount(asset=Asset(symbol="BTC"), amount=Decimal("1"))
        asset_out = AssetAmount(asset=Asset(symbol="EUR"), amount=Decimal("20000"))
        fee = AssetAmount(asset=Asset(symbol="EUR"), amount=Decimal("10"))
        
        transaction = Transaction(
            timestamp=timestamp,
            transaction_type=TransactionType.BUY,
            asset_in=asset_in,
            asset_out=asset_out,
            fee=fee,
            exchange="Coinbase",
            trade_group="Investment",
            notes="Test buy transaction",
        )
        
        assert transaction.timestamp == timestamp
        assert transaction.transaction_type == TransactionType.BUY
        assert transaction.asset_in == asset_in
        assert transaction.asset_out == asset_out
        assert transaction.fee == fee
        assert transaction.exchange == "Coinbase"
        assert transaction.trade_group == "Investment"
        assert transaction.notes == "Test buy transaction"
        assert transaction.is_synthetic is False

    def test_sell_transaction_creation(self):
        """Test creating a Sell transaction."""
        timestamp = datetime(2023, 1, 2, 12, 0, 0)
        asset_in = AssetAmount(asset=Asset(symbol="EUR"), amount=Decimal("21000"))
        asset_out = AssetAmount(asset=Asset(symbol="BTC"), amount=Decimal("1"))
        fee = AssetAmount(asset=Asset(symbol="EUR"), amount=Decimal("10.5"))
        
        transaction = Transaction(
            timestamp=timestamp,
            transaction_type=TransactionType.SELL,
            asset_in=asset_in,
            asset_out=asset_out,
            fee=fee,
            exchange="Binance",
        )
        
        assert transaction.timestamp == timestamp
        assert transaction.transaction_type == TransactionType.SELL
        assert transaction.asset_in == asset_in
        assert transaction.asset_out == asset_out
        assert transaction.fee == fee
        assert transaction.exchange == "Binance"

    def test_deposit_transaction_creation(self):
        """Test creating a Deposit transaction."""
        timestamp = datetime(2023, 1, 3, 12, 0, 0)
        asset_in = AssetAmount(asset=Asset(symbol="EUR"), amount=Decimal("5000"))
        
        transaction = Transaction(
            timestamp=timestamp,
            transaction_type=TransactionType.DEPOSIT,
            asset_in=asset_in,
            exchange="Kraken",
        )
        
        assert transaction.timestamp == timestamp
        assert transaction.transaction_type == TransactionType.DEPOSIT
        assert transaction.asset_in == asset_in
        assert transaction.exchange == "Kraken"

    def test_transaction_string_representation(self):
        """Test the string representation of various Transaction types."""
        # Buy transaction
        buy_tx = Transaction(
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            transaction_type=TransactionType.BUY,
            asset_in=AssetAmount(asset=Asset(symbol="BTC"), amount=Decimal("1")),
        )
        assert str(buy_tx).startswith("Buy:")
        
        # Sell transaction
        sell_tx = Transaction(
            timestamp=datetime(2023, 1, 2, 12, 0, 0),
            transaction_type=TransactionType.SELL,
            asset_out=AssetAmount(asset=Asset(symbol="BTC"), amount=Decimal("1")),
        )
        assert str(sell_tx).startswith("Sell:")
        
        # Trade transaction
        trade_tx = Transaction(
            timestamp=datetime(2023, 1, 3, 12, 0, 0),
            transaction_type=TransactionType.TRADE,
            asset_in=AssetAmount(asset=Asset(symbol="ETH"), amount=Decimal("10")),
            asset_out=AssetAmount(asset=Asset(symbol="BTC"), amount=Decimal("0.5")),
        )
        assert "Trade:" in str(trade_tx)