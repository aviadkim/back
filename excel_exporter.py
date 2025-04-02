"""
Adapter for excel_exporter.py
This redirects to the new vertical slice architecture.

Original file: /workspaces/back/excel_exporter.py
New location: /workspaces/back/project_organized/features/document_export/excel_exporter
"""
import logging
from project_organized.features.document_export.excel_exporter import *

logging.warning("Using excel_exporter.py from deprecated location. Please update imports to use 'from project_organized.features.document_export.excel_exporter import ...'")
