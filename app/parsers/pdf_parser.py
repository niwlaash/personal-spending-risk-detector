"""
PDF parser for bank statement PDFs.
Uses pdfplumber to extract tabular data from PDF statements.
"""

import re
from typing import List, Optional

import pandas as pd
import pdfplumber

from app.parsers.base_parser import BaseParser


class PDFParser(BaseParser):
    """
    Parser for PDF bank statements using pdfplumber.

    This is a generic PDF parser that attempts to extract tabular data.
    For best results, bank-specific subclasses should be created.
    """

    def parse(self, file_path: str) -> pd.DataFrame:
        """
        Parse a PDF bank statement.

        Extracts tables from all pages and combines them into
        a standardized DataFrame.

        Args:
            file_path: Path to the PDF file.

        Returns:
            Standardized DataFrame with columns: date, description, amount, balance.
        """
        all_rows: List[List[str]] = []

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if row and any(cell for cell in row if cell):
                            # Clean each cell
                            cleaned = [cell.strip() if cell else "" for cell in row]
                            all_rows.append(cleaned)

        if not all_rows:
            raise ValueError("No tabular data found in PDF.")

        # Try to identify header row and create DataFrame
        df = self._build_dataframe(all_rows)

        # Validate
        self.validate(df)

        # Parse dates
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

        # Clean amount
        df["amount"] = pd.to_numeric(
            df["amount"].astype(str).str.replace(",", "").str.strip(),
            errors="coerce",
        )

        # Clean balance
        if "balance" in df.columns:
            df["balance"] = pd.to_numeric(
                df["balance"].astype(str).str.replace(",", "").str.strip(),
                errors="coerce",
            )
        else:
            df["balance"] = None

        # Clean description
        df["description"] = df["description"].astype(str).str.strip().str.upper()

        # Drop rows with missing essentials
        df = df.dropna(subset=["date", "description", "amount"])
        df = df.reset_index(drop=True)

        return df[["date", "description", "amount", "balance"]]

    def _build_dataframe(self, rows: List[List[str]]) -> pd.DataFrame:
        """
        Attempt to build a DataFrame from raw extracted rows.
        Tries to identify column headers automatically.
        """
        # Look for a header row containing date-like keywords
        header_idx = None
        for i, row in enumerate(rows):
            row_lower = [str(cell).lower() for cell in row]
            if any(
                keyword in " ".join(row_lower)
                for keyword in ["date", "tarikh", "transaction"]
            ):
                header_idx = i
                break

        if header_idx is not None:
            headers = [str(h).strip().lower() for h in rows[header_idx]]
            data = rows[header_idx + 1 :]
        else:
            # Assume first row is header
            headers = [str(h).strip().lower() for h in rows[0]]
            data = rows[1:]

        # Ensure consistent column count
        max_cols = len(headers)
        normalized_data = []
        for row in data:
            if len(row) < max_cols:
                row.extend([""] * (max_cols - len(row)))
            elif len(row) > max_cols:
                row = row[:max_cols]
            normalized_data.append(row)

        df = pd.DataFrame(normalized_data, columns=headers)

        # Map common column names
        column_map = {
            "tarikh": "date",
            "transaction date": "date",
            "keterangan": "description",
            "details": "description",
            "particulars": "description",
            "jumlah": "amount",
            "debit": "amount",
            "baki": "balance",
            "running balance": "balance",
        }

        rename = {}
        for col in df.columns:
            if col in column_map:
                rename[col] = column_map[col]
        df = df.rename(columns=rename)

        return df
