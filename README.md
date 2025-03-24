# מערכת ניתוח מסמכים פיננסיים

מערכת לניתוח מסמכים פיננסיים בעברית ושפות אחרות באמצעות בינה מלאכותית. המערכת מאפשרת העלאת קבצי PDF, Excel וקבצי CSV, ומספקת ממשק צ'אט חכם לשאילת שאלות אודות המסמכים.

## תכונות עיקריות

- **ניתוח מסמכים**: תמיכה בקבצי PDF, Excel ו-CSV
- **תמיכה רב-לשונית**: עברית, אנגלית ושפות נוספות
- **OCR מובנה**: עם תמיכה בשפה העברית
- **צ'אט מבוסס AI**: אינטראקציה טבעית עם המסמכים
- **ממשק משתמש חדשני**: עיצוב אינטואיטיבי ומגיב
- **כלי אבחון**: לזיהוי וטיפול בתקלות במערכת

## התקנה מקומית

### דרישות מערכת

- Python 3.9 או גרסה חדשה יותר
- MongoDB
- Tesseract OCR עם תמיכה בעברית
- poppler-utils (לעיבוד קבצי PDF)

### הוראות התקנה

1. שיבוט המאגר:
   ```bash
   git clone https://github.com/aviadkim/back.git
   cd back
   ```

2. יצירת סביבה וירטואלית:
   ```bash
   python -m venv venv
   source venv/bin/activate  # לינוקס/מק
   # או
   venv\Scripts\activate     # חלונות
   ```

3. התקנת תלויות:
   ```bash
   pip install -r requirements.txt
   ```

4. התקנת Tesseract OCR:
   - **לינוקס**: `sudo apt-get install tesseract-ocr tesseract-ocr-heb poppler-utils`
   - **מק**: `brew install tesseract tesseract-lang poppler`
   - **חלונות**: הורד והתקן מ-[UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

5. הגדרת משתני סביבה:
   - העתק את הקובץ `.env.sample` לקובץ `.env` ומלא את הערכים הנדרשים.

6. הפעלת השרת:
   ```bash
   python app.py
   ```

7. גישה לאפליקציה:
   - פתח דפדפן בכתובת: `http://localhost:5000`

## הפעלה בענן (Render)

1. הירשם ל-[Render](https://render.com/) וחבר את חשבון ה-GitHub שלך
2. צור שירות חדש וקשר אותו למאגר `aviadkim/back`
3. הגדר את השירות:
   - **סוג**: Web Service
   - **תבנית ייצור**: Docker
   - **ענף**: master
   - **משתני סביבה**: הגדר את המשתנים מקובץ `.env.sample`
   - **תכנית אחסון**: הוסף נפח אחסון למסמכים

4. לחץ "Deploy" והמתן לסיום התהליך
5. גש לכתובת ה-URL שתוצג לאחר ההפעלה

## אבחון בעיות

המערכת כוללת כלי אבחון מובנה לזיהוי בעיות בעיבוד קבצי PDF:

1. גש לכתובת `/test` במערכת שלך (לדוגמה, `http://localhost:5000/test` או `https://your-app.onrender.com/test`)
2. לחץ על כפתור "אבחון מערכת PDF"
3. הפעל את הבדיקה באמצעות לחיצה על כפתור "הפעל בדיקה"
4. בדוק את הבעיות המוצגות ופתור אותן לפי ההמלצות

## רישיון

זכויות יוצרים © 2025
