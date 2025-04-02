"""
Adapter for financial_data_extractor.py
This redirects to the new vertical slice architecture.

Original file: /workspaces/back/financial_data_extractor.py
New location: /workspaces/back/project_organized/features/financial_analysis/extractors.financial_data_extractor
"""
import logging
from project_organized.features.financial_analysis.extractors.financial_data_extractor import *

logging.warning("Using financial_data_extractor.py from deprecated location. Please update imports to use 'from project_organized.features.financial_analysis.extractors.financial_data_extractor import ...'")
