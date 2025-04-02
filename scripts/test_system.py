#!/usr/bin/env python3
"""
סקריפט בדיקה למערכת המשופרת

סקריפט זה בודק את תפקוד המערכת המשופרת על ידי:
1. הורדת המודלים הנדרשים אם הם לא קיימים
2. מריץ את הניתוח המלא על קובץ דוגמה
3. מציג סיכום של התוצאות שהתקבלו
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
import webbrowser

def main():
    # נתיב בסיס של הפרויקט 
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scripts_dir = os.path.join(base_dir, "scripts")
    test_docs_dir = os.path.join(base_dir, "test_documents")
    output_dir = os.path.join(base_dir, "test_results")
    
    # יצירת תיקיית פלט אם לא קיימת
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*60)
    print("בודק את מערכת ניתוח דפי חשבון בנק המשופרת")
    print("="*60)
    
    # בדיקה אם המודלים קיימים ומוריד אותם במידת הצורך
    print("\n[1/3] בודק אם המודלים הנדרשים קיימים...")
    models_dir = os.path.join(base_dir, "models")
    if not os.path.exists(models_dir) or not os.listdir(models_dir):
        print("המודלים לא נמצאו. מוריד את המודלים הנדרשים...")
        try:
            subprocess.run([sys.executable, os.path.join(scripts_dir, "download_models.py")], check=True)
        except subprocess.CalledProcessError:
            print("שגיאה בהורדת המודלים. אנא בדוק את החיבור לאינטרנט ונסה שוב.")
            sys.exit(1)
    else:
        print("המודלים קיימים במערכת.")
    
    # מציאת קובץ דוגמה לבדיקה
    print("\n[2/3] מאתר קובץ דוגמה לבדיקה...")
    sample_files = list(Path(test_docs_dir).glob("*.pdf"))
    
    if not sample_files:
        print("לא נמצאו קבצי PDF בתיקיית test_documents!")
        print("אנא הוסף קבצי דוגמה לתיקייה והרץ את הסקריפט שוב.")
        sys.exit(1)
    
    # בחירת הקובץ הראשון שנמצא
    sample_file = str(sample_files[0])
    print(f"נמצא קובץ דוגמה: {os.path.basename(sample_file)}")
    
    # הרצת הניתוח
    print("\n[3/3] מריץ ניתוח על קובץ הדוגמה...")
    print("    זה עשוי לקחת מספר דקות, בהתאם לחומרה ולגודל הקובץ...")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [
                sys.executable, 
                os.path.join(scripts_dir, "analyze_bank_statement.py"),
                sample_file,
                "--output_dir", output_dir,
                "--visualize"
            ], 
            capture_output=True,
            text=True,
            check=True
        )
        
        output_text = result.stdout
        
        # הצגת פלט ההרצה
        print("\n" + output_text)
        
    except subprocess.CalledProcessError as e:
        print(f"\nשגיאה בעיבוד הקובץ: {e}")
        print(f"פלט השגיאה: {e.stderr}")
        sys.exit(1)
    
    elapsed_time = time.time() - start_time
    
    # חיפוש קובץ ה-HTML שנוצר
    html_files = list(Path(output_dir).glob("*.html"))
    
    if html_files:
        html_report = str(html_files[0])
        print(f"\nדוח HTML נוצר: {os.path.basename(html_report)}")
        
        # פתיחת הדוח בדפדפן
        print("פותח את הדוח בדפדפן...")
        webbrowser.open(f"file://{os.path.abspath(html_report)}")
    
    # חיפוש קבצי CSV שנוצרו
    csv_files = list(Path(output_dir).glob("*.csv"))
    if csv_files:
        print(f"\nנוצרו {len(csv_files)} קבצי CSV עם נתוני הטבלאות:")
        for csv_file in csv_files:
            print(f"- {os.path.basename(csv_file)}")
    
    # סיכום
    print("\n" + "="*60)
    print(f"הניתוח הושלם בהצלחה תוך {elapsed_time:.2f} שניות")
    print(f"תוצאות הניתוח נשמרו בתיקייה: {output_dir}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main() 