"""
Adapter for enhanced_financial_extractor.py
This redirects to the new vertical slice architecture.

Original file: /workspaces/back/enhanced_financial_extractor.py
New location: /workspaces/back/project_organized/features/financial_analysis/extractors.enhanced_financial_extractor
"""
import logging
from project_organized.features.financial_analysis.extractors.enhanced_financial_extractor import *

logging.warning("Using enhanced_financial_extractor.py from deprecated location. Please update imports to use 'from project_organized.features.financial_analysis.extractors.enhanced_financial_extractor import ...'")
