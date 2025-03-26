from flask import Blueprint

# Create Blueprint for PDF scanning feature
pdf_scanning_bp = Blueprint('pdf_scanning', __name__, url_prefix='/api/pdf')

# Import routes after creating Blueprint to avoid circular imports
from . import routes
