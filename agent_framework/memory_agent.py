from typing import List, Dict, Optional, Union
import os
import pickle
import hashlib
import logging

# הגדרת לוגר
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryAgent:
    """
    סוכן לניהול זיכרון ואחסון מסמכים - גרסה קלה למשאבים
    """
    
    def __init__(self, embedding_model_name: str = "dummy"):
        """
        אתחול סוכן הזיכרון - גרסה קלה
        
        Args:
            embedding_model_name: לא בשימוש בגרסה זו
        """
        self.documents = {}  # מילון לאחסון מסמכים גולמיים
        
        # יצירת ספריית אחסון
        os.makedirs("data/embeddings", exist_ok=True)
        
        logger.info("Initialized lightweight memory agent for Render")
    
    def add_document(self, document_id: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """
        הוספת מסמך למאגר - גרסה פשוטה
        
        Args:
            document_id: מזהה ייחודי למסמך
            content: תוכן המסמך
            metadata: מטה-דאטה נוסף על המסמך (אופציונלי)
            
        Returns:
            bool: האם הפעולה הצליחה
        """
        try:
            # שמירת המסמך המקורי
            if metadata is None:
                metadata = {}
            
            self.documents[document_id] = {
                "content": content[:1000] + "...", # שומר רק את תחילת המסמך לחיסכון בזיכרון
                "metadata": metadata
            }
            
            return True
        except Exception as e:
            logger.error(f"שגיאה בהוספת מסמך: {e}")
            return False
    
    def get_relevant_context(self, query: str, document_ids: Optional[List[str]] = None, k: int = 5) -> str:
        """
        שליפת מידע רלוונטי מהמסמכים - בגרסה זו מחזיר טקסט קבוע
        
        Args:
            query: שאילתת חיפוש
            document_ids: רשימת מזהי מסמכים להגבלת החיפוש (אופציונלי)
            k: מספר תוצאות לשליפה
            
        Returns:
            str: הקשר רלוונטי מהמסמכים
        """
        # בגרסה זו, נשלוף רק את תוכן המסמכים שצוינו
        if not self.documents:
            return "אין מידע זמין."
            
        if document_ids:
            # שליפת תוכן מסמכים ספציפיים
            relevant_docs = []
            for doc_id in document_ids:
                if doc_id in self.documents:
                    doc_content = self.documents[doc_id]["content"]
                    relevant_docs.append(f"מסמך {doc_id}:\n{doc_content[:300]}...")
            
            if relevant_docs:
                return "\n\n".join(relevant_docs)
            else:
                return "המסמכים שצוינו אינם קיימים במערכת."
        else:
            # שליפת תוכן כל המסמכים (מוגבל לכמה הראשונים)
            sample_docs = list(self.documents.items())[:3]
            relevant_docs = []
            
            for doc_id, doc_data in sample_docs:
                doc_content = doc_data["content"]
                relevant_docs.append(f"מסמך {doc_id}:\n{doc_content[:300]}...")
            
            return "\n\n".join(relevant_docs)
    
    def clear_memory(self) -> bool:
        """
        מחיקת כל המידע מהזיכרון
        
        Returns:
            bool: האם הפעולה הצליחה
        """
        try:
            self.documents = {}
            return True
        except Exception as e:
            logger.error(f"שגיאה במחיקת זיכרון: {e}")
            return False
