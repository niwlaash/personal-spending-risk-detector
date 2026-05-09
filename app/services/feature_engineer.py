"""
Feature engineering service.
Extracts spending patterns, risk indicators, and burnout signals
from categorized transaction data.
"""

from typing import Any, Dict

import numpy as np
import pandas as pd

from app.config import LATE_NIGHT_END, LATE_NIGHT_START


class FeatureEngineer:
    """
    Extracts behavioral and financial features from transaction data.

    Features include:
        - Spending trends (daily, weekly, monthly)
        - Spending growth rates
        - Category breakdowns
        - Late-night transaction frequency
        - Food delivery patterns
        - Savings rate estimation
    """

    def extract_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract all features from the transaction DataFrame.

        Args:
            df: Categorized transaction DataFrame with columns:
                date, description, amount, balance, category.

        Returns:
            Dictionary of computed features.
        """
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])

        features = {}

        # --- Spending patterns ---
        features["spending_summary"] = self._spending_summary(df)
        features["daily_spending"] = self._daily_spending(df)
        features["weekly_spending"] = self._weekly_spending(df)
        features["monthly_spending"] = self._monthly_spending(df)
        features["category_breakdown"] = self._category_breakdown(df)

        # --- Risk indicators ---
        features["spending_growth_rate"] = self._spending_growth_rate(df)
        features["food_delivery_frequency"] = self._food_delivery_frequency(df)
        features["late_night_ratio"] = self._late_night_ratio(df)
        features["spending_spike_count"] = self._spending_spike_count(df)

        # --- Burnout signals ---
        features["weekday_vs_weekend_ratio"] = self._weekday_vs_weekend_ratio(df)
        features["grab_food_trend"] = self._grab_food_trend(df)
        features["savings_rate"] = self._savings_rate(df)

        # --- Balance trend ---
        features["balance_trend"] = self._balance_trend(df)

        # --- Income vs Expense ---
        features["income_vs_expense"] = self._income_vs_expense(df)

        return features

    def _spending_summary(self, df: pd.DataFrame) -> Dict[str, float]:
        """Total spending, income, and net for the period."""
        expenses = df[df["amount"] < 0]["amount"].sum()
        income = df[df["amount"] > 0]["amount"].sum()
        return {
            "total_expenses": abs(expenses),
            "total_income": income,
            "net": income + expenses,
            "transaction_count": len(df),
        }

    def _daily_spending(self, df: pd.DataFrame) -> pd.Series:
        """Average daily spending amount."""
        expenses = df[df["amount"] < 0].copy()
        daily = expenses.groupby(expenses["date"].dt.date)["amount"].sum().abs()
        return daily

    def _weekly_spending(self, df: pd.DataFrame) -> pd.Series:
        """Weekly total spending."""
        expenses = df[df["amount"] < 0].copy()
        expenses["week"] = expenses["date"].dt.isocalendar().week
        weekly = expenses.groupby("week")["amount"].sum().abs()
        return weekly

    def _monthly_spending(self, df: pd.DataFrame) -> pd.Series:
        """Monthly total spending."""
        expenses = df[df["amount"] < 0].copy()
        expenses["month"] = expenses["date"].dt.to_period("M").astype(str)
        monthly = expenses.groupby("month")["amount"].sum().abs()
        return monthly

    def _category_breakdown(self, df: pd.DataFrame) -> Dict[str, float]:
        """Spending by category."""
        expenses = df[df["amount"] < 0].copy()
        breakdown = expenses.groupby("category")["amount"].sum().abs().to_dict()
        return breakdown

    def _spending_growth_rate(self, df: pd.DataFrame) -> float:
        """
        Compare spending in the second half vs the first half of the period.
        Returns percentage growth (positive = spending increased).
        """
        expenses = df[df["amount"] < 0].copy()
        if expenses.empty:
            return 0.0

        midpoint = (
            expenses["date"].min()
            + (expenses["date"].max() - expenses["date"].min()) / 2
        )

        first_half = expenses[expenses["date"] <= midpoint]["amount"].sum()
        second_half = expenses[expenses["date"] > midpoint]["amount"].sum()

        if first_half == 0:
            return 0.0

        growth = ((abs(second_half) - abs(first_half)) / abs(first_half)) * 100
        return round(growth, 2)

    def _food_delivery_frequency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Count food delivery transactions and compute weekly average."""
        food_keywords = ["grab", "foodpanda", "food panda", "grabfood"]
        mask = (
            df["description"]
            .str.lower()
            .str.contains("|".join(food_keywords), na=False)
        )
        food_txns = df[mask]
        total = len(food_txns)

        # Weekly average
        if total > 0 and not food_txns.empty:
            date_range = (food_txns["date"].max() - food_txns["date"].min()).days
            weeks = max(date_range / 7, 1)
            weekly_avg = round(total / weeks, 1)
        else:
            weekly_avg = 0

        return {"total_count": total, "weekly_average": weekly_avg}

    def _late_night_ratio(self, df: pd.DataFrame) -> float:
        """
        Ratio of transactions occurring during late-night hours.
        Late night: 10 PM to 5 AM.
        """
        if df.empty:
            return 0.0

        # Only consider if we have time information
        has_time = df["date"].dt.hour.sum() > 0
        if not has_time:
            # If all times are midnight (00:00), we likely don't have time data
            return -1.0  # Sentinel: time data unavailable

        hours = df["date"].dt.hour
        late_night = ((hours >= LATE_NIGHT_START) | (hours < LATE_NIGHT_END)).sum()
        return round(late_night / len(df), 4)

    def _spending_spike_count(self, df: pd.DataFrame) -> int:
        """
        Count days where spending exceeds 2x the average daily spending.
        These are sudden spending spikes that may indicate stress purchases.
        """
        expenses = df[df["amount"] < 0].copy()
        daily = expenses.groupby(expenses["date"].dt.date)["amount"].sum().abs()

        if daily.empty:
            return 0

        avg = daily.mean()
        threshold = avg * 2
        spikes = (daily > threshold).sum()
        return int(spikes)

    def _weekday_vs_weekend_ratio(self, df: pd.DataFrame) -> float:
        """
        Ratio of weekday spending to weekend spending.
        Higher ratio = more weekday spending (potential burnout signal).
        """
        expenses = df[df["amount"] < 0].copy()
        expenses["is_weekday"] = expenses["date"].dt.dayofweek < 5

        weekday_total = expenses[expenses["is_weekday"]]["amount"].sum()
        weekend_total = expenses[~expenses["is_weekday"]]["amount"].sum()

        if weekend_total == 0:
            return float("inf") if weekday_total != 0 else 1.0

        return round(abs(weekday_total) / abs(weekend_total), 2)

    def _grab_food_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze GrabFood spending trend over the period.
        Increasing trend is a burnout signal.
        """
        grab_mask = df["description"].str.lower().str.contains("grab", na=False)
        grab_txns = df[grab_mask & (df["amount"] < 0)].copy()

        if grab_txns.empty:
            return {"trend": "no_data", "total_spent": 0}

        grab_txns["week"] = grab_txns["date"].dt.isocalendar().week
        weekly = grab_txns.groupby("week")["amount"].sum().abs()

        if len(weekly) < 2:
            trend = "insufficient_data"
        else:
            # Simple trend: compare last half average vs first half average
            mid = len(weekly) // 2
            first_avg = weekly.iloc[:mid].mean()
            second_avg = weekly.iloc[mid:].mean()

            if second_avg > first_avg * 1.2:
                trend = "increasing"
            elif second_avg < first_avg * 0.8:
                trend = "decreasing"
            else:
                trend = "stable"

        return {
            "trend": trend,
            "total_spent": round(grab_txns["amount"].sum(), 2),
        }

    def _savings_rate(self, df: pd.DataFrame) -> float:
        """
        Estimate savings rate: (income - expenses) / income.
        Returns as a ratio (e.g. 0.20 = 20%).
        """
        income = df[df["amount"] > 0]["amount"].sum()
        expenses = abs(df[df["amount"] < 0]["amount"].sum())

        if income == 0:
            return 0.0

        savings = income - expenses
        rate = savings / income
        return round(rate, 4)

    def _balance_trend(self, df: pd.DataFrame) -> str:
        """
        Determine the overall balance trend.
        """
        if "balance" not in df.columns or df["balance"].dropna().empty:
            return "no_data"

        balances = df["balance"].dropna()
        if len(balances) < 2:
            return "insufficient_data"

        first_balance = balances.iloc[0]
        last_balance = balances.iloc[-1]

        if last_balance > first_balance * 1.05:
            return "increasing"
        elif last_balance < first_balance * 0.95:
            return "decreasing"
        else:
            return "stable"

    def _income_vs_expense(self, df: pd.DataFrame) -> Dict[str, float]:
        """Compare total income vs total expenses."""
        income = df[df["amount"] > 0]["amount"].sum()
        expenses = abs(df[df["amount"] < 0]["amount"].sum())
        ratio = round(expenses / income, 4) if income > 0 else float("inf")
        return {
            "income": round(income, 2),
            "expenses": round(expenses, 2),
            "expense_to_income_ratio": ratio,
        }
