import os
import logging
import requests
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from config.aws_config import GEMINI_API_KEY, HUGGINGFACE_API_KEY, OPENAI_API_KEY

class AIService:
    """שירות לעיבוד טקסט באמצעות מודלי AI"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.openai_api_key = OPENAI_API_KEY
        self.gemini_api_key = GEMINI_API_KEY
        self.huggingface_api_key = HUGGINGFACE_API_KEY

        # בחר את המודל הזמין
        if self.openai_api_key:
            self.model_type = 'openai'
        elif self.gemini_api_key:
            self.model_type = 'gemini'
        elif self.huggingface_api_key:
            self.model_type = 'huggingface'
        else:
            self.model_type = None
            self.logger.warning("No AI model API keys found.")

    def ask_question(self, question, context):
        """שאל שאלה על טקסט"""
        if not self.model_type:
            return "AI service not configured. Please provide API keys."

        try:
            if self.model_type == 'openai':
                return self._ask_openai(question, context)
            elif self.model_type == 'gemini':
                return self._ask_gemini(question, context)
            elif self.model_type == 'huggingface':
                return self._ask_huggingface(question, context)
        except Exception as e:
            self.logger.error(f"Error in AI questioning: {str(e)}")
            return f"Error processing question: {str(e)}"

    def analyze_text(self, text):
        """ניתוח תוכן טקסט לזיהוי ישויות ותובנות"""
        if not self.model_type:
            return {"error": "AI service not configured. Please provide API keys."}

        try:
            prompt = f"""
            Analyze the following financial document text and extract:
            1. Document type (annual report, quarterly report, portfolio statement, etc.)
            2. ISIN codes (format: XX0000000000)
            3. Company names
            4. Financial metrics (numbers, percentages, dates)
            5. Key financial ratios

            Text:
            {text[:4000]}  # limit text length

            Respond with a JSON structure with these categories.
            """

            if self.model_type == 'openai':
                return self._analyze_openai(prompt)
            elif self.model_type == 'gemini':
                return self._analyze_gemini(prompt)
            elif self.model_type == 'huggingface':
                return self._analyze_huggingface(prompt)
        except Exception as e:
            self.logger.error(f"Error in AI analysis: {str(e)}")
            return {"error": f"Error analyzing text: {str(e)}"}

    def _ask_openai(self, question, context):
        """שאל שאלה באמצעות OpenAI"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }

        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are a financial document assistant. Answer questions using only the context provided."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
            ],
            "temperature": 0.3,
            "max_tokens": 500
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")

    def _ask_gemini(self, question, context):
        """שאל שאלה באמצעות Google Gemini"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_api_key}"

        data = {
            "contents": [
                {
                    "parts": [
                        {"text": f"You are a financial document assistant. Answer using only the context provided.\n\nContext: {context}\n\nQuestion: {question}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 500
            }
        }

        response = requests.post(url, json=data)

        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            raise Exception(f"Gemini API error: {response.status_code} - {response.text}")

    def _ask_huggingface(self, question, context):
        """שאל שאלה באמצעות Hugging Face"""
        headers = {
            "Authorization": f"Bearer {self.huggingface_api_key}"
        }

        # שימוש במודל מתאים משירות Inference API
        api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

        prompt = f"""
        <s>[INST] You are a financial document assistant. Answer using only the context provided.

        Context: {context}

        Question: {question} [/INST]</s>
        """

        response = requests.post(api_url, headers=headers, json={"inputs": prompt})

        if response.status_code == 200:
            return response.json()[0]["generated_text"].split("[/INST]</s>")[-1].strip()
        else:
            raise Exception(f"Hugging Face API error: {response.status_code} - {response.text}")

    def _analyze_openai(self, prompt):
        """ניתוח תוכן באמצעות OpenAI"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }

        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1000
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )

        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            # חילוץ ה-JSON מהתשובה
            try:
                # מנסה למצוא מבנה JSON בתשובה
                json_str = content
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0]
                return json.loads(json_str)
            except:
                return {"text_analysis": content}
        else:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")

    def _analyze_gemini(self, prompt):
        """ניתוח תוכן באמצעות Google Gemini"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_api_key}"

        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1000
            }
        }

        response = requests.post(url, json=data)

        if response.status_code == 200:
            content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            # חילוץ ה-JSON מהתשובה
            try:
                # מנסה למצוא מבנה JSON בתשובה
                json_str = content
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0]
                return json.loads(json_str)
            except:
                return {"text_analysis": content}
        else:
            raise Exception(f"Gemini API error: {response.status_code} - {response.text}")

    def _analyze_huggingface(self, prompt):
        """ניתוח תוכן באמצעות Hugging Face"""
        headers = {
            "Authorization": f"Bearer {self.huggingface_api_key}"
        }

        # שימוש במודל מתאים משירות Inference API
        api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

        response = requests.post(api_url, headers=headers, json={"inputs": prompt})

        if response.status_code == 200:
            content = response.json()[0]["generated_text"]
            # חילוץ ה-JSON מהתשובה
            try:
                # מנסה למצוא מבנה JSON בתשובה
                json_str = content
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0]
                return json.loads(json_str)
            except:
                return {"text_analysis": content}
        else:
            raise Exception(f"Hugging Face API error: {response.status_code} - {response.text}")