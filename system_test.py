#!/usr/bin/env python3
"""
בדיקת מערכת מקיפה עבור מערכת FinDoc Analyzer
בודק את כל הרכיבים המרכזיים של המערכת
"""

import os
import sys
import json
import requests
import time
import platform
import subprocess
from datetime import datetime
import webbrowser

# צבעים להדפסה בטרמינל
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """מדפיס כותרת בצבע כחול"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 50}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(50)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 50}{Colors.END}\n")

def print_success(text):
    """מדפיס הודעת הצלחה בצבע ירוק"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    """מדפיס הודעת שגיאה בצבע אדום"""
    print(f"{Colors.FAIL}✗ {text}{Colors.END}")

def print_warning(text):
    """מדפיס אזהרה בצבע צהוב"""
    print(f"{Colors.WARNING}! {text}{Colors.END}")

def print_info(text):
    """מדפיס מידע בצבע רגיל"""
    print(f"  {text}")

def test_server_connection(url="http://localhost:5000"):
    """בודק אם השרת פועל"""
    print_header("בדיקת חיבור לשרת")
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"השרת פועל: {data.get('message', 'OK')}")
            return True
        else:
            print_error(f"קוד תגובה לא צפוי: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"לא ניתן להתחבר לשרת: {e}")
        print_info("האם השרת פועל? נסה להריץ: ./run_hebrew_frontend.sh")
        return False

def test_frontend(url="http://localhost:5000"):
    """בודק אם הפרונטאנד נטען"""
    print_header("בדיקת טעינת הפרונטאנד")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            if "FinDoc Analyzer" in response.text:
                print_success("הפרונטאנד נטען בהצלחה")
                return True
            else:
                print_warning("הפרונטאנד נטען אך התוכן לא נראה כמצופה")
                return True
        else:
            print_error(f"קוד תגובה לא צפוי בטעינת הפרונטאנד: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"שגיאה בטעינת הפרונטאנד: {e}")
        return False

def test_file_upload(url="http://localhost:5000", test_file=None):
    """בודק את יכולת העלאת הקבצים"""
    print_header("בדיקת העלאת קבצים")
    
    # יצירת קובץ בדיקה אם לא סופק
    if not test_file:
        test_file = "test_document.txt"
        with open(test_file, "w") as f:
            f.write("זהו קובץ בדיקה עבור מערכת ניתוח מסמכים.\n")
            f.write("אחת שתיים שלוש ארבע חמש.\n")
            f.write("1234567890\n")
        print_info(f"נוצר קובץ בדיקה: {test_file}")
    
    try:
        files = {'file': open(test_file, 'rb')}
        data = {'language': 'he'}
        
        response = requests.post(f"{url}/api/upload", files=files, data=data)
        
        if response.status_code in [200, 201]:
            result = response.json()
            print_success(f"העלאת הקובץ הצליחה: {result.get('message', 'OK')}")
            doc_id = result.get('document_id')
            if doc_id:
                print_info(f"מזהה מסמך: {doc_id}")
            return True
        else:
            print_error(f"שגיאה בהעלאת הקובץ: {response.status_code}")
            print_info(response.text)
            return False
    except Exception as e:
        print_error(f"שגיאה בהעלאת הקובץ: {e}")
        return False

def test_chatbot(url="http://localhost:5000"):
    """בודק את פונקציונליות הצ'אטבוט"""
    print_header("בדיקת הצ'אטבוט")
    
    try:
        # יצירת סשן חדש
        session_response = requests.post(
            f"{url}/api/chat/session",
            json={"user_id": "test_user"}
        )
        
        if session_response.status_code != 200:
            print_error(f"שגיאה ביצירת סשן צ'אט: {session_response.status_code}")
            return False
            
        session_data = session_response.json()
        session_id = session_data.get("session_id")
        
        if not session_id:
            print_error("לא התקבל מזהה סשן")
            return False
            
        print_success(f"נוצר סשן צ'אט: {session_id}")
        
        # שליחת שאלה
        query_response = requests.post(
            f"{url}/api/chat/query",
            json={"session_id": session_id, "query": "מהם מספרי ה-ISIN במסמך?"}
        )
        
        if query_response.status_code != 200:
            print_error(f"שגיאה בשליחת שאלה: {query_response.status_code}")
            return False
            
        query_data = query_response.json()
        answer = query_data.get("answer")
        
        if answer:
            print_success("התקבלה תשובה מהצ'אטבוט")
            print_info(f"שאלה: מהם מספרי ה-ISIN במסמך?")
            print_info(f"תשובה: {answer}")
            return True
        else:
            print_warning("התקבלה תשובה ריקה מהצ'אטבוט")
            return False
            
    except Exception as e:
        print_error(f"שגיאה בבדיקת הצ'אטבוט: {e}")
        return False

