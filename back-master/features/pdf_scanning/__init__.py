"""
PDF Scanning Feature Module
"""

from flask import Blueprint

# Create a Blueprint for this feature
pdf_scanning_bp = Blueprint('pdf_scanning', __name__)

# Import routes to register them with the blueprint
from . import routes
