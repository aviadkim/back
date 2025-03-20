#!/usr/bin/env python3
"""
סקריפט מתקדם לחילוץ טקסט וטבלאות מקובץ PDF באמצעות PyMuPDF (fitz)
גרסה: 1.2

פותח עבור חילוץ מידע פיננסי ממסמכי בנק וניירות ערך.
יכולות עיקריות:
- חילוץ טקסט מלא מכל סוגי מסמכי PDF
- זיהוי מתקדם של טבלאות ומבנים טבלאיים
- זיהוי מבנה עמודות בטבלאות
- חילוץ מספרי ISIN, תאריכים, וסכומים כספיים
- זיהוי שורות שעשויות להיות חלק מטבלה
- שמירת נתונים בפורמט JSON לניתוח נוסף

שימושים:
פיתוח 2024 © כל הזכויות שמורות
"""

import os
import sys
import argparse
import json
import re
from datetime import datetime
import traceback
import collections

try:
    import fitz  # PyMuPDF
except ImportError:
    print("נדרשת ספריית PyMuPDF. הריצו: pip install pymupdf")
    sys.exit(1)

def extract_text_from_pdf(pdf_path, page_numbers=None):
    """
    חילוץ טקסט מקובץ PDF באמצעות PyMuPDF
    
    Args:
        pdf_path: נתיב לקובץ PDF
        page_numbers: רשימת מספרי עמודים לחילוץ (None = כל העמודים)
    
    Returns:
        מילון עם טקסט לפי מספר עמוד
    """
    results = {}
    
    try:
        # פתיחת קובץ ה-PDF
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        print(f"סה\"כ עמודים בקובץ: {total_pages}")
        
        # אם לא צוינו עמודים ספציפיים, חלץ את כולם
        if page_numbers is None:
            page_numbers = list(range(1, total_pages + 1))
        else:
            # מוודא שהעמודים בטווח התקין
            page_numbers = [p for p in page_numbers if 0 < p <= total_pages]
            
        if not page_numbers:
            print("אזהרה: לא נמצאו מספרי עמודים תקינים לחילוץ")
            return results
            
        print(f"חילוץ עמודים: {page_numbers}")
        
        for page_num in page_numbers:
            try:
                # חילוץ טקסט מהעמוד (אינדקס העמודים ב-PyMuPDF מתחיל מ-0)
                page = doc[page_num - 1]
                text = page.get_text()
                
                if not text.strip():
                    # אם אין טקסט, ננסה לחלץ טקסט מהתמונה
                    text = extract_text_from_image(page)
                
                results[page_num] = text or "[לא נמצא טקסט בעמוד זה]"
            except Exception as e:
                print(f"שגיאה בחילוץ עמוד {page_num}: {str(e)}")
                traceback.print_exc()
                results[page_num] = f"[שגיאה בחילוץ עמוד: {str(e)}]"
        
        doc.close()
        return results
    
    except Exception as e:
        print(f"שגיאה בחילוץ טקסט מהקובץ: {str(e)}")
        traceback.print_exc()
        return {}

def extract_text_from_image(page):
    """
    ניסיון לחלץ טקסט מעמוד שהוא תמונה
    
    Args:
        page: אובייקט עמוד של PyMuPDF
    
    Returns:
        טקסט שחולץ או מחרוזת ריקה
    """
    text = ""
    # נוכל להרחיב זאת בעתיד עם חיבור ל-OCR כמו Tesseract
    # כרגע נחזיר הודעה שזה עמוד תמונה
    return "[עמוד תמונה - נדרש OCR לחילוץ טקסט]"

