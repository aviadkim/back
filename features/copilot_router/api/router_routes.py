from flask import Blueprint, request, jsonify

# Import the service for this feature
try:
    from features.copilot_router.services.router_service import get_router_service
except ImportError:
    print("Error: Failed to import get_router_service from copilot_router service.")
    # Define a dummy function if import fails

    def get_router_service():
        return None

# Define the blueprint. The URL prefix might be adjusted later in app.py if needed,
# but defining it here makes sense for modularity.
router_routes = Blueprint('copilot_router', __name__, url_prefix='/api/copilot')


@router_routes.route('/route', methods=['POST'])
def route_copilot_request_route():
    """
    Main API endpoint for CopilotKit frontend requests.
    It routes the request to the appropriate specialized assistant service.
    Expects 'message' and 'context' in the JSON payload.
    """
    router_service = get_router_service()
    if not router_service:
        return jsonify({"error": "Router service not available"}), 500

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415  # Unsupported Media Type

    data = request.get_json()
    message = data.get('message')
    context = data.get('context', {})  # Default to empty dict if not provided

    if message is None:
        # Message is generally expected from CopilotKit
        return jsonify({"error": "Missing 'message' in request body"}), 400

    try:
        # Call the router service to handle the request and get a response
        # The route_request method should return a Flask Response object (e.g., from jsonify)
        response = router_service.route_request(message, context)
        return response
    except Exception as e:
        print(f"Error routing copilot request: {e}")
        # Provide a generic error response
        return jsonify({"error": "An internal error occurred while routing the request"}), 500

# Renamed function to avoid potential name collisions