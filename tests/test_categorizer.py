"""
Unit tests for the Categorizer service.
"""

import pandas as pd
import pytest

from app.services.categorizer import Categorizer


@pytest.fixture
def categorizer():
    return Categorizer()


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2026-03-01",
                    "2026-03-02",
                    "2026-03-03",
                    "2026-03-04",
                    "2026-03-05",
                    "2026-03-06",
                    "2026-03-07",
                ]
            ),
            "description": [
                "GRAB FOOD NASI LEMAK",
                "PETRONAS BANDAR UTAMA",
                "SHOPEE PURCHASE",
                "UNIFI BILL PAYMENT",
                "GSC CINEMA TICKET",
                "SALARY CREDIT",
                "RANDOM UNKNOWN MERCHANT",
            ],
            "amount": [-18.50, -85.00, -129.90, -159.00, -38.00, 5500.00, -50.00],
            "balance": [
                6181.50,
                6096.50,
                5966.60,
                5807.60,
                5769.60,
                11269.60,
                11219.60,
            ],
        }
    )


class TestCategorizer:
    """Tests for rule-based Categorizer."""

    def test_categorizes_grab_food(self, categorizer):
        """Grab food should be Food & Beverage."""
        df = pd.DataFrame(
            {
                "description": ["GRAB FOOD NASI LEMAK"],
                "date": ["2026-03-01"],
                "amount": [-18],
                "balance": [1000],
            }
        )
        result = categorizer.categorize(df)
        assert result["category"].iloc[0] == "Food & Beverage"

    def test_categorizes_transport(self, categorizer):
        """Petronas should be Transport."""
        df = pd.DataFrame(
            {
                "description": ["PETRONAS FUEL"],
                "date": ["2026-03-01"],
                "amount": [-85],
                "balance": [1000],
            }
        )
        result = categorizer.categorize(df)
        assert result["category"].iloc[0] == "Transport"

    def test_categorizes_shopping(self, categorizer):
        """Shopee should be Shopping."""
        df = pd.DataFrame(
            {
                "description": ["SHOPEE PURCHASE"],
                "date": ["2026-03-01"],
                "amount": [-130],
                "balance": [1000],
            }
        )
        result = categorizer.categorize(df)
        assert result["category"].iloc[0] == "Shopping"

    def test_categorizes_bills(self, categorizer):
        """Unifi should be Bills."""
        df = pd.DataFrame(
            {
                "description": ["UNIFI BILL PAYMENT"],
                "date": ["2026-03-01"],
                "amount": [-159],
                "balance": [1000],
            }
        )
        result = categorizer.categorize(df)
        assert result["category"].iloc[0] == "Bills"

    def test_categorizes_entertainment(self, categorizer):
        """GSC Cinema should be Entertainment."""
        df = pd.DataFrame(
            {
                "description": ["GSC CINEMA TICKET"],
                "date": ["2026-03-01"],
                "amount": [-38],
                "balance": [1000],
            }
        )
        result = categorizer.categorize(df)
        assert result["category"].iloc[0] == "Entertainment"

    def test_categorizes_income(self, categorizer):
        """Salary should be Income."""
        df = pd.DataFrame(
            {
                "description": ["SALARY CREDIT"],
                "date": ["2026-03-01"],
                "amount": [5500],
                "balance": [5500],
            }
        )
        result = categorizer.categorize(df)
        assert result["category"].iloc[0] == "Income"

    def test_unknown_falls_to_other(self, categorizer):
        """Unrecognized merchants should be categorized as Other."""
        df = pd.DataFrame(
            {
                "description": ["XYZABC RANDOM PLACE"],
                "date": ["2026-03-01"],
                "amount": [-50],
                "balance": [1000],
            }
        )
        result = categorizer.categorize(df)
        assert result["category"].iloc[0] == "Other"

    def test_all_categories_assigned(self, categorizer, sample_df):
        """Every transaction should have a category after categorization."""
        result = categorizer.categorize(sample_df)
        assert result["category"].notna().all()
        assert (result["category"] != "").all()

    def test_tng_is_transport(self, categorizer):
        """Touch N Go should be Transport."""
        df = pd.DataFrame(
            {
                "description": ["TNG EWALLET TOPUP"],
                "date": ["2026-03-01"],
                "amount": [-50],
                "balance": [1000],
            }
        )
        result = categorizer.categorize(df)
        assert result["category"].iloc[0] == "Transport"

    def test_foodpanda_is_food(self, categorizer):
        """FoodPanda should be Food & Beverage."""
        df = pd.DataFrame(
            {
                "description": ["FOODPANDA SUSHI KING"],
                "date": ["2026-03-01"],
                "amount": [-42],
                "balance": [1000],
            }
        )
        result = categorizer.categorize(df)
        assert result["category"].iloc[0] == "Food & Beverage"
