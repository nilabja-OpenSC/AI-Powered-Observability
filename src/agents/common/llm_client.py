"""
LLM Client for AI-Powered Observability Platform

Provides unified interface for OpenAI and Groq LLMs with:
- Automatic provider selection based on environment
- Retry logic with exponential backoff
- Token usage tracking
- Structured logging
- Error handling
"""

import os
import time
from typing import Optional, Dict, Any, List
from enum import Enum

import structlog
from openai import OpenAI, OpenAIError
from groq import Groq, GroqError

logger = structlog.get_logger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    GROQ = "groq"


class LLMClient:
    """
    Unified LLM client supporting OpenAI and Groq.
    
    Automatically selects provider based on environment variables:
    - OPENAI_API_KEY → OpenAI
    - GROQ_API_KEY → Groq
    
    Falls back to OpenAI if both are available.
    """
    
    def __init__(
        self,
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize LLM client.
        
        Args:
            provider: LLM provider (auto-detected if None)
            model: Model name (uses env default if None)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
            max_retries: Maximum retry attempts
            retry_delay: Initial retry delay in seconds
        """
        self.provider = provider or self._detect_provider()
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Initialize client based on provider
        if self.provider == LLMProvider.OPENAI:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.model = model or os.getenv("OPENAI_MODEL", "gpt-4")
        elif self.provider == LLMProvider.GROQ:
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            self.model = model or os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        
        logger.info(
            "llm_client_initialized",
            provider=self.provider,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
    
    def _detect_provider(self) -> LLMProvider:
        """Auto-detect LLM provider from environment variables"""
        llm_provider = os.getenv("LLM_PROVIDER", "").lower()
        
        if llm_provider == "groq" and os.getenv("GROQ_API_KEY"):
            return LLMProvider.GROQ
        elif llm_provider == "openai" and os.getenv("OPENAI_API_KEY"):
            return LLMProvider.OPENAI
        elif os.getenv("OPENAI_API_KEY"):
            return LLMProvider.OPENAI
        elif os.getenv("GROQ_API_KEY"):
            return LLMProvider.GROQ
        else:
            raise ValueError("No LLM API key found in environment")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate text completion.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Override default temperature
            max_tokens: Override default max_tokens
        
        Returns:
            Generated text
        
        Raises:
            OpenAIError, GroqError: On API errors after retries
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temp,
                    max_tokens=tokens,
                )
                
                duration = time.time() - start_time
                
                result = response.choices[0].message.content
                usage = response.usage
                
                logger.info(
                    "llm_generation_success",
                    provider=self.provider,
                    model=self.model,
                    duration=duration,
                    prompt_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens,
                    total_tokens=usage.total_tokens,
                )
                
                return result
            
            except (OpenAIError, GroqError) as e:
                logger.warning(
                    "llm_generation_error",
                    provider=self.provider,
                    attempt=attempt + 1,
                    max_retries=self.max_retries,
                    error=str(e),
                )
                
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                else:
                    logger.error(
                        "llm_generation_failed",
                        provider=self.provider,
                        error=str(e),
                    )
                    raise
    
    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            response_format: JSON schema for response (optional)
        
        Returns:
            Parsed JSON response
        """
        import json
        
        # Add JSON formatting instruction to prompt
        json_prompt = f"{prompt}\n\nRespond with valid JSON only."
        
        response_text = self.generate(
            prompt=json_prompt,
            system_prompt=system_prompt,
        )
        
        try:
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()
            
            result = json.loads(json_str)
            
            logger.info(
                "llm_structured_generation_success",
                provider=self.provider,
            )
            
            return result
        
        except json.JSONDecodeError as e:
            logger.error(
                "llm_json_parse_error",
                provider=self.provider,
                error=str(e),
                response=response_text[:200],
            )
            raise ValueError(f"Failed to parse JSON response: {e}")
    
    def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate response with tool calling support.
        
        Args:
            prompt: User prompt
            tools: List of tool definitions (OpenAI function calling format)
            system_prompt: System prompt (optional)
        
        Returns:
            Response with tool calls
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=self.temperature,
            )
            
            message = response.choices[0].message
            
            result = {
                "content": message.content,
                "tool_calls": [],
            }
            
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    result["tool_calls"].append({
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    })
            
            logger.info(
                "llm_tool_generation_success",
                provider=self.provider,
                tool_calls_count=len(result["tool_calls"]),
            )
            
            return result
        
        except (OpenAIError, GroqError) as e:
            logger.error(
                "llm_tool_generation_error",
                provider=self.provider,
                error=str(e),
            )
            raise


# Made with Bob