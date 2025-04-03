"""
Adapter for financial_document_qa.py
This redirects to the new vertical slice architecture.

Original file: /workspaces/back/financial_document_qa.py
New location: /workspaces/back/project_organized/features/document_qa/financial_document_qa
"""
import logging
from project_organized.features.document_qa.financial_document_qa import *

logging.warning("Using financial_document_qa.py from deprecated location. Please update imports to use 'from project_organized.features.document_qa.financial_document_qa import ...'")
