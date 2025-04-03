import pytest
from app import create_app
from config import Config
import database

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['MONGODB_URI'] = Config.MONGODB_URI + '_test'
    
    with app.app_context():
        database.connect_db()
        yield app
        database.close_db_connection()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()
