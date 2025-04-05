"""
מתאם סוכנים לניתוח מסמכים פיננסיים
"""

import os
import logging
import uuid
from datetime import datetime

# Import Financial Agents
from agents.financial.document_processing_agent import DocumentProcessingAgent
from agents.financial.portfolio_analysis_agent import PortfolioAnalysisAgent
from agents.financial.financial_advisor_agent import FinancialAdvisorAgent
from agents.financial.consolidated_reports_agent import ConsolidatedReportsAgent
from agents.financial.budget_tracking_agent import BudgetTrackingAgent
from agents.financial.report_comparison_agent import ReportComparisonAgent


logger = logging.getLogger(__name__)

class AgentCoordinator:
    """
    מתאם סוכנים המתזמן ומנהל את הפעולות של הסוכנים השונים במערכת
    """
    
    def __init__(self, models_config=None):
        """
        יוצר מתאם סוכנים חדש
        
        Args:
            models_config: תצורת המודלים לשימוש (ברירת מחדל: None)
        """
        self.models_config = models_config or {
            "default": "gemini",
            "available": ["gemini", "llama", "mistral"]
        }
        
        # אחסון בזיכרון של מקטעי מסמכים - במערכת אמיתית זה היה במסד נתונים
        self.document_chunks = {}
        # אחסון בזיכרון של סשנים - במערכת אמיתית זה היה במסד נתונים
        self.sessions = {}

        # Instantiate agents
        self.document_processing_agent = DocumentProcessingAgent()
        self.portfolio_analysis_agent = PortfolioAnalysisAgent()
        self.financial_advisor_agent = FinancialAdvisorAgent()
        self.consolidated_reports_agent = ConsolidatedReportsAgent()
        self.budget_tracking_agent = BudgetTrackingAgent()
        self.report_comparison_agent = ReportComparisonAgent()
        
        # TODO: Implement agent registration/mapping if a more formal mechanism is needed
        self.registered_agents = {
            "document_processing": self.document_processing_agent,
            "portfolio_analysis": self.portfolio_analysis_agent,
            "financial_advice": self.financial_advisor_agent,
            "consolidated_reports": self.consolidated_reports_agent,
            "budget_tracking": self.budget_tracking_agent,
            "report_comparison": self.report_comparison_agent,
        }
        
        logger.info(f"Agent Coordinator initialized with models: {self.models_config['available']} and agents: {list(self.registered_agents.keys())}")
    
    def process_document(self, document_path, options=None):
        """
        מעבד מסמך באמצעות הסוכנים
        
        Args:
            document_path: נתיב למסמך
            options: אפשרויות עיבוד
            
        Returns:
            dict: תוצאות העיבוד
        """
        options = options or {}
        document_id = os.path.basename(document_path).replace('.', '_')
        
        logger.info(f"Processing document: {document_id}")
        
        # סימולציה של עיבוד מסמך
        processing_result = {
            "document_id": document_id,
            "processed_at": datetime.now().isoformat(),
            "chunks_count": 10,
            "model_used": self.models_config["default"],
            "metadata": {
                "title": "דוח שנתי 2024",
                "language": "he",
                "confidence": 0.95
            }
        }
        
        # אחסון נתונים מדומים עבור המסמך
        self.document_chunks[document_id] = [
            {
                "id": f"chunk_{i}",
                "document_id": document_id,
                "text": f"מקטע מספר {i} של המסמך.",
                "embedding": [0.1, 0.2, 0.3]  # סימולציה של embedding
            }
            for i in range(10)
        ]
        
        return processing_result
    
    def create_session(self, user_id, documents=None):
        """
        יצירת סשן צ'אט חדש
        
        Args:
            user_id: מזהה המשתמש
            documents: רשימת מזהי מסמכים לקשר לסשן
            
        Returns:
            str: מזהה הסשן החדש
        """
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "documents": documents or [],
            "history": []
        }
        
        logger.info(f"Created new session: {session_id} for user: {user_id}")
        return session_id
    
    def process_query(self, session_id, query, context=None):
        """
        מעבד שאלה ומחזיר תשובה
        
        Args:
            session_id: מזהה הסשן
            query: השאלה שנשאלה
            context: הקשר נוסף (ברירת מחדל: None)
            
        Returns:
            dict: תשובה ומידע נוסף
        """
        if session_id not in self.sessions:
            session_id = self.create_session('anonymous')
        
        # שמירת השאלה בהיסטוריה
        self.sessions[session_id]["history"].append({
            "role": "user",
            "content": query,
            "timestamp": datetime.now().isoformat()
        })
        
        # יצירת תשובה לדוגמה
        sample_answers = {
            "מהם מספרי ה-ISIN במסמך?": "במסמך זוהו מספרי ISIN הבאים: US0378331005 (Apple Inc.), US88160R1014 (Tesla Inc.), וכן DE000BAY0017 (Bayer AG).",
            "מהן החברות המוזכרות במסמך?": "החברות המוזכרות במסמך הן: אפל, טסלה, מיקרוסופט, אמזון, וגוגל.",
            "סכם את הנתונים הפיננסיים העיקריים": "הנתונים הפיננסיים העיקריים: סך הנכסים: 1.2 מיליון ₪, תשואה שנתית: 8.7%, מדד חידות: 112, תשואת דיבידנד: 3.2%, ויחס P/E ממוצע: 22.4."
        }
        
        # בחירת תשובה המבוססת על תבניות נפוצות או תשובה כללית
        answer = None
        for key_question, key_answer in sample_answers.items():
            if key_question in query or any(word in query for word in key_question.split()):
                answer = key_answer
                break
        
        if not answer:
            answer = f"אני מבין את שאלתך: '{query}'. במסמך נמצאו מספר פרטים פיננסיים, כולל תשואות, השוואת מדדים ונתוני חברות. האם תרצה מידע ספציפי יותר?"
        
        # שמירת התשובה בהיסטוריה
        self.sessions[session_id]["history"].append({
            "role": "assistant",
            "content": answer,
            "timestamp": datetime.now().isoformat()
        })
        
        # סימולציה של שימוש במודל
        model_used = self.models_config["default"]
        if "gemini" in query.lower():
            model_used = "gemini"
        elif "llama" in query.lower():
            model_used = "llama"
        elif "mistral" in query.lower():
            model_used = "mistral"
        
        logger.info(f"Processed query for session: {session_id} using model: {model_used}")
        
        return {
            "answer": answer,
            "session_id": session_id,
            "model_used": model_used,
            "sources": []  # במערכת אמיתית, כאן היו מוצגים מקורות המידע
        }
    
    def get_session_history(self, session_id):
        """
        קבלת היסטוריית הסשן
        
        Args:
            session_id: מזהה הסשן
            
        Returns:
            list: היסטוריית השיחה
        """
        if session_id not in self.sessions:
            return []
        
        return self.sessions[session_id]["history"]
