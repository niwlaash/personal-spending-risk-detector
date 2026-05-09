"""
Unit tests for the RiskScorer service.
"""

import pytest

from app.services.risk_scorer import RiskScorer


@pytest.fixture
def scorer():
    return RiskScorer()


def _make_features(**overrides):
    """Helper to create a features dict with sensible defaults."""
    defaults = {
        "income_vs_expense": {
            "income": 5000,
            "expenses": 3000,
            "expense_to_income_ratio": 0.6,
        },
        "savings_rate": 0.4,
        "balance_trend": "stable",
        "spending_growth_rate": 5.0,
        "food_delivery_frequency": {"total_count": 4, "weekly_average": 1.0},
        "late_night_ratio": 0.05,
        "weekday_vs_weekend_ratio": 1.5,
        "grab_food_trend": {"trend": "stable", "total_spent": -100},
        "spending_spike_count": 0,
    }
    defaults.update(overrides)
    return defaults


class TestRiskScorer:
    """Tests for RiskScorer."""

    def test_score_returns_all_keys(self, scorer):
        """Score result should have all expected keys."""
        features = _make_features()
        result = scorer.score(features)
        assert "financial_risk_score" in result
        assert "financial_risk_level" in result
        assert "burnout_risk_score" in result
        assert "burnout_risk_level" in result
        assert "financial_components" in result
        assert "burnout_components" in result

    def test_scores_in_range(self, scorer):
        """Both scores should be between 0 and 100."""
        features = _make_features()
        result = scorer.score(features)
        assert 0 <= result["financial_risk_score"] <= 100
        assert 0 <= result["burnout_risk_score"] <= 100

    def test_low_risk_profile(self, scorer):
        """A healthy spending profile should produce low risk."""
        features = _make_features(
            income_vs_expense={
                "income": 5000,
                "expenses": 2000,
                "expense_to_income_ratio": 0.4,
            },
            savings_rate=0.6,
            balance_trend="increasing",
            spending_growth_rate=-5.0,
            food_delivery_frequency={"total_count": 2, "weekly_average": 0.5},
            late_night_ratio=0.02,
            weekday_vs_weekend_ratio=1.2,
            grab_food_trend={"trend": "decreasing", "total_spent": -50},
            spending_spike_count=0,
        )
        result = scorer.score(features)
        assert result["financial_risk_level"] == "Low"
        assert result["burnout_risk_level"] == "Low"

    def test_high_financial_risk(self, scorer):
        """Overspending profile should produce high financial risk."""
        features = _make_features(
            income_vs_expense={
                "income": 3000,
                "expenses": 4500,
                "expense_to_income_ratio": 1.5,
            },
            savings_rate=-0.5,
            balance_trend="decreasing",
            spending_growth_rate=60.0,
        )
        result = scorer.score(features)
        assert result["financial_risk_score"] >= 60
        assert result["financial_risk_level"] in ("High", "Critical")

    def test_high_burnout_risk(self, scorer):
        """Burnout-profile features should produce high burnout risk."""
        features = _make_features(
            food_delivery_frequency={"total_count": 50, "weekly_average": 8.0},
            late_night_ratio=0.4,
            weekday_vs_weekend_ratio=5.0,
            grab_food_trend={"trend": "increasing", "total_spent": -800},
            spending_spike_count=6,
        )
        result = scorer.score(features)
        assert result["burnout_risk_score"] >= 60
        assert result["burnout_risk_level"] in ("High", "Critical")

    def test_risk_levels_correct_thresholds(self, scorer):
        """Verify risk level thresholds."""
        assert scorer._level(10, 30, 60, 80) == "Low"
        assert scorer._level(35, 30, 60, 80) == "Medium"
        assert scorer._level(65, 30, 60, 80) == "High"
        assert scorer._level(85, 30, 60, 80) == "Critical"

    def test_edge_case_zero_income(self, scorer):
        """Zero income should produce very high financial risk."""
        features = _make_features(
            income_vs_expense={
                "income": 0,
                "expenses": 1000,
                "expense_to_income_ratio": float("inf"),
            },
            savings_rate=0,
        )
        result = scorer.score(features)
        assert result["financial_risk_score"] >= 60

    def test_financial_components_present(self, scorer):
        """Financial components breakdown should have all 4 components."""
        features = _make_features()
        result = scorer.score(features)
        fc = result["financial_components"]
        assert "expense_to_income" in fc
        assert "savings_rate" in fc
        assert "balance_trend" in fc
        assert "spending_growth" in fc

    def test_burnout_components_present(self, scorer):
        """Burnout components breakdown should have all 5 components."""
        features = _make_features()
        result = scorer.score(features)
        bc = result["burnout_components"]
        assert "food_delivery" in bc
        assert "late_night" in bc
        assert "weekday_spending" in bc
        assert "grab_trend" in bc
        assert "spending_spikes" in bc
