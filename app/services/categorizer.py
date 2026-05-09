"""
Transaction categorization service.
Phase 1: Rule-based categorization using keyword matching.
"""

from typing import Optional

import pandas as pd

from app.config import CATEGORIES, MALAYSIA_MERCHANTS


class Categorizer:
    """
    Rule-based transaction categorizer.

    Uses keyword matching against Malaysia-specific merchant names
    to assign categories to transactions.
    """

    def __init__(self):
        """Initialize with the default Malaysia merchant mapping."""
        self.merchant_map = MALAYSIA_MERCHANTS

    def categorize(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Categorize all transactions in the DataFrame.

        Args:
            df: DataFrame with a 'description' column.

        Returns:
            DataFrame with a 'category' column added/updated.
        """
        df = df.copy()
        df["category"] = df["description"].apply(self._classify)
        return df

    def _classify(self, description: str) -> str:
        """
        Classify a single transaction description into a category.

        Uses keyword matching against known Malaysian merchants
        and general spending patterns.

        Args:
            description: Transaction description string.

        Returns:
            Category string.
        """
        if not isinstance(description, str):
            return "Other"

        desc_lower = description.lower()

        # Check against Malaysia-specific merchant keywords
        for keyword, category in self.merchant_map.items():
            if keyword in desc_lower:
                return category

        # General keyword fallback rules
        food_keywords = [
            "restaurant",
            "cafe",
            "coffee",
            "food",
            "eat",
            "bakery",
            "nasi",
            "makan",
            "ayam",
            "kopitiam",
            "mamak",
            "warung",
            "kedai makan",
        ]
        transport_keywords = [
            "fuel",
            "petrol",
            "parking",
            "toll",
            "lrt",
            "mrt",
            "bus",
            "taxi",
            "ride",
        ]
        shopping_keywords = [
            "mall",
            "store",
            "mart",
            "shop",
            "purchase",
            "buy",
            "retail",
            "market",
            "bazaar",
        ]
        bill_keywords = [
            "bill",
            "utility",
            "electric",
            "water",
            "internet",
            "phone",
            "insurance",
            "rental",
            "rent",
            "loan",
            "payment",
            "bayaran",
        ]
        entertainment_keywords = [
            "movie",
            "game",
            "concert",
            "ticket",
            "theme park",
            "karaoke",
            "bowling",
            "gym",
            "fitness",
        ]
        income_keywords = [
            "salary",
            "gaji",
            "bonus",
            "transfer in",
            "credit",
            "dividend",
            "refund",
            "cashback",
        ]

        for kw in income_keywords:
            if kw in desc_lower:
                return "Income"
        for kw in food_keywords:
            if kw in desc_lower:
                return "Food & Beverage"
        for kw in transport_keywords:
            if kw in desc_lower:
                return "Transport"
        for kw in shopping_keywords:
            if kw in desc_lower:
                return "Shopping"
        for kw in bill_keywords:
            if kw in desc_lower:
                return "Bills"
        for kw in entertainment_keywords:
            if kw in desc_lower:
                return "Entertainment"

        return "Other"
