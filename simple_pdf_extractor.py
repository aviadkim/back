from utils.pdf.pypdf_adapter import get_pdf_reader, get_page_count, get_page, extract_text
import os
import json

def extract_pdf_text(pdf_path):
    """Extract text from a PDF file using PyPDF2"""
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File not found: {pdf_path}")
        return None
    
    try:
        # Open the PDF
        with open(pdf_path, 'rb') as file:
            reader = get_pdf_reader(file)
            page_count = get_page_count(reader)
            
            print(f"PDF has {page_count} pages")
            
            # Extract text from each page
            document = {}
            for i in range(page_count):
                print(f"Processing page {i+1}/{page_count}")
                page = get_page(reader, i)
                text = extract_text(page)
                
                document[i] = {
                    "page_num": i+1,
                    "text": text
                }
            
            return document
    
    except Exception as e:
        print(f"❌ Error extracting text: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python simple_pdf_extractor.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    document = extract_pdf_text(pdf_path)
    
    if document:
        print("\n=== Extraction Results ===")
        for page_num, page_data in document.items():
            text = page_data["text"]
            preview = text[:100] + "..." if len(text) > 100 else text
            print(f"Page {page_data['page_num']}: {preview}")
        
        # Save results to file
        output_file = f"{os.path.splitext(os.path.basename(pdf_path))[0]}_text.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(document, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to {output_file}")
