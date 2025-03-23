# מערכת ניתוח מסמכים פיננסיים - גרסה 2.1

מערכת AI מתקדמת לניתוח מסמכים פיננסיים, המאפשרת העלאת מסמכים וצ'אט אינטראקטיבי איתם.

## תכונות עיקריות

- 📄 עיבוד מסמכי PDF, Excel ו-CSV עם תמיכה משופרת
- 🔍 חילוץ טקסט מ-PDF באמצעות OCR מתקדם רב-שפתי
- 💬 צ'אטבוט AI משופר לשאלות ותשובות על המסמכים
- 📊 זיהוי וחילוץ מדויק יותר של טבלאות ממסמכים
- 📱 ממשק משתמש רספונסיבי בעברית עם תצוגה משופרת

## התקנה מהירה

### דרישות מקדימות

- Python 3.8 או גרסה חדשה יותר
- Docker (למסד נתונים MongoDB)
- Tesseract OCR (לשיפור חילוץ טקסט)

### שלבים להתקנה

1. שכפול המאגר והתקנת סביבה וירטואלית:

```bash
git clone https://github.com/aviadkim/back.git
cd back
python -m venv venv
source venv/bin/activate  # Linux/Mac
# או
venv\Scripts\activate     # Windows
```

2. התקנת תלויות:

```bash
pip install -r requirements.txt
```

3. עריכת קובץ `.env` עם הגדרות מתאימות:

```
# הגדרות API חיצוניים
HUGGINGFACE_API_KEY=your_key_here  # החלף במפתח שלך להשתמש ב-AI אמיתי
```

4. הרצת סקריפט האתחול:

```bash
python start.py
```

הסקריפט ידאג:
- ליצירת כל התיקיות הנדרשות
- לאימות הגדרות הסביבה
- להפעלת MongoDB
- להרצת בדיקות
- להפעלת השרת

## שימוש במערכת

לאחר הפעלת השרת, גש לכתובת: http://localhost:5000

המערכת כוללת שלושה חלקים עיקריים:
1. **אזור העלאת מסמכים** - להעלאת קבצי PDF, Excel או CSV חדשים
2. **רשימת מסמכים** - הצגת המסמכים שהועלו ואפשרויות לצפייה ומחיקה
3. **צ'אטבוט משופר** - לשאילת שאלות על המסמכים שהועלו

## תמיכה ב-OCR משופר

המערכת כוללת תמיכה משופרת בחילוץ טקסט אוטומטי (OCR) ממסמכי PDF סרוקים, כולל:
- זיהוי טקסט משופר בעברית
- תמיכה ברב-שפתיות
- ביצועים משופרים

### התקנת Tesseract OCR

**Windows:**
1. הורד והתקן מ: https://github.com/UB-Mannheim/tesseract/wiki
2. הוסף לנתיב המערכת (PATH)
3. וודא שהתקנת את חבילות השפה העברית והאנגלית

**Linux:**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-heb tesseract-ocr-eng
```

**Mac:**
```bash
brew install tesseract
brew install tesseract-lang
```

## חידושים בגרסה 2.1

גרסה 2.1 מביאה מספר שיפורים משמעותיים:

1. **ממשק צ'אטבוט משופר**
   - נראות משופרת בכל הרזולוציות
   - טיפול טוב יותר בהיסטוריית שיחה
   - תצוגה משופרת של תשובות ומקורות

2. **OCR מתקדם יותר**
   - תמיכה טובה יותר בעברית
   - שיפור יכולת זיהוי טבלאות
   - מהירות עיבוד משופרת

3. **ניהול מפתחות API משופר**
   - אבטחה טובה יותר של מפתחות
   - טיפול חכם יותר בשגיאות תקשורת
   - תמיכה במספר ספקי AI

4. **ביצועים משופרים**
   - טעינה מהירה יותר של מסמכים
   - חיפוש מהיר יותר במסמכים
   - צריכת משאבים נמוכה יותר

למידע מפורט על השינויים בגרסה 2.1, ראה את [תיעוד הגרסה](VERSION.md).

## פיתוח נוסף

כדי להוסיף תכונות או לתרום למערכת:

1. צור ענף (branch) חדש עבור התכונה שלך
2. פתח בקשת משיכה (pull request) עם הסברים על השינויים שביצעת
3. וודא שכל הבדיקות עוברות

## פתרון בעיות נפוצות

### הצ'אטבוט לא מופיע
- וודא שנקודת הקצה `/api/health` מחזירה תשובה תקינה
- בדוק את קונסולת הדפדפן לשגיאות JavaScript

### מודל ה-AI מחזיר רק "תשובות דמה"
- וודא שיש לך מפתח Hugging Face API תקף בקובץ `.env`
- בדוק את הלוגים ב-`logs/app.log` לשגיאות אתחול מודל

### שגיאת OCR
- וודא שהתקנת Tesseract OCR כראוי
- בדוק שהנתיב ל-Tesseract נכון והוא זמין בסביבת המערכת

## יצירת קשר ותמיכה

לשאלות, תמיכה או דיווח על באגים, אנא צור [issue חדש](https://github.com/aviadkim/back/issues) או פנה ישירות למפתחים.
