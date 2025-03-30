from typing import Any, Dict, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
import os
import requests
import json
from dotenv import load_dotenv

class ChatOpenRouter(BaseChatModel):
    """Custom OpenRouter chat model wrapper."""

    api_key: str
    model_name: str = "mistralai/mistral-small-3.1-24b-instruct:free" # Default model
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    site_url: Optional[str] = None
    site_name: Optional[str] = None
    api_base: str = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None, **kwargs):
        super().__init__(**kwargs) # Call BaseChatModel's __init__ first

        load_dotenv() # Load .env variables

        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        if not self.api_key:
             raise ValueError("OpenRouter API key not provided or found in environment variables.")

        if model_name:
            self.model_name = model_name
        # If no model_name provided, self.model_name retains its default value

        # Set other parameters from kwargs if they exist as class attributes
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        # Load optional headers from env
        self.site_url = os.getenv("SITE_URL", "http://localhost:5000") # Default if not set
        self.site_name = os.getenv("SITE_NAME", "Financial Document Processor") # Default if not set


    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs) -> ChatResult:
        """Generate a response using the OpenRouter API."""

        # Convert LangChain messages to OpenRouter format
        or_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                or_messages.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                or_messages.append({"role": "assistant", "content": message.content})
            elif isinstance(message, SystemMessage):
                 or_messages.append({"role": "system", "content": message.content})
            else:
                 # Handle other potential message types or raise an error
                 or_messages.append({"role": "user", "content": str(message.content)})


        # Prepare request
        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-Title": self.site_name
        }
        data = {
            "model": self.model_name,
            "messages": or_messages,
            "temperature": self.temperature
        }

        if self.max_tokens:
            data["max_tokens"] = self.max_tokens
        if stop:
             data["stop"] = stop # Pass stop sequences if provided

        # Add any additional valid API parameters from kwargs
        # Be careful only to pass parameters OpenRouter supports
        supported_extra_params = ["frequency_penalty", "presence_penalty", "seed", "response_format"]
        for key, value in kwargs.items():
            if key in supported_extra_params:
                data[key] = value

        # Make request
        response = requests.post(url, headers=headers, json=data, timeout=90) # Increased timeout
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        response_json = response.json()

        # Process response
        # Ensure choices exist and are not empty
        if not response_json.get("choices") or len(response_json["choices"]) == 0:
             raise ValueError("Received empty 'choices' list from OpenRouter API.")

        # Ensure message content exists
        message_data = response_json["choices"][0].get("message", {})
        content = message_data.get("content")
        if content is None:
             # Handle potential refusals or empty content
             refusal = message_data.get("refusal")
             if refusal:
                  raise ValueError(f"OpenRouter model refused to respond: {refusal}")
             else:
                  # If content is None and no refusal, treat as empty response
                  content = ""


        ai_message = AIMessage(content=content)

        # Extract LLM output details if needed (e.g., usage)
        llm_output = {
             "token_usage": response_json.get("usage"),
             "model_name": response_json.get("model", self.model_name)
        }

        return ChatResult(
            generations=[ChatGeneration(message=ai_message, generation_info=llm_output)]
        )

    async def _agenerate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs) -> ChatResult:
        """Async version of generate."""
        # NOTE: This uses requests, which is blocking.
        # For true async, you'd need an async HTTP client like httpx or aiohttp.
        # This implementation provides async compatibility but runs synchronously.
        import asyncio
        # Run the synchronous _generate method in a default executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._generate, messages, stop, **kwargs)


    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "openrouter-chat-custom" # Custom identifier