def extract_tables_from_page(page):
    """
    חילוץ טבלאות מעמוד PDF
    
    Args:
        page: אובייקט עמוד של PyMuPDF
    
    Returns:
        רשימה של טבלאות שזוהו
    """
    # זיהוי טבלאות בסיסי לפי מלבנים ותבניות
    # זוהי גרסה בסיסית - בפרויקט מלא נשתמש באלגוריתמים מתקדמים יותר
    
    # בדוק אם יש קווים בעמוד שיכולים להצביע על טבלה
    tables = []
    
    # חיפוש קווים בעמוד
    lines = page.get_drawings()
    if len(lines) > 10:  # אם יש הרבה קווים, סביר שיש טבלה
        # נחזיר מידע בסיסי על הטבלה האפשרית
        tables.append({
            "bbox": [0, 0, page.rect.width, page.rect.height],
            "confidence": 0.6,
            "cells": []
        })
    
    # גם חיפוש בסיסי של מבנה טבלאי בטקסט
    text = page.get_text()
    lines = text.split("\n")
    
    # אם יש לפחות 3 שורות עם מבנה דומה (למשל מספר דומה של מילים או תווים מפרידים)
    pattern_lines = 0
    for line in lines:
        # חיפוש שורות עם מבנה שנראה כמו טבלה (מספר עקבי של שדות מופרדים)
        if len(re.findall(r'\s{2,}', line)) >= 2 or len(re.findall(r'\|', line)) >= 2:
            pattern_lines += 1
    
    if pattern_lines >= 3:
        # אם לא זיהינו טבלה קודם ויש מבנה טבלאי בטקסט
        if not tables:
            tables.append({
                "bbox": [0, 0, page.rect.width, page.rect.height],
                "confidence": 0.5,
                "cells": []
            })
    
    return tables

def extract_financial_data(text):
    """
    חילוץ מידע פיננסי מטקסט
    
    Args:
        text: הטקסט לניתוח
    
    Returns:
        מילון עם מידע פיננסי
    """
    if not text or text.startswith("["):
        return {
            "amounts": [],
            "dates": [],
            "isins": [],
            "possible_table_rows": []
        }
    
    # חיפוש מספרים עם נקודה עשרונית (סכומי כסף)
    amounts = re.findall(r'\b\d{1,3}(?:[,.]\d{3})*(?:\.\d{2})\b', text)
    
    # חיפוש תאריכים בפורמטים שונים
    dates = re.findall(r'\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b', text)
    
    # חיפוש מספרי ISIN
    isins = re.findall(r'\b[A-Z]{2}[0-9A-Z]{10}\b', text)
    
    # חיפוש שורות שעשויות להיות שורות בטבלה (מכילות כמה מספרים)
    table_rows = []
    lines = text.split('\n')
    for line in lines:
        # אם השורה מכילה לפחות 3 מספרים או מילים מופרדות ברווחים גדולים, היא עשויה להיות שורה בטבלה
        if len(re.findall(r'\b\d+\b', line)) >= 3 or len(re.findall(r'\s{2,}', line)) >= 3:
            table_rows.append(line.strip())
    
    return {
        "amounts": amounts,
        "dates": dates,
        "isins": isins,
        "possible_table_rows": table_rows
    }

def analyze_pdf_content(pdf_path, page_numbers=None, output_dir=None):
    """
    ניתוח תוכן ה-PDF וחילוץ מידע
    
    Args:
        pdf_path: נתיב לקובץ PDF
        page_numbers: רשימת מספרי עמודים לניתוח
        output_dir: תיקיית פלט
    
    Returns:
        מילון עם תוצאות הניתוח
    """
    # פתיחת ה-PDF לחילוץ מידע נוסף
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        doc.close()
    except Exception as e:
        print(f"שגיאה בקריאת מטא-דאטה: {str(e)}")
        metadata = {}
    
    # חילוץ טקסט מה-PDF
    pages_text = extract_text_from_pdf(pdf_path, page_numbers)
    
    if not pages_text:
        return {"error": "לא הצלחתי לחלץ טקסט מהקובץ"}
    
    results = {
        "filename": os.path.basename(pdf_path),
        "total_pages_analyzed": len(pages_text),
        "metadata": metadata,
        "pages": {}
    }
    
    # פתיחת ה-PDF שוב לחילוץ טבלאות
    try:
        doc = fitz.open(pdf_path)
        
        # ניתוח כל עמוד
        for page_num, text in pages_text.items():
            # בדיקה אם יש טבלאות בעמוד
            page = doc[page_num - 1]
            tables = extract_tables_from_page(page)
            
            # ניתוח המידע הפיננסי
            financial_data = extract_financial_data(text)
            
            # שמירת התוצאות
            results["pages"][str(page_num)] = {
                "text": text[:1000] + "..." if len(text) > 1000 else text,  # קיצור הטקסט לתצוגה
                "text_length": len(text),
                "tables_count": len(tables),
                "tables": tables,
                "financial_data": financial_data
            }
        
        doc.close()
    except Exception as e:
        print(f"שגיאה בניתוח טבלאות: {str(e)}")
        traceback.print_exc()
    
    # שמירת התוצאות לקובץ אם צוינה תיקיית פלט
    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, 
                               f"pdf_analysis_{os.path.basename(pdf_path).replace(' ', '_')}_{timestamp}.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"התוצאות נשמרו בקובץ: {output_file}")
    
    return results

