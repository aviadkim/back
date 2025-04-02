"""Tests for the PDF processor"""
import os
import sys
import unittest
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from project_organized.features.pdf_processing.processor import EnhancedPDFProcessor

class TestProcessor(unittest.TestCase):
    """Test cases for the PDF processor"""
    
    def test_initialization(self):
        """Test processor initialization"""
        processor = EnhancedPDFProcessor()
        self.assertIsNotNone(processor)
        self.assertEqual(processor.language, 'heb+eng')
        self.assertEqual(processor.dpi, 300)
        self.assertEqual(processor.thread_count, 4)
        self.assertEqual(processor.extraction_dir, 'extractions')
        
    def test_extraction_dir_creation(self):
        """Test that extraction directory is created"""
        extraction_dir = 'test_extractions'
        processor = EnhancedPDFProcessor(extraction_dir=extraction_dir)
        self.assertTrue(os.path.exists(extraction_dir))
        # Clean up
        if os.path.exists(extraction_dir):
            try:
                os.rmdir(extraction_dir)
            except OSError:
                pass  # Directory might not be empty

if __name__ == '__main__':
    unittest.main()
