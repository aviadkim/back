"""
Adapter for simple_qa.py
This redirects to the new vertical slice architecture.

Original file: /workspaces/back/simple_qa.py
New location: /workspaces/back/project_organized/features/document_qa/simple_qa
"""
import logging
from project_organized.features.document_qa.simple_qa import *

logging.warning("Using simple_qa.py from deprecated location. Please update imports to use 'from project_organized.features.document_qa.simple_qa import ...'")
