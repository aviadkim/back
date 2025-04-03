import os
import logging
import uuid
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, BinaryIO
from werkzeug.utils import secure_filename
import pandas as pd

# הגדרת לוגר
logger = logging.getLogger(__name__)

# הגדרת תיקיות
UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls', 'csv', 'docx', 'doc', 'txt'}

def ensure_directories():
    """
    וידוא קיום התיקיות הנדרשות
    """
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(DATA_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(DATA_FOLDER, 'processed'), exist_ok=True)
    logger.info("Directories verified/created")

def allowed_file(filename: str) -> bool:
    """
    בדיקה אם סיומת הקובץ מותרת
    
    Args:
        filename: שם הקובץ
        
    Returns:
        bool: האם הקובץ מסוג מותר
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file: BinaryIO, original_filename: str = None) -> Tuple[str, str]:
    """
    שמירת קובץ שהועלה
    
    Args:
        file: אובייקט הקובץ
        original_filename: שם הקובץ המקורי (אופציונלי)
        
    Returns:
        Tuple[str, str]: (נתיב הקובץ, שם הקובץ החדש)
    """
    if not original_filename:
        original_filename = file.filename
    
    # יצירת שם קובץ בטוח
    filename = secure_filename(original_filename)
    
    # הוספת חותמת זמן וזיהוי ייחודי לשם הקובץ
    unique_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    basename, extension = os.path.splitext(filename)
    new_filename = f"{basename}_{timestamp}_{unique_id}{extension}"
    
    # נתיב מלא לשמירת הקובץ
    file_path = os.path.join(UPLOAD_FOLDER, new_filename)
    
    # שמירת הקובץ
    file.save(file_path)
    logger.info(f"File saved: {file_path}")
    
    return file_path, new_filename

def save_json_data(data: Dict[str, Any], filename: str = None) -> str:
    """
    שמירת נתונים כקובץ JSON
    
    Args:
        data: הנתונים לשמירה
        filename: שם הקובץ (אופציונלי)
        
    Returns:
        str: נתיב הקובץ שנשמר
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"data_{timestamp}_{unique_id}.json"
    
    file_path = os.path.join(DATA_FOLDER, 'processed', filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"JSON data saved: {file_path}")
    return file_path

def load_json_data(filename: str) -> Optional[Dict[str, Any]]:
    """
    טעינת נתונים מקובץ JSON
    
    Args:
        filename: שם הקובץ
        
    Returns:
        Dict: הנתונים שנטענו, או None אם הקובץ לא קיים
    """
    # אם ניתן רק שם הקובץ ללא נתיב, מניחים שהוא בתיקיית processed
    if not os.path.dirname(filename):
        file_path = os.path.join(DATA_FOLDER, 'processed', filename)
    else:
        file_path = filename
    
    if not os.path.exists(file_path):
        logger.warning(f"JSON file not found: {file_path}")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"JSON data loaded: {file_path}")
        return data
    except Exception as e:
        logger.error(f"Error loading JSON data: {e}")
        return None

def delete_file(file_path: str) -> bool:
    """
    מחיקת קובץ
    
    Args:
        file_path: נתיב הקובץ
        
    Returns:
        bool: האם המחיקה הצליחה
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File deleted: {file_path}")
            return True
        else:
            logger.warning(f"File not found: {file_path}")
            return False
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return False

def process_csv(file_path: str) -> Optional[List[Dict[str, Any]]]:
    """
    עיבוד קובץ CSV
    
    Args:
        file_path: נתיב הקובץ
        
    Returns:
        List[Dict]: נתוני ה-CSV, או None אם הייתה שגיאה
    """
    try:
        # ניסיון לקרוא עם קידוד UTF-8
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            # אם זה נכשל, ננסה עם קידוד ISO-8859-8 (עברית)
            df = pd.read_csv(file_path, encoding='ISO-8859-8')
        
        # המרת DataFrame לרשימת מילונים
        data = df.to_dict(orient='records')
        
        logger.info(f"CSV processed successfully: {file_path}")
        return data
    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        return None

def process_excel(file_path: str) -> Optional[Dict[str, List[Dict[str, Any]]]]:
    """
    עיבוד קובץ Excel
    
    Args:
        file_path: נתיב הקובץ
        
    Returns:
        Dict: מילון עם נתוני הגיליונות, או None אם הייתה שגיאה
    """
    try:
        # קריאת קובץ אקסל
        xls = pd.ExcelFile(file_path)
        
        # קריאת כל הגיליונות
        sheets = {}
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            sheets[sheet_name] = df.to_dict(orient='records')
        
        logger.info(f"Excel processed successfully: {file_path}")
        return sheets
    except Exception as e:
        logger.error(f"Error processing Excel: {e}")
        return None

def save_to_excel(data: List[Dict[str, Any]], filename: str = None) -> str:
    """
    שמירת נתונים לקובץ Excel
    
    Args:
        data: הנתונים לשמירה
        filename: שם הקובץ (אופציונלי)
        
    Returns:
        str: נתיב הקובץ שנשמר
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"export_{timestamp}_{unique_id}.xlsx"
    
    file_path = os.path.join(DATA_FOLDER, 'processed', filename)
    
    try:
        # המרת נתונים ל-DataFrame
        df = pd.DataFrame(data)
        
        # שמירה לקובץ Excel
        df.to_excel(file_path, index=False)
        
        logger.info(f"Data saved to Excel: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving to Excel: {e}")
        return ""

def get_file_list(directory: str = None, extensions: List[str] = None) -> List[Dict[str, Any]]:
    """
    קבלת רשימת קבצים בתיקייה
    
    Args:
        directory: התיקייה לסריקה (ברירת מחדל: תיקיית העלאות)
        extensions: סיומות קבצים לסינון (ברירת מחדל: כל הקבצים)
        
    Returns:
        List[Dict]: רשימת קבצים עם מידע
    """
    if directory is None:
        directory = UPLOAD_FOLDER
    
    if not os.path.exists(directory):
        logger.warning(f"Directory not found: {directory}")
        return []
    
    files = []
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        # אם זו תיקייה, דלג
        if os.path.isdir(file_path):
            continue
        
        # אם יש סינון סיומות וזו לא סיומת מתאימה, דלג
        if extensions and not any(filename.lower().endswith(f".{ext.lower()}") for ext in extensions):
            continue
        
        # תאריך שינוי אחרון
        mod_time = os.path.getmtime(file_path)
        mod_date = datetime.fromtimestamp(mod_time).isoformat()
        
        # גודל הקובץ
        size = os.path.getsize(file_path)
        
        files.append({
            "filename": filename,
            "path": file_path,
            "size": size,
            "modified": mod_date,
            "extension": os.path.splitext(filename)[1].lower()[1:]
        })
    
    # מיון לפי תאריך שינוי (מהחדש לישן)
    files.sort(key=lambda x: x["modified"], reverse=True)
    
    return files
