# מערכת ניתוח מסמכים פיננסיים

מערכת לניהול וניתוח מסמכים פיננסיים המבוססת על תכנון Vertical Slice Architecture.

## מבנה הפרויקט

```
/workspaces/back/
├── agent_framework/          # מסגרת הסוכנים החכמים
│   ├── coordinator.py       # מתאם בין הסוכנים השונים
│   ├── memory_agent.py      # סוכן לניהול זיכרון ושמירת מידע
│   └── __init__.py
│
├── routes/                  # ניתוב בקשות HTTP
│   ├── document_routes.py   # ניתוב לטיפול במסמכים
│   ├── langchain_routes.py  # ניתוב לפעולות AI
│   └── __init__.py
│
├── models/                  # מודלים של בסיס הנתונים
│   ├── document_models.py   # מודל למסמכים
│   └── __init__.py
│
├── services/               # שירותי עסקים
│   └── document_service.py # לוגיקה עסקית לטיפול במסמכים
│
├── utils/                  # כלי עזר
│   └── pdf_processor.py    # מעבד קבצי PDF
│
├── uploads/               # תיקיית העלאת קבצים
├── frontend/build/        # קבצי הבuild של הפרונטאנד
├── app.py                # אפליקציית Flask הראשית
├── .env                  # משתני סביבה
└── docker-compose.yml    # תצורת Docker
```

## הוראות התקנה מקומית

### 1. קלון של הרפוזיטורי והקמת סביבה וירטואלית
```bash
# קלון של הרפוזיטורי
git clone https://github.com/aviadkim/back.git
cd back

# הקמת סביבה וירטואלית
python -m venv venv
source venv/bin/activate  # בלינוקס/מאק
# או
venv\Scripts\activate     # בחלונות
```

### 2. התקנת תלויות Python
```bash
pip install -r requirements.txt
```

### 3. הגדרת משתני סביבה (.env)
הקובץ `.env` כבר קיים בפרויקט, אך נדרש למלא בו את המפתחות האישיים:

```ini
# הגדרות כלליות
FLASK_ENV=development
PORT=5000

# הגדרות API חיצוניים
HUGGINGFACE_API_KEY=your_huggingface_api_key_here  # החלף בערך שקיבלת
MISTRAL_API_KEY=your_mistral_api_key_here          # אופציונלי - רק אם משתמשים
OPENAI_API_KEY=your_openai_api_key_here            # אופציונלי - רק אם משתמשים

# הגדרות מסד נתונים
MONGO_URI=mongodb://localhost:27017/financial_documents

# הגדרות אבטחה
SECRET_KEY=your_secret_key_here  # החלף בערך רנדומלי אישי
JWT_SECRET=your_jwt_secret_here  # החלף בערך רנדומלי אישי  

# הגדרות שפה
DEFAULT_LANGUAGE=he
```

### 4. יצירת תיקיות נדרשות
```bash
mkdir -p uploads data data/embeddings data/templates logs
```

### 5. הפעלת MongoDB
```bash
docker-compose up -d
```

### 6. הפעלת השרת
```bash
python app.py
```

## פריסה ל-AWS Elastic Beanstalk

המערכת מוגדרת לפריסה אוטומטית ל-AWS Elastic Beanstalk באמצעות GitHub Actions.

### דרישות מקדימות:

1. חשבון AWS עם הרשאות ל-Elastic Beanstalk
2. מפתחות גישה ל-AWS (Access Key ID ו-Secret Access Key)

### הגדרת GitHub Secrets:

הוסף את הסודות הבאים ל-GitHub repository:

1. `AWS_ACCESS_KEY_ID`: מפתח גישה ל-AWS
2. `AWS_SECRET_ACCESS_KEY`: המפתח הסודי המשויך למפתח הגישה

### תהליך הפריסה:

1. כל דחיפה לענף `master` או `main` תפעיל את workflow הפריסה אוטומטית
2. ניתן גם להפעיל את הפריסה באופן ידני מעמוד ה-Actions בגיטהאב

### איתור היישום המפורס:

לאחר פריסה מוצלחת, ניתן לגשת ליישום בכתובת שתסופק על ידי Elastic Beanstalk.
ניתן למצוא את הכתובת מקונסול AWS Elastic Beanstalk תחת הסביבה `financial-docs-env`.

## טסטים

להרצת הטסטים:

```bash
# התקנת pytest
pip install pytest pytest-flask

# הרצת הטסטים
python -m pytest tests/
```

## מקורות נוספים

למידע נוסף ופרטים על הארכיטקטורה, ראה את הקובץ `מדריך התקנה והתקדמות למערכת ניתוח מסמכים פיננסיים.md`.
