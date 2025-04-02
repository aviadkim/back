"""
Adapter for enhanced_pdf_processor.py
This redirects to the new vertical slice architecture.

Original file: /workspaces/back/enhanced_pdf_processor.py
New location: /workspaces/back/project_organized/features/pdf_processing/processor.py
"""
import logging
from project_organized.features.pdf_processing.processor import *

logging.warning("Using enhanced_pdf_processor.py from deprecated location. Please update imports to use 'from project_organized.features.pdf_processing.processor import ...'")
