"""
Enhanced LLM client supporting multiple providers (OpenAI, Anthropic, Google).
With AUDIT LOGGING capabilities.
"""

from __future__ import annotations

import os
import asyncio
import logging
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

# Ensure outputs directory exists for audit logs
AUDIT_LOG_DIR = Path("outputs/audit_logs")
AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_LOG_FILE = AUDIT_LOG_DIR / "llm_audit.jsonl"


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    tokens_used: Dict[str, int]
    finish_reason: str
    metadata: Dict[str, Any]


class LLMProvider(ABC):
    def __init__(self, api_key: str, cost_manager: Any):
        self.api_key = api_key
        self.cost_manager = cost_manager
    
    @abstractmethod
    async def complete(self, messages: List[Dict], model: str, **kwargs) -> LLMResponse:
        pass


class OpenAIProvider(LLMProvider):
    async def complete(self, messages: List[Dict], model: str, **kwargs) -> LLMResponse:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=self.api_key)
        
        # Prepare params
        params = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.0),
            "max_tokens": kwargs.get("max_tokens", 4000),
        }
        if kwargs.get("json_mode"):
            params["response_format"] = {"type": "json_object"}

        response = await client.chat.completions.create(**params)
        
        usage = response.usage
        tokens = {
            "prompt": usage.prompt_tokens,
            "completion": usage.completion_tokens,
            "total": usage.total_tokens
        }
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=model,
            provider="openai",
            tokens_used=tokens,
            finish_reason=response.choices[0].finish_reason,
            metadata={"id": response.id}
        )


class AnthropicProvider(LLMProvider):
    async def complete(self, messages: List[Dict], model: str, **kwargs) -> LLMResponse:
        from anthropic import AsyncAnthropic
        client = AsyncAnthropic(api_key=self.api_key)
        
        sys_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msgs = [m for m in messages if m["role"] != "system"]
        
        response = await client.messages.create(
            model=model,
            system=sys_msg,
            messages=user_msgs,
            temperature=kwargs.get("temperature", 0.0),
            max_tokens=kwargs.get("max_tokens", 4000)
        )
        
        tokens = {
            "prompt": response.usage.input_tokens,
            "completion": response.usage.output_tokens,
            "total": response.usage.input_tokens + response.usage.output_tokens
        }
        
        return LLMResponse(
            content=response.content[0].text,
            model=model,
            provider="anthropic",
            tokens_used=tokens,
            finish_reason=response.stop_reason,
            metadata={"id": response.id}
        )

# Mock Google Provider for consistency if not installed or configured, 
# otherwise use real implementation if desired. Keeping structure simple.
class GoogleProvider(LLMProvider):
    async def complete(self, messages: List[Dict], model: str, **kwargs) -> LLMResponse:
        # Simplified placeholder/implementation
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        gemini = genai.GenerativeModel(model)
        
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        response = await gemini.generate_content_async(prompt)
        
        # Rough token estimation
        tokens = {
            "prompt": len(prompt) // 4,
            "completion": len(response.text) // 4,
            "total": (len(prompt) + len(response.text)) // 4
        }
        
        return LLMResponse(
            content=response.text,
            model=model,
            provider="google",
            tokens_used=tokens,
            finish_reason="stop",
            metadata={}
        )


class LLMClientV2:
    def __init__(self, cost_manager: Any):
        self.cost_manager = cost_manager
        self.providers: Dict[str, LLMProvider] = {}
        
        # Init Providers
        if os.getenv("OPENAI_API_KEY"):
            self.providers["openai"] = OpenAIProvider(os.getenv("OPENAI_API_KEY"), cost_manager)
        if os.getenv("ANTHROPIC_API_KEY"):
            self.providers["anthropic"] = AnthropicProvider(os.getenv("ANTHROPIC_API_KEY"), cost_manager)
        if os.getenv("GOOGLE_API_KEY"):
            self.providers["google"] = GoogleProvider(os.getenv("GOOGLE_API_KEY"), cost_manager)

    def _get_provider_name(self, model: str) -> str:
        if "gpt" in model.lower(): return "openai"
        if "claude" in model.lower(): return "anthropic"
        if "gemini" in model.lower(): return "google"
        return "openai" # Default fallback

    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 4000,
        json_mode: bool = False,
        **kwargs
    ) -> LLMResponse:
        provider_name = self._get_provider_name(model)
        provider = self.providers.get(provider_name)
        
        if not provider:
            raise ValueError(f"Provider {provider_name} not properly configured (check API keys).")

        # 1. Budget Check
        start_time = time.time()
        self.cost_manager.check_and_update(model, 0, 0) # Update "last used" tracking or similar if implemented
        
        # 2. Execution
        try:
            response = await provider.complete(
                messages, model, 
                temperature=temperature, 
                max_tokens=max_tokens, 
                json_mode=json_mode, 
                **kwargs
            )
            
            # 3. Cost Update
            cost_info = self.cost_manager.check_and_update(
                model, 
                response.tokens_used["prompt"], 
                response.tokens_used["completion"]
            )
            
            # 4. Audit Logging
            self._log_audit(
                messages=messages,
                response=response,
                duration=time.time() - start_time,
                cost=cost_info.get("cost_increment", 0.0) if isinstance(cost_info, dict) else 0.0
            )
            
            return response
            
        except Exception as e:
            logger.error(f"LLM Call Failed: {e}")
            self._log_audit(
                messages=messages, 
                response=None, 
                duration=time.time() - start_time, 
                error=str(e)
            )
            raise

    def _log_audit(
        self, 
        messages: List[Dict], 
        response: Optional[LLMResponse], 
        duration: float, 
        cost: float = 0.0, 
        error: Optional[str] = None
    ):
        """Append interaction details to the audit log."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "model": response.model if response else "unknown",
            "provider": response.provider if response else "unknown",
            "duration_sec": round(duration, 2),
            "cost_usd": round(cost, 6),
            "status": "success" if not error else "error",
            "error": error,
            "tokens": response.tokens_used if response else {},
            "prompt": messages, # Valid JSON list
            # Truncate very long response content in log to save space if needed, 
            # currently saving full for audit purposes as requested.
            "response_content": response.content if response else None 
        }
        
        try:
            with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")