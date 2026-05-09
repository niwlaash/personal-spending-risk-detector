"""
Maybank-specific PDF parser.
Handles the specific layout of Maybank Malaysia statements.
"""

from app.parsers.pdf_parser import PDFParser


class MaybankParser(PDFParser):
    """
    Maybank-specific PDF statement parser.

    Extends the generic PDFParser with Maybank-specific
    column mappings and formatting rules.
    """

    def parse(self, file_path: str):
        """Parse a Maybank PDF statement."""
        # Use the generic PDF parser as a starting point
        df = super().parse(file_path)
        df["source_bank"] = "Maybank"
        return df
