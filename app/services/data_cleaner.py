"""
Data cleaning service.
Handles deduplication, normalization, and standardization of transactions.
"""

import re

import pandas as pd


class DataCleaner:
    """Cleans and normalizes raw transaction data."""

    # Common noise patterns in Malaysian bank descriptions
    NOISE_PATTERNS = [
        r"\b\d{6,}\b",  # Long numeric sequences (reference numbers)
        r"\bREF\s*:?\s*\d+",  # Reference numbers
        r"\bTRX\s*:?\s*\d+",  # Transaction IDs
        r"\bMY\s+\d+",  # Country codes with numbers
        r"\s{2,}",  # Multiple spaces
    ]

    # Merchant name normalization map
    MERCHANT_NORMALIZATIONS = {
        r"GRAB\s*(FOOD|CAR|PAY|RIDE)?\s*\*?": "GRAB",
        r"FOOD\s*PANDA": "FOODPANDA",
        r"TOUCH\s*[N'&]\s*GO": "TOUCH N GO",
        r"SHOPEE\s*(PAY|MALL)?": "SHOPEE",
        r"LAZADA\s*(MALL)?": "LAZADA",
        r"MC\s*DONALD": "MCDONALD",
        r"STARBUCK\s*S?": "STARBUCKS",
    }

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize transaction data.

        Steps:
            1. Remove duplicate transactions
            2. Normalize merchant/description names
            3. Standardize date and amount formats
            4. Remove noise from descriptions

        Args:
            df: Raw transaction DataFrame.

        Returns:
            Cleaned DataFrame.
        """
        df = df.copy()

        # Step 1: Remove exact duplicates
        df = df.drop_duplicates(subset=["date", "description", "amount"], keep="first")

        # Step 2: Normalize descriptions
        df["description"] = df["description"].apply(self._normalize_description)

        # Step 3: Ensure date is datetime
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # Step 4: Ensure amount is numeric
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

        # Step 5: Drop rows with NaN in essential columns
        df = df.dropna(subset=["date", "description", "amount"])

        # Step 6: Sort by date
        df = df.sort_values("date").reset_index(drop=True)

        return df

    def _normalize_description(self, desc: str) -> str:
        """
        Normalize a transaction description string.

        Removes noise, standardizes merchant names, and trims whitespace.
        """
        if not isinstance(desc, str):
            return str(desc).upper().strip()

        desc = desc.upper().strip()

        # Remove noise patterns
        for pattern in self.NOISE_PATTERNS:
            desc = re.sub(pattern, " ", desc, flags=re.IGNORECASE)

        # Normalize merchant names
        for pattern, replacement in self.MERCHANT_NORMALIZATIONS.items():
            desc = re.sub(pattern, replacement, desc, flags=re.IGNORECASE)

        # Clean up whitespace
        desc = re.sub(r"\s+", " ", desc).strip()

        return desc
