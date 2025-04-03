import logging
import uuid
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

from agent_framework.coordinator import AgentCoordinator
from agent_framework.nlp_agent import NaturalLanguageQueryAgent
from agent_framework.table_generator import CustomTableGenerator

# הגדרת לוגר
logger = logging.getLogger(__name__)

class ChatbotService:
    """
    שירות לניהול הצ'אטבוט ושיחות משתמשים
    """
    
    def __init__(self):
        """אתחול שירות הצ'אטבוט"""
        self.coordinator = AgentCoordinator()
        self.nlp_agent = NaturalLanguageQueryAgent()
        self.table_generator = CustomTableGenerator()
        
        # מיפוי של שיחות למשתמשים
        self.session_user_map = {}
        
        # רשימת שאלות שכיחות לפי קטגוריות
        self.common_questions = {
            'asset_allocation': [
                {'he': 'מה הרכב התיק הנוכחי שלי?', 'en': 'What is my current asset allocation?'},
                {'he': 'איזה אחוז מהתיק שלי מושקע באג"ח?', 'en': 'What percentage of my portfolio is invested in bonds?'},
                {'he': 'מה היחס בין מניות לאג"ח בתיק?', 'en': 'What is the ratio between stocks and bonds in my portfolio?'},
            ],
            'performance': [
                {'he': 'מה הייתה התשואה של התיק בשנה האחרונה?', 'en': 'What was my portfolio\'s performance in the last year?'},
                {'he': 'אילו נכסים הניבו את התשואה הגבוהה ביותר?', 'en': 'Which assets had the highest return?'},
                {'he': 'האם יש נכסים שביצעו גרוע במיוחד?', 'en': 'Are there any assets that performed particularly poorly?'},
            ],
            'risk': [
                {'he': 'מה רמת הסיכון של התיק שלי?', 'en': 'What is the risk level of my portfolio?'},
                {'he': 'איזה יחס שארפ יש לתיק?', 'en': 'What is the Sharpe ratio of my portfolio?'},
                {'he': 'איך ניתן להפחית את הסיכון בתיק?', 'en': 'How can I reduce the risk in my portfolio?'},
            ],
            'currency': [
                {'he': 'מה החשיפה המטבעית של התיק שלי?', 'en': 'What is my portfolio\'s currency exposure?'},
                {'he': 'כמה מהתיק מושקע בדולר?', 'en': 'How much of my portfolio is invested in USD?'},
                {'he': 'האם כדאי לגדר את החשיפה המטבעית?', 'en': 'Should I hedge the currency exposure?'},
            ],
            'table_generation': [
                {'he': 'הצג טבלה של כל האג"ח בתיק', 'en': 'Show a table of all bonds in my portfolio'},
                {'he': 'צור טבלה של הנכסים עם תשואה שלילית', 'en': 'Create a table of assets with negative returns'},
                {'he': 'הצג טבלה מסכמת של הרכב התיק לפי סוגי נכסים', 'en': 'Show a summary table of portfolio composition by asset type'},
            ]
        }
    
    def create_session(self, user_id: str, document_ids: List[str] = None, language: str = 'he') -> str:
        """
        יצירת שיחה חדשה
        
        Args:
            user_id: מזהה המשתמש
            document_ids: רשימת מזהי מסמכים להתחלת השיחה
            language: שפת השיחה
            
        Returns:
            מזהה השיחה החדשה
        """
        # יצירת מזהה שיחה חדש
        session_id = str(uuid.uuid4())
        
        # קבלת/יצירת סוכן זיכרון לשיחה
        memory_agent = self.coordinator.get_memory_agent(session_id)
        
        # שמירת קשר בין שיחה למשתמש
        self.session_user_map[session_id] = user_id
        
        # שמירת מידע בהקשר השיחה
        memory_agent.store_context('user_id', user_id)
        memory_agent.store_context('language', language)
        memory_agent.store_context('created_at', datetime.now().isoformat())
        
        # הוספת מסמכים לשיחה אם נתנו
        if document_ids:
            for doc_id in document_ids:
                memory_agent.add_document_reference(doc_id)
                
        # הוספת הודעת פתיחה
        welcome_message = "שלום, איך אוכל לעזור לך עם המסמכים הפיננסיים שלך?" if language == 'he' else \
                          "Hello, how can I help you with your financial documents?"
        memory_agent.add_message(role="assistant", content=welcome_message)
        
        logger.info(f"Created new chat session {session_id} for user {user_id}")
        return session_id
    
    def create_temporary_session(self, document_ids: List[str], language: str = 'he') -> str:
        """
        יצירת שיחה זמנית עבור שאילתה חד פעמית
        
        Args:
            document_ids: רשימת מזהי מסמכים לשיחה
            language: שפת השיחה
            
        Returns:
            מזהה השיחה הזמנית
        """
        # יצירת מזהה שיחה חדש עם תחילית temp-
        session_id = f"temp-{str(uuid.uuid4())}"
        
        # קבלת/יצירת סוכן זיכרון לשיחה
        memory_agent = self.coordinator.get_memory_agent(session_id)
        
        # שמירת מידע בהקשר השיחה
        memory_agent.store_context('temporary', True)
        memory_agent.store_context('language', language)
        memory_agent.store_context('created_at', datetime.now().isoformat())
        
        # הוספת מסמכים לשיחה
        for doc_id in document_ids:
            memory_agent.add_document_reference(doc_id)
        
        logger.info(f"Created temporary chat session {session_id}")
        return session_id
    
    def generate_suggested_questions(self, session_id: str, query: str, language: str = 'he', 
                                     result: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        יצירת שאלות המשך מומלצות בהתאם לשאלה הנוכחית והתשובה
        
        Args:
            session_id: מזהה השיחה
            query: השאלה הנוכחית
            language: שפת השיחה
            result: תוצאת השאלה הנוכחית (אופציונלי)
            
        Returns:
            רשימת שאלות המשך מומלצות
        """
        suggested_questions = []
        
        # קבלת סוכן הזיכרון לשיחה
        memory_agent = self.coordinator.get_memory_agent(session_id)
        
        # בחירת שאלות מהקטגוריות הרלוונטיות ביותר
        relevant_categories = self._get_relevant_categories(query, result)
        
        for category in relevant_categories:
            if category in self.common_questions:
                # בחירת השאלות בשפה הנכונה
                lang_key = 'he' if language == 'he' else 'en'
                category_questions = [q[lang_key] for q in self.common_questions[category]]
                
                # הוספת שאלות רלוונטיות
                suggested_questions.extend(category_questions[:2])  # לכל היותר 2 שאלות מקטגוריה
        
        # הגבלה ל-5 שאלות מקסימום
        return suggested_questions[:5]
    
    def generate_document_suggestions(self, document_id: str, language: str = 'he') -> List[str]:
        """
        יצירת שאלות מומלצות למסמך ספציפי
        
        Args:
            document_id: מזהה המסמך
            language: שפת השאלות
            
        Returns:
            רשימת שאלות מומלצות
        """
        # כאן יש לשלוף את סוג המסמך ולייצר שאלות מותאמות אישית
        # לצורך הדגמה, נחזיר שאלות כלליות
        
        # בחירת שאלות בשפה הנכונה
        lang_key = 'he' if language == 'he' else 'en'
        
        # בחירת שאלות מקטגוריות שונות
        suggested_questions = []
        for category in self.common_questions.keys():
            if self.common_questions[category]:
                suggested_questions.append(self.common_questions[category][0][lang_key])
        
        return suggested_questions
    
    def get_session_user(self, session_id: str) -> str:
        """
        קבלת מזהה המשתמש לפי מזהה השיחה
        
        Args:
            session_id: מזהה השיחה
            
        Returns:
            מזהה המשתמש או 'anonymous' אם לא נמצא
        """
        return self.session_user_map.get(session_id, 'anonymous')
    
    def remove_session(self, session_id: str) -> None:
        """
        הסרת שיחה מהמיפוי
        
        Args:
            session_id: מזהה השיחה להסרה
        """
        if session_id in self.session_user_map:
            del self.session_user_map[session_id]
            logger.info(f"Removed session {session_id} from user mapping")
    
    def _get_relevant_categories(self, query: str, result: Optional[Dict[str, Any]]) -> List[str]:
        """
        זיהוי קטגוריות השאלות הרלוונטיות ביותר להמשך השיחה
        
        Args:
            query: השאלה הנוכחית
            result: תוצאת השאלה הנוכחית (אופציונלי)
            
        Returns:
            רשימת קטגוריות רלוונטיות
        """
        query = query.lower()
        
        # התאמה לפי מילות מפתח בשאלה
        relevant_categories = []
        
        # אם השאלה עוסקת בהרכב התיק
        if any(keyword in query for keyword in ['הרכב', 'חלוקה', 'allocation', 'composition', 'breakdown']):
            relevant_categories.append('asset_allocation')
            
        # אם השאלה עוסקת בביצועים
        if any(keyword in query for keyword in ['תשואה', 'ביצועים', 'החזר', 'performance', 'return', 'yield']):
            relevant_categories.append('performance')
            
        # אם השאלה עוסקת בסיכון
        if any(keyword in query for keyword in ['סיכון', 'תנודתיות', 'שארפ', 'risk', 'volatility', 'sharpe']):
            relevant_categories.append('risk')
            
        # אם השאלה עוסקת במטבעות
        if any(keyword in query for keyword in ['מטבע', 'דולר', 'שקל', 'יורו', 'currency', 'dollar', 'euro']):
            relevant_categories.append('currency')
            
        # אם השאלה עוסקת בטבלאות
        if any(keyword in query for keyword in ['טבלה', 'הצג', 'רשימה', 'table', 'list', 'show']):
            relevant_categories.append('table_generation')
        
        # אם לא נמצאו קטגוריות רלוונטיות, החזר את כולן
        if not relevant_categories:
            return list(self.common_questions.keys())
        
        return relevant_categories
