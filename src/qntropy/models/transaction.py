"""Data models for representing cryptocurrency transactions."""

from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator


class TransactionType(str, Enum):
    """Types of cryptocurrency transactions."""

    # Core transaction types
    BUY = "Buy"                                            # Purchase of crypto with fiat
    SELL = "Sell"                                          # Sale of crypto to fiat
    TRADE = "Trade"                                        # Crypto-to-crypto exchange
    
    # Deposit/withdrawal transactions
    DEPOSIT = "Deposit"                                    # Incoming transfer to account/wallet
    WITHDRAWAL = "Withdrawal"                              # Outgoing transfer from account/wallet
    TRANSFER = "Transfer"                                  # Transfer between own wallets (non-taxable)
    
    # Income transactions
    STAKING_REWARD = "Staking Reward"                      # Income from staking
    INTEREST = "Interest"                                  # Income from lending/interest
    AIRDROP = "Airdrop"                                    # Free tokens received
    MINING = "Mining"                                      # Mining rewards
    
    # Fee transaction
    FEE = "Fee"                                            # Transaction fee (separate entry)
    
    # System-generated transactions
    SYNTHETIC_DEPOSIT = "Synthetic Deposit"                # Generated for balance reconciliation
    CONSOLIDATION_ADJUSTMENT = "Consolidation Adjustment"  # Final balance adjustment


class Asset(BaseModel):
    """Model representing a cryptocurrency asset."""

    symbol: str = Field(..., description="Asset symbol (e.g., BTC, ETH)")
    name: Optional[str] = Field(None, description="Full name of the asset")

    def __str__(self) -> str:
        """Return string representation of the asset."""
        return self.symbol


class AssetAmount(BaseModel):
    """Model representing an amount of a specific asset."""

    asset: Asset
    amount: Decimal = Field(..., description="Amount of the asset")

    def __str__(self) -> str:
        """Return string representation of the asset amount."""
        return f"{self.amount} {self.asset}"

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Validate that amount is not negative."""
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return v


class Transaction(BaseModel):
    """Model representing a cryptocurrency transaction."""

    # Core transaction data
    timestamp: datetime = Field(..., description="Date and time of the transaction")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    
    # Asset being purchased/received
    asset_in: Optional[AssetAmount] = Field(None, description="Asset received (if any)")
    
    # Asset being sold/sent
    asset_out: Optional[AssetAmount] = Field(None, description="Asset sent (if any)")
    
    # Transaction fee
    fee: Optional[AssetAmount] = Field(None, description="Fee paid for the transaction")
    
    # Additional metadata
    exchange: Optional[str] = Field(None, description="Exchange or platform where the transaction occurred")
    trade_group: Optional[str] = Field(None, description="Group identifier for related trades")
    notes: Optional[str] = Field(None, description="Additional notes or comments about the transaction")
    
    # Original data source
    source_file: Optional[str] = Field(None, description="Source file this transaction was imported from")
    source_line: Optional[int] = Field(None, description="Line number in source file")
    
    # Price data (if available)
    price_eur: Optional[Decimal] = Field(None, description="Price in EUR at transaction time")
    price_source: Optional[str] = Field(None, description="Source of price data")

    # Flag for synthetic transactions
    is_synthetic: bool = Field(False, description="Whether this is a synthetically generated transaction")
    
    @field_validator('transaction_type')
    @classmethod
    def validate_transaction_type(cls, v: TransactionType, values: dict) -> TransactionType:
        """Validate that the transaction data is consistent with the transaction type."""
        # This could be expanded to add validations specific to transaction types
        # For example, Buy transactions should have asset_in but might not have asset_out (if bought with fiat)
        return v

    def __str__(self) -> str:
        """Return string representation of the transaction."""
        if self.transaction_type in [TransactionType.BUY, TransactionType.DEPOSIT, TransactionType.STAKING_REWARD]:
            return f"{self.transaction_type.value}: {self.asset_in}"
        elif self.transaction_type in [TransactionType.SELL, TransactionType.WITHDRAWAL]:
            return f"{self.transaction_type.value}: {self.asset_out}"
        elif self.transaction_type == TransactionType.TRADE:
            return f"Trade: {self.asset_out} -> {self.asset_in}"
        else:
            return f"{self.transaction_type.value} at {self.timestamp}"