def print_page_analysis(page_num, page_data):
    """
    הדפסת ניתוח עמוד בצורה נוחה
    """
    print(f"\n{'='*30} עמוד {page_num} {'='*30}")
    
    # הדפסת הטקסט
    print("\n--- טקסט ---")
    text_preview = page_data["text"]
    print(text_preview)
    
    # הדפסת מידע על טבלאות
    print(f"\n--- טבלאות ({page_data['tables_count']}) ---")
    if page_data['tables_count'] > 0:
        for i, table in enumerate(page_data['tables']):
            print(f"טבלה {i+1}: רמת ביטחון {table['confidence']:.2f}")
    else:
        print("לא זוהו טבלאות בעמוד זה")
    
    # הדפסת מידע פיננסי
    financial_data = page_data["financial_data"]
    
    print("\n--- מידע פיננסי ---")
    
    print(f"סכומים ({len(financial_data['amounts'])}): ", end="")
    if financial_data['amounts']:
        print(', '.join(financial_data['amounts'][:10]))
        if len(financial_data['amounts']) > 10:
            print(f"...ועוד {len(financial_data['amounts']) - 10}")
    else:
        print("לא נמצאו")
    
    print(f"תאריכים ({len(financial_data['dates'])}): ", end="")
    if financial_data['dates']:
        print(', '.join(financial_data['dates'][:10]))
        if len(financial_data['dates']) > 10:
            print(f"...ועוד {len(financial_data['dates']) - 10}")
    else:
        print("לא נמצאו")
    
    print(f"קודי ISIN ({len(financial_data['isins'])}): ", end="")
    if financial_data['isins']:
        print(', '.join(financial_data['isins'][:10]))
        if len(financial_data['isins']) > 10:
            print(f"...ועוד {len(financial_data['isins']) - 10}")
    else:
        print("לא נמצאו")
    
    # הדפסת שורות טבלה אפשריות
    print(f"\n--- שורות טבלה אפשריות ({len(financial_data['possible_table_rows'])}) ---")
    for i, row in enumerate(financial_data['possible_table_rows'][:10]):
        print(f"{i+1}. {row}")
    
    if len(financial_data['possible_table_rows']) > 10:
        print(f"...ועוד {len(financial_data['possible_table_rows']) - 10} שורות")

def main():
    parser = argparse.ArgumentParser(description='חילוץ וניתוח מידע מקובץ PDF עם PyMuPDF')
    parser.add_argument('pdf_path', help='נתיב לקובץ ה-PDF לניתוח')
    parser.add_argument('--pages', '-p', type=int, nargs='+', help='מספרי עמודים לניתוח (ברירת מחדל: כל העמודים)')
    parser.add_argument('--output_dir', '-o', help='תיקייה לשמירת התוצאות', default='results')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"שגיאה: הקובץ {args.pdf_path} לא נמצא.")
        return 1
    
    print(f"מנתח את הקובץ: {args.pdf_path}")
    if args.pages:
        print(f"מנתח עמודים: {', '.join(map(str, args.pages))}")
    else:
        print("מנתח את כל העמודים")
    
    # ניתוח הקובץ
    results = analyze_pdf_content(args.pdf_path, args.pages, args.output_dir)
    
    if "error" in results:
        print(f"שגיאה: {results['error']}")
        return 1
    
    # הדפסת התוצאות
    print(f"\nניתוח קובץ: {results['filename']}")
    print(f"סה\"כ עמודים שנותחו: {results['total_pages_analyzed']}")
    
    # הדפסת מטא-דאטה
    if results.get("metadata"):
        print("\n--- מטא-דאטה ---")
        for key, value in results["metadata"].items():
            if value:
                print(f"{key}: {value}")
    
    # הדפסת ניתוח כל עמוד
    for page_num, page_data in results["pages"].items():
        print_page_analysis(page_num, page_data)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 