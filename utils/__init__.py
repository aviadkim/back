# utils/__init__.py
# ייבוא פונקציות שימושיות

from .pdf_processor import PDFProcessor

# יצירת פונקציית מעטפת לתאימות לאחור
def extract_text_from_pdf(pdf_path, ocr_enabled=True, lang="heb+eng"):
    """
    פונקציית עזר לחילוץ טקסט מקובץ PDF - לצורך תאימות לאחור
    
    Args:
        pdf_path: נתיב לקובץ PDF
        ocr_enabled: האם להפעיל OCR
        lang: שפת OCR
        
    Returns:
        str: הטקסט המחולץ
    """
    processor = PDFProcessor(ocr_enabled=ocr_enabled, lang=lang)
    return processor.extract_text(pdf_path)
