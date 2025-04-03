import os
import logging
from typing import List, Dict, Any, Optional, Union
import json
import requests
from huggingface_hub import HfApi, HfFolder
import google.generativeai as genai

# הגדרת לוגר
logger = logging.getLogger(__name__)

# מפתחות API
HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')
MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY') # Added Google API Key

class AIModel:
    """
    מעטפת כללית למודלי AI
    """
    def __init__(self, model_name: str = "mistral-7b-instruct", provider: str = "huggingface"):
        """
        אתחול מודל AI
        
        Args:
            model_name: שם המודל לשימוש
            provider: ספק המודל (huggingface/mistral/openai/gemini)
        """
        self.model_name = model_name
        self.provider = provider.lower()
        
        # בדיקת זמינות המודל וה-API Key
        self._check_availability()
    
    def _check_availability(self) -> bool:
        """
        בדיקת זמינות ה-API והמודל
        
        Returns:
            bool: האם המודל זמין
        """
        try:
            if self.provider == "huggingface":
                if not HUGGINGFACE_API_KEY:
                    logger.warning("Hugging Face API key not found")
                    return False
                
                # בדיקת הרשאות ל-Hugging Face
                api = HfApi(token=HUGGINGFACE_API_KEY)
                models = api.list_models(filter="text-generation", limit=1)
                return len(list(models)) > 0
                
            elif self.provider == "mistral":
                if not MISTRAL_API_KEY:
                    logger.warning("Mistral API key not found")
                    return False
                return True
                
            elif self.provider == "openai":
                if not OPENAI_API_KEY:
                    logger.warning("OpenAI API key not found")
                    return False
                return True

            elif self.provider == "gemini":
                if not GOOGLE_API_KEY:
                    logger.warning("Google API key (for Gemini) not found in environment")
                    return False
                try:
                    genai.configure(api_key=GOOGLE_API_KEY)
                    # Attempt a lightweight call to list models
                    models = genai.list_models()
                    # Check if at least one model suitable for text generation exists
                    if any('generateContent' in m.supported_generation_methods for m in models):
                         logger.info("Google GenAI (Gemini) API connection successful.")
                         return True
                    else:
                         logger.warning("No suitable text generation models found for Google GenAI.")
                         return False
                except Exception as e:
                    logger.error(f"Error checking Google GenAI availability: {e}")
                    return False
                
            else:
                logger.warning(f"Unsupported AI provider: {self.provider}")
                return False
                
        except Exception as e:
            logger.error(f"Error checking AI model availability: {e}")
            return False
    
    def generate_text(self, prompt: str, max_length: int = 500) -> str:
        """
        יצירת טקסט באמצעות המודל
        
        Args:
            prompt: הטקסט ההתחלתי
            max_length: אורך מקסימלי של התוצאה
            
        Returns:
            str: הטקסט שנוצר
        """
        try:
            if self.provider == "huggingface":
                return self._generate_text_huggingface(prompt, max_length)
            elif self.provider == "mistral":
                return self._generate_text_mistral(prompt, max_length)
            elif self.provider == "openai":
                return self._generate_text_openai(prompt, max_length)
            elif self.provider == "gemini":
                return self._generate_text_gemini(prompt, max_length)
            else:
                return f"Error: Unsupported provider '{self.provider}'"
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return f"Error generating text: {str(e)}"
    
    def _generate_text_huggingface(self, prompt: str, max_length: int) -> str:
        """
        יצירת טקסט באמצעות Hugging Face API
        """
        API_URL = f"https://api-inference.huggingface.co/models/{self.model_name}"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": max_length,
                "do_sample": True,
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code != 200:
            logger.error(f"Hugging Face API error: {response.text}")
            return f"Error: {response.text}"
        
        # חילוץ התשובה (המבנה תלוי במודל)
        try:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '')
            elif isinstance(result, dict):
                return result.get('generated_text', '')
            else:
                return str(result)
        except Exception as e:
            logger.error(f"Error parsing Hugging Face response: {e}")
            return f"Error parsing response: {str(e)}"
    
    def _generate_text_mistral(self, prompt: str, max_length: int) -> str:
        """
        יצירת טקסט באמצעות Mistral AI API
        """
        if not MISTRAL_API_KEY:
            return "Error: Mistral API key not available"
        
        API_URL = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_length,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code != 200:
            logger.error(f"Mistral API error: {response.text}")
            return f"Error: {response.text}"
        
        result = response.json()
        return result.get('choices', [{}])[0].get('message', {}).get('content', '')
    
    def _generate_text_openai(self, prompt: str, max_length: int) -> str:
        """
        יצירת טקסט באמצעות OpenAI API
        """
        if not OPENAI_API_KEY:
            return "Error: OpenAI API key not available"
        
        API_URL = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_length,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code != 200:
            logger.error(f"OpenAI API error: {response.text}")
            return f"Error: {response.text}"
        
        result = response.json()
        return result.get('choices', [{}])[0].get('message', {}).get('content', '')

    def _generate_text_gemini(self, prompt: str, max_length: int) -> str:
        """
        Generates text using the Google Generative AI (Gemini) API.
        Note: max_length is not directly equivalent to max_tokens for Gemini,
        but we use generation_config for control.
        """
        if not GOOGLE_API_KEY:
            logger.error("Google API key (for Gemini) not available")
            return "Error: Google API key not available"
        
        try:
            # Ensure genai is configured (might be redundant if _check_availability ran)
            genai.configure(api_key=GOOGLE_API_KEY)
            
            # Select the model
            # TODO: Consider making safety_settings configurable
            model = genai.GenerativeModel(self.model_name)
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                # max_output_tokens=max_length, # Use this if precise token limit is needed
                temperature=0.7,
                top_p=0.9
            )
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract the text from the response
            if response.parts:
                return response.text
            elif response.prompt_feedback and response.prompt_feedback.block_reason:
                 # Handle cases where content was blocked due to safety settings
                 block_reason = response.prompt_feedback.block_reason
                 logger.warning(f"Gemini content generation blocked. Reason: {block_reason}")
                 return f"Error: Content generation blocked by safety settings ({block_reason})."
            else:
                # Handle other potential empty response scenarios
                logger.warning(f"Gemini response did not contain expected text parts. Response: {response}")
                return "Error: Received empty or unexpected response from Gemini."

        except Exception as e:
            logger.error(f"Error generating text with Gemini: {e}")
            return f"Error generating text with Gemini: {str(e)}"


