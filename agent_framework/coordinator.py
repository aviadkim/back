import logging
import uuid
import os
from typing import Dict, List, Any, Optional, Tuple
from .memory_agent import MemoryAgent
import json

# הגדרת לוגר
logger = logging.getLogger(__name__)

class AgentCoordinator:
    """
    מתאם הסוכנים - אחראי על ניהול והפעלה של הסוכנים השונים במערכת.
    מאפשר תיאום בין הסוכנים, ניתוב פעולות, וניהול זרימת העבודה.
    """
    
    def __init__(self):
        """אתחול מתאם הסוכנים"""
        # מילון של סוכני זיכרון פעילים לפי מזהה שיחה
        self.active_memory_agents: Dict[str, MemoryAgent] = {}
        
        # נתיב לתיקיית הנתונים
        self.data_dir = 'data'
        
        # וודא שהתיקיות הנדרשות קיימות
        os.makedirs(os.path.join(self.data_dir, 'memory'), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'embeddings'), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'templates'), exist_ok=True)
    
    def get_memory_agent(self, session_id: Optional[str] = None) -> MemoryAgent:
        """
        קבלת סוכן זיכרון עבור שיחה ספציפית
        
        Args:
            session_id: מזהה השיחה (אם לא ניתן, נוצר חדש)
            
        Returns:
            סוכן זיכרון לשיחה
        """
        # אם לא ניתן מזהה שיחה, צור חדש
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # אם הסוכן כבר קיים, החזר אותו
        if session_id in self.active_memory_agents:
            return self.active_memory_agents[session_id]
        
        # אחרת, צור סוכן חדש
        memory_agent = MemoryAgent(session_id)
        self.active_memory_agents[session_id] = memory_agent
        
        return memory_agent
    
    def process_document(self, file_path: str, language: str = 'he') -> Dict[str, Any]:
        """
        עיבוד מסמך
        
        Args:
            file_path: נתיב לקובץ
            language: שפת המסמך
            
        Returns:
            תוצאות העיבוד
        """
        # כאן יתבצע תיאום בין הסוכנים השונים לעיבוד המסמך
        # כרגע זוהי פונקציה מלאכותית, בהמשך תממש תיאום אמיתי
        
        logger.info(f"Processing document: {file_path}, language: {language}")
        
        result = {
            "document_id": os.path.basename(file_path),
            "language": language,
            "status": "processed"
        }
        
        return result
    
    def process_query(self, session_id: str, query: str, 
                      document_ids: Optional[List[str]] = None,
                      language: str = 'he') -> Dict[str, Any]:
        """
        עיבוד שאילתה למערכת
        
        Args:
            session_id: מזהה השיחה
            query: השאילתה עצמה
            document_ids: רשימת מזהי מסמכים רלוונטיים (אופציונלי)
            language: שפת השאילתה
            
        Returns:
            תשובה לשאילתה
        """
        logger.info(f"Processing query for session {session_id}: {query}")
        
        # קבלת סוכן הזיכרון לשיחה
        memory_agent = self.get_memory_agent(session_id)
        
        # שמירת השאילתה בהיסטוריה
        memory_agent.add_message(role="user", content=query)
        
        # אם יש מסמכים ספציפיים שצוינו, הוסף אותם להקשר
        if document_ids:
            for doc_id in document_ids:
                memory_agent.add_document_reference(doc_id)
        
        # ניתן להוסיף כאן קריאה לסוכנים נוספים:
        # 1. חיפוש מסמכים רלוונטיים
        # 2. חילוץ מידע ייעודי
        # 3. ניתוח הוראות במשפט
        # 4. חיפוש מידע בבסיס הנתונים
        
        # כרגע זוהי תשובה מלאכותית
        answer = f"תשובה לשאלה: {query}"
        
        # שמירת התשובה בהיסטוריה
        memory_agent.add_message(role="assistant", content=answer)
        
        result = {
            "session_id": session_id,
            "query": query,
            "answer": answer,
            "language": language,
            "document_references": memory_agent.get_document_references()
        }
        
        return result
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """
        קבלת רשימת שיחות פעילות
        
        Returns:
            רשימת שיחות פעילות עם נתוני סיכום
        """
        active_sessions = []
        
        # איסוף מידע על שיחות פעילות בזיכרון
        for session_id, memory_agent in self.active_memory_agents.items():
            summary = memory_agent.get_memory_summary()
            active_sessions.append(summary)
        
        # בדיקה גם לקבצי זיכרון שנשמרו בדיסק ולא טעונים כרגע
        memory_dir = os.path.join(self.data_dir, 'memory')
        if os.path.exists(memory_dir):
            for filename in os.listdir(memory_dir):
                if filename.endswith('.json'):
                    session_id = os.path.splitext(filename)[0]
                    
                    # אם השיחה כבר נמצאת ברשימה, דלג
                    if session_id in [s["session_id"] for s in active_sessions]:
                        continue
                    
                    # קרא מידע בסיסי מהקובץ
                    try:
                        with open(os.path.join(memory_dir, filename), 'r', encoding='utf-8') as f:
                            memory_data = json.load(f)
                            summary = {
                                "session_id": session_id,
                                "created_at": memory_data.get("created_at", ""),
                                "updated_at": memory_data.get("updated_at", ""),
                                "message_count": len(memory_data.get("message_history", [])),
                                "document_count": len(memory_data.get("document_references", [])),
                                "from_disk": True
                            }
                            active_sessions.append(summary)
                    except Exception as e:
                        logger.error(f"Error reading memory file {filename}: {e}")
        
        # מיון לפי תאריך עדכון אחרון
        active_sessions.sort(
            key=lambda x: x.get("updated_at", ""),
            reverse=True
        )
        
        return active_sessions
    
    def clear_session(self, session_id: str) -> bool:
        """
        ניקוי נתוני שיחה
        
        Args:
            session_id: מזהה השיחה
            
        Returns:
            האם הפעולה הצליחה
        """
        try:
            # אם השיחה פעילה, נקה את הזיכרון
            if session_id in self.active_memory_agents:
                self.active_memory_agents[session_id].clear_all()
                del self.active_memory_agents[session_id]
            
            # מחק את קובץ הזיכרון מהדיסק
            memory_file = os.path.join(self.data_dir, 'memory', f'{session_id}.json')
            if os.path.exists(memory_file):
                os.remove(memory_file)
            
            logger.info(f"Cleared session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing session {session_id}: {e}")
            return False
