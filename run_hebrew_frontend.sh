#!/bin/bash

echo "===== הרצת הפרונטאנד העשיר בעברית ====="

# הפסקת כל התהליכים הקודמים של פלאסק
echo "עוצר תהליכים קודמים..."
pkill -f "python.*app.py" || true

# משיכת שינויים חדשים מהגיט
echo "מושך שינויים חדשים מהרפוזיטורי..."
git pull

# הפיכת הסקריפטים להרצה
chmod +x fix_environment.sh
chmod +x build_frontend.sh

# הרצת סקריפט תיקון בעיות
echo "מתקן בעיות בסביבה..."
./fix_environment.sh

# הרצת סקריפט בניית פרונטאנד
echo "בונה את הפרונטאנד..."
./build_frontend.sh

# תיקון הרשאות להרצת תסריטים
chmod +x simple_app.py

# הפעלת השרת
echo "מפעיל את השרת..."
python simple_app.py
