#!/bin/bash
echo "Creating adapters for original files..."

# Create adapter for PDF processor
if [ -f "enhanced_pdf_processor.py" ]; then
  cat > enhanced_pdf_processor.py.adapter << 'EOL'
"""
Adapter for enhanced_pdf_processor.py
This redirects to the new vertical slice architecture.
"""
import logging
from project_organized.features.pdf_processing.processor import EnhancedPDFProcessor

logging.warning("Using enhanced_pdf_processor.py from deprecated location. Please update imports to use 'from features.pdf_processing import EnhancedPDFProcessor'")
EOL

  echo "Created adapter for enhanced_pdf_processor.py"
  echo "To apply: mv enhanced_pdf_processor.py.adapter enhanced_pdf_processor.py.new"
fi

# Create financial extractor adapter
if [ -f "financial_data_extractor.py" ]; then
  cat > financial_data_extractor.py.adapter << 'EOL'
"""
Adapter for financial_data_extractor.py
This redirects to the new vertical slice architecture.
"""
import logging
from project_organized.features.financial_analysis.extractors import FinancialDataExtractor

logging.warning("Using financial_data_extractor.py from deprecated location. Please update imports.")
EOL

  echo "Created adapter for financial_data_extractor.py"
fi

echo "Adapters created. Apply them when ready to redirect imports to the new architecture."
