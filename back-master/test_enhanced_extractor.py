from enhanced_financial_extractor import EnhancedFinancialExtractor
import json
import requests
import os

def test_extraction_with_sample_text():
    """Test the enhanced extractor with a sample text"""
    print("Testing enhanced extractor with sample text...")
    
    sample_text = """
    Financial Portfolio Summary
    
    Client: Test Client
    Account Number: ACC123456
    Valuation Date: April 1, 2025
    
    Securities:
    ISIN            Security Name        Quantity    Market Value
    US0378331005    Apple Inc.           100         $18,500
    US5949181045    Microsoft Corp       75          $25,000
    US88160R1014    Tesla Inc            30          $7,500
    CH1908490000    Credit Suisse AG     200         €15,000
    XS2530201644    Deutsche Bank AG     150         $12,000
    
    Asset Allocation:
    Asset Class     Allocation (%)
    Equities        65%
    Bonds           25%
    Cash            10%
    """
    
    extractor = EnhancedFinancialExtractor()
    result = extractor.extract_data(sample_text)
    
    print(f"Extracted {len(result['isins'])} ISINs")
    print(f"Extracted {len(result['securities'])} securities")
    print(f"Extracted {len(result['percentages'])} percentages")
    print(f"Extracted {len(result['tables'])} tables")
    
    return result

def test_enhanced_api_endpoint():
    """Test the enhanced API endpoint"""
    print("\nTesting enhanced API endpoint...")
    
    # Get a document ID from the list of documents
    try:
        response = requests.get("http://localhost:5001/api/documents")
        if response.status_code == 200:
            documents = response.json().get('documents', [])
            if documents:
                document_id = documents[0]['document_id']
                print(f"Using document ID: {document_id}")
                
                # Test the enhanced endpoint
                response = requests.get(f"http://localhost:5001/api/documents/{document_id}/enhanced")
                print(f"Status code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    enhanced_data = data.get('enhanced_data', {})
                    print(f"Enhanced data returned with {len(enhanced_data.get('isins', []))} ISINs")
                    return True
                else:
                    print(f"Error response: {response.text}")
            else:
                print("No documents found")
        else:
            print(f"Error getting documents: {response.status_code}")
    except Exception as e:
        print(f"Error testing enhanced endpoint: {e}")
    
    return False

if __name__ == "__main__":
    # Test with sample text
    test_extraction_with_sample_text()
    
    # Test API endpoint
    test_enhanced_api_endpoint()
