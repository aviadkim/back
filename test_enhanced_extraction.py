from enhanced_financial_extractor import extract_isin_numbers, extract_financial_metadata, analyze_portfolio
import json
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_enhanced_extraction.py <ocr_json_file>")
        sys.exit(1)
    
    # Load OCR data
    ocr_path = sys.argv[1]
    with open(ocr_path, 'r', encoding='utf-8') as f:
        ocr_data = json.load(f)
    
    # Combine all text
    all_text = ""
    for page_num, page_data in ocr_data.items():
        all_text += page_data.get("text", "") + "\n\n"
    
    # Extract ISIN numbers
    isin_numbers = extract_isin_numbers(all_text)
    print(f"Found {len(isin_numbers)} ISIN numbers")
    
    # Extract financial metadata
    financial_data = extract_financial_metadata(all_text, isin_numbers)
    
    # Save enhanced financial data
    output_path = ocr_path.replace("_ocr.json", "_enhanced_financial.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(financial_data, f, indent=2, ensure_ascii=False)
    
    print(f"Enhanced financial data saved to {output_path}")
    
    # Sample data
    print("\nSample extraction for first ISIN:")
    first_isin = next(iter(financial_data))
    print(json.dumps(financial_data[first_isin], indent=2))
    
    # Analyze portfolio
    print("\nAnalyzing portfolio...")
    analysis = analyze_portfolio(financial_data)
    
    # Save analysis
    analysis_path = ocr_path.replace("_ocr.json", "_portfolio_analysis.json")
    with open(analysis_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"Portfolio analysis saved to {analysis_path}")
    
    # Print portfolio summary
    if analysis.get("top_holdings"):
        print("\nTop 3 holdings:")
        for i, holding in enumerate(analysis["top_holdings"][:3]):
            print(f"  {i+1}. {holding.get('name', 'Unknown')} ({holding.get('isin', 'Unknown')}) - {holding.get('percentage', 0):.2f}%")

if __name__ == "__main__":
    main()
