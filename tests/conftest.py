import pytest
import os
import sys
import tempfile

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from config import Config

@pytest.fixture(autouse=True)
def app_context():
    """Create application context for tests."""
    with app.app_context():
        yield

@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        'TESTING': True,
        'MONGODB_URI': 'mongodb://localhost:27017/test_db',
        'UPLOAD_FOLDER': tempfile.mkdtemp()
    }

@pytest.fixture
def test_client(test_config):
    """Test client."""
    app.config.update(test_config)
    with app.test_client() as client:
        yield client
