from flask import Blueprint

# Create Blueprint for chatbot feature
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/api/chat')

# Import routes after creating Blueprint to avoid circular imports
from . import routes
