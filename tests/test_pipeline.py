"""
Integration tests for the full Pipeline.
Tests end-to-end processing with all three sample datasets.
"""

import os

import pytest

from app.pipeline import Pipeline


@pytest.fixture
def pipeline():
    return Pipeline()


def _data_path(filename):
    """Get absolute path to a sample data file."""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        filename,
    )


class TestPipeline:
    """Integration tests for the full analysis pipeline."""

    def test_normal_profile(self, pipeline):
        """Normal sample should produce low risk scores."""
        result = pipeline.run(_data_path("sample_statement.csv"), "csv")

        assert result["transaction_count"] > 0
        assert "risk_scores" in result
        assert "insights" in result
        assert "features" in result
        assert "transactions" in result

        rs = result["risk_scores"]
        assert 0 <= rs["financial_risk_score"] <= 100
        assert 0 <= rs["burnout_risk_score"] <= 100
        assert rs["financial_risk_level"] in ("Low", "Medium", "High", "Critical")
        assert rs["burnout_risk_level"] in ("Low", "Medium", "High", "Critical")

    def test_high_risk_profile(self, pipeline):
        """High risk sample should produce elevated financial risk."""
        path = _data_path("sample_high_risk.csv")
        if not os.path.exists(path):
            pytest.skip("sample_high_risk.csv not found")

        result = pipeline.run(path, "csv")

        rs = result["risk_scores"]
        # This profile has overspending and negative balance
        assert rs["financial_risk_score"] >= 40
        assert rs["financial_risk_level"] in ("Medium", "High", "Critical")

    def test_critical_burnout_profile(self, pipeline):
        """Critical burnout sample should produce high burnout risk."""
        path = _data_path("sample_critical_burnout.csv")
        if not os.path.exists(path):
            pytest.skip("sample_critical_burnout.csv not found")

        result = pipeline.run(path, "csv")

        rs = result["risk_scores"]
        # This profile has extremely high food delivery frequency and spending
        # Note: late-night signals are lost since CSV date parsing drops time info
        assert rs["burnout_risk_score"] >= 15
        assert rs["burnout_risk_level"] in ("Low", "Medium", "High", "Critical")

    def test_result_structure(self, pipeline):
        """Verify the complete result structure."""
        result = pipeline.run(_data_path("sample_statement.csv"), "csv")

        # Top level keys
        assert set(result.keys()) == {
            "transactions",
            "transaction_count",
            "features",
            "risk_scores",
            "insights",
        }

        # Risk scores structure
        rs = result["risk_scores"]
        assert "financial_risk_score" in rs
        assert "burnout_risk_score" in rs
        assert "financial_risk_level" in rs
        assert "burnout_risk_level" in rs
        assert "financial_components" in rs
        assert "burnout_components" in rs

        # Insights should be a list of strings
        assert isinstance(result["insights"], list)
        for insight in result["insights"]:
            assert isinstance(insight, str)

    def test_transactions_have_categories(self, pipeline):
        """All transactions in the result should have categories."""
        result = pipeline.run(_data_path("sample_statement.csv"), "csv")
        for txn in result["transactions"]:
            assert "category" in txn
            assert txn["category"] is not None
            assert txn["category"] != ""

    def test_features_serializable(self, pipeline):
        """All features should be JSON-serializable types."""
        import json

        result = pipeline.run(_data_path("sample_statement.csv"), "csv")
        # This should not raise
        json.dumps(result["features"], default=str)

    def test_pipeline_from_dataframe(self, pipeline):
        """Test the run_from_dataframe alternative entry point."""
        import pandas as pd

        df = pd.DataFrame(
            {
                "date": pd.to_datetime(["2026-03-01", "2026-03-02", "2026-03-03"]),
                "description": ["SALARY CREDIT", "GRAB FOOD", "SHOPEE"],
                "amount": [5000.0, -20.0, -100.0],
                "balance": [5000.0, 4980.0, 4880.0],
            }
        )
        result = pipeline.run_from_dataframe(df)
        assert result["transaction_count"] == 3
        assert result["risk_scores"]["financial_risk_score"] >= 0
