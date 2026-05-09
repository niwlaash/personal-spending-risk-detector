"""
Unit tests for the FeatureEngineer service.
"""

import pandas as pd
import pytest

from app.services.feature_engineer import FeatureEngineer


@pytest.fixture
def engineer():
    return FeatureEngineer()


@pytest.fixture
def categorized_df():
    """A categorized DataFrame simulating a month of transactions."""
    return pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2026-03-01",
                    "2026-03-02",
                    "2026-03-03",
                    "2026-03-04",
                    "2026-03-05",
                    "2026-03-10",
                    "2026-03-15",
                    "2026-03-20",
                    "2026-03-25",
                    "2026-03-30",
                ]
            ),
            "description": [
                "SALARY CREDIT",
                "GRAB FOOD NASI LEMAK",
                "PETRONAS FUEL",
                "SHOPEE PURCHASE",
                "UNIFI BILL",
                "GRAB FOOD PIZZA",
                "SALARY ADVANCE",
                "GRAB FOOD KFC",
                "SHOPEE PURCHASE",
                "GRAB FOOD MEE",
            ],
            "amount": [
                5500.00,
                -18.50,
                -85.00,
                -129.90,
                -159.00,
                -45.00,
                2000.00,
                -28.00,
                -175.00,
                -12.00,
            ],
            "balance": [
                6200.00,
                6181.50,
                6096.50,
                5966.60,
                5807.60,
                5762.60,
                7762.60,
                7734.60,
                7559.60,
                7547.60,
            ],
            "category": [
                "Income",
                "Food & Beverage",
                "Transport",
                "Shopping",
                "Bills",
                "Food & Beverage",
                "Income",
                "Food & Beverage",
                "Shopping",
                "Food & Beverage",
            ],
        }
    )


class TestFeatureEngineer:
    """Tests for FeatureEngineer."""

    def test_spending_summary(self, engineer, categorized_df):
        """Should compute correct totals."""
        features = engineer.extract_features(categorized_df)
        summary = features["spending_summary"]
        assert summary["total_income"] == 7500.00
        assert summary["total_expenses"] > 0
        assert summary["transaction_count"] == 10

    def test_category_breakdown(self, engineer, categorized_df):
        """Category breakdown should have correct categories."""
        features = engineer.extract_features(categorized_df)
        breakdown = features["category_breakdown"]
        assert "Food & Beverage" in breakdown
        assert "Transport" in breakdown
        assert "Shopping" in breakdown

    def test_food_delivery_frequency(self, engineer, categorized_df):
        """Should detect grab food transactions."""
        features = engineer.extract_features(categorized_df)
        food = features["food_delivery_frequency"]
        assert food["total_count"] >= 3  # We have at least 3 GRAB FOOD txns

    def test_savings_rate(self, engineer, categorized_df):
        """Savings rate should be between -inf and 1."""
        features = engineer.extract_features(categorized_df)
        sr = features["savings_rate"]
        assert sr <= 1.0

    def test_balance_trend(self, engineer, categorized_df):
        """Balance trend should be a valid string."""
        features = engineer.extract_features(categorized_df)
        assert features["balance_trend"] in [
            "increasing",
            "decreasing",
            "stable",
            "no_data",
            "insufficient_data",
        ]

    def test_income_vs_expense(self, engineer, categorized_df):
        """Income and expense should be computed correctly."""
        features = engineer.extract_features(categorized_df)
        ie = features["income_vs_expense"]
        assert ie["income"] == 7500.00
        assert ie["expenses"] > 0
        assert ie["expense_to_income_ratio"] > 0

    def test_spending_growth_rate_is_numeric(self, engineer, categorized_df):
        """Growth rate should be a number."""
        features = engineer.extract_features(categorized_df)
        assert isinstance(features["spending_growth_rate"], (int, float))

    def test_spending_spike_count(self, engineer, categorized_df):
        """Spike count should be a non-negative integer."""
        features = engineer.extract_features(categorized_df)
        assert features["spending_spike_count"] >= 0

    def test_weekday_vs_weekend_ratio(self, engineer, categorized_df):
        """Ratio should be a positive number."""
        features = engineer.extract_features(categorized_df)
        ratio = features["weekday_vs_weekend_ratio"]
        assert ratio > 0

    def test_empty_dataframe(self, engineer):
        """Should handle empty DataFrame gracefully."""
        empty_df = pd.DataFrame(
            {
                "date": pd.Series(dtype="datetime64[ns]"),
                "description": pd.Series(dtype="str"),
                "amount": pd.Series(dtype="float64"),
                "balance": pd.Series(dtype="float64"),
                "category": pd.Series(dtype="str"),
            }
        )
        features = engineer.extract_features(empty_df)
        assert features["spending_summary"]["transaction_count"] == 0
