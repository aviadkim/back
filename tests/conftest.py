import os
import sys
import pytest
from flask import Flask

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def app():
    """Create a Flask app for testing"""
    from app import app as flask_app
    flask_app.config.update({
        "TESTING": True,
    })
    yield flask_app

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()
