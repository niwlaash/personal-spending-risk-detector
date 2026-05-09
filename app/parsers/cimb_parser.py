"""
CIMB-specific PDF parser.
Handles the specific layout of CIMB Malaysia statements.
"""

from app.parsers.pdf_parser import PDFParser


class CIMBParser(PDFParser):
    """
    CIMB-specific PDF statement parser.

    Extends the generic PDFParser with CIMB-specific
    column mappings and formatting rules.
    """

    def parse(self, file_path: str):
        """Parse a CIMB PDF statement."""
        df = super().parse(file_path)
        df["source_bank"] = "CIMB"
        return df
