"""
Pipeline orchestrator.
Ties together parsing, cleaning, categorization, feature extraction,
risk scoring, and insight generation into a single pipeline.
"""

from typing import Any, Dict

import pandas as pd

from app.parsers.csv_parser import CSVParser
from app.parsers.pdf_parser import PDFParser
from app.services.categorizer import Categorizer
from app.services.data_cleaner import DataCleaner
from app.services.feature_engineer import FeatureEngineer
from app.services.insight_generator import InsightGenerator
from app.services.risk_scorer import RiskScorer


class Pipeline:
    """End-to-end analysis pipeline for bank statements."""

    def __init__(self):
        self.csv_parser = CSVParser()
        self.pdf_parser = PDFParser()
        self.cleaner = DataCleaner()
        self.categorizer = Categorizer()
        self.feature_engineer = FeatureEngineer()
        self.risk_scorer = RiskScorer()
        self.insight_generator = InsightGenerator()

    def run(self, file_path: str, file_type: str = "csv") -> Dict[str, Any]:
        """
        Run the full analysis pipeline on a bank statement file.

        Args:
            file_path: Path to the uploaded file.
            file_type: Either 'csv' or 'pdf'.

        Returns:
            Dictionary with transactions, features, risk_scores, and insights.
        """
        # 1. Parse
        if file_type == "pdf":
            raw_df = self.pdf_parser.parse(file_path)
        else:
            raw_df = self.csv_parser.parse(file_path)

        # 2. Clean
        cleaned_df = self.cleaner.clean(raw_df)

        # 3. Categorize
        categorized_df = self.categorizer.categorize(cleaned_df)

        # 4. Feature extraction
        features = self.feature_engineer.extract_features(categorized_df)

        # 5. Risk scoring
        risk_scores = self.risk_scorer.score(features)

        # 6. Insight generation
        insights = self.insight_generator.generate(features, risk_scores)

        # Convert non-serializable objects
        serializable_features = self._make_serializable(features)

        return {
            "transactions": categorized_df.to_dict(orient="records"),
            "transaction_count": len(categorized_df),
            "features": serializable_features,
            "risk_scores": risk_scores,
            "insights": insights,
        }

    def run_from_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run pipeline from an already-parsed DataFrame."""
        cleaned_df = self.cleaner.clean(df)
        categorized_df = self.categorizer.categorize(cleaned_df)
        features = self.feature_engineer.extract_features(categorized_df)
        risk_scores = self.risk_scorer.score(features)
        insights = self.insight_generator.generate(features, risk_scores)
        serializable_features = self._make_serializable(features)
        return {
            "transactions": categorized_df.to_dict(orient="records"),
            "transaction_count": len(categorized_df),
            "features": serializable_features,
            "risk_scores": risk_scores,
            "insights": insights,
        }

    def _make_serializable(self, features: Dict) -> Dict:
        """Convert pandas Series and other non-serializable types."""
        import datetime

        result = {}
        for key, value in features.items():
            if isinstance(value, pd.Series):
                # Convert keys to strings (handles datetime.date keys)
                result[key] = {str(k): v for k, v in value.to_dict().items()}
            elif isinstance(value, (dict, list, str, int, float, bool)):
                result[key] = value
            else:
                result[key] = str(value)
        return result
