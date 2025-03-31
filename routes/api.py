from flask import Blueprint, jsonify
import logging

# Create API blueprint
api_blueprint = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

@api_blueprint.route('/', methods=['GET'])
def api_root():
    """API root endpoint."""
    # Consider reading version from a central place, e.g., config or VERSION file
    version = "6.1.0" # Placeholder, update dynamically if possible
    return jsonify({
        "status": "success",
        "message": "Financial Document Analyzer API",
        "version": version
    })

# Add other general, non-document-specific API routes here if needed
# e.g., authentication routes (/auth/login, /auth/register), user profile routes etc.