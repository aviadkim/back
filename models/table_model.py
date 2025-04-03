import pandas as pd
from typing import List, Dict, Any, Optional
import json
import os
import logging

# הגדרת לוגר
logger = logging.getLogger(__name__)

class TableModel:
    """
    מודל לניהול טבלאות מיובאות ממסמכים פיננסיים
    """
    
    def __init__(self, name: str, headers: List[str], data: List[List[Any]], metadata: Optional[Dict[str, Any]] = None):
        """
        אתחול מודל טבלה
        
        Args:
            name: שם הטבלה
            headers: כותרות העמודות בטבלה
            data: נתוני הטבלה (רשימה של רשימות)
            metadata: מטה-דאטה נוסף על הטבלה (אופציונלי)
        """
        self.name = name
        self.headers = headers
        self.data = data
        self.metadata = metadata or {}
        
        # המרה ל-DataFrame של פנדס
        self.df = pd.DataFrame(data, columns=headers)
    
    @classmethod
    def from_dict(cls, table_dict: Dict[str, Any]) -> 'TableModel':
        """
        יצירת מודל טבלה מתוך מילון
        
        Args:
            table_dict: מילון עם נתוני הטבלה
            
        Returns:
            TableModel: מודל טבלה
        """
        name = table_dict.get('name', 'Unnamed Table')
        headers = table_dict.get('headers', [])
        data = table_dict.get('data', [])
        metadata = table_dict.get('metadata', {})
        
        return cls(name, headers, data, metadata)
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, name: str = 'Unnamed Table', metadata: Optional[Dict[str, Any]] = None) -> 'TableModel':
        """
        יצירת מודל טבלה מתוך DataFrame של פנדס
        
        Args:
            df: DataFrame של פנדס
            name: שם הטבלה
            metadata: מטה-דאטה נוסף על הטבלה (אופציונלי)
            
        Returns:
            TableModel: מודל טבלה
        """
        headers = df.columns.tolist()
        data = df.values.tolist()
        
        return cls(name, headers, data, metadata)
    
    @classmethod
    def from_pdf_table(cls, table_data: Dict[str, Any], index: int = 0) -> 'TableModel':
        """
        יצירת מודל טבלה מתוך נתוני טבלה שחולצו מקובץ PDF
        
        Args:
            table_data: נתוני טבלה שחולצו מ-PDF
            index: אינדקס הטבלה
            
        Returns:
            TableModel: מודל טבלה
        """
        try:
            name = f"Table_{index}"
            
            # ניסיון לחלץ שורות מהטבלה
            rows = table_data.get('rows', [])
            
            if rows:
                # הנחה: השורה הראשונה היא הכותרות
                headers = rows[0].split() if len(rows) > 0 else []
                
                # שאר השורות הן הנתונים
                data = [row.split() for row in rows[1:]]
                
                # מידע נוסף על הטבלה
                metadata = {
                    'source': 'pdf',
                    'page': table_data.get('page', 0),
                    'content': table_data.get('content', '')
                }
                
                return cls(name, headers, data, metadata)
            else:
                # אם אין שורות מוגדרות, ננסה להשתמש בתוכן הגולמי
                content = table_data.get('content', '')
                content_lines = content.strip().split('\n')
                
                if content_lines:
                    headers = content_lines[0].split() if len(content_lines) > 0 else []
                    data = [line.split() for line in content_lines[1:] if line.strip()]
                    
                    metadata = {
                        'source': 'pdf',
                        'page': table_data.get('page', 0),
                        'content': content
                    }
                    
                    return cls(name, headers, data, metadata)
                else:
                    # אם אין מספיק מידע, נחזיר טבלה ריקה
                    return cls(name, [], [], {'source': 'pdf', 'error': 'No data extracted'})
        
        except Exception as e:
            logger.error(f"Error creating table model from PDF table: {e}")
            # נחזיר טבלה ריקה עם מידע על השגיאה
            return cls(f"Table_{index}", [], [], {'source': 'pdf', 'error': str(e)})
    
    def to_dict(self) -> Dict[str, Any]:
        """
        המרת מודל הטבלה למילון
        
        Returns:
            Dict: מילון עם נתוני הטבלה
        """
        return {
            'name': self.name,
            'headers': self.headers,
            'data': self.data,
            'metadata': self.metadata
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        המרת מודל הטבלה ל-DataFrame של פנדס
        
        Returns:
            pd.DataFrame: DataFrame של פנדס
        """
        return self.df
    
    def to_excel(self, filepath: str) -> None:
        """
        ייצוא מודל הטבלה לקובץ אקסל
        
        Args:
            filepath: נתיב לקובץ אקסל
        """
        self.df.to_excel(filepath, sheet_name=self.name, index=False)
    
    def to_csv(self, filepath: str) -> None:
        """
        ייצוא מודל הטבלה לקובץ CSV
        
        Args:
            filepath: נתיב לקובץ CSV
        """
        self.df.to_csv(filepath, index=False)
    
    def to_json(self, filepath: str) -> None:
        """
        ייצוא מודל הטבלה לקובץ JSON
        
        Args:
            filepath: נתיב לקובץ JSON
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    def get_column(self, column_name: str) -> List[Any]:
        """
        קבלת ערכי עמודה ספציפית
        
        Args:
            column_name: שם העמודה
            
        Returns:
            List: רשימת ערכי העמודה
        """
        if column_name in self.df.columns:
            return self.df[column_name].tolist()
        return []
    
    def find_rows(self, column_name: str, value: Any) -> pd.DataFrame:
        """
        חיפוש שורות לפי ערך בעמודה מסוימת
        
        Args:
            column_name: שם העמודה
            value: הערך לחיפוש
            
        Returns:
            pd.DataFrame: DataFrame עם השורות שנמצאו
        """
        if column_name in self.df.columns:
            return self.df[self.df[column_name] == value]
        return pd.DataFrame()
    
    def get_stats(self, column_name: str) -> Dict[str, Any]:
        """
        קבלת סטטיסטיקות על עמודה מספרית
        
        Args:
            column_name: שם העמודה
            
        Returns:
            Dict: מילון עם ערכים סטטיסטיים
        """
        if column_name in self.df.columns and pd.api.types.is_numeric_dtype(self.df[column_name]):
            return {
                'mean': self.df[column_name].mean(),
                'median': self.df[column_name].median(),
                'min': self.df[column_name].min(),
                'max': self.df[column_name].max(),
                'std': self.df[column_name].std()
            }
        return {}
    
    def transform_column(self, column_name: str, transform_func) -> None:
        """
        ביצוע טרנספורמציה על עמודה
        
        Args:
            column_name: שם העמודה
            transform_func: פונקציית טרנספורמציה
        """
        if column_name in self.df.columns:
            self.df[column_name] = self.df[column_name].apply(transform_func)
            # עדכון הנתונים המקוריים
            self.data = self.df.values.tolist()
    
    def add_column(self, column_name: str, values: List[Any]) -> None:
        """
        הוספת עמודה חדשה
        
        Args:
            column_name: שם העמודה
            values: ערכי העמודה
        """
        if len(values) == len(self.df):
            self.df[column_name] = values
            self.headers = self.df.columns.tolist()
            self.data = self.df.values.tolist()
    
    def detect_financial_columns(self) -> List[str]:
        """
        זיהוי עמודות פיננסיות
        
        Returns:
            List[str]: רשימת שמות העמודות הפיננסיות
        """
        financial_columns = []
        
        # זיהוי עמודות מספריות
        for column in self.df.columns:
            # בדיקה אם העמודה מספרית
            if pd.api.types.is_numeric_dtype(self.df[column]):
                financial_columns.append(column)
            
            # בדיקה לפי שם העמודה
            column_lower = column.lower()
            if any(term in column_lower for term in ['amount', 'price', 'value', 'total', 'balance', 'סכום', 'מחיר', 'ערך', 'יתרה']):
                if column not in financial_columns:
                    financial_columns.append(column)
        
        return financial_columns
    
    @staticmethod
    def save_template(template_name: str, headers: List[str], rules: Dict[str, Any]) -> None:
        """
        שמירת תבנית טבלה לשימוש חוזר
        
        Args:
            template_name: שם התבנית
            headers: כותרות העמודות
            rules: חוקים לעיבוד הטבלה
        """
        template_dir = 'data/templates'
        os.makedirs(template_dir, exist_ok=True)
        
        template_data = {
            'name': template_name,
            'headers': headers,
            'rules': rules,
            'created_at': datetime.now().isoformat()
        }
        
        template_path = os.path.join(template_dir, f"{template_name.replace(' ', '_')}.json")
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def load_template(template_name: str) -> Dict[str, Any]:
        """
        טעינת תבנית טבלה
        
        Args:
            template_name: שם התבנית
            
        Returns:
            Dict: נתוני התבנית
        """
        template_path = os.path.join('data/templates', f"{template_name.replace(' ', '_')}.json")
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    @staticmethod
    def list_templates() -> List[str]:
        """
        קבלת רשימת התבניות הזמינות
        
        Returns:
            List[str]: רשימת שמות התבניות
        """
        template_dir = 'data/templates'
        os.makedirs(template_dir, exist_ok=True)
        
        templates = []
        for filename in os.listdir(template_dir):
            if filename.endswith('.json'):
                template_name = filename.replace('.json', '').replace('_', ' ')
                templates.append(template_name)
        
        return templates

# ייבוא נדרש לפונקציות נוספות
from datetime import datetime
