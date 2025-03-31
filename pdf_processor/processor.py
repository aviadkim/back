import os
import logging
import tempfile
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import time

# Assuming extractors and analyzers are in sibling directories
# Adjust imports based on your actual project structure
try:
    from .extraction.text_extractor import PDFTextExtractor
    from .tables.enhanced_table_extractor import EnhancedTableExtractor
    from .analysis.financial_analyzer import FinancialAnalyzer # Assuming this exists
    from .analysis.isin_detector import ISINDetector
except ImportError:
    # Fallback for different structure or testing
    logger.warning("Relative imports failed. Trying absolute imports assuming pdf_processor is in PYTHONPATH.")
    from pdf_processor.extraction.text_extractor import PDFTextExtractor
    from pdf_processor.tables.enhanced_table_extractor import EnhancedTableExtractor
    # Create a dummy FinancialAnalyzer if it doesn't exist for now
    try:
        from pdf_processor.analysis.financial_analyzer import FinancialAnalyzer
    except ImportError:
        logger.warning("FinancialAnalyzer not found. Creating a dummy class.")
        class FinancialAnalyzer:
            def extract_financial_metrics(self, text: str) -> Dict: return {}
            def classify_table(self, df) -> str: return "Unknown"
            def analyze_financial_table(self, df, table_type: str) -> Dict: return {}
    from pdf_processor.analysis.isin_detector import ISINDetector


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
            # Handle comma-separated string
            additional_languages = [lang.strip() for lang in additional_languages.split(',') if lang.strip()]
        elif not isinstance(additional_languages, list):
             additional_languages = []


        # Create the language string for OCR (e.g., "eng+heb")
        self.language = language
        if additional_languages:
            # Ensure 'language' is included and languages are unique
            lang_set = set([language] + additional_languages)
            self.language = '+'.join(sorted(list(lang_set))) # Sort for consistency

        self.logger.info(f"Initializing PDFProcessor with language: {self.language}")

        # Initialize extractors and analyzers
        self.text_extractor = PDFTextExtractor(language=self.language)
        self.table_extractor = EnhancedTableExtractor(language=self.language)
        self.financial_analyzer = FinancialAnalyzer() # Use dummy if real one not found

        # Load ISIN database if available
        isin_db_path = self.config.get('isin_db_path')
        self.isin_detector = ISINDetector(isin_db_path=isin_db_path) # ISINDetector handles path check

        # Add a check for the convert_to_dataframe method in table_extractor
        if not hasattr(self.table_extractor, 'convert_to_dataframe'):
             self.logger.warning("EnhancedTableExtractor does not have 'convert_to_dataframe' method. Creating a dummy.")
             # Add a dummy method if it's missing
             import pandas as pd
             def dummy_convert(table_dict):
                 try:
                     return pd.DataFrame(table_dict.get('rows', []), columns=table_dict.get('header'))
                 except Exception as e:
                     self.logger.error(f"Error in dummy convert_to_dataframe: {e}")
                     return pd.DataFrame() # Return empty DataFrame on error
             self.table_extractor.convert_to_dataframe = dummy_convert


    def process_document(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process a PDF document to extract and analyze its content.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary with extracted document data and analysis
        """
        start_time = time.time()
        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.is_file():
             self.logger.error(f"PDF file not found or is not a file: {pdf_path}")
             return {"error": "File not found", "filename": os.path.basename(pdf_path)}

        self.logger.info(f"Starting processing of document: {pdf_path}")

        result = {
            "filename": pdf_path_obj.name,
            "processing_time": None,
            "pages": [],
            "tables": [],
            "financialData": {
                "isinNumbers": [],
                "financialMetrics": {}
            },
            "metadata": {}, # Placeholder for future metadata extraction
            "error": None # Initialize error as None
        }

        try:
            # Step 1: Extract text content (returns dict {page_num: {text: ..., dimensions: ...}})
            self.logger.info("Step 1: Extracting text...")
            document_text = self.text_extractor.extract_document(pdf_path)
            if not document_text:
                 self.logger.warning("Text extraction returned no data.")


            # Step 2: Extract tables (returns dict {page_num: [table1, table2, ...]})
            self.logger.info("Step 2: Extracting tables...")
            table_data = self.table_extractor.extract_tables_from_pdf(pdf_path)
            if not table_data:
                 self.logger.warning("Table extraction returned no data.")


            # Process each page found during text extraction
            self.logger.info("Step 3: Analyzing text and metrics per page...")
            all_page_numbers = sorted(list(document_text.keys()))
            for page_num_0based in all_page_numbers:
                page_data = document_text[page_num_0based]
                page_text = page_data.get("text", "")
                page_num_1based = page_num_0based + 1 # Convert to 1-based for reporting

                # Add page text to result
                result["pages"].append({
                    "pageNumber": page_num_1based, # Report 1-based page number
                    "textLength": len(page_text),
                    "dimensions": page_data.get("dimensions", {})
                    # Avoid storing full text in main result for large docs? Configurable?
                    # "text": page_text,
                })

                # Process text for ISIN numbers
                isin_results = self.isin_detector.detect_isin_numbers(page_text)
                for isin in isin_results:
                    # Avoid duplicates
                    if not any(existing["code"] == isin["code"] for existing in result["financialData"]["isinNumbers"]):
                        result["financialData"]["isinNumbers"].append({
                            "code": isin["code"],
                            "description": isin.get("description", ""), # Use .get for safety
                            "confidence": isin.get("confidence", "unknown"),
                            "context": isin.get("context", ""),
                            "pageNumber": page_num_1based # Report 1-based page number
                        })

                # Extract financial metrics from text
                financial_metrics = self.financial_analyzer.extract_financial_metrics(page_text)
                if financial_metrics:
                    # Aggregate metrics
                    for metric_type, values in financial_metrics.items():
                        if metric_type not in result["financialData"]["financialMetrics"]:
                            result["financialData"]["financialMetrics"][metric_type] = []
                        # Ensure values are appended correctly
                        if isinstance(values, list):
                            result["financialData"]["financialMetrics"][metric_type].extend(values)
                        else:
                            result["financialData"]["financialMetrics"][metric_type].append(values)


            # Process tables found during table extraction
            self.logger.info("Step 4: Analyzing extracted tables...")
            all_table_pages = sorted(list(table_data.keys()))
            for page_num_0based in all_table_pages:
                tables_on_page = table_data[page_num_0based]
                page_num_1based = page_num_0based + 1 # Convert to 1-based for reporting

                for table_index, table in enumerate(tables_on_page):
                    try:
                        # Convert to DataFrame for analysis
                        # Check if convert_to_dataframe exists and handle potential errors
                        if hasattr(self.table_extractor, 'convert_to_dataframe'):
                            df = self.table_extractor.convert_to_dataframe(table)
                        else:
                            # Should have been handled in __init__, but double-check
                            self.logger.error("convert_to_dataframe method missing from table_extractor.")
                            df = pd.DataFrame() # Empty DataFrame

                        if df.empty and (table.get('rows') or table.get('header')):
                             self.logger.warning(f"DataFrame conversion resulted in empty DF for table {table.get('id', table_index)} on page {page_num_1based}, but raw data exists.")


                        # Classify the table
                        table_type = self.financial_analyzer.classify_table(df)

                        # Analyze table based on its type
                        table_analysis = self.financial_analyzer.analyze_financial_table(df, table_type)

                        # Look for ISIN numbers in the table
                        isin_results_table = self.isin_detector.detect_isin_in_table(df)

                        # Add to ISIN list (avoid duplicates)
                        for isin in isin_results_table:
                            if not any(existing["code"] == isin["code"] for existing in result["financialData"]["isinNumbers"]):
                                result["financialData"]["isinNumbers"].append({
                                    "code": isin["code"],
                                    "description": isin.get("description", ""),
                                    "confidence": isin.get("confidence", "unknown"),
                                    # Add table context if available
                                    "source": "table",
                                    "pageNumber": page_num_1based # Report 1-based page number
                                })

                        # Format the table for the result
                        formatted_table = {
                            "pageNumber": page_num_1based, # Report 1-based page number
                            "tableId": table.get("id", f"page{page_num_1based}-table{table_index}"),
                            "rowCount": table.get("row_count", len(table.get("rows",[]))),
                            "colCount": table.get("col_count", len(table.get("header",[]))),
                            "header": table.get("header", []),
                            "rows": table.get("rows", []), # Include raw rows
                            "tableType": table_type,
                            "analysis": table_analysis,
                            "extractionMethod": table.get("extraction_method", "unknown")
                        }

                        result["tables"].append(formatted_table)
                    except Exception as table_err:
                         self.logger.error(f"Error processing table {table_index} on page {page_num_1based}: {str(table_err)}", exc_info=True)
                         # Add info about the failed table?
                         result["tables"].append({
                             "pageNumber": page_num_1based,
                             "tableId": table.get("id", f"page{page_num_1based}-table{table_index}"),
                             "error": f"Failed to process table: {str(table_err)}"
                         })


            # Finalize processing time
            end_time = time.time()
            result["processing_time"] = round(end_time - start_time, 2)

            self.logger.info(f"Completed processing of document: {pdf_path} in {result['processing_time']:.2f} seconds")
            return result

        except Exception as e:
            self.logger.error(f"Fatal error processing document {pdf_path}: {str(e)}", exc_info=True)

            # Return partial results with error information
            result["error"] = f"Fatal processing error: {str(e)}"
            if result["processing_time"] is None: # Ensure processing time is set even on error
                 result["processing_time"] = round(time.time() - start_time, 2)
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
                output_dir = os.path.dirname(output_path)
                if output_dir: # Ensure directory exists only if path includes one
                     os.makedirs(output_dir, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    # Use default=str for non-serializable types like numpy int64
                    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
                self.logger.info(f"Saved processing results to {output_path}")
            except Exception as e:
                self.logger.error(f"Error saving results to {output_path}: {str(e)}")
                # Optionally add save error to results?
                results["save_error"] = f"Failed to save results: {str(e)}"


        return results

# Example Usage (Optional)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Starting PDFProcessor example")

    # Create dummy dependencies if they don't exist
    dummy_pdf_path = "test_dummy.pdf" # Assumes dummy PDF exists from table extractor example
    output_json_path = "test_outputs/processor_results.json"
    isin_db_path = "test_outputs/isin_db.json"

    if not os.path.exists(dummy_pdf_path):
        logger.error(f"Dummy PDF '{dummy_pdf_path}' not found. Please run enhanced_table_extractor.py first or provide a PDF.")
        # Attempt to create it again if reportlab is available
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.units import inch
            os.makedirs(os.path.dirname(dummy_pdf_path), exist_ok=True)
            logger.info(f"Creating dummy PDF: {dummy_pdf_path}")
            c = canvas.Canvas(dummy_pdf_path, pagesize=letter)
            # Page 1
            textobject = c.beginText(inch, 10*inch)
            textobject.textLine("Page 1: Financial Report")
            textobject.textLine("ISIN: US0378331005 (Apple Inc.)")
            textobject.textLine("")
            textobject.textLine("Portfolio Value: $1,234,567.89")
            textobject.textLine("")
            textobject.textLine("Security | Quantity | Price | Market Value")
            textobject.textLine("---------|----------|-------|-------------")
            textobject.textLine("AAPL     | 100      | 175.0 | 17,500.00")
            textobject.textLine("MSFT     | 50       | 300.0 | 15,000.00")
            c.drawText(textobject)
            c.showPage()
            # Page 2
            textobject = c.beginText(inch, 10*inch)
            textobject.textLine("Page 2: More Details")
            textobject.textLine("Another ISIN: IL0010811143")
            textobject.textLine("Total Assets: ₪500,000")
            c.drawText(textobject)
            c.save()
            logger.info(f"Dummy PDF created.")
        except ImportError:
             logger.error("reportlab not installed. Cannot create dummy PDF.")
             exit()
        except Exception as e:
             logger.error(f"Failed to create dummy PDF: {e}")
             exit()


    # Configuration for the processor
    config = {
        'default_language': 'eng',
        'additional_languages': ['heb'],
        'isin_db_path': isin_db_path
    }

    # Initialize processor
    processor = PDFProcessor(config=config)

    # Process the dummy PDF
    logger.info(f"Processing document: {dummy_pdf_path}")
    results = processor.process_file(dummy_pdf_path, output_path=output_json_path)

    # Print summary
    if results and results.get("error") is None:
        logger.info("Processing successful!")
        logger.info(f"  - Pages processed: {len(results.get('pages', []))}")
        logger.info(f"  - Tables found: {len(results.get('tables', []))}")
        logger.info(f"  - ISINs found: {len(results.get('financialData', {}).get('isinNumbers', []))}")
        logger.info(f"  - Processing time: {results.get('processing_time', 'N/A')} seconds")
        logger.info(f"Full results saved to: {output_json_path}")
    elif results:
        logger.error(f"Processing failed: {results.get('error')}")
    else:
        logger.error("Processing returned no results.")


    logger.info("PDFProcessor example finished.")
