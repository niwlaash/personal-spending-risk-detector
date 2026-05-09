"""
CSV parser for bank statement CSV exports.
Handles generic CSV formats with flexible column mapping.
"""

from typing import Dict, Optional

import pandas as pd

from app.parsers.base_parser import BaseParser


class CSVParser(BaseParser):
    """
    Parser for CSV bank statement exports.

    Supports flexible column name mapping to handle different CSV formats
    from various banks.
    """

    # Common column name variants that map to our standard names
    DEFAULT_COLUMN_MAP = {
        # date variants
        "date": "date",
        "transaction date": "date",
        "trans date": "date",
        "value date": "date",
        "posting date": "date",
        "tarikh": "date",
        # description variants
        "description": "description",
        "transaction description": "description",
        "details": "description",
        "particulars": "description",
        "narrative": "description",
        "remarks": "description",
        "keterangan": "description",
        # amount variants
        "amount": "amount",
        "transaction amount": "amount",
        "debit": "amount",
        "credit": "amount",
        "jumlah": "amount",
        # balance variants
        "balance": "balance",
        "running balance": "balance",
        "available balance": "balance",
        "baki": "balance",
    }

    def __init__(self, column_map: Optional[Dict[str, str]] = None):
        """
        Initialize CSV parser with optional custom column mapping.

        Args:
            column_map: Custom mapping from CSV column names to standard names.
        """
        self.column_map = column_map or self.DEFAULT_COLUMN_MAP

    def parse(self, file_path: str) -> pd.DataFrame:
        """
        Parse a CSV bank statement file.

        Args:
            file_path: Path to the CSV file.

        Returns:
            Standardized DataFrame with columns: date, description, amount, balance.
        """
        # Read CSV with flexible options
        df = pd.read_csv(file_path, encoding="utf-8-sig")

        # Normalize column names to lowercase for matching
        df.columns = [col.strip().lower() for col in df.columns]

        # Apply column mapping
        rename_map = {}
        for original_col in df.columns:
            if original_col in self.column_map:
                rename_map[original_col] = self.column_map[original_col]

        df = df.rename(columns=rename_map)

        # Handle separate debit/credit columns
        if "debit" in df.columns and "credit" in df.columns:
            df["amount"] = df.apply(self._merge_debit_credit, axis=1)
            df = df.drop(columns=["debit", "credit"], errors="ignore")

        # Validate required columns exist
        self.validate(df)

        # Parse dates
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

        # Clean amount
        df["amount"] = pd.to_numeric(
            df["amount"].astype(str).str.replace(",", "").str.strip(),
            errors="coerce",
        )

        # Clean balance if present
        if "balance" in df.columns:
            df["balance"] = pd.to_numeric(
                df["balance"].astype(str).str.replace(",", "").str.strip(),
                errors="coerce",
            )
        else:
            df["balance"] = None

        # Clean description
        df["description"] = df["description"].astype(str).str.strip().str.upper()

        # Drop rows where essential fields are missing
        df = df.dropna(subset=["date", "description", "amount"])

        # Select only standard columns
        result = df[["date", "description", "amount", "balance"]].copy()
        result = result.reset_index(drop=True)

        return result

    @staticmethod
    def _merge_debit_credit(row) -> float:
        """Merge separate debit/credit columns into a single amount."""
        debit = pd.to_numeric(
            str(row.get("debit", "")).replace(",", "").strip() or "0",
            errors="coerce",
        )
        credit = pd.to_numeric(
            str(row.get("credit", "")).replace(",", "").strip() or "0",
            errors="coerce",
        )
        debit = debit if pd.notna(debit) else 0
        credit = credit if pd.notna(credit) else 0

        if debit != 0:
            return -abs(debit)
        return abs(credit)
