# PDF Bank Statement Analyzer

מערכת לניתוח אוטומטי של דפי חשבון מבנקים שונים.

## תכונות מרכזיות

- זיהוי טקסט אוטומטי מדפי חשבון בנק בפורמט PDF
- זיהוי ניירות ערך וסיווגם
- הוצאת נתונים מפורטים כולל ISIN, שם, סוג, מטבע, ערך נקוב, מחיר ועוד
- תמיכה בפורמטים שונים של דפי חשבון

## התקנה

1. התקן את התלויות הנדרשות:

```bash
pip install -r requirements.txt
```

2. ודא שהתקנת Tesseract OCR במחשב שלך:
   - לWindows: ניתן להוריד מ [כאן](https://github.com/UB-Mannheim/tesseract/wiki)
   - לLinux: `sudo apt install tesseract-ocr`

3. התקן Poppler (נדרש עבור עיבוד PDF):
   - לWindows: כלול בתיקיה test_documents/poppler-23.11.0
   - לLinux: `sudo apt install poppler-utils`

## שימוש

ניתן לעבד מסמך PDF באמצעות הפקודה:

```bash
python scripts/test_document.py "path/to/your/document.pdf" [--page PAGE_NUMBER]
```

## הערות

- המערכת יכולה לעבוד גם על מחשב ללא GPU, אך עם GPU התהליך יהיה מהיר יותר
- התוצאות נשמרות בתיקיית models/ וניתן לעיין בהן לאחר העיבוד