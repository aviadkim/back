import os
import json
from dotenv import load_dotenv
from gemini_financial_processor import GeminiFinancialProcessor, FinancialInstrument

# Load environment variables (especially GEMINI_API_KEY)
load_dotenv()

# Specify the PDF file to process
pdf_path = "uploads/2._Messos_28.02.2025.pdf"

print(f"--- Starting Gemini Processing Test ---")
print(f"Processing file: {pdf_path}")

if not os.path.exists(pdf_path):
    print(f"ERROR: PDF file not found at {pdf_path}")
else:
    try:
        # Instantiate the processor (ensure API key is loaded via .env or config)
        processor = GeminiFinancialProcessor()

        # Process the document
        results = processor.process_document(pdf_path)

        print(f"\n--- Extraction Results ---")
        if results:
            print(f"Successfully extracted {len(results)} financial instruments.")
            # Convert Pydantic models to dictionaries for JSON serialization
            results_dict = [instrument.model_dump() for instrument in results]
            # Print results as JSON for clarity
            print(json.dumps(results_dict, indent=2))
        elif isinstance(results, list) and not results:
             print("No financial instruments were extracted by the processor.")
        else:
            # This case might indicate an error returned as non-list or None
            print("An unexpected issue occurred during processing. No results list returned.")

    except ValueError as ve:
        print(f"ERROR: Configuration or Value Error - {ve}")
    except Exception as e:
        import traceback
        print(f"ERROR: An unexpected error occurred during the test execution: {e}")
        print(f"Traceback:\n{traceback.format_exc()}")

print(f"\n--- Gemini Processing Test Finished ---")