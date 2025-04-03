from gemini_financial_processor import GeminiFinancialProcessor, FinancialInstrument # Import model too if needed for type hints or checks
import os
from dotenv import load_dotenv

def test_api_auth():
    """Test Gemini API authentication with a simple request."""
    load_dotenv()
    
    print("Testing Gemini API authentication...")
    
    try:
        # Initialize processor with API key from .env
        # Initialize processor - it will load the key from Config/env
        processor = GeminiFinancialProcessor()
        
        # Test with minimal text
        test_text = "This is a test document containing one stock: Apple (AAPL) worth $100"
        # Use the internal method for a direct test, similar to before
        results = processor._extract_financial_instruments(test_text)

        # Check if the result is a list and not empty
        if isinstance(results, list) and results:
            # Assuming the first result is a FinancialInstrument object
            if isinstance(results[0], FinancialInstrument):
                 print("✅ Authentication successful! Received valid response from Gemini API")
                 print(f"Extracted instrument name (example): {results[0].name}")
            else:
                 print("⚠️ Authentication succeeded but response format might be incorrect.")
                 print(f"DEBUG: Received data type: {type(results[0])}")
        elif isinstance(results, list) and not results:
             print("✅ Authentication successful (API call likely worked), but no instruments extracted from test text.")
        else:
            # This case covers errors during the API call handled within _extract_financial_instruments
            print("❌ Authentication or processing likely failed. Check logs/previous errors.")
            
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")

if __name__ == "__main__":
    test_api_auth()