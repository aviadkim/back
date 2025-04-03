print("Testing imports...")

try:
    print("Importing cv2...")
    import cv2
    print("✅ cv2 imported successfully")
except ImportError as e:
    print(f"❌ Error importing cv2: {str(e)}")

try:
    print("\nImporting pdf_processor components...")
    from pdf_processor.extraction.text_extractor import PDFTextExtractor
    from pdf_processor.tables.table_extractor import TableExtractor
    from pdf_processor.analysis.financial_analyzer import FinancialAnalyzer
    print("✅ pdf_processor components imported successfully")
except ImportError as e:
    print(f"❌ Error importing pdf_processor components: {str(e)}")
    import traceback
    traceback.print_exc()

try:
    print("\nImporting routes...")
    from routes.document import document_api
    print("✅ routes imported successfully")
except ImportError as e:
    print(f"❌ Error importing routes: {str(e)}")
    import traceback
    traceback.print_exc()

print("\nDone testing imports")
