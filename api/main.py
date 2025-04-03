"""
API מינימלי עבור מערכת לעיבוד דפי בנק
"""

import os
import sys
import json
import tempfile
import shutil
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging

# הוספת נתיב הפרויקט ל-Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ייבוא הפונקציות מהגרסה הישנה והחדשה
from scripts.process_document import extract_tables_from_image, extract_securities
from scripts.improved_table_extraction import extract_tables_hybrid
from scripts.improved_securities_extraction import extract_securities_hybrid, extract_text_from_image
from scripts.benchmark_pages import analyze_specific_pages, convert_pdf_to_images

# יצירת אובייקט ה-API
app = FastAPI(
    title="מערכת לעיבוד דפי בנק אוטומטית",
    description="API לעיבוד דפי בנק ומסמכים פיננסיים",
    version="1.2.0"
)

# ייבוא נתיבים
from api.routes.pdf_analysis import router as pdf_router

# רישום נתיבים
app.include_router(pdf_router)

# הגדרת CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# הגדרת ה-logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PageRange(BaseModel):
    start_page: int
    end_page: Optional[int] = None

@app.get("/")
async def root():
    """נקודת הכניסה הראשית ל-API"""
    return {"message": "ברוכים הבאים ל-API של מערכת עיבוד דפי בנק אוטומטית"}

@app.post("/analyze/benchmark")
async def analyze_benchmark(
    file: UploadFile = File(...),
    start_page: int = Form(1),
    end_page: Optional[int] = Form(None)
):
    """
    מבצע השוואה בין הגרסה הישנה לחדשה על דפים ספציפיים בקובץ PDF
    
    Args:
        file: קובץ ה-PDF לניתוח
        start_page: מספר עמוד התחלתי
        end_page: מספר עמוד סופי (אופציונלי)
    
    Returns:
        תוצאות ההשוואה והקישור לגרף ההשוואה
    """
    try:
        # יצירת תיקייה זמנית
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, file.filename)
        
        # שמירת הקובץ המועלה
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"הקובץ {file.filename} הועלה בהצלחה")
        
        # ניתוח העמודים הספציפיים
        results = analyze_specific_pages(pdf_path, start_page, end_page)
        
        # הכנת התוצאות
        output = {
            "results": results,
            "file": file.filename,
            "pages_analyzed": {
                "start_page": start_page,
                "end_page": end_page or "סוף"
            }
        }
        
        # החזרת התוצאות
        return JSONResponse(content=output)
        
    except Exception as e:
        logger.error(f"שגיאה בעיבוד הקובץ: {str(e)}")
        raise HTTPException(status_code=500, detail=f"שגיאה בעיבוד הקובץ: {str(e)}")
    finally:
        # ניקוי התיקייה הזמנית
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir)

@app.post("/analyze/page")
async def analyze_single_page(
    file: UploadFile = File(...),
    page_num: int = Form(1),
    use_new_version: bool = Form(True)
):
    """
    מנתח עמוד בודד מתוך קובץ PDF באמצעות הגרסה החדשה או הישנה
    
    Args:
        file: קובץ ה-PDF לניתוח
        page_num: מספר העמוד לניתוח
        use_new_version: האם להשתמש בגרסה החדשה (ברירת מחדל: כן)
    
    Returns:
        תוצאות הניתוח
    """
    try:
        # יצירת תיקייה זמנית
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, file.filename)
        
        # שמירת הקובץ המועלה
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"הקובץ {file.filename} הועלה בהצלחה")
        
        # המרת העמוד לתמונה
        image_paths = convert_pdf_to_images(pdf_path, temp_dir, page_num, page_num)
        
        if not image_paths:
            raise HTTPException(status_code=400, detail="לא ניתן להמיר את העמוד לתמונה")
        
        image_path = image_paths[0]
        import cv2
        import numpy as np
        
        # טעינת התמונה
        img = cv2.imread(image_path)
        if img is None:
            raise HTTPException(status_code=400, detail="לא ניתן לטעון את התמונה")
        
        results = {}
        
        # חילוץ טקסט מהתמונה
        text = extract_text_from_image(img)
        results["extracted_text"] = text
        
        # חילוץ טבלאות
        if use_new_version:
            tables = extract_tables_hybrid(img)
        else:
            tables = extract_tables_from_image(img, page_number=page_num)
        
        results["tables_count"] = len(tables)
        results["tables"] = tables
        
        # זיהוי ניירות ערך
        if use_new_version:
            securities = extract_securities_hybrid(img=img)
        else:
            securities = extract_securities(text, tables=tables, img=img)
        
        results["securities_count"] = len(securities)
        results["securities"] = securities
        
        # החזרת התוצאות
        return JSONResponse(content=results)
        
    except Exception as e:
        logger.error(f"שגיאה בעיבוד העמוד: {str(e)}")
        raise HTTPException(status_code=500, detail=f"שגיאה בעיבוד העמוד: {str(e)}")
    finally:
        # ניקוי התיקייה הזמנית
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir)

@app.post("/analyze/document")
async def analyze_document(
    file: UploadFile = File(...),
    pages: List[PageRange] = None,
    use_new_version: bool = Form(True)
):
    """
    מנתח מסמך שלם או טווח עמודים ספציפי
    
    Args:
        file: קובץ ה-PDF לניתוח
        pages: רשימת טווחי עמודים לניתוח
        use_new_version: האם להשתמש בגרסה החדשה (ברירת מחדל: כן)
    
    Returns:
        תוצאות הניתוח
    """
    # יש להשלים את המימוש
    pass

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 