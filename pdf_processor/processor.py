import os
import logging
import tempfile
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import time

from .extraction.text_extractor import PDFTextExtractor
from .tables.enhanced_table_extractor import EnhancedTableExtractor
from .analysis.financial_analyzer import FinancialAnalyzer
from .analysis.isin_detector import ISINDetector

logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    Main processor for PDF documents, integrating all extraction and analysis components.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the PDF processor with configuration.

        Args:
            config: Configuration dictionary with settings for the processor
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Set up extractors and analyzers
        language = self.config.get('default_language', 'eng')
        additional_languages = self.config.get('additional_languages', ['heb'])

        if isinstance(additional_languages, str):
            additional_languages = additional_languages.split(',')

        # Create the language string for OCR
        self.language = language
        if additional_languages:
            self.language = '+'.join([language] + additional_languages)

        # Initialize extractors and analyzers
        self.text_extractor = PDFTextExtractor(language=self.language)
        self.table_extractor = EnhancedTableExtractor(language=self.language)
        self.financial_analyzer = FinancialAnalyzer()

        # Load ISIN database if available
        isin_db_path = self.config.get('isin_db_path')
        if isin_db_path and not os.path.exists(isin_db_path):
            # Create empty database if it doesn't exist
            try:
                os.makedirs(os.path.dirname(isin_db_path), exist_ok=True)
                with open(isin_db_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
            except Exception as e:
                self.logger.warning(f"Failed to create ISIN database file: {str(e)}")
                isin_db_path = None

        self.isin_detector = ISINDetector(isin_db_path=isin_db_path)

    def process_document(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process a PDF document to extract and analyze its content.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary with extracted document data and analysis
        """
        start_time = time.time()
        self.logger.info(f"Starting processing of document: {pdf_path}")

        result = {
            "filename": os.path.basename(pdf_path),
            "processing_time": None,
            "pages": [],
            "tables": [],
            "financialData": {
                "isinNumbers": [],
                "financialMetrics": {}
            },
            "metadata": {}
        }

        try:
            # Step 1: Extract text content
            document_text = self.text_extractor.extract_document(pdf_path)

            # Step 2: Extract tables
            table_data = self.table_extractor.extract_tables_from_pdf(pdf_path)

            # Process each page
            for page_num, page_data in document_text.items():
                # Add page text to result
                result["pages"].append({
                    "pageNumber": page_num,
                    "text": page_data.get("text", ""),
                    "dimensions": page_data.get("dimensions", {})
                })

                # Process text for ISIN numbers
                isin_results = self.isin_detector.detect_isin_numbers(page_data.get("text", ""))
                for isin in isin_results:
                    if not any(existing["code"] == isin["code"] for existing in result["financialData"]["isinNumbers"]):
                        result["financialData"]["isinNumbers"].append({
                            "code": isin["code"],
                            "description": isin["description"],
                            "pageNumber": page_num
                        })

                # Extract financial metrics from text
                financial_metrics = self.financial_analyzer.extract_financial_metrics(page_data.get("text", ""))
                if financial_metrics:
                    # Aggregate metrics
                    for metric_type, values in financial_metrics.items():
                        if metric_type not in result["financialData"]["financialMetrics"]:
                            result["financialData"]["financialMetrics"][metric_type] = []
                        result["financialData"]["financialMetrics"][metric_type].extend(values)

            # Process tables
            for page_num, tables in table_data.items():
                for table in tables:
                    # Convert to DataFrame for analysis
                    df = self.table_extractor.convert_to_dataframe(table)

                    # Classify the table
                    table_type = self.financial_analyzer.classify_table(df)

                    # Analyze table based on its type
                    table_analysis = self.financial_analyzer.analyze_financial_table(df, table_type)

                    # Look for ISIN numbers in the table
                    isin_results = self.isin_detector.detect_isin_in_table(df)

                    # Add to ISIN list
                    for isin in isin_results:
                        if not any(existing["code"] == isin["code"] for existing in result["financialData"]["isinNumbers"]):
                            result["financialData"]["isinNumbers"].append({
                                "code": isin["code"],
                                "description": isin["description"],
                                "pageNumber": page_num
                            })

                    # Format the table for the result
                    formatted_table = {
                        "pageNumber": page_num,
                        "tableIndex": table["id"],
                        "header": table["header"],
                        "rows": table["rows"],
                        "tableType": table_type,
                        "analysis": table_analysis
                    }

                    result["tables"].append(formatted_table)

            # Add processing time
            result["processing_time"] = time.time() - start_time

            self.logger.info(f"Completed processing of document: {pdf_path} in {result['processing_time']:.2f} seconds")
            return result

        except Exception as e:
            self.logger.error(f"Error processing document {pdf_path}: {str(e)}")

            # Return partial results with error information
            result["error"] = str(e)
            result["processing_time"] = time.time() - start_time
            return result

    def process_file(self, file_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a file and optionally save the results.

        Args:
            file_path: Path to the PDF file
            output_path: Optional path to save the results JSON

        Returns:
            Dictionary with processing results
        """
        results = self.process_document(file_path)

        if output_path:
            try:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                self.logger.info(f"Saved processing results to {output_path}")
            except Exception as e:
                self.logger.error(f"Error saving results to {output_path}: {str(e)}")

        return results
