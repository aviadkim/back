from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging # Added logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
logger.info("Loading environment variables from .env...")
load_dotenv()
logger.info("Environment variables loaded.")

# Create Flask app
app = Flask(__name__)
CORS(app) # Enable CORS for all routes

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    logger.info("Health check endpoint called.")
    return jsonify({
        "status": "ok",
        "message": "System is operational"
    })

@app.route('/api/openrouter/test')
def test_openrouter():
    """Test OpenRouter integration."""
    logger.info("OpenRouter test endpoint called.")
    try:
        import requests
        import json
        # No need to import os again, already imported
        # No need to import dotenv again, already loaded

        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            logger.error("OPENROUTER_API_KEY not found in environment")
            return jsonify({"error": "OPENROUTER_API_KEY not found in environment"}), 500

        # Use primary model for the test, fallback to a default if not set
        model_to_test = os.getenv('OPENROUTER_PRIMARY_MODEL', 'mistralai/mistral-small-3.1-24b-instruct:free')
        site_url = os.getenv('SITE_URL', 'http://localhost:5000')
        site_name = os.getenv('SITE_NAME', 'Financial Document Processor')

        logger.info(f"Testing OpenRouter with model: {model_to_test}")

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": site_url,
            "X-Title": site_name
        }
        data = {
            "model": model_to_test,
            "messages": [
                {"role": "user", "content": "What is the capital of France?"}
            ]
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)
        logger.info(f"OpenRouter API response status: {response.status_code}")

        # Try to parse JSON, handle potential errors
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            logger.error(f"Failed to decode OpenRouter JSON response. Status: {response.status_code}, Body: {response.text}")
            return jsonify({
                "error": "Failed to decode response from OpenRouter",
                "status_code": response.status_code,
                "response_text": response.text
            }), 502 # Bad Gateway might be appropriate

        return jsonify({
            "status": response.status_code,
            "response": response_data
        })
    except requests.exceptions.RequestException as e:
         logger.error(f"Error during OpenRouter API request: {str(e)}")
         return jsonify({"error": f"API Request Error: {str(e)}"}), 500
    except Exception as e:
        logger.exception("An unexpected error occurred in /api/openrouter/test") # Log full traceback
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    logger.info(f"Starting simplified server on port {port}, debug mode: {debug_mode}")
    # Use debug=False for production environments if FLASK_ENV is not 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)