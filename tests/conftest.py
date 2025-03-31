import pytest
import os
import sys
import tempfile

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app # Import the factory function
# from config import Config # Config is now handled within app.py and configuration.py
# Remove the old app_context fixture, context is handled by test_client
# @pytest.fixture(autouse=True)
# def app_context():
#     """Create application context for tests."""
#     with app.app_context():
#         yield

@pytest.fixture(scope='module')
def app():
    """Create and configure a new app instance for each test module."""
    # Create app with test config
    # Note: You might want to load a specific test .env file here if needed
    # For now, rely on default config values or environment variables
    app = create_app()
    app.config.update({
        "TESTING": True,
        # Add other test-specific config overrides if necessary
        # e.g., 'MONGO_URI': 'mongodb://localhost:27017/test_db'
        # Ensure UPLOAD_FOLDER exists for tests if needed, or mock file operations
        'UPLOAD_FOLDER': tempfile.mkdtemp()
    })

    # TODO: Set up any test database connections or initial data here

    yield app

    # TODO: Clean up test database or other resources here
    # Example: Clean up temp upload folder
    import shutil
    shutil.rmtree(app.config['UPLOAD_FOLDER'])


@pytest.fixture(scope='module')
def test_client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope='module')
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()