def test_documents_list(url="http://localhost:5000"):
    """בודק את יכולת הצגת רשימת המסמכים"""
    print_header("בדיקת רשימת מסמכים")
    
    try:
        response = requests.get(f"{url}/api/documents")
        
        if response.status_code != 200:
            print_error(f"שגיאה בקבלת רשימת מסמכים: {response.status_code}")
            return False
            
        documents = response.json()
        
        if isinstance(documents, list):
            print_success(f"התקבלה רשימת מסמכים. מספר מסמכים: {len(documents)}")
            if documents:
                print_info("מסמכים שהתקבלו:")
                for i, doc in enumerate(documents[:3], 1):  # הצג עד 3 מסמכים
                    print_info(f"  {i}. {doc.get('filename', 'ללא שם')} ({doc.get('id', 'ללא מזהה')})")
                if len(documents) > 3:
                    print_info(f"  ... ועוד {len(documents) - 3} מסמכים")
            return True
        else:
            print_error("תשובה לא צפויה מהשרת (לא רשימה)")
            return False
            
    except Exception as e:
        print_error(f"שגיאה בקבלת רשימת מסמכים: {e}")
        return False

def check_environment():
    """בודק את סביבת ההפעלה"""
    print_header("בדיקת סביבת הפעלה")
    
    # בדיקת מערכת הפעלה
    print_info(f"מערכת הפעלה: {platform.system()} {platform.release()}")
    
    # בדיקת גרסת Python
    print_info(f"גרסת Python: {platform.python_version()}")
    
    # בדיקת תיקיות נדרשות
    required_dirs = ['frontend', 'uploads', 'features', 'agent_framework']
    for dir_name in required_dirs:
        if os.path.isdir(dir_name):
            print_success(f"תיקייה {dir_name} קיימת")
        else:
            print_warning(f"תיקייה {dir_name} לא קיימת")
            
    # בדיקת קבצים חשובים
    important_files = ['simple_app.py', 'run_hebrew_frontend.sh', 'fix_environment.sh', 'build_frontend.sh']
    for file_name in important_files:
        if os.path.isfile(file_name):
            print_success(f"קובץ {file_name} קיים")
        else:
            print_warning(f"קובץ {file_name} לא קיים")
    
    # בדיקת Docker
    try:
        docker_result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if docker_result.returncode == 0:
            print_success(f"Docker מותקן: {docker_result.stdout.strip()}")
        else:
            print_warning("Docker לא מותקן או לא פועל")
    except:
        print_warning("אין גישה ל-Docker")
        
    # בדיקת MongoDB
    try:
        mongo_result = subprocess.run(['docker', 'ps', '-f', 'name=mongo'], capture_output=True, text=True)
        if "mongo" in mongo_result.stdout:
            print_success("MongoDB פועל")
        else:
            print_warning("MongoDB לא פועל")
    except:
        print_warning("לא ניתן לבדוק את סטטוס MongoDB")
        
    return True

def open_ui(url="http://localhost:5000"):
    """פותח את ממשק המשתמש בדפדפן"""
    print_header("פתיחת ממשק המשתמש")
    try:
        print_info(f"פותח דפדפן בכתובת: {url}")
        webbrowser.open(url)
        print_success("הדפדפן נפתח בהצלחה")
    except Exception as e:
        print_error(f"שגיאה בפתיחת הדפדפן: {e}")
        
def run_all_tests():
    """מריץ את כל הבדיקות"""
    print_header("בדיקת מערכת כוללת לפרויקט FinDoc Analyzer")
    print_info(f"תאריך בדיקה: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # בדיקת סביבה
    env_success = check_environment()
    
    # בדיקת חיבור לשרת
    server_success = test_server_connection()
    if not server_success:
        answer = input("האם להמשיך בבדיקות למרות שהשרת לא פועל? (כ/ל): ")
        if answer.lower() not in ["כ", "כן", "y", "yes"]:
            return
    
    # בדיקת הפרונטאנד
    if server_success:
        frontend_success = test_frontend()
    else:
        frontend_success = False
        print_warning("דילוג על בדיקת הפרונטאנד כי השרת לא פועל")
    
    # בדיקת יכולות API
    if server_success:
        # בדיקת העלאת קבצים
        upload_success = test_file_upload()
        
        # בדיקת רשימת מסמכים
        documents_success = test_documents_list()
        
        # בדיקת צ'אטבוט
        chatbot_success = test_chatbot()
    else:
        upload_success = documents_success = chatbot_success = False
        print_warning("דילוג על בדיקות API כי השרת לא פועל")
    
    # סיכום
    print_header("סיכום תוצאות הבדיקה")
    
    results = {
        "סביבה": env_success,
        "חיבור לשרת": server_success,
        "פרונטאנד": frontend_success,
        "העלאת קבצים": upload_success,
        "רשימת מסמכים": documents_success,
        "צ'אטבוט": chatbot_success
    }
    
    for test_name, result in results.items():
        if result is True:
            print_success(f"{test_name}: תקין")
        elif result is False:
            print_error(f"{test_name}: נכשל")
        else:
            print_warning(f"{test_name}: לא נבדק")
    
    # פתיחת הממשק בדפדפן
    if server_success and frontend_success:
        answer = input("\nהאם לפתוח את ממשק המשתמש בדפדפן? (כ/ל): ")
        if answer.lower() in ["כ", "כן", "y", "yes"]:
            open_ui()
    
    print_header("בדיקת המערכת הושלמה")

if __name__ == "__main__":
    run_all_tests()
