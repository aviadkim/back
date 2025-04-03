#!/bin/bash
# בדיקה מהירה של התיקון
echo "===== מתחיל בדיקה מהירה ====="
python test_quick_extraction.py

# אם הבדיקה המהירה עוברת, נריץ את הבדיקה המלאה
if [ $? -eq 0 ]; then
  echo -e "\n\n===== הבדיקה המהירה עברה בהצלחה, מריץ בדיקה מלאה... ====="
  echo -e "\n----- בדיקת קובץ התוצאה -----"
  python test_extraction_fix.py
  
  echo -e "\n----- בדיקת שלמות המערכת -----"
  python run_verification_tests.py
  
  if [ $? -eq 0 ]; then
    echo -e "\n✅ כל הבדיקות עברו בהצלחה! ניתן לאשר את התיקון."
  else
    echo -e "\n❌ חלק מהבדיקות נכשלו. נדרש לבדוק את הבעיות."
  fi
else
  echo -e "\n❌ הבדיקה המהירה נכשלה, יש לבדוק את הבעיה לפני המשך."
fi
