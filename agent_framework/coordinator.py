import os
import logging
import json
import re
from typing import List, Dict, Any, Optional
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import Document as LangchainDocument
from langchain.chains import LLMChain
from langchain.callbacks import get_openai_callback
from .memory_agent import MemoryAgent

# Set up logging
logger = logging.getLogger(__name__)

class AgentCoordinator:
    """
    Coordinator for AI agents in the document processing system
    
    This class manages the coordination between different agents and components
    to provide advanced AI capabilities for document analysis and chat.
    """
    
    def __init__(self):
        """Initialize the agent coordinator"""
        # Load API keys from environment variables
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        self.huggingface_api_key = os.environ.get('HUGGINGFACE_API_KEY')
        self.mistral_api_key = os.environ.get('MISTRAL_API_KEY')
        
        # Choose LLM based on available API keys
        self._setup_llm()
        
        # Initialize memory agent
        self.memory_agent = MemoryAgent()
        
    def _setup_llm(self):
        """Set up the Language Model based on available API keys"""
        if self.openai_api_key:
            # Use OpenAI GPT if available
            self.llm = ChatOpenAI(
                model_name="gpt-4o", 
                temperature=0,
                api_key=self.openai_api_key
            )
            self.llm_provider = "openai"
            logger.info("Using OpenAI GPT-4o for agent.")
        elif self.mistral_api_key:
            # Use Mistral AI if available
            # Note: Requires mistralai package to be installed
            try:
                from langchain.chat_models import ChatMistralAI
                self.llm = ChatMistralAI(
                    model="mistral-large-latest", 
                    temperature=0,
                    api_key=self.mistral_api_key
                )
                self.llm_provider = "mistral"
                logger.info("Using Mistral AI for agent.")
            except ImportError:
                logger.warning("Mistral AI package not installed. Falling back to other providers.")
                self.llm = None
                self.llm_provider = None
        elif self.huggingface_api_key:
            # Use Hugging Face model if available
            try:
                from langchain.llms import HuggingFaceHub
                self.llm = HuggingFaceHub(
                    repo_id="meta-llama/Llama-2-70b-chat-hf",
                    temperature=0,
                    huggingfacehub_api_token=self.huggingface_api_key
                )
                self.llm_provider = "huggingface"
                logger.info("Using Hugging Face model for agent.")
            except ImportError:
                logger.warning("Hugging Face Hub package not installed. No LLM available.")
                self.llm = None
                self.llm_provider = None
        else:
            # No LLM available
            logger.warning("No API keys found for any LLM provider. AI functionality will be limited.")
            self.llm = None
            self.llm_provider = None
            
    def analyze_document(self, document_id: str, text_content: str, document_type: str, language: str) -> Dict[str, Any]:
        """
        Analyze document content with AI
        
        Args:
            document_id (str): The document ID
            text_content (str): The document text content
            document_type (str): The document type
            language (str): The document language
            
        Returns:
            dict: Analysis results with tables, entities, and financial data
        """
        if not self.llm:
            logger.warning("No LLM available for document analysis.")
            return {
                "tables": [],
                "entities": [],
                "financial_data": {}
            }
            
        try:
            logger.info(f"Analyzing document {document_id} of type {document_type}")
            
            # Select prompt based on document type and language
            system_prompt = self._get_analysis_system_prompt(document_type, language)
            
            # Prepare prompt template
            prompt = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(system_prompt),
                HumanMessagePromptTemplate.from_template("{text}")
            ])
            
            # Create LLM chain
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Track token usage
            with get_openai_callback() as cb:
                # Limit text content to avoid token limits
                max_tokens = 12000  # Approximate limit for context
                truncated_text = self._truncate_text(text_content, max_tokens)
                
                # Run the chain
                result = chain.run(text=truncated_text)
                
                logger.info(f"Analysis completed with {cb.total_tokens} tokens ({cb.prompt_tokens} prompt, {cb.completion_tokens} completion)")
            
            # Parse the result
            try:
                # The result should be in JSON format
                result_json = json.loads(result)
                return {
                    "tables": result_json.get("tables", []),
                    "entities": result_json.get("entities", []),
                    "financial_data": result_json.get("financial_data", {})
                }
            except json.JSONDecodeError:
                logger.error(f"Failed to parse analysis result as JSON: {result[:500]}...")
                # Try to extract JSON from the text (sometimes the model adds extra text)
                json_str = self._extract_json_from_text(result)
                if json_str:
                    result_json = json.loads(json_str)
                    return {
                        "tables": result_json.get("tables", []),
                        "entities": result_json.get("entities", []),
                        "financial_data": result_json.get("financial_data", {})
                    }
                    
                # Return empty results if parsing fails
                return {
                    "tables": [],
                    "entities": [],
                    "financial_data": {}
                }
                
        except Exception as e:
            logger.exception(f"Error analyzing document {document_id}: {str(e)}")
            return {
                "tables": [],
                "entities": [],
                "financial_data": {}
            }
            
    def process_query(
        self, 
        query: str, 
        document_ids: List[str], 
        language: str = 'he',
        chat_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Process a chat query about documents
        
        Args:
            query (str): The user query
            document_ids (List[str]): List of document IDs to reference
            language (str): The query language
            chat_history (List[Dict]): Chat history as a list of message objects
            
        Returns:
            dict: Response with answer, document references, and suggested questions
        """
        if not self.llm:
            logger.warning("No LLM available for query processing.")
            return {
                "answer": "I'm sorry, but the AI service is currently unavailable. Please try again later.",
                "document_references": [],
                "suggested_questions": []
            }
            
        try:
            logger.info(f"Processing query: {query}")
            
            # Get relevant document context from memory agent
            document_contexts = []
            document_references = []
            
            for doc_id in document_ids:
                context = self.memory_agent.get_document_context(doc_id, query)
                if context:
                    document_contexts.append(context["content"])
                    document_references.append({
                        "document_id": doc_id,
                        "title": context.get("title", "Unknown Document"),
                        "relevance": "high"
                    })
            
            # If no context was found, return a message
            if not document_contexts:
                return {
                    "answer": "I couldn't find any relevant information in the documents you provided. Please try a different question or upload more documents.",
                    "document_references": [],
                    "suggested_questions": self._generate_general_questions(language)
                }
                
            # Combine document contexts
            combined_context = "\n\n".join(document_contexts)
            
            # Format chat history if provided
            formatted_history = ""
            if chat_history and len(chat_history) > 0:
                # Get last few messages (up to 10)
                recent_history = chat_history[-10:]
                for msg in recent_history:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    
                    if role == "user":
                        formatted_history += f"User: {content}\n"
                    elif role == "assistant":
                        formatted_history += f"Assistant: {content}\n"
            
            # Select prompt based on language
            system_prompt = self._get_chat_system_prompt(language)
            
            # Prepare prompt template
            prompt = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(system_prompt),
                HumanMessagePromptTemplate.from_template(
                    "Document Context:\n{context}\n\n"
                    "Chat History:\n{history}\n\n"
                    "User Query: {query}\n\n"
                    "Provide your answer in {language}."
                )
            ])
            
            # Create LLM chain
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Track token usage
            with get_openai_callback() as cb:
                # Ensure we don't exceed token limits
                max_context_tokens = 6000  # Reserve space for the rest of the prompt
                truncated_context = self._truncate_text(combined_context, max_context_tokens)
                
                # Run the chain
                result = chain.run(
                    context=truncated_context,
                    history=formatted_history,
                    query=query,
                    language=language
                )
                
                logger.info(f"Query processed with {cb.total_tokens} tokens ({cb.prompt_tokens} prompt, {cb.completion_tokens} completion)")
            
            # Generate suggested follow-up questions
            suggested_questions = self._generate_suggested_questions(query, result, language)
            
            return {
                "answer": result,
                "document_references": document_references,
                "suggested_questions": suggested_questions
            }
            
        except Exception as e:
            logger.exception(f"Error processing query: {str(e)}")
            return {
                "answer": f"I'm sorry, but I encountered an error while processing your query. Please try again.",
                "document_references": [],
                "suggested_questions": []
            }
            
    def generate_table(self, document_ids: List[str], table_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a table from document data
        
        Args:
            document_ids (List[str]): List of document IDs to extract data from
            table_spec (Dict): Table specification with columns, filters, etc.
            
        Returns:
            dict: Generated table data
        """
        if not self.llm:
            logger.warning("No LLM available for table generation.")
            return {
                "table_data": {
                    "headers": [],
                    "rows": []
                }
            }
            
        try:
            logger.info(f"Generating table with spec: {table_spec}")
            
            # Get document contexts
            document_contexts = []
            for doc_id in document_ids:
                # For tables, we need more complete document content
                context = self.memory_agent.get_document_full_content(doc_id)
                if context:
                    document_contexts.append(context)
            
            # If no context was found, return empty table
            if not document_contexts:
                return {
                    "table_data": {
                        "headers": [],
                        "rows": []
                    }
                }
                
            # Combine document contexts
            combined_context = "\n\n".join(document_contexts)
            
            # Format table specification
            formatted_spec = json.dumps(table_spec, ensure_ascii=False, indent=2)
            
            # Prepare system prompt for table generation
            system_prompt = """You are a financial data extraction specialist. Your task is to extract structured data from financial documents and generate tables according to specifications.

Follow these guidelines:
1. Analyze the document content carefully to identify relevant data.
2. Extract data according to the provided table specification.
3. Format the data into a structured table with headers and rows.
4. Apply any filters or sorting specified in the table specification.
5. Return your response in valid JSON format that matches this structure:
{
  "table_data": {
    "headers": ["Column1", "Column2", ...],
    "rows": [
      ["Value1", "Value2", ...],
      ["Value1", "Value2", ...],
      ...
    ]
  }
}

Be precise and ensure all data is correctly extracted. If you cannot find data for a requested column, use null or appropriate placeholders."""
            
            # Prepare prompt template
            prompt = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(system_prompt),
                HumanMessagePromptTemplate.from_template(
                    "Document Content:\n{context}\n\n"
                    "Table Specification:\n{spec}\n\n"
                    "Generate a table according to this specification. Return ONLY the JSON structure with the table data."
                )
            ])
            
            # Create LLM chain
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Track token usage
            with get_openai_callback() as cb:
                # Ensure we don't exceed token limits
                max_context_tokens = 7000  # Reserve space for the rest of the prompt
                truncated_context = self._truncate_text(combined_context, max_context_tokens)
                
                # Run the chain
                result = chain.run(
                    context=truncated_context,
                    spec=formatted_spec
                )
                
                logger.info(f"Table generation completed with {cb.total_tokens} tokens ({cb.prompt_tokens} prompt, {cb.completion_tokens} completion)")
            
            # Parse the result
            try:
                # The result should be in JSON format
                result_json = json.loads(result)
                return result_json
            except json.JSONDecodeError:
                logger.error(f"Failed to parse table generation result as JSON: {result[:500]}...")
                # Try to extract JSON from the text
                json_str = self._extract_json_from_text(result)
                if json_str:
                    result_json = json.loads(json_str)
                    return result_json
                    
                # Return empty table if parsing fails
                return {
                    "table_data": {
                        "headers": [],
                        "rows": []
                    }
                }
                
        except Exception as e:
            logger.exception(f"Error generating table: {str(e)}")
            return {
                "table_data": {
                    "headers": [],
                    "rows": []
                }
            }
            
    def _truncate_text(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to fit within token limit
        
        Args:
            text (str): The text to truncate
            max_tokens (int): Maximum number of tokens
            
        Returns:
            str: Truncated text
        """


    def _truncate_text(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to fit within token limit
        
        Args:
            text (str): The text to truncate
            max_tokens (int): Maximum number of tokens
            
        Returns:
            str: Truncated text
        """
        # Very rough approximation: 1 token ~= 4 characters for English, ~= 2-3 characters for Hebrew
        avg_chars_per_token = 3  # Conservative estimate
        max_chars = max_tokens * avg_chars_per_token
        
        if len(text) <= max_chars:
            return text
            
        # If text is too long, truncate from middle to keep beginning and end
        # This is often better for financial documents where important info is at the start and end
        keep_start = int(max_chars * 0.7)  # Keep more from the start
        keep_end = int(max_chars * 0.3)    # Keep less from the end
        
        truncated = text[:keep_start] + "\n\n[...content truncated for length...]\n\n" + text[-keep_end:]
        
        return truncated
    
    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """
        Extract JSON string from text
        
        Args:
            text (str): Text that may contain JSON
            
        Returns:
            Optional[str]: Extracted JSON string or None
        """
        # Look for JSON between curly braces
        match = re.search(r'({[\s\S]*})', text)
        if match:
            json_str = match.group(1)
            try:
                # Validate it's valid JSON
                json.loads(json_str)
                return json_str
            except json.JSONDecodeError:
                pass
                
        # Look for JSON between triple backticks
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if match:
            json_str = match.group(1)
            try:
                # Validate it's valid JSON
                json.loads(json_str)
                return json_str
            except json.JSONDecodeError:
                pass
                
        return None
    
    def _get_analysis_system_prompt(self, document_type: str, language: str) -> str:
        """
        Get system prompt for document analysis based on document type and language
        
        Args:
            document_type (str): Document type
            language (str): Document language
            
        Returns:
            str: System prompt
        """
        # Base prompt template
        if language == 'he':
            base_prompt = """אתה מומחה לניתוח מסמכים פיננסיים. המשימה שלך היא לנתח את המסמך המצורף ולחלץ ממנו מידע מובנה.

עליך לנתח את תוכן המסמך ולחזור עם המידע הבא במבנה JSON:
1. טבלאות שמופיעות במסמך (tables)
2. ישויות מזוהות כגון תאריכים, סכומים, מספרי חשבון, וכדומה (entities)
3. נתונים פיננסיים כגון סכומים, יתרות, תשואות, וכדומה (financial_data)

החזר את התוצאה במבנה JSON תקין בפורמט הבא:
{
  "tables": [
    {
      "headers": ["כותרת1", "כותרת2", ...],
      "rows": [
        ["ערך1", "ערך2", ...],
        ["ערך1", "ערך2", ...],
        ...
      ]
    }
  ],
  "entities": [
    {
      "type": "סוג הישות (DATE, AMOUNT, ACCOUNT_NUMBER, וכו')",
      "text": "הטקסט המקורי",
      "value": "הערך המעובד (למשל תאריך מתוקנן)",
      "confidence": 0.95
    }
  ],
  "financial_data": {
    "סוג נתון פיננסי": "ערך"
  }
}

בנוסף, תוכל להתאים את הניתוח לסוג המסמך הספציפי."""
        else:
            base_prompt = """You are a financial document analysis expert. Your task is to analyze the provided document and extract structured information.

Analyze the document content and return the following information in JSON format:
1. Tables that appear in the document (tables)
2. Identified entities such as dates, amounts, account numbers, etc. (entities)
3. Financial data such as sums, balances, returns, etc. (financial_data)

Return the result in valid JSON format as follows:
{
  "tables": [
    {
      "headers": ["Header1", "Header2", ...],
      "rows": [
        ["Value1", "Value2", ...],
        ["Value1", "Value2", ...],
        ...
      ]
    }
  ],
  "entities": [
    {
      "type": "Entity type (DATE, AMOUNT, ACCOUNT_NUMBER, etc.)",
      "text": "Original text",
      "value": "Processed value (e.g., normalized date)",
      "confidence": 0.95
    }
  ],
  "financial_data": {
    "financial_data_type": "value"
  }
}

Additionally, adapt your analysis to the specific document type."""
        
        # Add document-specific instructions
        document_specific = ""
        if document_type == 'bankStatement':
            if language == 'he':
                document_specific = """
זהו דף חשבון בנק. תן תשומת לב מיוחדת ל:
- יתרת החשבון הנוכחית
- תנועות אחרונות בחשבון (הפקדות, משיכות, העברות)
- עמלות ודמי ניהול
- פרטי החשבון (מספר חשבון, סניף, וכו')
"""
            else:
                document_specific = """
This is a bank statement. Pay special attention to:
- Current account balance
- Recent account transactions (deposits, withdrawals, transfers)
- Fees and management charges
- Account details (account number, branch, etc.)
"""
        elif document_type == 'investmentReport':
            if language == 'he':
                document_specific = """
זהו דוח השקעות. תן תשומת לב מיוחדת ל:
- שווי תיק ההשקעות הכולל
- הקצאת נכסים (מניות, אג"ח, מזומן, וכו')
- ביצועי ההשקעות (תשואות)
- עמלות ודמי ניהול
- חשיפה מטבעית
"""
            else:
                document_specific = """
This is an investment report. Pay special attention to:
- Total portfolio value
- Asset allocation (stocks, bonds, cash, etc.)
- Investment performance (returns)
- Fees and management charges
- Currency exposure
"""
        elif document_type == 'taxDocument':
            if language == 'he':
                document_specific = """
זהו מסמך מס. תן תשומת לב מיוחדת ל:
- סכומי מס לתשלום או החזר
- הכנסות מדווחות
- ניכויים וזיכויים
- פרטי הנישום
"""
            else:
                document_specific = """
This is a tax document. Pay special attention to:
- Tax amounts due or refund
- Reported income
- Deductions and credits
- Taxpayer details
"""
        elif document_type == 'invoice':
            if language == 'he':
                document_specific = """
זוהי חשבונית. תן תשומת לב מיוחדת ל:
- סכום לתשלום
- פרטי המוצרים או השירותים
- מע"מ
- פרטי הספק והלקוח
- תאריך ומספר חשבונית
"""
            else:
                document_specific = """
This is an invoice. Pay special attention to:
- Amount due
- Product or service details
- VAT/tax
- Supplier and customer details
- Date and invoice number
"""
        
        return base_prompt + document_specific
    
    def _get_chat_system_prompt(self, language: str) -> str:
        """
        Get system prompt for chat based on language
        
        Args:
            language (str): Chat language
            
        Returns:
            str: System prompt
        """
        if language == 'he':
            return """אתה עוזר פיננסי מומחה שעוזר למשתמשים להבין את המסמכים הפיננסיים שלהם.

המשימה שלך היא לענות על שאלות המשתמש לגבי המסמכים שלו בצורה מדויקת ומועילה, תוך הסתמכות על ההקשר שסופק.

הדרכות:
1. היעזר בהקשר המסמך שסופק כדי לענות על שאלות.
2. אם המידע הדרוש לא נמצא בהקשר, ציין זאת בבירור.
3. התאם את התשובות שלך לשפה העברית ולמונחים פיננסיים בעברית.
4. תן הסברים ברורים ופשוטים למושגים פיננסיים מורכבים.
5. אם אתה מתייחס למספרים או נתונים ממסמכים, וודא שהם מדויקים.
6. אל תמציא או תשער מידע שאינו נוכח בהקשר שסופק.

ענה בעברית תקנית וברורה."""
        else:
            return """You are an expert financial assistant helping users understand their financial documents.

Your task is to answer the user's questions about their documents accurately and helpfully, based on the provided context.

Guidelines:
1. Use the provided document context to answer questions.
2. If the necessary information is not in the context, clearly state this.
3. Tailor your answers to the English language and financial terminology.
4. Provide clear and simple explanations for complex financial concepts.
5. When referring to numbers or data from documents, ensure they are accurate.
6. Do not make up or guess information that is not present in the provided context.

Answer in clear and proper English."""
    
    def _generate_suggested_questions(self, query: str, response: str, language: str) -> List[str]:
        """
        Generate suggested follow-up questions based on query and response
        
        Args:
            query (str): User query
            response (str): Assistant response
            language (str): Language
            
        Returns:
            List[str]: Suggested questions
        """
        # If we have a working LLM, use it to generate better suggestions
        if self.llm:
            try:
                system_prompt = """Based on the user's query and your response, generate 3 relevant follow-up questions that the user might want to ask next. The questions should be directly related to the content discussed and should help the user explore the topic further.

Return ONLY the questions as a JSON array of strings. For example:
["Question 1?", "Question 2?", "Question 3?"]

Make sure the questions are:
1. Relevant to the current conversation
2. Not redundant with information already provided
3. Likely to provide valuable additional information
4. Written in the same language as the conversation"""

                prompt = ChatPromptTemplate.from_messages([
                    SystemMessagePromptTemplate.from_template(system_prompt),
                    HumanMessagePromptTemplate.from_template(
                        "User Query: {query}\n\n"
                        "Your Response: {response}\n\n"
                        "Language: {language}\n\n"
                        "Generate 3 suggested follow-up questions:"
                    )
                ])
                
                chain = LLMChain(llm=self.llm, prompt=prompt)
                result = chain.run(query=query, response=response, language=language)
                
                # Try to parse the result as JSON
                try:
                    suggestions = json.loads(result)
                    if isinstance(suggestions, list) and len(suggestions) > 0:
                        # Limit to 3 suggestions
                        return suggestions[:3]
                except:
                    pass
            except Exception as e:
                logger.warning(f"Error generating suggested questions: {str(e)}")
        
        # Fallback to document-type specific questions
        return self._generate_general_questions(language)
    
    def _generate_general_questions(self, language: str) -> List[str]:
        """
        Generate general financial questions based on language
        
        Args:
            language (str): Language
            
        Returns:
            List[str]: General questions
        """
        if language == 'he':
            return [
                "מה היתרה העדכנית בחשבון שלי?",
                "מהן ההוצאות הגדולות ביותר בחודש האחרון?",
                "מהי התשואה הכוללת של תיק ההשקעות שלי?",
                "האם יש המלצות לחיסכון בהוצאות?"
            ]
        else:
            return [
                "What is my current account balance?",
                "What are my largest expenses in the last month?",
                "What is the overall return of my investment portfolio?",
                "Are there any recommendations for saving on expenses?"
            ]    
        # Very rough approximation: 1 token ~= 4 characters for
