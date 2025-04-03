# Create a conftest.py file in the root of project_organized to help with imports
import os
import sys
import pytest

# Add the parent directory to the path so tests can import modules
sys.path.insert(0, os.path.abspath('..'))

@pytest.fixture
def test_pdf_path():
    """Fixture providing a path to a test PDF"""
    test_dir = os.path.join('..', 'uploads')
    return os.path.join(test_dir, 'doc_de0c7654_2._Messos_28.02.2025.pdf')
