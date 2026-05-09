"""
Base parser interface for bank statement parsers.
All bank-specific parsers should inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd


class BaseParser(ABC):
    """Abstract base class for all bank statement parsers."""

    REQUIRED_COLUMNS = ["date", "description", "amount"]

    @abstractmethod
    def parse(self, file_path: str) -> pd.DataFrame:
        """
        Parse a bank statement file and return a standardized DataFrame.

        Expected output columns:
            - date (datetime): Transaction date
            - description (str): Transaction description
            - amount (float): Transaction amount (negative for debits)
            - balance (float, optional): Account balance after transaction

        Args:
            file_path: Path to the bank statement file.

        Returns:
            pd.DataFrame with standardized columns.
        """
        pass

    def validate(self, df: pd.DataFrame) -> bool:
        """Validate that the DataFrame has the required columns."""
        for col in self.REQUIRED_COLUMNS:
            if col not in df.columns:
                raise ValueError(f"Missing required column: '{col}'")
        return True
