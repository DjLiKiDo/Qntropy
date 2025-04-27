"""Custom exceptions for the Qntropy application."""


class QntropyBaseException(Exception):
    """Base exception for all Qntropy exceptions."""

    pass


class ImporterException(QntropyBaseException):
    """Base exception for importer related errors."""

    pass


class CSVFormatException(ImporterException):
    """Exception raised when the CSV format is invalid."""

    pass


class DataValidationException(ImporterException):
    """Exception raised when data validation fails."""

    pass


class ReconciliationException(QntropyBaseException):
    """Base exception for reconciliation related errors."""

    pass


class InsufficientBalanceException(ReconciliationException):
    """Exception raised when a transaction would result in a negative balance."""

    pass


class UnreconcilableTransactionException(ReconciliationException):
    """Exception raised when a transaction cannot be reconciled."""

    pass


class TaxCalculationException(QntropyBaseException):
    """Base exception for tax calculation related errors."""

    pass


class MissingPriceDataException(TaxCalculationException):
    """Exception raised when price data is missing for a transaction."""

    pass


class ConfigurationException(QntropyBaseException):
    """Exception raised for configuration related errors."""

    pass
