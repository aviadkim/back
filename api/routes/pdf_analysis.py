"""
נתיב API לניתוח קבצי PDF באמצעות PyMuPDF

מאפשר גישה לפונקציות מתוך הסקריפט pdf_mupdf_reader.py דרך ממשק REST
"""

import os
import sys
import tempfile
import shutil
from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# הוספת נתיב הפרויקט ל-Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# ייבוא הפונקציות מהסקריפט
from scripts.pdf_mupdf_reader import (
    extract_text_from_pdf,
    extract_tables_from_page,
    extract_financial_data,
    analyze_pdf_content
)

router = APIRouter(
    prefix="/pdf",
    tags=["pdf-analysis"],
    responses={404: {"description": "לא נמצא"}},
)

class PdfAnalysisResponse(BaseModel):
    filename: str
    total_pages_analyzed: int
    pages: dict
    metadata: Optional[dict] = None

@router.post("/analyze", response_model=PdfAnalysisResponse)
async def analyze_pdf(
    file: UploadFile = File(...),
    pages: List[int] = Query(None, description="מספרי עמודים לניתוח (ריק = כל העמודים)"),
):
    """
    ניתוח קובץ PDF באמצעות PyMuPDF
    
    מבצע ניתוח מקיף של קובץ PDF, כולל:
    - חילוץ טקסט מכל העמודים או עמודים ספציפיים
    - זיהוי טבלאות וניתוח מבנה
    - חילוץ מידע פיננסי (מספרי ISIN, תאריכים, סכומים)
    
    Args:
        file: קובץ ה-PDF לניתוח
        pages: מספרי עמודים ספציפיים לניתוח (אם ריק, ינותחו כל העמודים)
    
    Returns:
        תוצאות הניתוח בפורמט JSON
    """
    try:
        # יצירת תיקייה זמנית
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, file.filename)
        
        # שמירת הקובץ המועלה
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # אם הועברו מספרי עמודים, המר אותם למספרים
        page_numbers = pages if pages else None
        
        # ניתוח המסמך
        output_dir = os.path.join(temp_dir, "results")
        results = analyze_pdf_content(pdf_path, page_numbers, output_dir)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בעיבוד ה-PDF: {str(e)}")
    finally:
        # ניקוי התיקייה הזמנית
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir)

@router.post("/extract-text")
async def extract_text_from_document(
    file: UploadFile = File(...),
    pages: List[int] = Query(None, description="מספרי עמודים לחילוץ (ריק = כל העמודים)"),
):
    """
    חילוץ טקסט מקובץ PDF
    
    מחלץ טקסט מכל העמודים או עמודים ספציפיים בקובץ PDF
    
    Args:
        file: קובץ ה-PDF
        pages: מספרי עמודים ספציפיים לחילוץ (אם ריק, יחולץ מכל העמודים)
    
    Returns:
        הטקסט שחולץ לפי מספרי עמודים
    """
    try:
        # יצירת תיקייה זמנית
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, file.filename)
        
        # שמירת הקובץ המועלה
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # אם הועברו מספרי עמודים, המר אותם למספרים
        page_numbers = pages if pages else None
        
        # חילוץ הטקסט
        text_results = extract_text_from_pdf(pdf_path, page_numbers)
        
        return JSONResponse(content={
            "filename": file.filename,
            "pages": text_results
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בחילוץ טקסט מה-PDF: {str(e)}")
    finally:
        # ניקוי התיקייה הזמנית
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir)

@router.post("/extract-tables")
async def extract_tables(
    file: UploadFile = File(...),
    page: int = Form(..., description="מספר העמוד לחילוץ טבלאות"),
):
    """
    חילוץ טבלאות מעמוד ספציפי בקובץ PDF
    
    Args:
        file: קובץ ה-PDF
        page: מספר העמוד לחילוץ טבלאות
    
    Returns:
        הטבלאות שזוהו בעמוד
    """
    try:
        # יצירת תיקייה זמנית
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, file.filename)
        
        # שמירת הקובץ המועלה
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # פתיחת הקובץ וקבלת העמוד
        import fitz
        doc = fitz.open(pdf_path)
        
        if page < 1 or page > len(doc):
            raise HTTPException(status_code=400, detail=f"מספר עמוד לא תקין: {page}, הקובץ מכיל {len(doc)} עמודים")
        
        # חילוץ טבלאות מהעמוד
        pdf_page = doc[page - 1]
        tables = extract_tables_from_page(pdf_page)
        
        return JSONResponse(content={
            "filename": file.filename,
            "page": page,
            "tables_count": len(tables),
            "tables": tables
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בחילוץ טבלאות מה-PDF: {str(e)}")
    finally:
        # ניקוי התיקייה הזמנית
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir)

@router.post("/extract-financial-data")
async def extract_financial(
    file: UploadFile = File(...),
    pages: List[int] = Query(None, description="מספרי עמודים לחילוץ (ריק = כל העמודים)"),
):
    """
    חילוץ מידע פיננסי מקובץ PDF
    
    מחלץ מידע פיננסי כמו מספרי ISIN, תאריכים וסכומים מהמסמך
    
    Args:
        file: קובץ ה-PDF
        pages: מספרי עמודים ספציפיים לחילוץ (אם ריק, יחולץ מכל העמודים)
    
    Returns:
        המידע הפיננסי שחולץ
    """
    try:
        # יצירת תיקייה זמנית
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, file.filename)
        
        # שמירת הקובץ המועלה
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # חילוץ טקסט מהמסמך
        text_results = extract_text_from_pdf(pdf_path, pages)
        
        # חילוץ מידע פיננסי מכל עמוד
        financial_data = {}
        for page_num, text in text_results.items():
            if isinstance(text, dict) and "text" in text:
                # בגרסה חדשה יותר, הטקסט מוחזר כמילון
                financial_data[str(page_num)] = extract_financial_data(text["text"])
            else:
                # בגרסה ישנה יותר, הטקסט מוחזר כמחרוזת
                financial_data[str(page_num)] = extract_financial_data(text)
        
        return JSONResponse(content={
            "filename": file.filename,
            "pages_analyzed": list(financial_data.keys()),
            "financial_data": financial_data
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה בחילוץ מידע פיננסי מה-PDF: {str(e)}")
    finally:
        # ניקוי התיקייה הזמנית
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir) 