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

    def test_asset_amount_validation(self):
        """Test validation of AssetAmount."""
        asset = Asset(symbol="BTC")
        
        # Test with valid amount
        AssetAmount(asset=asset, amount=Decimal("0"))
        AssetAmount(asset=asset, amount=Decimal("1.23456789"))
        
        # Test with invalid amount
        with pytest.raises(ValidationError):
            AssetAmount(asset=asset, amount=Decimal("-1"))


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