# מערכת לניתוח אוטומטי של דפי חשבון בנק ומסמכים פיננסיים

מערכת מתקדמת לזיהוי, חילוץ, ועיבוד מידע פיננסי מדפי חשבון בנק ומסמכים פיננסיים אחרים. המערכת מסוגלת לזהות טבלאות, לחלץ טקסט, לזהות ניירות ערך, ולהציג את המידע באופן מובנה.

## תכונות עיקריות

* זיהוי וחילוץ טקסט אוטומטי ממסמכי PDF ותמונות של דפי בנק
* זיהוי וחילוץ טבלאות משופר עם שיטה היברידית המשלבת עיבוד תמונה ולמידה עמוקה
* זיהוי ניירות ערך ומספרי ISIN בשיטה היברידית (ביטויים רגולריים + מודל שפה)
* תמיכה בזיהוי מספרי ISIN, שמות ניירות ערך, וסיווגם
* יצירת דוחות מסכמים בפורמט HTML וייצוא נתונים בפורמט CSV
* תמיכה בשפות עברית ואנגלית
* ממשק API לשילוב עם מערכות אחרות
* מודל SaaS מוכן לפריסה בענן

## התקנה ואתחול מהיר

### אפשרות 1: הפעלה עם Docker (הדרך המומלצת)

הדרך הקלה ביותר להפעיל את המערכת היא באמצעות Docker:

```bash
# קלון של הרפוזיטורי
git clone https://github.com/aviadkim/back.git
cd back

# הוספת מפתחות API בקובץ .env
# יש לערוך את הקובץ ולהוסיף מפתחות API אמיתיים
nano .env

# הפעלת המערכת עם Docker
docker-compose up -d
```

המערכת תהיה זמינה בכתובת http://localhost:5000

### אפשרות 2: התקנה מקומית

#### דרישות מערכת
* Python 3.8 ומעלה
* Tesseract OCR עם תמיכה בעברית ואנגלית
* MongoDB

#### צעדי התקנה

1. **הורדת הקוד והתקנת סביבה וירטואלית**

```bash
# קלון של הרפוזיטורי
git clone https://github.com/aviadkim/back.git
cd back

# יצירת סביבה וירטואלית
python -m venv venv
source venv/bin/activate  # בלינוקס/מאק
# או
venv\Scripts\activate     # בחלונות
```

2. **התקנת תלויות Python**

```bash
pip install -r requirements.txt
```

3. **הגדרת קובץ .env**

```bash
# העתקת קובץ הדוגמה
cp .env.example .env
# יש לערוך את הקובץ ולהגדיר את המפתחות האישיים
```

4. **התקנת Tesseract OCR**

בחלונות:
1. הורד את הגרסה העדכנית מ [האתר הרשמי](https://github.com/UB-Mannheim/tesseract/wiki)
2. התקן עם תמיכה בשפה העברית והאנגלית
3. הוסף את נתיב ההתקנה למשתנה הסביבה PATH

בלינוקס:
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
sudo apt-get install -y tesseract-ocr-heb tesseract-ocr-eng
```

במאק:
```bash
brew install tesseract
brew install tesseract-lang
```

5. **הפעלת MongoDB**

```bash
docker-compose up -d mongodb
```

6. **יצירת תיקיות נדרשות**

```bash
mkdir -p uploads data data/embeddings data/templates logs
```

7. **הפעלת האפליקציה**

```bash
python app.py
```

האפליקציה תרוץ בכתובת: http://localhost:5000

## שימוש ב-API

### בדיקת תקינות המערכת

```bash
curl http://localhost:5000/health
```

### העלאת מסמך לעיבוד

```bash
curl -X POST -F "file=@/path/to/your/document.pdf" -F "language=he" http://localhost:5000/api/upload
```

### קבלת רשימת מסמכים מעובדים

```bash
curl http://localhost:5000/api/documents
```

### שאילת שאלות על מסמך

```bash
curl -X POST -H "Content-Type: application/json" -d '{"question":"מה סך כל ההשקעות באג\"ח?", "document_id":"document_12345.pdf"}' http://localhost:5000/api/chat
```

## הגדרת מפתחות API של Hugging Face

### יצירת מפתח SSH

1. צור מפתח SSH בטרמינל:
   ```bash
   ssh-keygen -t ed25519 -C "huggingface-key"
   ```
2. הצג את המפתח הציבורי שלך:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
3. העתק את הפלט המלא

### הוספת מפתח SSH לחשבון Hugging Face

1. היכנס ל-[הגדרות החשבון > SSH & GPG Keys](https://huggingface.co/settings/keys)
2. לחץ על "Add SSH key"
3. הזן שם למפתח (למשל "מחשב עבודה")
4. הדבק את המפתח הציבורי בשדה המתאים
5. לחץ על "Add key"

### יצירת מפתח API

1. גש ל-[הגדרות החשבון > Access Tokens](https://huggingface.co/settings/tokens)
2. לחץ על "New token"
3. תן לטוקן שם (למשל "FinancialDocAnalyzer")
4. בחר את ההרשאות הנדרשות (מומלץ: Read)
5. לחץ על "Generate a token"
6. העתק את הטוקן והוסף אותו לקובץ .env:
   ```
   HUGGINGFACE_API_KEY=YOUR_TOKEN_HERE
   ```

## פריסה כשירות SaaS בענן

המערכת כוללת קובץ `deploy.sh` שמאפשר פריסה אוטומטית לשירותי ענן שונים:

```bash
# פריסה ל-AWS (ברירת מחדל)
./deploy.sh

# פריסה ל-Google Cloud
./deploy.sh gcp

# פריסה ל-Azure
./deploy.sh azure
```

### שינויים נדרשים לסביבת ייצור

1. עדכן את קובץ `.env` עם הגדרות הייצור:
   - שנה `FLASK_ENV=production`
   - הוסף `USE_CLOUD_OCR=True` לשימוש ב-OCR בענן
   - הגדר את פרטי החיבור למסד נתונים בענן
   - הוסף מפתחות לשירותי OCR בענן (AWS, Google, Azure)

2. הגדר מדיניות אבטחה מתאימה:
   - הוסף HTTPS עם תעודה מאומתת
   - הוסף מערכת אימות משתמשים (Auth0, Cognito, וכו')
   - הגדר גישה מוגבלת ל-API

3. הגדר מערכת ניטור וניהול שגיאות:
   - התחבר לשירות כמו CloudWatch, Stackdriver
   - הגדר התראות על שגיאות משמעותיות

## פיתוח נוסף

### בדיקות אוטומטיות

הרץ את הבדיקות האוטומטיות:

```bash
pytest
```

### פיתוח תכונות חדשות

1. צור ענף חדש:
   ```bash
   git checkout -b feature/new-feature
   ```

2. פתח בקשת משיכה (Pull Request) לשילוב השינויים

## רישיון

זכויות יוצרים (c) 2025 Aviad Kim. כל הזכויות שמורות.
