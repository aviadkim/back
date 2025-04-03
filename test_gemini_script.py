import os
import sys
from dotenv import load_dotenv
# Add current dir to path to find modules
sys.path.append(os.getcwd())
from gemini_financial_processor import GeminiFinancialProcessor
from config import Config # Ensure config is loaded for API key

load_dotenv() # Load .env

pdf_path = "uploads/2._Messos_28.02.2025.pdf" # Use the correct path

print(f"--- Starting Gemini Processor Test ---")
print(f"Current Working Directory: {os.getcwd()}")
print(f"Checking for PDF at: {os.path.abspath(pdf_path)}")

if os.path.exists(pdf_path):
    try:
        # Ensure API key is available (optional check, processor does it too)
        if not Config.GEMINI_API_KEY:
             print("ERROR: Gemini API key not found in environment/config.")
        else:
            print(f"INFO: Attempting to process {pdf_path} with Gemini...")
            processor = GeminiFinancialProcessor()
            results = processor.process_document(pdf_path)
            print(f"\n--- Gemini Extraction Results ---")
            if results:
                print(f"Extracted {len(results)} financial instruments:")
                for i, instrument in enumerate(results):
                     # Convert Pydantic model to dict for printing
                     try:
                         # Use model_dump() for Pydantic v2+ or dict() for v1
                         if hasattr(instrument, 'model_dump'):
                             data = instrument.model_dump(exclude_unset=True)
                         else:
                             data = instrument.dict(exclude_unset=True)
                     except AttributeError:
                         data = instrument # Assume it's already a dict if not Pydantic
                     print(f" {i+1}. {data}") # Print the whole dict for clarity
            else:
                print("No financial instruments extracted by Gemini or an error occurred.")
    except ValueError as ve:
         print(f"ERROR: {ve}") # Catch API key error from processor init
    except Exception as main_err:
         print(f"ERROR during processing: {main_err}")
         import traceback
         print(traceback.format_exc())
else:
    print(f"ERROR: Sample PDF not found at {pdf_path}")

print(f"--- Gemini Processor Test Finished ---")