import os
import logging
import json
import re
from typing import List, Dict, Any, Optional, Callable

# Langchain v0.1.x+ imports
from langchain_openai import ChatOpenAI
from langchain_mistralai import ChatMistralAI
from langchain_community.llms import HuggingFaceHub
from .fix_openrouter import ChatOpenRouter # Import custom implementation
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.language_models.chat_models import BaseChatModel # For type hinting
from langchain_core.exceptions import OutputParserException, LangChainException # For handling LLM call errors

# from langchain_core.documents import Document as LangchainDocument # F401 Unused import
from langchain.chains import LLMChain  # LLMChain still exists but consider LCEL later
from langchain_community.callbacks import get_openai_callback

from .memory_agent import MemoryAgent

# Set up logging
logger = logging.getLogger(__name__)


class AgentCoordinator:
    """
    Coordinator for AI agents in the document processing system.

    Manages LLM provider selection, model fallback, and task execution
    (analysis, querying, table generation).
    """

    def __init__(self):
        """Initialize the agent coordinator."""
        # Load API keys from environment variables
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.huggingface_api_key = os.environ.get("HUGGINGFACE_API_KEY")
        self.mistral_api_key = os.environ.get("MISTRAL_API_KEY")
        self.openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")

        # Read OpenRouter model hierarchy
        self.openrouter_primary_model = os.environ.get("OPENROUTER_PRIMARY_MODEL")
        self.openrouter_secondary_model = os.environ.get("OPENROUTER_SECONDARY_MODEL")
        self.openrouter_tertiary_model = os.environ.get("OPENROUTER_TERTIARY_MODEL") # Added tertiary
        self.openrouter_fallback_model = os.environ.get("OPENROUTER_FALLBACK_MODEL")

        # Determine LLM provider based on configuration
        self.llm_provider = os.environ.get("LLM_PROVIDER", "").lower()
        self._validate_provider_config() # Check if configured provider is usable

        # Initialize memory agent
        self.memory_agent = MemoryAgent()

    def _validate_provider_config(self):
        """Checks if the configured LLM provider has the necessary keys/models set."""
        if self.llm_provider == "openrouter":
            if not self.openrouter_api_key:
                logger.error("LLM_PROVIDER is 'openrouter' but OPENROUTER_API_KEY is missing.")
                self.llm_provider = None
            elif not (self.openrouter_primary_model or self.openrouter_secondary_model or self.openrouter_tertiary_model or self.openrouter_fallback_model):
                logger.error("LLM_PROVIDER is 'openrouter' but no OpenRouter models (PRIMARY, SECONDARY, TERTIARY, FALLBACK) are defined in .env.")
                self.llm_provider = None
            else:
                 logger.info(f"Using OpenRouter provider. Model priority: Primary='{self.openrouter_primary_model}', Secondary='{self.openrouter_secondary_model}', Tertiary='{self.openrouter_tertiary_model}', Fallback='{self.openrouter_fallback_model}'.")
        elif self.llm_provider == "huggingface":
            if not self.huggingface_api_key:
                logger.error("LLM_PROVIDER is 'huggingface' but HUGGINGFACE_API_KEY is missing.")
                self.llm_provider = None
            else:
                 logger.info("Using HuggingFace provider.")
        elif self.llm_provider == "mistral":
            if not self.mistral_api_key:
                logger.error("LLM_PROVIDER is 'mistral' but MISTRAL_API_KEY is missing.")
                self.llm_provider = None
            else:
                 logger.info("Using Mistral provider.")
        elif self.llm_provider == "openai":
            if not self.openai_api_key:
                logger.error("LLM_PROVIDER is 'openai' but OPENAI_API_KEY is missing.")
                self.llm_provider = None
            else:
                 logger.info("Using OpenAI provider.")
        elif self.llm_provider:
             logger.warning(f"LLM_PROVIDER is set to '{self.llm_provider}' but it's not a recognized provider (openrouter, huggingface, mistral, openai). No LLM will be used.")
             self.llm_provider = None
        else:
             # No provider explicitly set, determine fallback later if needed (though fallback isn't implemented here)
             logger.info("LLM_PROVIDER not set. Will attempt to use available keys if needed (not fully implemented for non-OpenRouter fallback).")
             # Decide if we want a default provider if none is set but keys exist?
             # For now, require LLM_PROVIDER to be set for non-OpenRouter usage.


    def _get_llm_instance(self, model_name: Optional[str] = None) -> Optional[BaseChatModel]:
        """
        Creates and returns an LLM instance based on the configured provider and optional model name.
        Used primarily by the fallback mechanism.
        """
        provider = self.llm_provider
        api_key = None
        llm_instance = None

        try:
            if provider == "openrouter":
                if not model_name or not self.openrouter_api_key: return None
                api_key = self.openrouter_api_key
                llm_instance = ChatOpenRouter(model_name=model_name, temperature=0, openrouter_api_key=api_key)
            elif provider == "huggingface":
                if not self.huggingface_api_key: return None
                api_key = self.huggingface_api_key
                # Note: HuggingFaceHub might not be a BaseChatModel, adjust if needed or use appropriate HF chat model
                llm_instance = HuggingFaceHub(repo_id=model_name or "google/flan-t5-large", huggingfacehub_api_token=api_key)
            elif provider == "mistral":
                if not self.mistral_api_key: return None
                api_key = self.mistral_api_key
                llm_instance = ChatMistralAI(model=model_name or "mistral-large-latest", temperature=0, api_key=api_key)
            elif provider == "openai":
                if not self.openai_api_key: return None
                api_key = self.openai_api_key
                llm_instance = ChatOpenAI(model_name=model_name or "gpt-4o", temperature=0, api_key=api_key)
            else:
                logger.warning(f"LLM provider '{provider}' not configured or supported for dynamic instance creation.")
                return None

            # Simple test call (optional, can add overhead)
            # llm_instance.invoke("Test")

            return llm_instance

        except ImportError as e:
             logger.error(f"Failed to import module for provider '{provider}': {e}. Make sure the necessary package is installed.")
             return None
        except Exception as e:
             logger.error(f"Failed to initialize LLM instance for provider '{provider}' (Model: {model_name}): {e}")
             return None


    def _run_chain_with_fallback(self, chain_creator: Callable[[BaseChatModel], LLMChain], input_data: Dict[str, Any]) -> Any:
        """
        Runs a LangChain chain with fallback logic, primarily for OpenRouter models.

        Args:
            chain_creator: A function that takes an LLM instance and returns a configured LLMChain.
            input_data: The input data for the chain's run method.

        Returns:
            The result from the chain run.

        Raises:
            RuntimeError: If no LLM provider is configured or if all models/providers fail.
            Exception: The last exception encountered if all attempts fail.
        """
        if not self.llm_provider:
            raise RuntimeError("No valid LLM provider configured or initialized.")

        # --- OpenRouter Fallback Logic ---
        if self.llm_provider == "openrouter":
            models_to_try = [
                self.openrouter_primary_model,
                self.openrouter_secondary_model,
                self.openrouter_tertiary_model,
                self.openrouter_fallback_model,
            ]
            last_exception = None

            for model_name in models_to_try:
                if not model_name: continue # Skip if model name is not configured

                logger.info(f"Attempting LLM call with OpenRouter model: {model_name}")
                llm_instance = self._get_llm_instance(model_name=model_name)
                if not llm_instance:
                    logger.warning(f"Could not get instance for model {model_name}, skipping.")
                    last_exception = last_exception or RuntimeError(f"Failed to get instance for {model_name}")
                    continue

                try:
                    chain = chain_creator(llm_instance)
                    # Langchain chains/LLMs can raise various exceptions on failure
                    result = chain.invoke(input_data) # Use invoke for newer LCEL style if chain supports it
                    # If chain.run is needed: result = chain.run(input_data)
                    # Check if result is dict and has 'text' key if using LLMChain.run
                    if isinstance(result, dict) and 'text' in result:
                         final_result = result['text']
                    elif isinstance(result, str):
                         final_result = result
                    # Handle AIMessage or other response objects if using invoke
                    elif hasattr(result, 'content'):
                         final_result = result.content
                    else:
                         # Fallback if structure is unexpected
                         final_result = str(result)

                    logger.info(f"Successfully completed call with OpenRouter model: {model_name}")
                    return final_result # Return on first success

                except Exception as e:
                    last_exception = e
                    logger.warning(f"Call failed with OpenRouter model {model_name}: {type(e).__name__} - {e}. Trying next model...")
                    # Optional: Add a small delay? time.sleep(1)

            # If all models failed
            logger.error("All configured OpenRouter models failed.")
            if last_exception:
                raise last_exception # Re-raise the last exception encountered
            else:
                raise RuntimeError("LLM call failed for all configured OpenRouter models, but no specific exception was caught.")

        # --- Logic for other providers (no fallback implemented here) ---
        else:
            # For non-OpenRouter, get the default instance for the provider
            # Note: _get_llm_instance uses default models if model_name is None
            llm_instance = self._get_llm_instance()
            if not llm_instance:
                 raise RuntimeError(f"Failed to initialize LLM for configured provider: {self.llm_provider}")

            chain = chain_creator(llm_instance)
            logger.info(f"Attempting LLM call with provider: {self.llm_provider}")

            try:
                # Handle OpenAI token counting separately if needed
                if self.llm_provider == "openai":
                     with get_openai_callback() as cb:
                         result = chain.invoke(input_data) # Use invoke
                         logger.info(
                             f"OpenAI call completed with {cb.total_tokens} tokens ({cb.prompt_tokens} prompt, {cb.completion_tokens} completion)"
                         )
                else:
                     result = chain.invoke(input_data) # Use invoke
                     logger.info(f"LLM call completed using provider: {self.llm_provider}")

                # Extract content based on response type
                if isinstance(result, dict) and 'text' in result:
                     return result['text']
                elif isinstance(result, str):
                     return result
                elif hasattr(result, 'content'):
                     return result.content
                else:
                     return str(result)

            except Exception as e:
                 logger.error(f"LLM call failed for provider {self.llm_provider}: {type(e).__name__} - {e}")
                 raise e # Re-raise the exception


    def analyze_document(
        self, document_id: str, text_content: str, document_type: str, language: str
    ) -> Dict[str, Any]:
        """Analyze document content with AI using fallback logic."""
        if not self.llm_provider:
            logger.warning("No LLM provider available for document analysis.")
            return {"tables": [], "entities": [], "financial_data": {}}

        try:
            logger.info(f"Analyzing document {document_id} of type {document_type}")

            system_prompt = self._get_analysis_system_prompt(document_type, language)
            prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate.from_template(system_prompt),
                    HumanMessagePromptTemplate.from_template("{text}"),
                ]
            )

            def create_analysis_chain(llm_instance):
                # Ensure the passed llm_instance is compatible with LLMChain
                # If llm_instance is BaseChatModel, it should work directly.
                # If it's a base LLM (like HuggingFaceHub), it should also work.
                return LLMChain(llm=llm_instance, prompt=prompt)

            max_tokens = 12000
            truncated_text = self._truncate_text(text_content, max_tokens)

            result_text = self._run_chain_with_fallback(
                chain_creator=create_analysis_chain,
                input_data={"text": truncated_text}
            )

            # Parse the result
            try:
                result_json = json.loads(result_text)
                return {
                    "tables": result_json.get("tables", []),
                    "entities": result_json.get("entities", []),
                    "financial_data": result_json.get("financial_data", {}),
                }
            except json.JSONDecodeError:
                logger.error(f"Failed to parse analysis result as JSON: {result_text[:500]}...")
                json_str = self._extract_json_from_text(result_text)
                if json_str:
                    try:
                        result_json = json.loads(json_str)
                        return {
                            "tables": result_json.get("tables", []),
                            "entities": result_json.get("entities", []),
                            "financial_data": result_json.get("financial_data", {}),
                        }
                    except json.JSONDecodeError:
                         logger.error("Extracted string is still not valid JSON.")
                return {"tables": [], "entities": [], "financial_data": {}}

        except Exception as e:
            logger.exception(f"Error analyzing document {document_id}: {str(e)}")
            return {"tables": [], "entities": [], "financial_data": {}}


    def process_query(
        self,
        query: str,
        document_ids: List[str],
        language: str = "he",
        chat_history: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Process a chat query about documents using fallback logic."""
        if not self.llm_provider:
            logger.warning("No LLM provider available for query processing.")
            return {"answer": "AI service unavailable.", "document_references": [], "suggested_questions": []}

        try:
            logger.info(f"Processing query: {query}")

            # Get context
            document_contexts = []
            document_references = []
            for doc_id in document_ids:
                context = self.memory_agent.get_document_context(doc_id, query)
                if context:
                    document_contexts.append(context["content"])
                    document_references.append({"document_id": doc_id, "title": context.get("title", "Unknown"), "relevance": "high"})

            if not document_contexts:
                return {"answer": "No relevant info found.", "document_references": [], "suggested_questions": self._generate_general_questions(language)}

            combined_context = "\n\n".join(document_contexts)
            formatted_history = ""
            if chat_history:
                for msg in chat_history[-10:]: # Limit history
                    formatted_history += f"{msg.get('role', '').capitalize()}: {msg.get('content', '')}\n"

            system_prompt = self._get_chat_system_prompt(language)
            prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate.from_template(system_prompt),
                    HumanMessagePromptTemplate.from_template(
                        "Document Context:\n{context}\n\nChat History:\n{history}\n\nUser Query: {query}\n\nProvide answer in {language}."
                    ),
                ]
            )

            def create_query_chain(llm_instance):
                return LLMChain(llm=llm_instance, prompt=prompt)

            max_context_tokens = 6000
            truncated_context = self._truncate_text(combined_context, max_context_tokens)

            result_text = self._run_chain_with_fallback(
                chain_creator=create_query_chain,
                input_data={
                    "context": truncated_context,
                    "history": formatted_history,
                    "query": query,
                    "language": language,
                }
            )

            suggested_questions = self._generate_suggested_questions(query, result_text, language)

            return {
                "answer": result_text,
                "document_references": document_references,
                "suggested_questions": suggested_questions,
            }

        except Exception as e:
            logger.exception(f"Error processing query: {str(e)}")
            return {"answer": "Error processing query.", "document_references": [], "suggested_questions": []}


    def generate_table(
        self, document_ids: List[str], table_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a table from document data using fallback logic."""
        if not self.llm_provider:
            logger.warning("No LLM provider available for table generation.")
            return {"table_data": {"headers": [], "rows": []}}

        try:
            logger.info(f"Generating table with spec: {table_spec}")

            # Get context
            document_contexts = []
            for doc_id in document_ids:
                context = self.memory_agent.get_document_full_content(doc_id)
                if context: document_contexts.append(context)
            if not document_contexts: return {"table_data": {"headers": [], "rows": []}}

            combined_context = "\n\n".join(document_contexts)
            formatted_spec = json.dumps(table_spec, ensure_ascii=False, indent=2)

            system_prompt = """You are a financial data extraction specialist... [rest of prompt] ... Return ONLY the JSON structure.""" # Truncated
            prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate.from_template(system_prompt),
                    HumanMessagePromptTemplate.from_template(
                        "Document Content:\n{context}\n\nTable Specification:\n{spec}\n\nGenerate table."
                    ),
                ]
            )

            def create_table_chain(llm_instance):
                return LLMChain(llm=llm_instance, prompt=prompt)

            max_context_tokens = 7000
            truncated_context = self._truncate_text(combined_context, max_context_tokens)

            result_text = self._run_chain_with_fallback(
                chain_creator=create_table_chain,
                input_data={"context": truncated_context, "spec": formatted_spec}
            )

            # Parse result
            try:
                result_json = json.loads(result_text)
                if "table_data" in result_json and "headers" in result_json["table_data"] and "rows" in result_json["table_data"]:
                     return result_json
                else:
                     logger.error(f"LLM table response missing structure: {result_text[:500]}...")
                     return {"table_data": {"headers": [], "rows": []}}
            except json.JSONDecodeError:
                logger.error(f"Failed to parse table result as JSON: {result_text[:500]}...")
                json_str = self._extract_json_from_text(result_text)
                if json_str:
                    try:
                        result_json = json.loads(json_str)
                        if "table_data" in result_json and "headers" in result_json["table_data"] and "rows" in result_json["table_data"]:
                             return result_json
                    except json.JSONDecodeError: pass
                return {"table_data": {"headers": [], "rows": []}}

        except Exception as e:
            logger.exception(f"Error generating table: {str(e)}")
            return {"table_data": {"headers": [], "rows": []}}


    # --- Helper methods (_truncate_text, _extract_json_from_text, prompts, etc.) ---

    def _truncate_text(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit."""
        # Simple character count approximation (adjust avg_chars_per_token as needed)
        avg_chars_per_token = 3
        max_chars = max_tokens * avg_chars_per_token
        if len(text) <= max_chars:
            return text
        keep_start = int(max_chars * 0.7)
        keep_end = int(max_chars * 0.3)
        return f"{text[:keep_start]}\n\n[...content truncated...]\n\n{text[-keep_end:]}"

    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """Extract JSON string from text, looking for {} or ```json ... ``` blocks."""
        # Look for JSON object pattern
        match = re.search(r"({[\s\S]*})", text)
        if match:
            json_str = match.group(1)
            try:
                json.loads(json_str)
                return json_str
            except json.JSONDecodeError: pass
        # Look for markdown code block pattern
        match = re.search(r"```(?:json)?\s*({[\s\S]*?})\s*```", text)
        if match:
            json_str = match.group(1)
            try:
                json.loads(json_str)
                return json_str
            except json.JSONDecodeError: pass
        return None

    def _get_analysis_system_prompt(self, document_type: str, language: str) -> str:
        """Get system prompt for document analysis."""
        # Base prompts (English/Hebrew)
        base_prompt_en = """You are a financial document analysis expert... [rest of prompt]""" # Truncated
        base_prompt_he = """אתה מומחה לניתוח מסמכים פיננסיים... [rest of prompt]""" # Truncated
        base_prompt = base_prompt_he if language == "he" else base_prompt_en

        # Document specific additions (English/Hebrew)
        doc_specific_en = {
            "bankStatement": "\nThis is a bank statement. Pay special attention to:...",
            "investmentReport": "\nThis is an investment report. Pay special attention to:...",
            "taxDocument": "\nThis is a tax document. Pay special attention to:...",
            "invoice": "\nThis is an invoice. Pay special attention to:...",
        }
        doc_specific_he = {
            "bankStatement": "\nזהו דף חשבון בנק. תן תשומת לב מיוחדת ל:...",
            "investmentReport": "\nזהו דוח השקעות. תן תשומת לב מיוחדת ל:...",
            "taxDocument": "\nזהו מסמך מס. תן תשומת לב מיוחדת ל:...",
            "invoice": "\nזוהי חשבונית. תן תשומת לב מיוחדת ל:...",
        }
        doc_specific = doc_specific_he if language == "he" else doc_specific_en
        return base_prompt + doc_specific.get(document_type, "") # Add specific instructions if type matches

    def _get_chat_system_prompt(self, language: str) -> str:
        """Get system prompt for chat."""
        prompt_en = """You are an expert financial assistant... [rest of prompt]""" # Truncated
        prompt_he = """אתה עוזר פיננסי מומחה... [rest of prompt]""" # Truncated
        return prompt_he if language == "he" else prompt_en

    def _generate_suggested_questions(
        self, query: str, response: str, language: str
    ) -> List[str]:
        """Generate suggested follow-up questions."""
        if not self.llm_provider: # Check if provider is available
             return self._generate_general_questions(language) # Fallback if no LLM

        try:
            system_prompt = """Based on the user's query and your response, generate 3 relevant follow-up questions... [rest of prompt]""" # Truncated
            prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate.from_template(system_prompt),
                    HumanMessagePromptTemplate.from_template(
                        "User Query: {query}\nYour Response: {response}\nLanguage: {language}\nGenerate 3 questions:"
                    ),
                ]
            )
            def create_suggestion_chain(llm_instance):
                return LLMChain(llm=llm_instance, prompt=prompt)

            result_text = self._run_chain_with_fallback(
                chain_creator=create_suggestion_chain,
                input_data={"query": query, "response": response, "language": language}
            )
            try:
                suggestions = json.loads(result_text)
                if isinstance(suggestions, list) and len(suggestions) > 0:
                    return [str(q) for q in suggestions[:3]] # Ensure strings and limit
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse suggested questions JSON: {result_text[:100]}...")
        except Exception as e:
            logger.warning(f"Error generating suggested questions with LLM: {str(e)}")

        # Fallback if LLM fails or isn't available
        return self._generate_general_questions(language)

    def _generate_general_questions(self, language: str) -> List[str]:
        """Generate general financial questions."""
        if language == "he":
            return [
                "מה היתרה העדכנית בחשבון שלי?",
                "מהן ההוצאות הגדולות ביותר בחודש האחרון?",
                "מהי התשואה הכוללת של תיק ההשקעות שלי?",
            ]
        else:
            return [
                "What is my current account balance?",
                "What are my largest expenses last month?",
                "What is the overall return of my portfolio?",
            ]
