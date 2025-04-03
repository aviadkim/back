"""AI service for accessing language models."""
import os
import logging
import json
import re
from typing import Dict, Any, Optional, List, Union
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIService:
    """Service for interacting with AI language models"""
    
    def __init__(self):
        # Load API keys and check if they need cleaning
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY", "").strip()
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        
        # Clean up potential Gemini key issues
        if " " in gemini_key:
            gemini_key = gemini_key.split()[-1]
            logger.info("Cleaned up Gemini API key")
            
        self.gemini_api_key = gemini_key
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        
        # Model configuration
        self.default_model = os.getenv("DEFAULT_MODEL", "fallback")
        self.huggingface_model = os.getenv("HUGGINGFACE_MODEL", "google/flan-t5-small")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-pro") 
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat-v3-0324:free")
        
        # Save key validity for later checks - use stricter validation
        self.has_valid_YOUR_HUGGINGFACE_API_KEY = bool(self.huggingface_api_key and len(self.huggingface_api_key) > 20 
                                    and not self.huggingface_api_key.startswith('YOUR_HUGGINGFACE_API_KEY'))
        self.has_valid_gemini_key = bool(self.gemini_api_key and len(self.gemini_api_key) > 20 
                                        and not self.gemini_api_key.startswith('YOUR_GEMINI_API_KEY'))
        self.has_valid_openrouter_key = bool(self.openrouter_api_key and len(self.openrouter_api_key) > 20 
                                            and self.openrouter_api_key.startswith('sk-or-'))
        
        # Print startup info in colorful format for better visibility
        if self.has_valid_openrouter_key:
            logger.info(f"Using OpenRouter with model: {self.openrouter_model}")
        elif not self.has_valid_YOUR_HUGGINGFACE_API_KEY and not self.has_valid_gemini_key:
            logger.warning("No valid API keys found for AI services. Using enhanced fallback responses.")
            logger.info("System will function with basic extraction capabilities.")
        else:
            if self.has_valid_YOUR_HUGGINGFACE_API_KEY:
                logger.info(f"Using Hugging Face model: {self.huggingface_model}")
            if self.has_valid_gemini_key:
                logger.info(f"Using Google Gemini model: {self.gemini_model}")
    
    def generate_response(self, prompt: str, context: str = "", model: Optional[str] = None) -> str:
        """Generate a response from an AI model
        
        Args:
            prompt: The prompt to send to the model
            context: Additional context for the model
            model: Optional model override (openrouter, huggingface, gemini, fallback)
            
        Returns:
            Generated response string
        """
        # Use fallback mode if specified or if it's the default
        model_to_use = model or self.default_model
        
        # Get the full prompt with context if available
        full_prompt = self._format_prompt(prompt, context)
        
        # Try OpenRouter first if available (best quality)
        if (model_to_use == "openrouter" or model_to_use == "default") and self.has_valid_openrouter_key:
            try:
                logger.info("Using OpenRouter API")
                return self._query_openrouter(full_prompt)
            except Exception as e:
                logger.error(f"OpenRouter API error: {e}")
                # Fall back to other models if available
                if self.has_valid_gemini_key:
                    logger.info("Falling back to Gemini")
                    return self._query_gemini(full_prompt)
                elif self.has_valid_YOUR_HUGGINGFACE_API_KEY:
                    logger.info("Falling back to HuggingFace")
                    return self._query_huggingface(full_prompt)
                else:
                    logger.info("Using fallback mode")
                    return self._enhanced_fallback_response(prompt, context)
        
        # Try to generate a response with the specified model or fallback
        try:
            if model_to_use == "huggingface" and self.has_valid_YOUR_HUGGINGFACE_API_KEY:
                try:
                    return self._query_huggingface(full_prompt)
                except Exception as e:
                    logger.error(f"HuggingFace API error: {e}")
                    return self._enhanced_fallback_response(prompt, context)
                    
            elif model_to_use == "gemini" and self.has_valid_gemini_key:
                try:
                    return self._query_gemini(full_prompt)
                except Exception as e:
                    logger.error(f"Gemini API error: {e}")
                    return self._enhanced_fallback_response(prompt, context)
            
            elif model_to_use == "fallback" or not any([self.has_valid_openrouter_key, self.has_valid_YOUR_HUGGINGFACE_API_KEY, self.has_valid_gemini_key]):
                logger.info("Using enhanced fallback response mode")
                return self._enhanced_fallback_response(prompt, context)
                    
            else:
                logger.info(f"Model {model_to_use} not available. Using enhanced fallback response.")
                return self._enhanced_fallback_response(prompt, context)
                
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self._enhanced_fallback_response(prompt, context)
    
    def _format_prompt(self, prompt: str, context: str) -> str:
        """Format the prompt with context"""
        if context:
            return f"""Context information:
{context}

Question: {prompt}

Answer based on the context information. If the answer cannot be found in the context, say so."""
        else:
            return prompt
    
    def _query_openrouter(self, prompt: str) -> str:
        """Query OpenRouter API for a response"""
        # Log the key format (not the whole key for security) to help with debugging
        key_prefix = self.openrouter_api_key[:8] + "..." if self.openrouter_api_key else "None"
        logger.info(f"Using OpenRouter key format: {key_prefix}")
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://financial-document-processor.dev",  # For OpenRouter stats
            "X-Title": "Financial Document Processor"  # For OpenRouter stats
        }
        
        payload = {
            "model": self.openrouter_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Log more details for debugging
        logger.info(f"OpenRouter request to model: {self.openrouter_model}")
        
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            try:
                return result["choices"][0]["message"]["content"].strip()
            except (KeyError, IndexError):
                logger.error(f"Unexpected response format from OpenRouter API: {result}")
                return "I couldn't generate a proper response."
        except requests.exceptions.HTTPError as e:
            logger.error(f"OpenRouter HTTP error: {e} (Status code: {e.response.status_code})")
            logger.error(f"Response text: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"OpenRouter error: {type(e).__name__}: {e}")
            raise
    
    def _query_huggingface(self, prompt: str) -> str:
        """Query Hugging Face API for a response"""
        headers = {
            "Authorization": f"Bearer {self.huggingface_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 250,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True
            }
        }
        
        # Try with a different Hugging Face model if the first one doesn't work
        try:
            api_url = f"https://api-inference.huggingface.co/models/{self.huggingface_model}"
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and result:
                return result[0].get("generated_text", "").replace(prompt, "").strip()
                
            logger.warning(f"Unexpected HuggingFace response format: {result}")
            return "I couldn't generate a proper response."
            
        except requests.RequestException as e:
            logger.warning(f"Error with {self.huggingface_model}: {e}")
            logger.info("Trying with a simpler HuggingFace model")
            
            # Try with a smaller, more reliable model
            try:
                backup_model = "google/flan-t5-small"
                api_url = f"https://api-inference.huggingface.co/models/{backup_model}"
                
                response = requests.post(api_url, headers=headers, json=payload, timeout=10)
                response.raise_for_status()
                
                result = response.json()
                if isinstance(result, list) and result:
                    return result[0].get("generated_text", "").strip()
                    
                return "I couldn't generate a proper response."
                
            except Exception:
                raise
    
    def _query_gemini(self, prompt: str) -> str:
        """Query Google Gemini API for a response"""
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.9,
                "maxOutputTokens": 250
            }
        }
        
        # Attempt to use Google Generative AI Python library if available
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel(self.gemini_model)
            response = model.generate_content(prompt)
            
            return response.text
            
        except ImportError:
            logger.warning("Google Generative AI library not available, using direct API call")
            
            # Fall back to direct API call
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_api_key}"
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            try:
                return result["candidates"][0]["content"]["parts"][0]["text"].strip()
            except (KeyError, IndexError):
                logger.error(f"Unexpected response format from Gemini API: {result}")
                return "I couldn't generate a proper response."
    
    def _enhanced_fallback_response(self, prompt: str, context: str) -> str:
        """Generate an enhanced fallback response using rule-based extraction
        
        This is used when no AI services are available.
        """
        # Convert to lowercase for easier matching
        prompt_lower = prompt.lower()
        
        # Extract specific information based on the question type
        
        # Handle date questions
        if any(word in prompt_lower for word in ["date", "when", "time", "day", "month", "year"]):
            return self._extract_date_information(prompt_lower, context)
            
        # Handle value/amount questions
        if any(word in prompt_lower for word in ["value", "worth", "amount", "price", "cost", "total", "sum"]):
            return self._extract_value_information(prompt_lower, context)
            
        # Handle questions about securities, ISINs, etc.
        if any(word in prompt_lower for word in ["security", "securities", "stock", "isin", "holding"]):
            return self._extract_security_information(prompt_lower, context)
            
        # Handle allocation questions
        if any(word in prompt_lower for word in ["allocation", "percent", "distribution", "breakdown"]):
            return self._extract_allocation_information(prompt_lower, context)
            
        # Handle general content questions with improved snippet extraction
        return self._extract_relevant_snippet(prompt_lower, context)
    
    def _extract_date_information(self, prompt_lower, context):
        """Extract date information from context"""
        # Common date formats
        date_patterns = [
            r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY or DD/MM/YYYY
            r'(\d{4}-\d{2}-\d{2})',      # YYYY-MM-DD
            r'(\d{1,2}\.\d{1,2}\.\d{4})', # DD.MM.YYYY
            r'([A-Z][a-z]+ \d{1,2},? \d{4})',  # Month DD, YYYY
            r'(\d{1,2} [A-Z][a-z]+ \d{4})'     # DD Month YYYY
        ]
        
        # Try to identify specific date types
        valuation_date = None
        report_date = None
        other_dates = []
        
        for pattern in date_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            for match in matches:
                # Look at surrounding text to determine date type
                snippet = self._get_surrounding_text(context, match, 30)
                if "valuation" in snippet.lower():
                    valuation_date = match
                elif "report" in snippet.lower() or "statement" in snippet.lower():
                    report_date = match
                else:
                    other_dates.append(match)
        
        # Respond based on the specific question
        if "valuation" in prompt_lower and valuation_date:
            return f"The valuation date is {valuation_date}."
        elif "report" in prompt_lower and report_date:
            return f"The report date is {report_date}."
        elif valuation_date:
            return f"The document has a valuation date of {valuation_date}."
        elif report_date:
            return f"The document has a report date of {report_date}."
        elif other_dates:
            if len(other_dates) == 1:
                return f"I found this date in the document: {other_dates[0]}"
            else:
                return f"I found several dates in the document: {', '.join(other_dates[:3])}" + ("..." if len(other_dates) > 3 else "")
        else:
            return "I couldn't find any dates in the document."
    
    def _extract_value_information(self, prompt_lower, context):
        """Extract value/amount information from context"""
        # Look for currency values
        money_patterns = [
            r'(\$[\d,]+\.?\d*)',  # $1,000.00
            r'(€[\d,]+\.?\d*)',   # €1,000.00
            r'(£[\d,]+\.?\d*)',   # £1,000.00
            r'(USD [\d,]+\.?\d*)', # USD 1,000.00
            r'(EUR [\d,]+\.?\d*)', # EUR 1,000.00
            r'([\d,]+\.?\d* dollars)', # 1,000.00 dollars
            r'([\d,]+\.?\d* euros)'    # 1,000.00 euros
        ]
        
        found_values = []
        portfolio_value = None
        
        # Search for portfolio value specifically
        portfolio_value_pattern = r'portfolio value .{0,20}([\$€£][\d,]+\.?\d*|[\d,]+\.?\d* (?:dollars|euros|USD|EUR))'
        portfolio_match = re.search(portfolio_value_pattern, context, re.IGNORECASE)
        if portfolio_match:
            portfolio_value = portfolio_match.group(1)
        
        # Find other values
        for pattern in money_patterns:
            matches = re.findall(pattern, context)
            for match in matches:
                if match != portfolio_value:  # Avoid duplicating portfolio value
                    found_values.append(match)
        
        # Respond based on the question
        if "portfolio" in prompt_lower and "value" in prompt_lower and portfolio_value:
            return f"The total portfolio value is {portfolio_value}."
        elif "portfolio" in prompt_lower and portfolio_value:
            return f"The portfolio is valued at {portfolio_value}."
        elif found_values:
            if len(found_values) == 1:
                return f"I found this value: {found_values[0]}"
            else:
                return f"I found these values: {', '.join(found_values[:5])}" + ("..." if len(found_values) > 5 else "")
        else:
            return "I couldn't find specific value information in the document."
    
    def _extract_security_information(self, prompt_lower, context):
        """Extract information about securities from context"""
        # Look for ISINs
        isin_pattern = r'([A-Z]{2}[A-Z0-9]{10})'
        isins = re.findall(isin_pattern, context)
        
        # Look for security names
        # Common company suffixes
        suffixes = r'Inc|Corp|Ltd|LLC|PLC|SA|AG|NV|SE'
        security_pattern = r'([A-Z][A-Za-z\.\s]+(?:' + suffixes + r'))'
        securities = re.findall(security_pattern, context)
        
        # Map ISINs to names if they appear together
        security_mappings = {}
        for isin in isins:
            # Get surrounding text
            surrounding = self._get_surrounding_text(context, isin, 50)
            # Look for company name near ISIN
            for security in securities:
                if security in surrounding:
                    security_mappings[isin] = security
                    break
        
        # Respond based on question
        if "isin" in prompt_lower:
            if isins:
                if len(isins) == 1:
                    isin = isins[0]
                    name = security_mappings.get(isin, "unknown security")
                    return f"I found this ISIN: {isin} ({name})"
                else:
                    return f"I found these ISINs: {', '.join(isins[:5])}" + ("..." if len(isins) > 5 else "")
            else:
                return "I couldn't find any ISINs in the document."
        elif any(name.lower() in prompt_lower for name in securities):
            # Question about a specific security
            for name in securities:
                if name.lower() in prompt_lower:
                    # Find the ISIN for this security
                    isin = next((i for i, n in security_mappings.items() if n == name), "unknown")
                    return f"Information about {name}: ISIN: {isin}"
            return "I couldn't find information about that specific security."
        else:
            # General security question
            if securities:
                if len(securities) <= 3:
                    return f"The document mentions these securities: {', '.join(securities)}"
                else:
                    return f"The document mentions {len(securities)} securities, including: {', '.join(securities[:3])}..."
            else:
                return "I couldn't find information about securities in the document."
    
    def _extract_allocation_information(self, prompt_lower, context):
        """Extract allocation or percentage information"""
        # Look for allocation patterns like "XX%"
        percentage_pattern = r'(\d+(?:\.\d+)?%)'
        percentages = re.findall(percentage_pattern, context)
        
        # Look for allocation categories with percentages
        allocation_pattern = r'([A-Za-z]+):\s*(\d+(?:\.\d+)?%)'
        allocations = re.findall(allocation_pattern, context)
        
        # Also look for words followed by percentages
        category_pattern = r'([A-Za-z]+)[\s:](\d+(?:\.\d+)?%)'
        categories = re.findall(category_pattern, context)
        
        if "portfolio" in prompt_lower and "allocation" in prompt_lower:
            if allocations:
                allocation_str = ", ".join([f"{a[0]}: {a[1]}" for a in allocations])
                return f"The portfolio allocation is: {allocation_str}"
            elif categories:
                category_str = ", ".join([f"{c[0]}: {c[1]}" for c in categories])
                return f"The allocation appears to be: {category_str}"
            elif percentages:
                return f"I found these percentages which might be related to allocation: {', '.join(percentages)}"
            else:
                return "I couldn't find portfolio allocation information in the document."
        else:
            if percentages:
                return f"I found these percentages: {', '.join(percentages)}"
            else:
                return "I couldn't find percentage information in the document."
    
    def _extract_relevant_snippet(self, prompt_lower, context):
        """Extract a relevant snippet based on the question"""
        # Remove stop words from prompt
        stop_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 
                     'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about', 'like', 'through'}
        words = [w for w in prompt_lower.split() if w not in stop_words and len(w) > 2]
        
        # Find the most relevant sentence containing keywords
        sentences = re.split(r'(?<=[.!?])\s+', context)
        best_sentence = ""
        best_score = 0
        
        for sentence in sentences:
            score = sum(1 for word in words if word in sentence.lower())
            if score > best_score:
                best_score = score
                best_sentence = sentence
        
        if best_score > 0:
            return f"Based on your question, I found this relevant information: \"{best_sentence.strip()}\""
        else:
            # Try keyword matching if no sentence matched well
            for word in words:
                if len(word) > 3 and word in context.lower():
                    start = context.lower().find(word)
                    snippet_start = max(0, start - 50)
                    snippet_end = min(len(context), start + len(word) + 100)
                    snippet = context[snippet_start:snippet_end]
                    return f"I found this information that might be relevant: \"...{snippet}...\""
            
            return "I couldn't find information directly related to your question in the document."
    
    def _get_surrounding_text(self, text, target, window=30):
        """Get text surrounding a target string"""
        if target not in text:
            return ""
            
        start = max(0, text.find(target) - window)
        end = min(len(text), text.find(target) + len(target) + window)
        return text[start:end]
