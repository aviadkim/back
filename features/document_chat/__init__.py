"""
Document Chat Feature Module
"""

from flask import Blueprint

# Create a Blueprint for this feature
document_chat_bp = Blueprint('document_chat', __name__)

# Import routes to register them with the blueprint
from . import routes
