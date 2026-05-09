"""
ML-based transaction categorizer.
Phase 2 upgrade path: Uses TF-IDF + Multinomial Naive Bayes to classify
transactions that the rule-based system cannot handle.
"""

import json
import os
import pickle
from typing import List, Optional, Tuple

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline as SkPipeline

from app.config import CATEGORIES

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "ml_categorizer.pkl")


class MLCategorizer:
    """
    ML-based transaction categorizer using TF-IDF + Naive Bayes.

    This is designed as an upgrade path from the rule-based categorizer.
    It can be trained on historically categorized transactions and used
    to classify new, unknown transactions.

    Usage:
        # Train
        ml_cat = MLCategorizer()
        ml_cat.train(descriptions, categories)
        ml_cat.save()

        # Predict
        ml_cat = MLCategorizer()
        ml_cat.load()
        category = ml_cat.predict("SOME UNKNOWN MERCHANT")
    """

    def __init__(self):
        """Initialize the ML categorizer with a TF-IDF + NB pipeline."""
        self.model: Optional[SkPipeline] = None
        self.is_trained = False
        self._build_pipeline()

    def _build_pipeline(self):
        """Build the sklearn pipeline: TF-IDF vectorizer → Naive Bayes."""
        self.model = SkPipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(
                        analyzer="char_wb",
                        ngram_range=(2, 5),
                        max_features=5000,
                        lowercase=True,
                        strip_accents="unicode",
                    ),
                ),
                ("clf", MultinomialNB(alpha=0.1)),
            ]
        )

    def train(
        self,
        descriptions: List[str],
        categories: List[str],
        test_size: float = 0.2,
    ) -> dict:
        """
        Train the ML categorizer on labeled transaction data.

        Args:
            descriptions: List of transaction description strings.
            categories: List of corresponding category labels.
            test_size: Fraction of data to hold out for evaluation.

        Returns:
            Dictionary with training metrics (accuracy, report).
        """
        if len(descriptions) != len(categories):
            raise ValueError("descriptions and categories must have same length")

        if len(descriptions) < 10:
            raise ValueError("Need at least 10 samples to train")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            descriptions,
            categories,
            test_size=test_size,
            random_state=42,
            stratify=categories if len(set(categories)) > 1 else None,
        )

        # Train
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = (pd.Series(y_pred) == pd.Series(y_test)).mean()

        report = classification_report(
            y_test, y_pred, output_dict=True, zero_division=0
        )

        return {
            "accuracy": round(accuracy, 4),
            "train_size": len(X_train),
            "test_size": len(X_test),
            "report": report,
        }

    def predict(self, description: str) -> str:
        """
        Predict category for a single transaction description.

        Args:
            description: Transaction description string.

        Returns:
            Predicted category string.
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() or load() first.")
        return self.model.predict([description])[0]

    def predict_batch(self, descriptions: List[str]) -> List[str]:
        """Predict categories for multiple descriptions."""
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() or load() first.")
        return self.model.predict(descriptions).tolist()

    def predict_proba(self, description: str) -> List[Tuple[str, float]]:
        """
        Predict category with confidence scores.

        Returns:
            List of (category, probability) tuples, sorted by probability desc.
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() or load() first.")
        probs = self.model.predict_proba([description])[0]
        classes = self.model.classes_
        results = list(zip(classes, probs))
        results.sort(key=lambda x: x[1], reverse=True)
        return [(cat, round(prob, 4)) for cat, prob in results]

    def save(self, path: Optional[str] = None):
        """Save the trained model to disk."""
        save_path = path or MODEL_PATH
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            pickle.dump(self.model, f)

    def load(self, path: Optional[str] = None):
        """Load a trained model from disk."""
        load_path = path or MODEL_PATH
        if not os.path.exists(load_path):
            raise FileNotFoundError(f"No model found at {load_path}")
        with open(load_path, "rb") as f:
            self.model = pickle.load(f)
        self.is_trained = True

    @staticmethod
    def generate_training_data() -> Tuple[List[str], List[str]]:
        """
        Generate synthetic training data from known Malaysian merchants.
        Useful for bootstrapping the model before real user data is available.

        Returns:
            Tuple of (descriptions, categories).
        """
        training_pairs = [
            # Food & Beverage
            ("GRAB FOOD NASI LEMAK", "Food & Beverage"),
            ("GRABFOOD MEE GORENG", "Food & Beverage"),
            ("FOODPANDA SUSHI KING", "Food & Beverage"),
            ("FOOD PANDA DELIVERY", "Food & Beverage"),
            ("STARBUCKS SUNWAY", "Food & Beverage"),
            ("STARBUCKS KLCC", "Food & Beverage"),
            ("MCDONALD DRIVE THRU", "Food & Beverage"),
            ("KFC DELIVERY", "Food & Beverage"),
            ("PIZZA HUT BANDAR", "Food & Beverage"),
            ("DOMINO PIZZA", "Food & Beverage"),
            ("NASI KANDAR LINE CLEAR", "Food & Beverage"),
            ("MAMAK RESTAURANT", "Food & Beverage"),
            ("KOPITIAM OLDTOWN", "Food & Beverage"),
            ("OLD TOWN WHITE COFFEE", "Food & Beverage"),
            ("SECRET RECIPE CAKE", "Food & Beverage"),
            ("SUSHI MENTAI", "Food & Beverage"),
            ("7-ELEVEN PURCHASE", "Food & Beverage"),
            ("FAMILY MART", "Food & Beverage"),
            ("TEALIVE BUBBLE TEA", "Food & Beverage"),
            ("CHATIME DRINK", "Food & Beverage"),
            # Transport
            ("TNG EWALLET TOPUP", "Transport"),
            ("TOUCH N GO RELOAD", "Transport"),
            ("PETRONAS FUEL", "Transport"),
            ("SHELL PETROL", "Transport"),
            ("GRABCAR RIDE", "Transport"),
            ("GRAB CAR PAYMENT", "Transport"),
            ("LRT TICKET PURCHASE", "Transport"),
            ("MRT FARE", "Transport"),
            ("TOLL PAYMENT PLUS", "Transport"),
            ("PARKING PAYMENT", "Transport"),
            ("TNG TOLL SMART", "Transport"),
            ("BHP PETROL STATION", "Transport"),
            ("CALTEX FUEL", "Transport"),
            # Shopping
            ("SHOPEE PURCHASE", "Shopping"),
            ("SHOPEEPAY MALL", "Shopping"),
            ("LAZADA ONLINE", "Shopping"),
            ("AEON MALL SHOPPING", "Shopping"),
            ("MR DIY PURCHASE", "Shopping"),
            ("IKEA FURNITURE", "Shopping"),
            ("WATSON PHARMACY", "Shopping"),
            ("GUARDIAN HEALTH", "Shopping"),
            ("UNIQLO CLOTHING", "Shopping"),
            ("PADINI OUTLET", "Shopping"),
            ("DAISO JAPAN", "Shopping"),
            ("POPULAR BOOKSTORE", "Shopping"),
            # Bills
            ("UNIFI BILL PAYMENT", "Bills"),
            ("MAXIS PHONE BILL", "Bills"),
            ("CELCOM POSTPAID", "Bills"),
            ("DIGI PHONE TOPUP", "Bills"),
            ("TNB ELECTRIC BILL", "Bills"),
            ("TENAGA NASIONAL", "Bills"),
            ("ASTRO SUBSCRIPTION", "Bills"),
            ("INSURANCE PREMIUM", "Bills"),
            ("WATER BILL PAYMENT", "Bills"),
            ("HOUSE RENTAL PAYMENT", "Bills"),
            ("LOAN REPAYMENT", "Bills"),
            ("CREDIT CARD PAYMENT", "Bills"),
            # Entertainment
            ("GSC CINEMA TICKET", "Entertainment"),
            ("TGV CINEMA BOOKING", "Entertainment"),
            ("NETFLIX SUBSCRIPTION", "Entertainment"),
            ("SPOTIFY PREMIUM", "Entertainment"),
            ("DISNEY PLUS HOTSTAR", "Entertainment"),
            ("YOUTUBE PREMIUM", "Entertainment"),
            ("PLAYSTATION STORE", "Entertainment"),
            ("STEAM GAMES", "Entertainment"),
            ("GYM FITNESS FIRST", "Entertainment"),
            ("ANYTIME FITNESS", "Entertainment"),
            # Income
            ("SALARY CREDIT", "Income"),
            ("GAJI BULANAN", "Income"),
            ("BONUS PAYMENT", "Income"),
            ("TRANSFER IN", "Income"),
            ("DIVIDEND PAYMENT", "Income"),
            ("REFUND CREDIT", "Income"),
            ("CASHBACK REWARD", "Income"),
            ("FREELANCE PAYMENT", "Income"),
        ]

        descriptions = [p[0] for p in training_pairs]
        categories = [p[1] for p in training_pairs]
        return descriptions, categories
