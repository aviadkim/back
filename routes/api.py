from flask import Blueprint, jsonify

# Create blueprint for general API routes
api_blueprint = Blueprint('api', __name__)

# Example route (can be removed or expanded later)
@api_blueprint.route('/status')
def api_status():
    """General API status endpoint."""
    return jsonify({'status': 'ok', 'message': 'API is running'})

# Add other general API routes here (e.g., auth, users)