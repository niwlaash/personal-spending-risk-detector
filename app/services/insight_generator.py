"""
Insight generation engine.
Produces human-readable, actionable insights from features and risk scores.
Malaysia-context aware.
"""

from typing import Any, Dict, List

from app.config import RECOMMENDED_SAVINGS_RATE


class InsightGenerator:
    """Generates human-readable financial and burnout insights."""

    def generate(
        self, features: Dict[str, Any], risk_scores: Dict[str, Any]
    ) -> List[str]:
        """Generate all insights from features and risk scores."""
        insights = []
        insights.extend(self._spending_insights(features))
        insights.extend(self._burnout_insights(features))
        insights.extend(self._financial_health_insights(features, risk_scores))
        insights.extend(self._suggestions(features, risk_scores))
        return insights

    def _spending_insights(self, f: Dict) -> List[str]:
        out = []
        summary = f.get("spending_summary", {})
        total_exp = summary.get("total_expenses", 0)
        total_inc = summary.get("total_income", 0)
        if total_exp > 0:
            out.append(
                f"📊 Total spending: RM {total_exp:,.2f} across {summary.get('transaction_count', 0)} transactions."
            )
        growth = f.get("spending_growth_rate", 0)
        if growth > 20:
            out.append(
                f"📈 Spending increased by {growth:.1f}% in the second half of the period — watch out!"
            )
        elif growth < -20:
            out.append(
                f"📉 Spending decreased by {abs(growth):.1f}% — great improvement!"
            )
        cat = f.get("category_breakdown", {})
        if cat:
            top = max(cat, key=cat.get)
            out.append(f"🏷️ Top spending category: {top} (RM {cat[top]:,.2f}).")
        return out

    def _burnout_insights(self, f: Dict) -> List[str]:
        out = []
        fd = f.get("food_delivery_frequency", {})
        wa = fd.get("weekly_average", 0)
        if wa >= 5:
            out.append(
                f"🍔 You order food delivery ~{wa:.0f}x/week. This may indicate stress or lack of time to cook."
            )
        elif wa >= 3:
            out.append(
                f"🍕 Moderate food delivery usage (~{wa:.0f}x/week). Consider meal prepping to save money."
            )

        lr = f.get("late_night_ratio", 0)
        if lr > 0.2:
            pct = lr * 100
            out.append(
                f"🌙 {pct:.0f}% of transactions happen late at night — a potential burnout signal."
            )

        gt = f.get("grab_food_trend", {})
        if gt.get("trend") == "increasing":
            out.append(
                "📱 GrabFood spending is trending upward — possible comfort/stress eating pattern."
            )

        wr = f.get("weekday_vs_weekend_ratio", 1.0)
        if wr > 3.0 and wr != float("inf"):
            out.append(
                f"📅 Weekday spending is {wr:.1f}x higher than weekends — heavy work-week spending detected."
            )

        spikes = f.get("spending_spike_count", 0)
        if spikes >= 3:
            out.append(
                f"⚡ {spikes} spending spike days detected — sudden large purchases may indicate emotional spending."
            )
        return out

    def _financial_health_insights(self, f: Dict, r: Dict) -> List[str]:
        out = []
        sr = f.get("savings_rate", 0)
        if sr < 0:
            out.append("🚨 You're spending more than you earn — negative savings rate!")
        elif sr < RECOMMENDED_SAVINGS_RATE:
            out.append(
                f"💰 Savings rate is {sr*100:.1f}%, below the recommended {RECOMMENDED_SAVINGS_RATE*100:.0f}%."
            )
        else:
            out.append(f"✅ Good savings rate: {sr*100:.1f}%!")

        bt = f.get("balance_trend", "no_data")
        if bt == "decreasing":
            out.append("📉 Your account balance is trending downward.")
        elif bt == "increasing":
            out.append("📈 Your account balance is trending upward — keep it up!")
        return out

    def _suggestions(self, f: Dict, r: Dict) -> List[str]:
        out = []
        bl = r.get("burnout_risk_level", "Low")
        fl = r.get("financial_risk_level", "Low")
        if bl in ("High", "Critical"):
            out.append(
                "💡 Suggestion: Plan meals earlier or batch-cook to reduce food delivery spending."
            )
            out.append(
                "💡 Suggestion: Set a monthly food delivery budget and track it."
            )
        if fl in ("High", "Critical"):
            out.append(
                "💡 Suggestion: Create a monthly budget and automate savings transfers on payday."
            )
            out.append(
                "💡 Suggestion: Review subscriptions and recurring charges for items you no longer use."
            )
        if bl == "Low" and fl == "Low":
            out.append("🎉 Your spending looks healthy! Keep maintaining good habits.")
        return out
