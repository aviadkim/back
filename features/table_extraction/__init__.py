"""
Table Extraction Feature Module
"""

from flask import Blueprint

# Create a Blueprint for this feature
table_extraction_bp = Blueprint('table_extraction', __name__)

# Import routes to register them with the blueprint
from . import routes
