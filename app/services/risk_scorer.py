"""
Risk scoring engine.
Computes Financial Risk Score (0-100) and Burnout Score (0-100).
"""

from typing import Any, Dict, Tuple

from app.config import (
    BURNOUT_RISK_HIGH,
    BURNOUT_RISK_LOW,
    BURNOUT_RISK_MEDIUM,
    FINANCIAL_RISK_HIGH,
    FINANCIAL_RISK_LOW,
    FINANCIAL_RISK_MEDIUM,
    RECOMMENDED_SAVINGS_RATE,
)


class RiskScorer:
    """Computes financial risk and burnout risk scores from features."""

    def score(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Compute all risk scores from extracted features."""
        fin_score, fin_comp = self._financial_risk(features)
        burn_score, burn_comp = self._burnout_risk(features)
        return {
            "financial_risk_score": fin_score,
            "financial_risk_level": self._level(
                fin_score,
                FINANCIAL_RISK_LOW,
                FINANCIAL_RISK_MEDIUM,
                FINANCIAL_RISK_HIGH,
            ),
            "burnout_risk_score": burn_score,
            "burnout_risk_level": self._level(
                burn_score, BURNOUT_RISK_LOW, BURNOUT_RISK_MEDIUM, BURNOUT_RISK_HIGH
            ),
            "financial_components": fin_comp,
            "burnout_components": burn_comp,
        }

    def _financial_risk(self, f: Dict) -> Tuple[float, Dict]:
        c = {}
        ie = f.get("income_vs_expense", {})
        r = ie.get("expense_to_income_ratio", 1.0)
        c["expense_to_income"] = (
            100
            if r >= 1.0
            else 80 if r >= 0.9 else 50 if r >= 0.7 else 25 if r >= 0.5 else 10
        )

        s = f.get("savings_rate", 0)
        c["savings_rate"] = (
            100
            if s <= 0
            else (
                75
                if s < 0.1
                else 50 if s < RECOMMENDED_SAVINGS_RATE else 20 if s < 0.3 else 5
            )
        )

        t = f.get("balance_trend", "no_data")
        c["balance_trend"] = {"decreasing": 80, "stable": 30, "increasing": 10}.get(
            t, 40
        )

        g = f.get("spending_growth_rate", 0)
        c["spending_growth"] = (
            90 if g > 50 else 65 if g > 25 else 40 if g > 10 else 20 if g > 0 else 10
        )

        total = (
            c["expense_to_income"] * 0.35
            + c["savings_rate"] * 0.30
            + c["balance_trend"] * 0.20
            + c["spending_growth"] * 0.15
        )
        return min(100, max(0, round(total, 1))), c

    def _burnout_risk(self, f: Dict) -> Tuple[float, Dict]:
        c = {}
        fd = f.get("food_delivery_frequency", {})
        wa = fd.get("weekly_average", 0)
        c["food_delivery"] = (
            90
            if wa >= 7
            else 70 if wa >= 5 else 45 if wa >= 3 else 20 if wa >= 1 else 5
        )

        lr = f.get("late_night_ratio", 0)
        c["late_night"] = (
            30
            if lr < 0
            else 85 if lr > 0.3 else 60 if lr > 0.2 else 35 if lr > 0.1 else 10
        )

        wr = f.get("weekday_vs_weekend_ratio", 1.0)
        c["weekday_spending"] = (
            70
            if wr == float("inf")
            else 80 if wr > 4 else 60 if wr > 3 else 40 if wr > 2 else 15
        )

        gt = f.get("grab_food_trend", {}).get("trend", "no_data")
        c["grab_trend"] = {"increasing": 85, "stable": 30, "decreasing": 10}.get(gt, 25)

        sp = f.get("spending_spike_count", 0)
        c["spending_spikes"] = (
            80 if sp >= 5 else 55 if sp >= 3 else 25 if sp >= 1 else 5
        )

        total = (
            c["food_delivery"] * 0.25
            + c["late_night"] * 0.20
            + c["weekday_spending"] * 0.20
            + c["grab_trend"] * 0.20
            + c["spending_spikes"] * 0.15
        )
        return min(100, max(0, round(total, 1))), c

    @staticmethod
    def _level(score, low, medium, high):
        if score >= high:
            return "Critical"
        if score >= medium:
            return "High"
        if score >= low:
            return "Medium"
        return "Low"
