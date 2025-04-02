"""Tests for PDF processor"""
import os
import pytest
import sys

# Fix imports to properly import the processor
sys.path.insert(0, os.path.abspath('../../../'))
from project_organized.features.pdf_processing.processor import EnhancedPDFProcessor

def test_processor_initialization():
    """Test that the PDF processor can be initialized correctly"""
    processor = EnhancedPDFProcessor()
    assert processor is not None
    assert processor.extraction_dir == 'extractions'
    assert processor.language == 'heb+eng'

def test_extraction_directory_creation():
    """Test that the extraction directory is created"""
    processor = EnhancedPDFProcessor(extraction_dir='test_extractions')
    assert os.path.exists('test_extractions')
    # Clean up
    if os.path.exists('test_extractions'):
        os.rmdir('test_extractions')
