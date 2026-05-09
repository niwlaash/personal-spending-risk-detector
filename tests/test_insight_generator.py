"""
Unit tests for the InsightGenerator service.
"""

import pytest

from app.services.insight_generator import InsightGenerator


@pytest.fixture
def generator():
    return InsightGenerator()


def _make_features(**overrides):
    """Helper to create features dict with defaults."""
    defaults = {
        "spending_summary": {
            "total_expenses": 3000,
            "total_income": 5000,
            "net": 2000,
            "transaction_count": 50,
        },
        "category_breakdown": {
            "Food & Beverage": 800,
            "Transport": 400,
            "Shopping": 1000,
            "Bills": 500,
            "Entertainment": 300,
        },
        "spending_growth_rate": 10.0,
        "food_delivery_frequency": {"total_count": 10, "weekly_average": 2.5},
        "late_night_ratio": 0.05,
        "weekday_vs_weekend_ratio": 1.5,
        "grab_food_trend": {"trend": "stable", "total_spent": -200},
        "spending_spike_count": 1,
        "savings_rate": 0.4,
        "balance_trend": "stable",
    }
    defaults.update(overrides)
    return defaults


def _make_risk_scores(**overrides):
    """Helper to create risk scores dict."""
    defaults = {
        "financial_risk_score": 25,
        "financial_risk_level": "Low",
        "burnout_risk_score": 20,
        "burnout_risk_level": "Low",
    }
    defaults.update(overrides)
    return defaults


class TestInsightGenerator:
    """Tests for InsightGenerator."""

    def test_generates_insights(self, generator):
        """Should return a non-empty list of insights."""
        features = _make_features()
        scores = _make_risk_scores()
        insights = generator.generate(features, scores)
        assert isinstance(insights, list)
        assert len(insights) > 0

    def test_spending_insights_include_total(self, generator):
        """Should mention total spending amount."""
        features = _make_features()
        scores = _make_risk_scores()
        insights = generator.generate(features, scores)
        text = "\n".join(insights)
        assert "3,000" in text or "3000" in text

    def test_top_category_mentioned(self, generator):
        """Should mention the top spending category."""
        features = _make_features()
        scores = _make_risk_scores()
        insights = generator.generate(features, scores)
        text = "\n".join(insights)
        assert "Shopping" in text  # Shopping is the highest at 1000

    def test_high_food_delivery_warning(self, generator):
        """High food delivery frequency should trigger a warning."""
        features = _make_features(
            food_delivery_frequency={"total_count": 40, "weekly_average": 6.0}
        )
        scores = _make_risk_scores()
        insights = generator.generate(features, scores)
        text = "\n".join(insights)
        assert "food delivery" in text.lower() or "order" in text.lower()

    def test_late_night_warning(self, generator):
        """High late-night ratio should trigger a warning."""
        features = _make_features(late_night_ratio=0.35)
        scores = _make_risk_scores()
        insights = generator.generate(features, scores)
        text = "\n".join(insights)
        assert "night" in text.lower() or "late" in text.lower()

    def test_low_savings_warning(self, generator):
        """Low savings rate should generate a warning."""
        features = _make_features(savings_rate=0.05)
        scores = _make_risk_scores()
        insights = generator.generate(features, scores)
        text = "\n".join(insights)
        assert "savings" in text.lower() or "saving" in text.lower()

    def test_good_savings_positive(self, generator):
        """Good savings rate should generate positive feedback."""
        features = _make_features(savings_rate=0.35)
        scores = _make_risk_scores()
        insights = generator.generate(features, scores)
        text = "\n".join(insights)
        assert "good" in text.lower() or "35" in text

    def test_suggestions_for_high_risk(self, generator):
        """High risk should produce actionable suggestions."""
        features = _make_features()
        scores = _make_risk_scores(
            financial_risk_level="High", burnout_risk_level="High"
        )
        insights = generator.generate(features, scores)
        text = "\n".join(insights)
        assert "suggestion" in text.lower() or "budget" in text.lower()

    def test_healthy_message_for_low_risk(self, generator):
        """Low risk on both should produce a positive message."""
        features = _make_features()
        scores = _make_risk_scores()
        insights = generator.generate(features, scores)
        text = "\n".join(insights)
        assert "healthy" in text.lower() or "good" in text.lower()

    def test_spending_growth_alert(self, generator):
        """High spending growth should trigger an alert."""
        features = _make_features(spending_growth_rate=45.0)
        scores = _make_risk_scores()
        insights = generator.generate(features, scores)
        text = "\n".join(insights)
        assert "increased" in text.lower() or "45" in text
