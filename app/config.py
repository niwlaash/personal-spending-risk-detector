"""
Application configuration and constants.
"""

import os

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./spending_risk.db")

# Risk score thresholds
FINANCIAL_RISK_LOW = 30
FINANCIAL_RISK_MEDIUM = 60
FINANCIAL_RISK_HIGH = 80

BURNOUT_RISK_LOW = 30
BURNOUT_RISK_MEDIUM = 60
BURNOUT_RISK_HIGH = 80

# Malaysia-specific merchant keywords mapping
MALAYSIA_MERCHANTS = {
    "grab": "Food & Beverage",
    "grabfood": "Food & Beverage",
    "grab food": "Food & Beverage",
    "foodpanda": "Food & Beverage",
    "food panda": "Food & Beverage",
    "shopee": "Shopping",
    "shopeepay": "Shopping",
    "lazada": "Shopping",
    "tng": "Transport",
    "touch n go": "Transport",
    "touch 'n go": "Transport",
    "petronas": "Transport",
    "shell": "Transport",
    "grabcar": "Transport",
    "grab car": "Transport",
    "unifi": "Bills",
    "maxis": "Bills",
    "celcom": "Bills",
    "digi": "Bills",
    "tnb": "Bills",
    "tenaga nasional": "Bills",
    "astro": "Bills",
    "netflix": "Entertainment",
    "spotify": "Entertainment",
    "disney": "Entertainment",
    "cinema": "Entertainment",
    "gsc": "Entertainment",
    "tgv": "Entertainment",
    "starbucks": "Food & Beverage",
    "mcdonald": "Food & Beverage",
    "kfc": "Food & Beverage",
    "pizza hut": "Food & Beverage",
    "domino": "Food & Beverage",
    "7-eleven": "Food & Beverage",
    "7 eleven": "Food & Beverage",
    "watson": "Shopping",
    "guardian": "Shopping",
    "aeon": "Shopping",
    "mr diy": "Shopping",
    "ikea": "Shopping",
    "salary": "Income",
    "gaji": "Income",
    "bonus": "Income",
    "allowance": "Income",
    "transfer in": "Income",
}

# Transaction categories
CATEGORIES = [
    "Food & Beverage",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Income",
    "Other",
]

# Late-night hours (burnout signal)
LATE_NIGHT_START = 22  # 10 PM
LATE_NIGHT_END = 5  # 5 AM

# Recommended savings rate (Malaysia context)
RECOMMENDED_SAVINGS_RATE = 0.20  # 20% of income
