#!/bin/bash
# סקריפט אתחול והתקנה למערכת ניתוח מסמכים פיננסיים
# =========================================================

# צבעים להודעות
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}      אתחול מערכת ניתוח מסמכים פיננסיים      ${NC}"
echo -e "${BLUE}======================================================${NC}"

# בדיקת דרישות מקדימות
echo -e "\n${BLUE}בודק דרישות מקדימות...${NC}"

# בדיקת Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✅ Python 3 מותקן${NC}"
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        echo -e "${GREEN}✅ Python 3 מותקן (כ-'python')${NC}"
        PYTHON_CMD=python
    else
        echo -e "${RED}❌ Python 3 לא נמצא. אנא התקן Python 3.8 או גרסה חדשה יותר${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Python לא נמצא. אנא התקן Python 3.8 או גרסה חדשה יותר${NC}"
    exit 1
fi

# בדיקת Docker
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker מותקן${NC}"
else
    echo -e "${YELLOW}⚠️ Docker לא נמצא. מומלץ להתקין Docker להפעלת MongoDB וליצירת סביבת SaaS${NC}"
    echo -e "   הורד מכאן: https://www.docker.com/products/docker-desktop/"
fi

# בדיקת pip
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✅ pip מותקן${NC}"
    PIP_CMD=pip3
elif command -v pip &> /dev/null; then
    echo -e "${GREEN}✅ pip מותקן${NC}"
    PIP_CMD=pip
else
    echo -e "${RED}❌ pip לא נמצא. אנא התקן pip${NC}"
    exit 1
fi

# בדיקת יצירת סביבה וירטואלית
echo -e "\n${BLUE}הקמת סביבה וירטואלית...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠️ תיקיית סביבה וירטואלית קיימת. משתמש בה${NC}"
else
    $PYTHON_CMD -m venv venv
    echo -e "${GREEN}✅ סביבה וירטואלית נוצרה בהצלחה${NC}"
fi

# הפעלת הסביבה הוירטואלית
echo -e "\n${BLUE}מפעיל את הסביבה הוירטואלית...${NC}"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    . venv/Scripts/activate
else
    # Linux / Mac
    . venv/bin/activate
fi
echo -e "${GREEN}✅ סביבה וירטואלית הופעלה${NC}"

# התקנת חבילות Python
echo -e "\n${BLUE}מתקין חבילות Python הנדרשות...${NC}"
$PIP_CMD install -r requirements.txt
echo -e "${GREEN}✅ החבילות הותקנו בהצלחה${NC}"

# בדיקת קובץ .env
echo -e "\n${BLUE}בודק קובץ הגדרות סביבה (.env)...${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ קובץ .env קיים${NC}"
else
    echo -e "${YELLOW}⚠️ קובץ .env לא נמצא. יוצר קובץ ברירת מחדל מתוך .env.example${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ קובץ .env נוצר מקובץ הדוגמה${NC}"
    else
        echo -e "${YELLOW}⚠️ לא נמצא קובץ .env.example. יוצר קובץ .env בסיסי${NC}"
        cat > .env << 'EOL'
# הגדרות כלליות
FLASK_ENV=development
PORT=5000

# הגדרות API חיצוניים
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# הגדרות מסד נתונים
MONGO_URI=mongodb://localhost:27017/financial_documents

# הגדרות אבטחה
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here

# הגדרות שפה
DEFAULT_LANGUAGE=he
EOL
        echo -e "${GREEN}✅ קובץ .env בסיסי נוצר${NC}"
    fi
    echo -e "${YELLOW}⚠️ אנא ערוך את קובץ .env והוסף את המפתחות האישיים שלך${NC}"
fi

# יצירת תיקיות נדרשות
echo -e "\n${BLUE}יוצר תיקיות נדרשות...${NC}"
mkdir -p uploads data data/embeddings data/templates logs
echo -e "${GREEN}✅ התיקיות נוצרו בהצלחה${NC}"

# בדיקת Tesseract OCR
echo -e "\n${BLUE}בודק התקנת Tesseract OCR...${NC}"
if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n 1)
    echo -e "${GREEN}✅ Tesseract OCR מותקן: $TESSERACT_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️ Tesseract OCR לא נמצא${NC}"
    echo -e "   מומלץ להתקין Tesseract OCR עם תמיכה בעברית ואנגלית"
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo -e "   הורד מכאן: https://github.com/UB-Mannheim/tesseract/wiki"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "   להתקנה במאק: brew install tesseract tesseract-lang"
    else
        echo -e "   להתקנה בלינוקס: sudo apt-get install tesseract-ocr tesseract-ocr-heb tesseract-ocr-eng"
    fi
    
    echo -e "${YELLOW}⚠️ המערכת תנסה להשתמש בשירותי OCR בענן אם הוגדרו${NC}"
fi

# הפעלת MongoDB באמצעות Docker
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo -e "\n${BLUE}מפעיל MongoDB באמצעות Docker...${NC}"
    
    # בדיקה אם MongoDB כבר רץ
    if docker ps --format '{{.Names}}' | grep -q "mongodb"; then
        echo -e "${GREEN}✅ MongoDB כבר רץ${NC}"
    else
        docker-compose up -d mongodb
        echo -e "${GREEN}✅ MongoDB הופעל בהצלחה${NC}"
    fi
else
    echo -e "\n${YELLOW}⚠️ Docker או docker-compose לא נמצאו, לא ניתן להפעיל MongoDB אוטומטית${NC}"
    echo -e "   וודא שיש לך גישה למסד נתונים MongoDB כפי שהוגדר בקובץ .env"
fi

# בדיקת חיבור ל-MongoDB
echo -e "\n${BLUE}בודק חיבור ל-MongoDB...${NC}"
$PYTHON_CMD -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

try:
    mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/financial_documents')
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    client.server_info()
    print('\033[0;32m✅ חיבור ל-MongoDB הצליח\033[0m')
except Exception as e:
    print(f'\033[0;31m❌ שגיאה בחיבור ל-MongoDB: {e}\033[0m')
    print('\033[0;33m⚠️ אנא וודא שמסד הנתונים פעיל ושהגדרות החיבור ב-.env נכונות\033[0m')
"

# בדיקת חיבור ל-Hugging Face
echo -e "\n${BLUE}בודק חיבור ל-Hugging Face API...${NC}"
$PYTHON_CMD test_huggingface.py

echo -e "\n${GREEN}=====================================================${NC}"
echo -e "${GREEN}    האתחול הושלם! המערכת מוכנה לשימוש    ${NC}"
echo -e "${GREEN}=====================================================${NC}"
echo -e "\nלהפעלת המערכת הרץ:"
echo -e "${BLUE}python app.py${NC}"
echo -e "\nהמערכת תיהיה זמינה בכתובת: http://localhost:5000"
echo -e "\nלפריסה בענן הרץ:"
echo -e "${BLUE}./deploy.sh [aws|gcp|azure]${NC}"

# הוספת הרשאות הרצה לסקריפטים
chmod +x deploy.sh

echo -e "\n${BLUE}תודה שבחרת להשתמש במערכת שלנו!${NC}"