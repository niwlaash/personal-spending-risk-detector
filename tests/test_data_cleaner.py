"""
Unit tests for the DataCleaner service.
"""

import pandas as pd
import pytest

from app.services.data_cleaner import DataCleaner


@pytest.fixture
def cleaner():
    return DataCleaner()


@pytest.fixture
def raw_df():
    """Raw DataFrame with duplicates, noise, and inconsistencies."""
    return pd.DataFrame(
        {
            "date": [
                "2026-03-01",
                "2026-03-01",
                "2026-03-02",
                "2026-03-03",
                "2026-03-03",
            ],
            "description": [
                "GRAB FOOD  REF: 123456 NASI LEMAK",
                "GRAB FOOD  REF: 123456 NASI LEMAK",  # duplicate
                "FOOD PANDA  TRX: 789 SUSHI",
                "SHOPEE  MY 999 PURCHASE",
                "starbucks sunway",  # lowercase
            ],
            "amount": [-18.50, -18.50, -42.00, -129.90, -22.00],
            "balance": [6131.50, 6131.50, 5159.10, 5029.20, 5007.20],
        }
    )


class TestDataCleaner:
    """Tests for DataCleaner."""

    def test_removes_duplicates(self, cleaner, raw_df):
        """Duplicate rows should be removed."""
        result = cleaner.clean(raw_df)
        assert len(result) == 4  # 5 rows → 4 after removing 1 duplicate

    def test_normalizes_descriptions(self, cleaner, raw_df):
        """Descriptions should be uppercased and noise removed."""
        result = cleaner.clean(raw_df)
        # All descriptions should be uppercase
        for desc in result["description"]:
            assert desc == desc.upper()

    def test_removes_reference_numbers(self, cleaner):
        """Reference numbers and TRX IDs should be stripped."""
        df = pd.DataFrame(
            {
                "date": ["2026-03-01"],
                "description": ["GRAB FOOD REF: 123456789 DELIVERY"],
                "amount": [-20.00],
                "balance": [1000.00],
            }
        )
        result = cleaner.clean(df)
        desc = result["description"].iloc[0]
        assert "123456789" not in desc

    def test_normalizes_merchant_names(self, cleaner):
        """Known merchant name variants should be normalized."""
        df = pd.DataFrame(
            {
                "date": ["2026-03-01", "2026-03-02"],
                "description": ["FOOD PANDA DELIVERY", "GRAB FOOD NASI LEMAK"],
                "amount": [-20.00, -15.00],
                "balance": [1000.00, 985.00],
            }
        )
        result = cleaner.clean(df)
        assert "FOODPANDA" in result["description"].iloc[0]
        assert "GRAB" in result["description"].iloc[1]

    def test_sorts_by_date(self, cleaner):
        """Output should be sorted by date ascending."""
        df = pd.DataFrame(
            {
                "date": ["2026-03-05", "2026-03-01", "2026-03-03"],
                "description": ["A", "B", "C"],
                "amount": [-10, -20, -30],
                "balance": [100, 200, 300],
            }
        )
        result = cleaner.clean(df)
        dates = result["date"].tolist()
        assert dates == sorted(dates)

    def test_drops_invalid_rows(self, cleaner):
        """Rows with NaN in essential fields should be dropped."""
        df = pd.DataFrame(
            {
                "date": ["2026-03-01", None, "2026-03-03"],
                "description": ["GRAB", "FOOD", None],
                "amount": [-10, -20, -30],
                "balance": [100, 200, 300],
            }
        )
        result = cleaner.clean(df)
        # Row 2 has None date (dropped), Row 3 has None description (dropped)
        # Row 1 is valid, Row 2 ("FOOD") has None date so dropped
        # Result: only rows with valid date + description remain
        assert len(result) <= 2
        assert result["date"].notna().all()
        assert result["amount"].notna().all()

    def test_ensures_numeric_amount(self, cleaner):
        """Amount column should be numeric after cleaning."""
        df = pd.DataFrame(
            {
                "date": ["2026-03-01"],
                "description": ["GRAB"],
                "amount": ["-18.50"],
                "balance": ["1000.00"],
            }
        )
        result = cleaner.clean(df)
        assert result["amount"].dtype in ["float64", "int64"]
