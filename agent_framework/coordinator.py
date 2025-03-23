from typing import List, Dict, Optional, Any, Union
import os
import json
import logging
from .memory_agent import MemoryAgent
from langchain_community.llms import HuggingFaceHub
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import hashlib

# הגדרת לוגר
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        self.memory_agent = MemoryAgent()
        self.document_store = {}
        self.conversation_history = {}
        self.default_language = default_language
        
        # הגדרת מודל שפה - אפשרות חינמית עם HuggingFace
        if api_key:
            # אם יש מפתח API, השתמש בו
            self.llm = HuggingFaceHub(
                repo_id="mistralai/Mistral-7B-Instruct-v0.2",
                huggingfacehub_api_token=api_key
            )
        else:
            # ללא מפתח, השתמש במודל מקומי קטן יותר
            try:
                from langchain_community.llms import HuggingFacePipeline
                from transformers import pipeline
                
                # מודל מקומי קטן יותר (3B או 7B)
                pipe = pipeline(
                    "text-generation",
                    model="TheBloke/Mistral-7B-Instruct-v0.2-GGUF", 
                    max_new_tokens=512,
                    temperature=0.7
                )
                
                self.llm = HuggingFacePipeline(pipeline=pipe)
                logger.info("מודל מקומי נטען בהצלחה")
            except Exception as e:
                logger.error(f"שגיאה בטעינת מודל מקומי: {e}")
                logger.warning("נופל חזרה לשימוש במודל דמה. בבקשה ספק מפתח API תקף לשימוש מלא.")
                self.llm = self._dummy_llm
        
        # בניית תבניות שאילתה
        self._setup_prompts()
    
    def process_document(self, document_id: str, content: str, metadata: Optional[Dict] = None, language: Optional[str] = None) -> bool:
        """
        עיבוד מסמך חדש
        
        Args:
            document_id: מזהה ייחודי למסמך
            content: תוכן המסמך
            metadata: מטה-דאטה על המסמך
            language: שפת המסמך (he/en)
            
        Returns:
            bool: האם העיבוד הצליח
        """
        logger.info(f"מעבד מסמך: {document_id}")
        
        # קביעת שפת המסמך
        doc_language = language if language else self.default_language
        
        try:
            # שמירת המסמך בזיכרון
            if not metadata:
                metadata = {}
            
            metadata["language"] = doc_language
            success = self.memory_agent.add_document(document_id, content, metadata)
            
            if success:
                # ניתוח המסמך וחילוץ מידע נוסף
                doc_summary = self._generate_document_summary(content, doc_language)
                
                # שמירת מידע נוסף על המסמך
                metadata.update({
                    "summary": doc_summary.get("summary", ""),
                    "document_type": doc_summary.get("document_type", "unknown"),
                    "key_points": doc_summary.get("key_points", [])
                })
                
                # עדכון המסמך במאגר הפנימי
                self.document_store[document_id] = {
                    "content": content,
                    "metadata": metadata,
                    "processed": True
                }
                
                return True
            else:
                logger.error(f"שגיאה בהוספת מסמך לזיכרון: {document_id}")
                return False
                
        except Exception as e:
            logger.error(f"שגיאה בעיבוד מסמך: {e}")
            return False
    
    def answer_question(self, question: str, document_ids: Optional[List[str]] = None, 
                        conversation_id: Optional[str] = None, language: Optional[str] = None) -> Dict[str, Any]:
        """
        מענה לשאלה על בסיס המסמכים
        
        Args:
            question: השאלה
            document_ids: רשימת מזהי מסמכים לחיפוש (אם לא צוין, יחפש בכל המסמכים)
            conversation_id: מזהה שיחה לשמירת היסטוריה
            language: שפת התשובה (he/en)
            
        Returns:
            Dict: מילון עם התשובה ומידע נוסף
        """
        logger.info(f"עונה לשאלה: {question}")
        
        # קביעת שפת התשובה
        response_language = language if language else self.default_language
        
        if not conversation_id:
            # יצירת מזהה שיחה חדש אם לא סופק
            conversation_id = hashlib.md5(question.encode()).hexdigest()[:10]
        
        # שליפת היסטוריית השיחה הקיימת
        conversation_history = self.conversation_history.get(conversation_id, [])
        
        try:
            # שליפת הקשר רלוונטי מהמסמכים
            context = self.memory_agent.get_relevant_context(question, document_ids)
            
            if not context or context == "אין מידע זמין." or context == "No information available.":
                no_info_message = {
                    "he": "אין לי מספיק מידע כדי לענות על השאלה הזו. האם תוכל להעלות מסמכים רלוונטיים?",
                    "en": "I don't have enough information to answer this question. Could you upload relevant documents?"
                }
                
                return {
                    "answer": no_info_message[response_language],
                    "confidence": 0.0,
                    "sources": [],
                    "conversation_id": conversation_id,
                    "language": response_language
                }
            
            # בניית שרשרת עם מודל השפה עבור מענה תלוי הקשר
            if response_language == "he":
                prompt = self._qa_prompt_he.format(
                    context=context, 
                    question=question,
                    conversation_history=self._format_conversation_history(conversation_history)
                )
            else:
                prompt = self._qa_prompt_en.format(
                    context=context, 
                    question=question,
                    conversation_history=self._format_conversation_history(conversation_history, language="en")
                )
            
            # קבלת תשובה ממודל השפה
            answer = self.llm(prompt)
            
            # עיבוד התשובה לפורמט מבני
            parsed_answer = self._parse_llm_response(answer)
            
            # עדכון היסטוריית השיחה
            conversation_history.append({"role": "user", "content": question})
            conversation_history.append({"role": "assistant", "content": parsed_answer.get("answer", "")})
            self.conversation_history[conversation_id] = conversation_history
            
            # הוספת מזהה שיחה ושפה לתשובה
            parsed_answer["conversation_id"] = conversation_id
            parsed_answer["language"] = response_language
            
            return parsed_answer
            
        except Exception as e:
            logger.error(f"שגיאה במענה לשאלה: {e}")
            error_message = {
                "he": "אירעה שגיאה בעיבוד השאלה. אנא נסה שוב.",
                "en": "An error occurred while processing your question. Please try again."
            }
            
            return {
                "answer": error_message[response_language],
                "confidence": 0.0,
                "sources": [],
                "conversation_id": conversation_id,
                "language": response_language
            }
    
    def get_document_summary(self, document_id: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        קבלת סיכום מסמך
        
        Args:
            document_id: מזהה המסמך
            language: שפת התשובה (he/en)
            
        Returns:
            Dict: מידע על המסמך
        """
        # קביעת שפת התשובה
        response_language = language if language else self.default_language
        
        if document_id in self.document_store:
            summary_data = self.document_store[document_id].get("metadata", {})
            
            # בדיקה אם צריך לתרגם את הסיכום
            doc_language = summary_data.get("language", self.default_language)
            
            if doc_language != response_language and "summary" in summary_data:
                # תרגום הסיכום בעת הצורך
                if response_language == "en" and doc_language == "he":
                    # תרגום מעברית לאנגלית
                    summary_data["summary"] = self._translate_text(
                        summary_data["summary"], source_lang="he", target_lang="en"
                    )
                elif response_language == "he" and doc_language == "en":
                    # תרגום מאנגלית לעברית
                    summary_data["summary"] = self._translate_text(
                        summary_data["summary"], source_lang="en", target_lang="he"
                    )
            
            # הוספת שפת התשובה למידע המוחזר
            summary_data["response_language"] = response_language
            
            return summary_data
        
        error_message = {
            "he": "מסמך לא נמצא",
            "en": "Document not found"
        }
        
        return {
            "error": error_message[response_language],
            "response_language": response_language
        }
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """
        מחיקת היסטוריית שיחה
        
        Args:
            conversation_id: מזהה השיחה למחיקה
            
        Returns:
            bool: האם המחיקה הצליחה
        """
        if conversation_id in self.conversation_history:
            del self.conversation_history[conversation_id]
            return True
        return False
    
    def set_language(self, language: str) -> bool:
        """
        שינוי שפת ברירת המחדל של המערכת
        
        Args:
            language: שפה (he/en)
            
        Returns:
            bool: האם השינוי הצליח
        """
        if language in ["he", "en"]:
            self.default_language = language
            return True
        return False
    
    def _generate_document_summary(self, content: str, language: str = "he") -> Dict[str, Any]:
        """
        יצירת סיכום למסמך
        
        Args:
            content: תוכן המסמך
            language: שפת הסיכום (he/en)
            
        Returns:
            Dict: מילון עם סיכום, סוג, ונקודות מפתח
        """
        try:
            # קיצור תוכן המסמך אם הוא ארוך מדי
            max_content_length = 4000
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
            # בחירת תבנית שאילתה לפי שפה
            if language == "he":
                prompt = self._summary_prompt_he.format(document=content)
            else:
                prompt = self._summary_prompt_en.format(document=content)
            
            # קבלת תשובה ממודל השפה
            summary_text = self.llm(prompt)
            
            # ניסיון לנתח את התשובה כ-JSON
            try:
                # לפעמים התשובה מוחזרת כ-JSON תקין
                summary_data = json.loads(summary_text)
            except json.JSONDecodeError:
                # אם לא JSON תקין, ננסה לחלץ בצורה ידנית
                if language == "he":
                    summary_data = {
                        "summary": self._extract_section(summary_text, "summary", "תקציר"),
                        "document_type": self._extract_section(summary_text, "document_type", "סוג מסמך"),
                        "key_points": self._extract_list(summary_text, "key_points", "נקודות מפתח")
                    }
                else:
                    summary_data = {
                        "summary": self._extract_section(summary_text, "summary", "Summary"),
                        "document_type": self._extract_section(summary_text, "document_type", "Document Type"),
                        "key_points": self._extract_list(summary_text, "key_points", "Key Points")
                    }
            
            return summary_data
            
        except Exception as e:
            logger.error(f"שגיאה ביצירת סיכום למסמך: {e}")
            
            if language == "he":
                return {
                    "summary": "לא ניתן ליצור סיכום",
                    "document_type": "unknown",
                    "key_points": []
                }
            else:
                return {
                    "summary": "Could not generate summary",
                    "document_type": "unknown",
                    "key_points": []
                }
    
    def _dummy_llm(self, prompt: str) -> str:
        """
        פונקציית LLM דמה כשאין גישה למודלים אמיתיים
        """
        # זיהוי אם השאילתה בעברית או אנגלית
        is_hebrew = any(c in "אבגדהוזחטיכלמנסעפצקרשת" for c in prompt)
        
        # מחזיר תשובות בסיסיות לשאלות נפוצות
        if is_hebrew:
            if "תאריך" in prompt or "מתי" in prompt:
                return "התאריך האחרון המוזכר במסמך הוא 23.03.2025."
            elif "סכום" in prompt or "כמה" in prompt:
                return "הסכום הכולל המוזכר הוא 1,250,000 ₪."
            elif "אחוז" in prompt or "%" in prompt:
                return "האחוז המוזכר הוא 7.5%."
            elif "תיק השקעות" in prompt:
                return """
                {
                    "answer": "תיק ההשקעות שלך מכיל 40% מניות, 30% אג\"ח, 20% מזומנים, ו-10% נדל\"ן. הביצועים השנתיים עומדים על 7.5%.",
                    "confidence": 0.85,
                    "sources": ["דוח תיק השקעות.pdf", "עמוד 3"]
                }
                """
            else:
                return """
                {
                    "answer": "מצאתי מידע רלוונטי במסמכים שלך. המסמכים מציגים דוחות פיננסיים עם פירוט נכסים והקצאות. יש בהם גם מידע על ביצועי השקעות ותחזיות עתידיות.",
                    "confidence": 0.6,
                    "sources": []
                }
                """
        else:
            # English responses
            if "date" in prompt or "when" in prompt:
                return "The last date mentioned in the document is 03/23/2025."
            elif "amount" in prompt or "how much" in prompt:
                return "The total amount mentioned is $350,000."
            elif "percent" in prompt or "%" in prompt:
                return "The percentage mentioned is 7.5%."
            elif "portfolio" in prompt:
                return """
                {
                    "answer": "Your portfolio contains 40% stocks, 30% bonds, 20% cash, and 10% real estate. The annual performance is 7.5%.",
                    "confidence": 0.85,
                    "sources": ["Investment Portfolio Report.pdf", "Page 3"]
                }
                """
            else:
                return """
                {
                    "answer": "I found relevant information in your documents. The documents present financial reports with details of assets and allocations. They also include information on investment performance and future forecasts.",
                    "confidence": 0.6,
                    "sources": []
                }
                """
    
    def _setup_prompts(self) -> None:
        """הגדרת תבניות שאילתה"""
        
        # תבנית לשאלות ותשובות בעברית
        self._qa_prompt_he = PromptTemplate.from_template(
            """
            אתה עוזר פיננסי מקצועי. המשימה שלך היא לענות על שאלות בנוגע למסמכים פיננסיים.
            
            ### הקשר מהמסמכים:
            {context}
            
            ### היסטוריית שיחה:
            {conversation_history}
            
            ### שאלה:
            {question}
            
            ### הנחיות:
            1. ענה רק על סמך המידע בהקשר שסופק. אל תמציא מידע.
            2. אם אינך יכול לענות על שאלה מהמידע שסופק, אמור זאת בכנות.
            3. התמקד במידע פיננסי רלוונטי.
            4. החזר תשובה בפורמט JSON עם השדות הבאים:
               - answer: תשובה מלאה לשאלה
               - confidence: רמת ביטחון בתשובה (0-1)
               - sources: מקורות למידע (אם ידועים)
            
            ### תשובה (בפורמט JSON):
            """
        )
        
        # תבנית לשאלות ותשובות באנגלית
        self._qa_prompt_en = PromptTemplate.from_template(
            """
            You are a professional financial assistant. Your task is to answer questions about financial documents.
            
            ### Context from documents:
            {context}
            
            ### Conversation history:
            {conversation_history}
            
            ### Question:
            {question}
            
            ### Instructions:
            1. Answer only based on the information provided in the context. Do not make up information.
            2. If you cannot answer a question from the provided information, say so honestly.
            3. Focus on relevant financial information.
            4. Return the answer in JSON format with the following fields:
               - answer: Complete answer to the question
               - confidence: Confidence level in the answer (0-1)
               - sources: Sources of information (if known)
            
            ### Answer (in JSON format):
            """
        )
        
        # תבנית לסיכום מסמכים בעברית
        self._summary_prompt_he = PromptTemplate.from_template(
            """
            מסמך פיננסי מוצג בפניך. נתח אותו וצור:
            1. תקציר קצר (עד 3 משפטים)
            2. זיהוי סוג המסמך (דוח בנקאי, דוח תיק השקעות, תדפיס עסקאות, וכו')
            3. 3-5 נקודות מפתח מהמסמך
            
            ### מסמך:
            {document}
            
            ### הנחיות:
            החזר את התשובה בפורמט JSON עם השדות:
            - summary: תקציר המסמך
            - document_type: סוג המסמך
            - key_points: מערך של נקודות מפתח
            
            ### תשובה (בפורמט JSON):
            """
        )
        
        # תבנית לסיכום מסמכים באנגלית
        self._summary_prompt_en = PromptTemplate.from_template(
            """
            A financial document is presented to you. Analyze it and create:
            1. A brief summary (up to 3 sentences)
            2. Identification of the document type (bank report, investment portfolio report, transaction printout, etc.)
            3. 3-5 key points from the document
            
            ### Document:
            {document}
            
            ### Instructions:
            Return the answer in JSON format with the fields:
            - summary: Document summary
            - document_type: Document type
            - key_points: Array of key points
            
            ### Answer (in JSON format):
            """
        )
    
    def _format_conversation_history(self, history: List[Dict[str, str]], language: str = "he") -> str:
        """
        פורמט היסטוריית שיחה לטקסט
        
        Args:
            history: רשימת הודעות בשיחה
            language: שפת הפורמט
            
        Returns:
            str: היסטוריית שיחה מפורמטת
        """
        if not history:
            return ""
        
        formatted_history = ""
        
        for message in history:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if language == "he":
                if role == "user":
                    formatted_history += f"משתמש: {content}\n\n"
                elif role == "assistant":
                    formatted_history += f"עוזר: {content}\n\n"
            else:
                if role == "user":
                    formatted_history += f"User: {content}\n\n"
                elif role == "assistant":
                    formatted_history += f"Assistant: {content}\n\n"
        
        return formatted_history
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        ניתוח תשובה ממודל השפה
        
        Args:
            response: תשובה גולמית ממודל השפה
            
        Returns:
            Dict: מילון מפורמט
        """
        try:
            # ניסיון לנתח את התשובה כ-JSON
            # חיפוש תוכן JSON בתוך טקסט רגיל
            json_pattern = r'(\{[\s\S]*\})'
            match = re.search(json_pattern, response)
            
            if match:
                json_text = match.group(1)
                return json.loads(json_text)
            
            # אם אין JSON, מחזיר את התשובה כמות שהיא
            return {
                "answer": response.strip(),
                "confidence": 0.5,
                "sources": []
            }
            
        except Exception as e:
            logger.error(f"שגיאה בניתוח תשובת LLM: {e}")
            return {
                "answer": response.strip(),
                "confidence": 0.5,
                "sources": []
            }
    
    def _extract_section(self, text: str, section_name: str, section_title: str) -> str:
        """
        חילוץ סעיף מתוך תשובה
        
        Args:
            text: הטקסט המלא
            section_name: שם הסעיף באנגלית לחיפוש
            section_title: כותרת הסעיף לחיפוש
            
        Returns:
            str: תוכן הסעיף
        """
        # חיפוש בפורמט סטנדרטי
        pattern = f'"{section_name}"\s*:\s*"([^"]*)"'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        
        # חיפוש לפי כותרת
        pattern = f'{section_title}:\s*(.*?)(?:\n\n|\n[A-Za-zא-ת])'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return ""
    
    def _extract_list(self, text: str, section_name: str, section_title: str) -> List[str]:
        """
        חילוץ רשימה מתוך תשובה
        
        Args:
            text: הטקסט המלא
            section_name: שם הסעיף באנגלית לחיפוש
            section_title: כותרת הסעיף לחיפוש
            
        Returns:
            List[str]: רשימת פריטים
        """
        # חיפוש בפורמט סטנדרטי
        pattern = f'"{section_name}"\s*:\s*\[(.*?)\]'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            items_str = match.group(1)
            items = re.findall(r'"([^"]*)"', items_str)
            return items
        
        # חיפוש לפי כותרת ורשימה ממוספרת או עם נקודות
        pattern = f'{section_title}:\s*(.*?)(?:\n\n|\Z)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            items_text = match.group(1).strip()
            items = re.findall(r'\d+\.\s*(.*?)(?:\n|$)', items_text)
            if not items:
                items = re.findall(r'[-•]\s*(.*?)(?:\n|$)', items_text)
            return items
        
        return []
    
    def _translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        תרגום טקסט משפה לשפה
        
        Args:
            text: הטקסט לתרגום
            source_lang: שפת המקור
            target_lang: שפת היעד
            
        Returns:
            str: טקסט מתורגם
        """
        try:
            # פונקציית תרגום פשוטה - במערכת אמיתית יש לשלב מודל תרגום
            # כגון מודל מ-HuggingFace או שירות תרגום חיצוני
            
            # עבור המחשה - מילון תרגומים בסיסי
            if source_lang == "he" and target_lang == "en":
                translations = {
                    "דוח בנקאי": "Bank Report",
                    "דוח תיק השקעות": "Investment Portfolio Report",
                    "תדפיס עסקאות": "Transaction Statement",
                    "אין מידע זמין": "No information available",
                    "לא ניתן ליצור סיכום": "Could not generate summary"
                }
                
                for heb, eng in translations.items():
                    text = text.replace(heb, eng)
                
            elif source_lang == "en" and target_lang == "he":
                translations = {
                    "Bank Report": "דוח בנקאי",
                    "Investment Portfolio Report": "דוח תיק השקעות",
                    "Transaction Statement": "תדפיס עסקאות",
                    "No information available": "אין מידע זמין",
                    "Could not generate summary": "לא ניתן ליצור סיכום"
                }
                
                for eng, heb in translations.items():
                    text = text.replace(eng, heb)
            
            return text
            
        except Exception as e:
            logger.error(f"שגיאה בתרגום טקסט: {e}")
            return text
import re
