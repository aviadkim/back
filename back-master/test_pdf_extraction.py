from pdf_processor.extraction.text_extractor import PDFTextExtractor
from pdf_processor.tables.table_extractor import TableExtractor
from pdf_processor.analysis.financial_analyzer import FinancialAnalyzer
import sys
import json
import os

def extract_pdf_content(pdf_path, language="heb+eng"):
    """Extract text, tables and financial data from a PDF file"""
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found at {pdf_path}")
        return None
    
    results = {
        "file": pdf_path,
        "language": language,
        "text_extraction": {},
        "tables": {},
        "financial_analysis": {}
    }
    
    # Extract text
    print(f"Extracting text from {pdf_path}...")
    try:
        text_extractor = PDFTextExtractor(language=language)
        document = text_extractor.extract_document(pdf_path)
        
        if document:
            results["text_extraction"]["status"] = "success"
            results["text_extraction"]["page_count"] = len(document)
            
            # Store sample text from each page
            text_samples = {}
            for page_num, page_data in document.items():
                text = page_data.get("text", "")
                text_samples[page_num] = text[:200] + "..." if len(text) > 200 else text
            
            results["text_extraction"]["text_samples"] = text_samples
            
            # Check for financial content
            has_financial = False
            for page_num, page_data in document.items():
                text = page_data.get("text", "")
                if text_extractor.is_potentially_financial(text):
                    has_financial = True
                    break
            results["text_extraction"]["potentially_financial"] = has_financial
        else:
            results["text_extraction"]["status"] = "failed"
            results["text_extraction"]["error"] = "No text extracted"
    
    except Exception as e:
        results["text_extraction"]["status"] = "error"
        results["text_extraction"]["error"] = str(e)
        import traceback
        traceback.print_exc()
    
    # Extract tables
    print("Extracting tables...")
    try:
        table_extractor = TableExtractor()
        tables = table_extractor.extract_tables(pdf_path)
        
        if tables:
            results["tables"]["status"] = "success"
            results["tables"]["page_count"] = len(tables)
            
            # Count tables per page
            table_counts = {}
            for page_num, page_tables in tables.items():
                table_counts[page_num] = len(page_tables)
            
            results["tables"]["table_counts"] = table_counts
            
            # Convert first table to DataFrame and get sample data
            if len(tables) > 0:
                first_page = next(iter(tables))
                if len(tables[first_page]) > 0:
                    first_table = tables[first_page][0]
                    df = table_extractor.convert_to_dataframe(first_table)
                    results["tables"]["first_table_shape"] = df.shape
                    # Get a sample of the table data
                    if not df.empty:
                        results["tables"]["first_table_sample"] = df.head(3).to_dict(orient='records')
        else:
            results["tables"]["status"] = "no_tables"
    except Exception as e:
        results["tables"]["status"] = "error"
        results["tables"]["error"] = str(e)
        import traceback
        traceback.print_exc()
    
    # Analyze financial data
    print("Analyzing financial data...")
    try:
        financial_analyzer = FinancialAnalyzer()
        
        # Extract metrics from text
        all_text = ""
        if "text_extraction" in results and results["text_extraction"].get("status") == "success":
            for page_num, page_data in document.items():
                all_text += page_data.get("text", "") + "\n\n"
        
        if all_text:
            metrics = financial_analyzer.extract_financial_metrics(all_text)
            results["financial_analysis"]["metrics"] = metrics
            results["financial_analysis"]["status"] = "success" if metrics else "no_metrics"
        else:
            results["financial_analysis"]["status"] = "no_text"
        
        # Analyze first table if available
        if "tables" in results and results["tables"].get("status") == "success":
            if "first_table_sample" in results["tables"]:
                import pandas as pd
                df = pd.DataFrame(results["tables"]["first_table_sample"])
                table_type = financial_analyzer.classify_table(df)
                results["financial_analysis"]["first_table_type"] = table_type
                
                # Analyze table
                table_analysis = financial_analyzer.analyze_financial_table(df, table_type)
                results["financial_analysis"]["table_analysis"] = table_analysis
    except Exception as e:
        results["financial_analysis"]["status"] = "error"
        results["financial_analysis"]["error"] = str(e)
        import traceback
        traceback.print_exc()
    
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_pdf_extraction.py <pdf_path> [language]")
        print("Example: python test_pdf_extraction.py test_documents/sample.pdf heb+eng")
        return
    
    pdf_path = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else "heb+eng"
    
    results = extract_pdf_content(pdf_path, language)
    if results:
        print("\n=== Extraction Results ===")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
        # Save results to file
        output_file = f"{os.path.splitext(os.path.basename(pdf_path))[0]}_extraction.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()
