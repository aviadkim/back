# מערכת לניתוח אוטומטי של דפי חשבון בנק ומסמכים פיננסיים

מערכת מתקדמת לזיהוי, חילוץ, ועיבוד מידע פיננסי מדפי חשבון בנק ומסמכים פיננסיים אחרים. המערכת מסוגלת לזהות טבלאות, לחלץ טקסט, לזהות ניירות ערך, ולהציג את המידע באופן מובנה.

## תכונות עיקריות

* זיהוי וחילוץ טקסט אוטומטי ממסמכי PDF ותמונות של דפי בנק
* זיהוי וחילוץ טבלאות משופר עם שיטה היברידית המשלבת עיבוד תמונה ולמידה עמוקה
* זיהוי ניירות ערך ומספרי ISIN בשיטה היברידית (ביטויים רגולריים + מודל שפה)
* תמיכה בזיהוי מספרי ISIN, שמות ניירות ערך, וסיווגם
* יצירת דוחות מסכמים בפורמט HTML וייצוא נתונים בפורמט CSV
* תמיכה בשפות עברית ואנגלית

## התקנה

### דרישות מערכת

* Python 3.8 ומעלה
* Tesseract OCR
* Poppler (להמרת PDF לתמונות)

### התקנת החבילות הדרושות

התקנת הדרישות מקובץ requirements.txt:

```bash
pip install -r requirements.txt
```

### התקנת Tesseract OCR

#### Windows
1. הורידו את הגרסה העדכנית מ [האתר הרשמי](https://github.com/UB-Mannheim/tesseract/wiki)
2. התקינו עם תמיכה בשפה העברית והאנגלית
3. הוסיפו את נתיב ההתקנה למשתנה הסביבה PATH

#### Linux
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-heb tesseract-ocr-eng
```

### התקנת Poppler (להמרת PDF)

#### Windows
קבצי Poppler כבר כלולים בספריית `test_documents/poppler-23.11.0` בפרויקט.

#### Linux
```bash
sudo apt-get install poppler-utils
```

## שימוש בגרסה המשופרת

### מנתח דפי בנק מתקדם

הסקריפט `scripts/analyze_bank_statement.py` משמש לניתוח מלא של דפי חשבון בנק עם כל השיפורים:

```bash
python scripts/analyze_bank_statement.py <נתיב_לקובץ> --output_dir output --visualize
```

פרמטרים:
* `נתיב_לקובץ` - הנתיב לקובץ ה-PDF או התמונה של דף החשבון
* `--output_dir` או `-o` - תיקיית הפלט (ברירת מחדל: "output")
* `--page` או `-p` - מספר עמוד ספציפי לניתוח (אופציונלי)
* `--visualize` או `-v` - ליצירת ויזואליזציה של הטבלאות שזוהו
* `--poppler_path` - נתיב מותאם אישית ל-Poppler (אופציונלי)

### חילוץ טבלאות משופר

ניתן להשתמש בסקריפט `scripts/improved_table_extraction.py` לחילוץ טבלאות בלבד:

```bash
python scripts/improved_table_extraction.py <נתיב_לתמונה> [תיקיית_פלט]
```

### זיהוי ניירות ערך משופר

ניתן להשתמש בסקריפט `scripts/improved_securities_extraction.py` לזיהוי ניירות ערך בלבד:

```bash
python scripts/improved_securities_extraction.py <נתיב_לתמונה | נתיב_לטקסט> [נתיב_פלט]
```

## השיפורים שהוטמעו

### שיפור בזיהוי טבלאות
- שימוש במודל TableTransformer לזיהוי טבלאות עם דיוק גבוה
- גישה היברידית המשלבת עיבוד תמונה קלאסי עם למידה עמוקה
- שיפור בחילוץ תוכן הטבלאות ומבנה הנתונים

### שיפור בזיהוי ניירות ערך
- שימוש במודל TinyLlama חינמי לזיהוי מידע על ניירות ערך
- גישה היברידית המשלבת ביטויים רגולריים עם מודל שפה
- חילוץ מידע מפורט יותר על ניירות ערך (סוג, מטבע, ערך, תאריך)

### תוצרי פלט משופרים
- דוחות HTML מפורטים עם המידע שזוהה
- קבצי CSV עם תוכן הטבלאות שזוהו
- ויזואליזציה של הטבלאות שזוהו על גבי המסמך המקורי

## הערות

* המערכת פועלת ללא צורך ב-GPU, אך ביצועים טובים יותר מושגים עם GPU
* המודלים יורדים אוטומטית בפעם הראשונה שהם נדרשים (כ-600MB לכל המודלים)
* הניתוח של עמוד אחד עשוי לקחת כ-30-60 שניות, תלוי בחומרה ובמורכבות המסמך

## דוגמה לדוח פלט

הרצה של הניתוח המתקדם יוצרת דוח HTML עם:
- פרטי חשבון שזוהו
- ניירות ערך שזוהו ומידע עליהם
- טבלאות שזוהו עם התוכן המלא שלהן
- תאריכים וסכומים שזוהו במסמך