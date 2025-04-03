import os
import json
from enhanced_financial_extractor import extract_isin_numbers, extract_financial_metadata, analyze_portfolio

def process_existing_documents(uploads_dir="uploads"):
    """Process existing documents with enhanced extraction"""
    if not os.path.exists(uploads_dir):
        print(f"Error: {uploads_dir} directory not found")
        return
    
    # Find OCR JSON files
    ocr_files = [f for f in os.listdir(uploads_dir) if f.endswith('_ocr.json')]
    
    if not ocr_files:
        print(f"No OCR files found in {uploads_dir}")
        return
    
    print(f"Found {len(ocr_files)} OCR files to process")
    
    for ocr_file in ocr_files:
        ocr_path = os.path.join(uploads_dir, ocr_file)
        doc_id = ocr_file.split('_ocr.json')[0]
        
        print(f"Processing {ocr_file}...")
        
        # Load OCR data
        with open(ocr_path, 'r', encoding='utf-8') as f:
            ocr_data = json.load(f)
        
        # Combine all text
        all_text = ""
        for page_num, page_data in ocr_data.items():
            all_text += page_data.get("text", "") + "\n\n"
        
        # Extract ISIN numbers
        isin_numbers = extract_isin_numbers(all_text)
        print(f"  Found {len(isin_numbers)} ISIN numbers")
        
        # Extract financial metadata
        financial_data = extract_financial_metadata(all_text, isin_numbers)
        
        # Save enhanced financial data
        enhanced_financial_path = os.path.join(uploads_dir, f"{doc_id}_enhanced_financial.json")
        with open(enhanced_financial_path, 'w', encoding='utf-8') as f:
            json.dump(financial_data, f, indent=2, ensure_ascii=False)
        
        print(f"  Enhanced financial data saved to {os.path.basename(enhanced_financial_path)}")
        
        # Analyze portfolio
        analysis = analyze_portfolio(financial_data)
        
        # Save analysis
        analysis_path = os.path.join(uploads_dir, f"{doc_id}_portfolio_analysis.json")
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"  Portfolio analysis saved to {os.path.basename(analysis_path)}")
    
    print("\nAll documents processed successfully")

if __name__ == "__main__":
    process_existing_documents()
