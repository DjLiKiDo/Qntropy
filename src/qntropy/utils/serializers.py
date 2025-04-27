"""Utility functions for serialization."""

import json
from datetime import datetime
from decimal import Decimal
from enum import Enum


class TransactionEncoder(json.JSONEncoder):
    """JSON encoder for Transaction objects and related classes."""

    def default(self, obj):
        """Convert objects to JSON serializable types."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)
