from typing import List, Dict, Optional, Any, Union
import os
import json
import logging
from .memory_agent import MemoryAgent
import re

# הגדרת לוגר
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DummyCoordinator:
    """
    מתאם דמה - גרסה קלה יותר למשאבים
    """
    def __init__(self):
        self.conversation_history = {}
        self.default_language = "he"
    
    def answer_question(self, **kwargs):
        """
        תשובה פשוטה לצורך בדיקה
        """
        question = kwargs.get("question", "")
        language = kwargs.get("language", "he")
        conversation_id = kwargs.get("conversation_id", "dummy_conversation")
        
        if not conversation_id in self.conversation_history:
            self.conversation_history[conversation_id] = []
        
        # שמירת השאלה בהיסטוריה
        self.conversation_history[conversation_id].append({
            "role": "user", 
            "content": question
        })
        
        # תשובה פשוטה
        if language == "he":
            answer = f"קיבלתי את השאלה: '{question}'. זו גרסת דמו של המערכת עם יכולות מוגבלות."
        else:
            answer = f"I received your question: '{question}'. This is a demo version of the system with limited capabilities."
        
        # שמירת התשובה בהיסטוריה
        self.conversation_history[conversation_id].append({
            "role": "assistant", 
            "content": answer
        })
        
        return {
            "answer": answer,
            "confidence": 0.7,
            "sources": [],
            "conversation_id": conversation_id,
            "language": language
        }
    
    def process_document(self, **kwargs):
        """
        עיבוד מסמך - גרסת דמו
        """
        document_id = kwargs.get("document_id", "")
        language = kwargs.get("language", "he")
        
        return True
    
    def get_document_summary(self, document_id, **kwargs):
        """
        סיכום מסמך - גרסת דמו
        """
        language = kwargs.get("language", "he")
        
        if language == "he":
            summary = "זהו סיכום דמו של המסמך. בגרסה המלאה, יוצג כאן סיכום מבוסס AI של התוכן."
        else:
            summary = "This is a demo summary of the document. In the full version, an AI-based summary of the content would be displayed here."
        
        return {
            "summary": summary,
            "document_id": document_id,
            "document_type": "demo",
            "key_points": ["נקודה 1", "נקודה 2", "נקודה 3"] if language == "he" else ["Point 1", "Point 2", "Point 3"],
            "response_language": language
        }
    
    def clear_conversation(self, conversation_id):
        """
        מחיקת היסטוריית שיחה
        """
        if conversation_id in self.conversation_history:
            del self.conversation_history[conversation_id]
            return True
        return False
    
    def set_language(self, language):
        """
        הגדרת שפה
        """
        if language in ["he", "en"]:
            self.default_language = language
            return True
        return False

class AgentCoordinator:
    """
    מתאם בין הסוכנים השונים במערכת.
    מנהל זרימת עבודה והאינטראקציה בין הרכיבים השונים.
    """
    
    def __init__(self, api_key: Optional[str] = None, default_language: str = "he"):
        """
        אתחול המתאם
        
        Args:
            api_key: מפתח API ל-HuggingFace או שירות LLM אחר
            default_language: שפת ברירת מחדל (he לעברית, en לאנגלית)
        """
        # For Render, we're using a lightweight version
        # The full version with models would be too resource-intensive
        self._dummy = DummyCoordinator()
        
        logger.info("Using lightweight coordinator for Render deployment")
    
    def answer_question(self, **kwargs):
        """Delegate to dummy implementation"""
        return self._dummy.answer_question(**kwargs)
    
    def process_document(self, **kwargs):
        """Delegate to dummy implementation"""
        return self._dummy.process_document(**kwargs)
    
    def get_document_summary(self, document_id, **kwargs):
        """Delegate to dummy implementation"""
        return self._dummy.get_document_summary(document_id, **kwargs)
    
    def clear_conversation(self, conversation_id):
        """Delegate to dummy implementation"""
        return self._dummy.clear_conversation(conversation_id)
    
    def set_language(self, language):
        """Delegate to dummy implementation"""
        return self._dummy.set_language(language)
    
    def _extract_section(self, text, section_name, section_title):
        """
        חילוץ סעיף מתוך תשובה
        
        Args:
            text: הטקסט המלא
            section_name: שם הסעיף באנגלית לחיפוש
            section_title: כותרת הסעיף לחיפוש
            
        Returns:
            str: תוכן הסעיף
        """
        # חיפוש בפורמט סטנדרטי - fixed escape sequence
        pattern = f'"{section_name}"\\s*:\\s*"([^"]*)"'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        
        # חיפוש לפי כותרת - fixed escape sequence
        pattern = f'{section_title}:\\s*(.*?)(?:\\n\\n|\\n[A-Za-zא-ת])'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return ""
    
    def _extract_list(self, text, section_name, section_title):
        """
        חילוץ רשימה מתוך תשובה
        
        Args:
            text: הטקסט המלא
            section_name: שם הסעיף באנגלית לחיפוש
            section_title: כותרת הסעיף לחיפוש
            
        Returns:
            List[str]: רשימת פריטים
        """
        # חיפוש בפורמט סטנדרטי - fixed escape sequence
        pattern = f'"{section_name}"\\s*:\\s*\\[(.*?)\\]'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            items_str = match.group(1)
            items = re.findall(r'"([^"]*)"', items_str)
            return items
        
        # חיפוש לפי כותרת ורשימה ממוספרת או עם נקודות - fixed escape sequence
        pattern = f'{section_title}:\\s*(.*?)(?:\\n\\n|\\Z)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            items_text = match.group(1).strip()
            items = re.findall(r'\d+\.\s*(.*?)(?:\n|$)', items_text)
            if not items:
                items = re.findall(r'[-•]\s*(.*?)(?:\n|$)', items_text)
            return items
        
        return []
