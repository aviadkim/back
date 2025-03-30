"""
Utilities package
"""

# Import common utilities
try:
    from .pdf_processor import PDFProcessor
except ImportError as e:
    import logging
    logging.warning(f"Could not import PDFProcessor: {e}")
