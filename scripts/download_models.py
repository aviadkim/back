#!/usr/bin/env python3
import os
import sys
from easyocr import easyocr

def download_models():
    """הורדת מודלים של EasyOCR"""
    try:
        print("מוריד מודלים של EasyOCR...")
        # יצירת מופע של EasyOCR יוריד אוטומטית את המודלים הנדרשים
        # תמיכה בשפות: עברית, אנגלית, ערבית, רוסית, סינית מפושטת ומסורתית
        ocr = easyocr.Reader(['heb', 'eng', 'ara', 'rus', 'chi_sim', 'chi_tra'])
        print("המודלים הורדו בהצלחה!")
    except Exception as e:
        print(f"שגיאה בהורדת המודלים: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    download_models() 