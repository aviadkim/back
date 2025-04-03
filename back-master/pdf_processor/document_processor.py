from typing import Dict, List, Any, Optional, Union
import logging
from pathlib import Path
import os

class DocumentProcessor:
    """Unified API for processing financial documents."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the document processor with configuration.

        Args:
            config: Configuration dictionary with processing options
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self._init_extractors()

    def _init_extractors(self):
        """Initialize text and table extractors based on configuration."""
        from pdf_processor.extraction.text_extractor import PDFTextExtractor
        from pdf_processor.tables.table_extractor import TableExtractor
        from pdf_processor.analysis.financial_analyzer import FinancialAnalyzer

        language = self.config.get('language', 'auto')
        if language == 'auto':
            # Default to English if auto-detection
            language = 'eng'
        elif language == 'he':
            language = 'heb'  # Tesseract uses 'heb' for Hebrew

        self.text_extractor = PDFTextExtractor(language=language)
        self.table_extractor = TableExtractor()
        self.financial_analyzer = FinancialAnalyzer()

    def process_document(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Process a document and extract financial information.

        Args:
            file_path: Path to the document file

        Returns:
            Dictionary containing extracted document information
        """
        try:
            self.logger.info(f"Processing document: {file_path}")
            file_path_str = str(file_path)

            # Extract text content
            document_text = self.text_extractor.extract_document(file_path_str)

            # Check if there was an error in text extraction
            if "error" in document_text:
                return document_text

            # Extract tables
            tables_data = self.table_extractor.extract_tables(file_path_str)

            # Convert tables to dataframes for analysis
            dataframes = {}
            for page_num, tables in tables_data.items():
                dataframes[page_num] = []
                for table in tables:
                    # Check if table extraction returned an error for this page
                    if isinstance(table, dict) and "error" in table:
                         self.logger.warning(f"Skipping analysis for table on page {page_num} due to extraction error: {table['error']}")
                         continue # Skip this table/page

                    df = self.table_extractor.convert_to_dataframe(table)
                    if not df.empty:
                        dataframes[page_num].append({
                            'dataframe': df,
                            'metadata': table
                        })

            # Analyze financial content
            financial_data = self._analyze_financial_content(document_text, dataframes)

            # Compile results
            results = {
                'document_text': document_text,
                'tables': tables_data,
                'financial_data': financial_data,
                'metadata': {
                    'filename': Path(file_path).name,
                    'page_count': len(document_text) if isinstance(document_text, dict) else 0,
                    'language': self._detect_language(document_text),
                    'processing_status': 'completed'
                }
            }

            self.logger.info(f"Document processing completed: {file_path}")
            return results

        except Exception as e:
            self.logger.error(f"Error processing document {file_path}: {str(e)}")
            return {
                'error': str(e),
                'metadata': {
                    'filename': Path(file_path).name,
                    'processing_status': 'failed'
                }
            }

    def _analyze_financial_content(self, document_text, dataframes):
        """Analyze document text and tables for financial information."""
        result = {
            'entities': [],
            'metrics': {},
            'tables_analysis': {}
        }

        # Check if document_text contains error
        if not isinstance(document_text, dict) or "error" in document_text:
            return result

        # Analyze text for financial entities and metrics
        for page_num, page_data in document_text.items():
            if not isinstance(page_data, dict) or "error" in page_data: # Check for page-level errors
                continue

            page_text = page_data.get('text', '')
            if page_text:
                # Extract metrics from text
                metrics = self.financial_analyzer.extract_financial_metrics(page_text)
                if metrics:
                    result['metrics'][page_num] = metrics

                # Check if text contains financial information
                if self.text_extractor.is_potentially_financial(page_text):
                    # Additional financial text analysis could go here
                    pass

        # Analyze tables
        for page_num, tables in dataframes.items():
            result['tables_analysis'][page_num] = []

            for table_data in tables:
                df = table_data['dataframe']
                table_type = self.financial_analyzer.classify_table(df)

                analysis = self.financial_analyzer.analyze_financial_table(
                    df, table_type
                )

                result['tables_analysis'][page_num].append({
                    'table_id': table_data['metadata'].get('id', 0),
                    'analysis': analysis
                })

        return result

    def _detect_language(self, document_text):
        """Detect the primary language of the document."""
        # Simple language detection based on page content
        # Could be enhanced with proper language detection library

        # Check if document_text contains error
        if not isinstance(document_text, dict) or "error" in document_text:
            return "unknown"

        hebrew_chars = set('אבגדהוזחטיכלמנסעפצקרשת')
        english_chars = set('abcdefghijklmnopqrstuvwxyz')

        hebrew_count = 0
        english_count = 0

        for page_num, page_data in document_text.items():
            if not isinstance(page_data, dict) or "error" in page_data: # Check for page-level errors
                continue

            text = page_data.get('text', '').lower()

            for char in text:
                if char in hebrew_chars:
                    hebrew_count += 1
                elif char in english_chars:
                    english_count += 1

        if hebrew_count > english_count:
            return 'he'
        else:
            return 'en'