class DocumentAnalyzer:
    """
    מנתח מסמכים באמצעות מודלי AI
    """
    def __init__(self, model_name: str = "mistral-7b-instruct", provider: str = "huggingface"):
        """
        אתחול מנתח המסמכים
        
        Args:
            model_name: שם המודל לשימוש
            provider: ספק המודל (huggingface/mistral/openai)
        """
        self.ai_model = AIModel(model_name, provider)
    
    def analyze_financial_document(self, text: str) -> Dict[str, Any]:
        """
        ניתוח מסמך פיננסי והחזרת מידע רלוונטי
        
        Args:
            text: טקסט המסמך
            
        Returns:
            Dict: מידע פיננסי שחולץ מהמסמך
        """
        # יצירת פרומפט לחילוץ מידע פיננסי
        prompt = f"""
        Analyze the following financial document and extract key information:
        
        {text[:2000]}... (document continues)
        
        Please extract and return the following data in JSON format:
        1. Company name
        2. Reporting period
        3. Total revenue
        4. Net profit/loss
        5. Key financial metrics
        6. Important dates mentioned
        """
        
        # ניתוח באמצעות המודל
        response = self.ai_model.generate_text(prompt, max_length=800)
        
        # ניסיון לפרסר את התשובה כ-JSON
        try:
            # חיפוש מבנה JSON בתשובה
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # אם לא נמצא JSON, מחזיר תשובה כמות שהיא במבנה מילון
                return {"analysis": response}
                
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse AI response as JSON: {response}")
            return {"analysis": response}
    
    def answer_question(self, text: str, question: str) -> str:
        """
        מענה לשאלה בהקשר של מסמך
        
        Args:
            text: טקסט המסמך
            question: השאלה לגבי המסמך
            
        Returns:
            str: תשובה לשאלה
        """
        # יצירת פרומפט שמשלב את המסמך והשאלה
        prompt = f"""
        Document:
        {text[:3000]}... (document continues)
        
        Question: {question}
        
        Answer the question based only on the information provided in the document.
        If the answer is not in the document, say "I don't have enough information to answer this question."
        """
        
        # מענה באמצעות המודל
        return self.ai_model.generate_text(prompt, max_length=500)
    
    def summarize_document(self, text: str, max_length: int = 300) -> str:
        """
        סיכום מסמך
        
        Args:
            text: טקסט המסמך
            max_length: אורך מקסימלי של הסיכום
            
        Returns:
            str: סיכום המסמך
        """
        # יצירת פרומפט לסיכום
        prompt = f"""
        Summarize the following document in a concise way:
        
        {text[:4000]}... (document continues)
        
        Key points to include in the summary:
        - Main topic or purpose of the document
        - Key financial information
        - Important conclusions or findings
        """
        
        # סיכום באמצעות המודל
        return self.ai_model.generate_text(prompt, max_length=max_length)
