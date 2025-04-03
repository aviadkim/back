import google.generativeai as genai
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Generic, TypeVar
import os
import google.api_core.exceptions
import json
import fitz  # PyMuPDF
from config import Config # Import Config to get the key

T = TypeVar('T')

class FinancialInstrument(BaseModel, Generic[T]):
    """Data model for financial instrument extracted from document."""
    isin: str = Field(description="ISIN code of the financial instrument")
    name: str = Field(description="Name of the financial instrument")
    type: Optional[str] = Field(default=None, description="Instrument type (stock, bond, ETF, etc.)")
    value: Optional[float] = Field(default=None, description="Current value of the instrument")
    currency: Optional[str] = Field(default=None, description="Currency of the instrument")
    percentage_in_portfolio: Optional[float] = Field(default=None, description="Percentage value in portfolio")

class GeminiFinancialProcessor:
    """Processes financial documents using Google Gemini AI."""

    def __init__(self, gemini_api_key=None):
        """Initializes the Gemini processor."""
        self.gemini_api_key = gemini_api_key or Config.GEMINI_API_KEY
        if not self.gemini_api_key:
            raise ValueError("Gemini API key is required. Check config.py or .env file.")

        try:
            genai.configure(api_key=self.gemini_api_key)
            # Using a cost-effective and capable model suitable for JSON extraction
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print("DEBUG: Gemini client configured successfully.")
        except Exception as e:
            print(f"ERROR: Failed to configure Gemini client: {str(e)}")
            raise  # Re-raise the exception to prevent using an uninitialized client

    def process_document(self, pdf_path):
        """Process PDF document and extract structured financial information."""
        try:
            # Text extraction using PyMuPDF (fitz)
            document = {}
            try:
                doc = fitz.open(pdf_path)
                if doc.is_encrypted:
                    # PyMuPDF handles decryption attempt automatically in open()
                    # If it fails, it raises an exception caught below.
                    # We could try doc.authenticate('') if needed, but open usually suffices.
                    print(f"INFO: PDF {pdf_path} is encrypted. PyMuPDF will attempt to open.")

                for i, page in enumerate(doc.pages()): # Use doc.pages()
                    try:
                        text = page.get_text("text") or '' # Use get_text()
                        document[str(i)] = {'text': text}
                    except Exception as page_err:
                        print(f"WARN: Error extracting text from page {i} using PyMuPDF in {pdf_path}: {page_err}")
                        document[str(i)] = {'text': ''} # Add empty text on error
                doc.close() # Close the document
            except fitz.fitz.PasswordError as decrypt_err:
                 print(f"ERROR: Failed to decrypt PDF {pdf_path} with empty password: {decrypt_err}")
                 return [] # Cannot proceed with encrypted file
            except Exception as fitz_err:
                print(f"ERROR: Failed to process PDF {pdf_path} with PyMuPDF: {fitz_err}")
                # Optionally, add fallback to OCR here if PyMuPDF fails fundamentally
                # For now, return empty list on PyMuPDF failure
                return []
            # Simple table extraction placeholder (remains unchanged)
            tables = {}

            # Combine document text
            all_text = self._combine_document_and_tables(document, tables)

            if not all_text.strip():
                print(f"WARN: No text extracted from document: {pdf_path}")
                return []

            # Process with LLM to extract structured financial data
            return self._extract_financial_instruments(all_text)

        except FileNotFoundError:
            print(f"ERROR: PDF file not found at {pdf_path}")
            return []
        except Exception as e:
            print(f"ERROR: Unexpected error processing document {pdf_path}: {str(e)}")
            # Consider logging traceback here
            return []

    def _combine_document_and_tables(self, document, tables):
        """Combine document text and tables into unified format."""
        content = []
        for page_num, page_data in document.items():
            try:
                page_num_int = int(page_num)
                content.append(f"--- PAGE {page_num_int + 1} TEXT ---\n{page_data.get('text', '')}\n")
            except (ValueError, KeyError):
                print(f"WARN: Skipping page data due to invalid format: {page_num}")
                continue
        # Placeholder for adding formatted table data if implemented
        # for table_id, table_data in tables.items():
        #     content.append(f"--- TABLE {table_id} ---\n{format_table(table_data)}\n")
        return "\n".join(content)

    def _extract_financial_instruments(self, text):
        """Extract financial instruments from document text using Gemini."""
        prompt = f"""
Analyze the following financial document text and extract all identifiable financial instruments.
For each instrument, provide the ISIN code (12-character alphanumeric), name, type (e.g., stock, bond, ETF), value, currency, and percentage in the portfolio if available.
Format the output as a JSON list of objects, where each object adheres *exactly* to the following structure (use null for missing optional fields):
{{
    "isin": "string (12 chars)",
    "name": "string",
    "type": "string or null",
    "value": "float or null",
    "currency": "string or null",
    "percentage_in_portfolio": "float or null"
}}

Ensure the output is *only* the JSON list, without any introductory text, explanations, or markdown formatting.

Document Text:
---
{text[:30000]}
---

JSON Output:
"""
        # Truncated text to avoid exceeding potential input limits, adjust as needed

        try:
            print(f"DEBUG: Sending request to Gemini API (model: {self.model.model_name})...")
            # print(f"DEBUG: Request text length (truncated): {len(text[:30000])} characters")

            # Configure response format for JSON
            generation_config = genai.types.GenerationConfig(
                response_mime_type="application/json"
            )

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                # Add safety settings if needed, e.g., block none
                # safety_settings={'HARASSMENT': 'BLOCK_NONE', ...}
            )

            print("DEBUG: Successfully received response from Gemini API")

            # Robustness checks
            if not response.candidates:
                 print("WARN: Gemini response blocked or empty. Feedback:", response.prompt_feedback)
                 return []
            # Compare finish_reason to the typical integer value for STOP (1)
            if response.candidates[0].finish_reason != 1:
                print(f"WARN: Gemini generation finished unexpectedly. Reason: {response.candidates[0].finish_reason}. Content: {response.text[:500]}...") # Log partial content
                # Consider checking safety ratings: response.candidates[0].safety_ratings
                return []

            # Attempt to parse the JSON response
            try:
                # Gemini with JSON mime type should return clean JSON, but strip just in case
                cleaned_json_text = response.text.strip()
                if not cleaned_json_text:
                    print("WARN: Received empty text response from Gemini.")
                    return []
                extracted_data = json.loads(cleaned_json_text)
            except json.JSONDecodeError as json_err:
                print(f"ERROR: Failed to decode JSON response from Gemini: {json_err}")
                print(f"DEBUG: Received text that failed JSON parsing:\n{response.text[:1000]}...") # Log partial text
                return []

            # Validate and convert JSON data to FinancialInstrument objects
            instruments = []
            if isinstance(extracted_data, list):
                for item_idx, item in enumerate(extracted_data):
                    if not isinstance(item, dict):
                        print(f"WARN: Skipping item #{item_idx} as it's not a dictionary: {item}")
                        continue
                    try:
                        # Pydantic will handle missing optional fields if they are None/null in JSON
                        instruments.append(FinancialInstrument(**item))
                    except ValidationError as val_err:
                        print(f"WARN: Skipping item #{item_idx} due to validation error: {val_err}. Item: {item}")
            # Handle case where Gemini might return a single object not in a list (less likely with JSON mime type)
            elif isinstance(extracted_data, dict):
                 try:
                     instruments.append(FinancialInstrument(**extracted_data))
                 except ValidationError as val_err:
                     print(f"WARN: Skipping single item due to validation error: {val_err}. Item: {extracted_data}")
            else:
                print(f"WARN: Unexpected JSON structure received from Gemini (expected list): {type(extracted_data)}")

            print(f"DEBUG: Extracted {len(instruments)} instruments.")
            return instruments

        except (genai.types.BlockedPromptException, genai.types.StopCandidateException) as safety_exception:
             print(f"ERROR: Gemini request blocked due to safety settings: {safety_exception}")
             return []
        except google.api_core.exceptions.PermissionDenied as perm_denied:
             print(f"ERROR: Gemini API permission denied. Check API key and project permissions: {perm_denied}")
             return []
        except google.api_core.exceptions.ResourceExhausted as rate_limit:
             print(f"ERROR: Gemini API rate limit exceeded: {rate_limit}")
             # Implement backoff/retry logic here if needed
             return []
        except Exception as e:
            # Catch other potential API errors or unexpected issues
            import traceback
            print(f"ERROR: Unexpected error during Gemini API call or processing: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return []


if __name__ == "__main__":
    # This block is for basic testing of the processor
    from dotenv import load_dotenv
    load_dotenv() # Ensure .env variables are loaded

    # Create dummy PDF for testing if sample doesn't exist
    sample_pdf = "test_samples/sample_financial.pdf"
    if not os.path.exists(sample_pdf):
        print(f"WARN: Sample PDF not found at {sample_pdf}. Skipping direct execution test.")
        # Consider creating a dummy PDF here if essential for basic testing
        # from reportlab.pdfgen import canvas
        # from reportlab.lib.pagesizes import letter
        # os.makedirs(os.path.dirname(sample_pdf), exist_ok=True)
        # c = canvas.Canvas(sample_pdf, pagesize=letter)
        # c.drawString(100, 750, "Sample Financial Document Text.")
        # c.drawString(100, 735, "ISIN: US0378331005, Name: Apple Inc., Type: Stock, Value: 170.0, Currency: USD")
        # c.save()
        # print(f"INFO: Created dummy PDF: {sample_pdf}")

    if os.path.exists(sample_pdf):
        try:
            processor = GeminiFinancialProcessor() # Instantiates with key from Config/.env
            results = processor.process_document(sample_pdf)
            print(f"\n--- Extraction Results ---")
            if results:
                print(f"Extracted {len(results)} financial instruments:")
                for i, instrument in enumerate(results):
                    print(f" {i+1}. ISIN: {instrument.isin}, Name: {instrument.name}, Type: {instrument.type or 'N/A'}, Value: {instrument.value or 'N/A'} {instrument.currency or ''}, %: {instrument.percentage_in_portfolio or 'N/A'}")
            else:
                print("No financial instruments extracted or an error occurred.")
        except ValueError as ve:
             print(f"ERROR in main execution: {ve}") # Catch API key error
        except Exception as main_err:
             print(f"ERROR during main execution test: {main_err}")
    else:
        print(f"INFO: Skipping execution as sample PDF not found: {sample_pdf}")