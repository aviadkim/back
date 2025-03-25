import logging
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# הגדרת לוגר
logger = logging.getLogger(__name__)

class MemoryAgent:
    """
    סוכן לניהול זיכרון ושמירת מידע בהקשר השיחה.
    מאפשר שמירה ושליפה של מידע לאורך שיחה, כולל היסטוריית שאלות ותשובות,
    מסמכים רלוונטיים, והקשרים נוספים.
    """
    
    def __init__(self, session_id: str, max_history: int = 10):
        """
        אתחול סוכן הזיכרון
        
        Args:
            session_id: מזהה ייחודי של השיחה
            max_history: מספר מקסימלי של הודעות לשמירה בהיסטוריה
        """
        self.session_id = session_id
        self.max_history = max_history
        self.memory_file = os.path.join('data', 'memory', f'{session_id}.json')
        
        # יוצר את התיקייה אם היא לא קיימת
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        
        # מאתחל זיכרון בסיסי
        self.memory = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "message_history": [],
            "document_references": [],
            "extracted_data": {},
            "context": {}
        }
        
        # טוען זיכרון קיים אם יש
        self._load_memory()
    
    def _load_memory(self):
        """טעינת זיכרון מקובץ אם קיים"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.memory = json.load(f)
                logger.info(f"Loaded memory for session {self.session_id}")
        except Exception as e:
            logger.error(f"Error loading memory: {e}")
    
    def _save_memory(self):
        """שמירת הזיכרון לקובץ"""
        try:
            self.memory["updated_at"] = datetime.now().isoformat()
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def add_message(self, role: str, content: str):
        """
        הוספת הודעה להיסטוריית השיחה
        
        Args:
            role: תפקיד השולח (user/system/assistant)
            content: תוכן ההודעה
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        # מוסיף את ההודעה לתחילת הרשימה (הודעות חדשות בהתחלה)
        self.memory["message_history"].insert(0, message)
        
        # מגביל את גודל ההיסטוריה
        if len(self.memory["message_history"]) > self.max_history:
            self.memory["message_history"] = self.memory["message_history"][:self.max_history]
        
        self._save_memory()
        logger.debug(f"Added message from {role} to session {self.session_id}")
    
    def get_message_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        קבלת היסטוריית השיחה
        
        Args:
            limit: מספר מקסימלי של הודעות להחזרה (ברירת מחדל: הכל)
            
        Returns:
            רשימת הודעות מההיסטוריה
        """
        if limit is None or limit > len(self.memory["message_history"]):
            limit = len(self.memory["message_history"])
        
        # מחזיר את ההודעות מהחדשה לישנה
        return self.memory["message_history"][:limit]
    
    def add_document_reference(self, document_id: str, relevance_score: float = 1.0):
        """
        הוספת הפניה למסמך רלוונטי לשיחה
        
        Args:
            document_id: מזהה המסמך
            relevance_score: ציון הרלוונטיות (0-1)
        """
        reference = {
            "document_id": document_id,
            "relevance_score": relevance_score,
            "timestamp": datetime.now().isoformat()
        }
        
        # בודק אם המסמך כבר קיים ומעדכן אותו
        for i, doc in enumerate(self.memory["document_references"]):
            if doc["document_id"] == document_id:
                self.memory["document_references"][i] = reference
                self._save_memory()
                return
        
        # אם המסמך לא קיים, מוסיף אותו
        self.memory["document_references"].append(reference)
        self._save_memory()
        logger.debug(f"Added document reference {document_id} to session {self.session_id}")
    
    def get_document_references(self) -> List[Dict[str, Any]]:
        """
        קבלת רשימת המסמכים הרלוונטיים לשיחה
        
        Returns:
            רשימת הפניות למסמכים
        """
        # מיון לפי ציון רלוונטיות (מהגבוה לנמוך)
        sorted_docs = sorted(
            self.memory["document_references"],
            key=lambda x: x["relevance_score"],
            reverse=True
        )
        return sorted_docs
    
    def store_context(self, key: str, value: Any):
        """
        שמירת מידע הקשרי נוסף
        
        Args:
            key: מפתח לאחסון
            value: ערך לאחסון
        """
        self.memory["context"][key] = value
        self._save_memory()
        logger.debug(f"Stored context {key} to session {self.session_id}")
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """
        קבלת מידע הקשרי שנשמר
        
        Args:
            key: מפתח לשליפה
            default: ערך ברירת מחדל אם המפתח לא קיים
            
        Returns:
            הערך המאוחסן או ברירת המחדל
        """
        return self.memory["context"].get(key, default)
    
    def store_extracted_data(self, category: str, data: Any):
        """
        שמירת מידע שחולץ מהשיחה או ממסמכים
        
        Args:
            category: קטגוריית המידע
            data: המידע שחולץ
        """
        self.memory["extracted_data"][category] = data
        self._save_memory()
        logger.debug(f"Stored extracted data for category {category}")
    
    def get_extracted_data(self, category: str = None) -> Dict[str, Any]:
        """
        קבלת מידע שחולץ
        
        Args:
            category: קטגוריה ספציפית (אופציונלי)
            
        Returns:
            כל המידע שחולץ או רק הקטגוריה המבוקשת
        """
        if category:
            return self.memory["extracted_data"].get(category, {})
        return self.memory["extracted_data"]
    
    def clear_history(self):
        """מחיקת היסטוריית ההודעות"""
        self.memory["message_history"] = []
        self._save_memory()
        logger.info(f"Cleared message history for session {self.session_id}")
    
    def clear_all(self):
        """מחיקת כל המידע בזיכרון"""
        self.memory = {
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "message_history": [],
            "document_references": [],
            "extracted_data": {},
            "context": {}
        }
        self._save_memory()
        logger.info(f"Cleared all memory for session {self.session_id}")
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """
        קבלת סיכום של הזיכרון
        
        Returns:
            מילון עם נתוני סיכום על הזיכרון
        """
        return {
            "session_id": self.session_id,
            "created_at": self.memory["created_at"],
            "updated_at": self.memory["updated_at"],
            "message_count": len(self.memory["message_history"]),
            "document_count": len(self.memory["document_references"]),
            "context_keys": list(self.memory["context"].keys()),
            "extracted_data_categories": list(self.memory["extracted_data"].keys())
        }
