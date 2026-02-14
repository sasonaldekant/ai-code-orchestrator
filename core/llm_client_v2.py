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
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from core.cost_manager import CostManager
from core.memory.user_prefs import UserPreferences
from core.cache_manager import CacheManager

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
    thinking: Optional[str] = None


class LLMProvider(ABC):
    def __init__(self, api_key: str, cost_manager: CostManager):
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
        
        # Combine text and thinking from all content blocks
        content_text = ""
        thinking_text = ""
        if hasattr(response, "content") and isinstance(response.content, list):
            for block in response.content:
                if block.type == "text":
                    content_text += block.text
                elif block.type == "thinking":
                    thinking_text += block.thinking
        elif hasattr(response, "content"):
             # Fallback for simple string content if API changes
             content_text = str(response.content)

        return LLMResponse(
            content=content_text,
            model=model,
            provider="anthropic",
            tokens_used=tokens,
            finish_reason=response.stop_reason,
            metadata={"id": response.id},
            thinking=thinking_text if thinking_text else None
        )

    def _get_provider_name(self, model: str) -> str:
        model_lower = model.lower()
        if "gpt" in model_lower: return "openai"
        if "claude" in model_lower: return "anthropic"
        if "gemini" in model_lower: return "google"
        if "sonar" in model_lower: return "perplexity"
        return "openai" # Default fallback

# Update Google provider to support JSON mode via generation_config
class GoogleProvider(LLMProvider):
    async def complete(self, messages: List[Dict], model: str, **kwargs) -> LLMResponse:
        import google.generativeai as genai
        genai.configure(api_key=self.api_key)
        
        # Configure generation config for JSON if requested
        safe_config = {}
        if kwargs.get("json_mode"):
            safe_config = {"response_mime_type": "application/json"}

        gemini = genai.GenerativeModel(model)
        
        # Format messages for Gemini
        prompt_parts = []
        for m in messages:
            content = m["content"]
            role = "user" if m["role"] in ["user", "system"] else "model"
            if isinstance(content, list):
                text_content = " ".join([p["text"] for p in content if p.get("type") == "text"])
                prompt_parts.append({"role": role, "parts": [text_content]})
            else:
                prompt_parts.append({"role": role, "parts": [str(content)]})
                
        # Send
        response = await gemini.generate_content_async(
            prompt_parts,
            generation_config=genai.types.GenerationConfig(
                temperature=kwargs.get("temperature", 0.0),
                max_output_tokens=kwargs.get("max_tokens", 4000),
                **safe_config
            )
        )
        
        tokens = {
            "prompt": 0, # Placeholder until usage metadata is parsed from response object
            "completion": 0,
            "total": 0
        }
        
        try:
             # Attempt to extract usage metadata if available in newer SDK
             if hasattr(response, "usage_metadata"):
                 tokens["prompt"] = response.usage_metadata.prompt_token_count
                 tokens["completion"] = response.usage_metadata.candidates_token_count
                 tokens["total"] = response.usage_metadata.total_token_count
        except:
             pass
        
        return LLMResponse(
            content=response.text,
            model=model,
            provider="google",
            tokens_used=tokens,
            finish_reason="stop",
            metadata={}
        )


class PerplexityProvider(OpenAIProvider):
    async def complete(self, messages: List[Dict], model: str, **kwargs) -> LLMResponse:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=self.api_key, base_url="https://api.perplexity.ai")
        
        # Prepare params
        params = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.0),
            "max_tokens": kwargs.get("max_tokens", 4000),
        }
        
        # Note: Perplexity might not support json_mode in all models, 
        # but the standard Sonar models usually do or ignore it gracefully.
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
            provider="perplexity",
            tokens_used=tokens,
            finish_reason=response.choices[0].finish_reason,
            metadata={"id": response.id}
        )


class LLMClientV2:
    def __init__(self, cost_manager: CostManager):
        self.cost_manager = cost_manager
        self.providers: Dict[str, LLMProvider] = {}
        self.user_prefs = UserPreferences()
        self.cache_manager = CacheManager()
        
        # Init Providers
        if os.getenv("OPENAI_API_KEY"):
            self.providers["openai"] = OpenAIProvider(os.getenv("OPENAI_API_KEY"), cost_manager)
        if os.getenv("ANTHROPIC_API_KEY"):
            self.providers["anthropic"] = AnthropicProvider(os.getenv("ANTHROPIC_API_KEY"), cost_manager)
        if os.getenv("GOOGLE_API_KEY"):
            self.providers["google"] = GoogleProvider(os.getenv("GOOGLE_API_KEY"), cost_manager)
        if os.getenv("PERPLEXITY_API_KEY"):
            self.providers["perplexity"] = PerplexityProvider(os.getenv("PERPLEXITY_API_KEY"), cost_manager)

    def _get_provider_name(self, model: str) -> str:
        model_lower = model.lower()
        if "gpt" in model_lower: return "openai"
        if "claude" in model_lower: return "anthropic"
        if "gemini" in model_lower: return "google"
        if "sonar" in model_lower: return "perplexity"
        return "openai" # Default fallback


    async def complete(
        self,
        messages: List[Dict[str, Union[str, List[Dict]]]],
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 4000,
        json_mode: bool = False,
        bypass_cache: bool = False,
        **kwargs
    ) -> LLMResponse:
        provider_name = self._get_provider_name(model)
        provider = self.providers.get(provider_name)
        
        if not provider:
            raise ValueError(f"Provider {provider_name} not properly configured (check API keys).")

        # 1. Budget Check
        start_time = time.time()
        self.cost_manager.check_and_update(model, 0, 0) # Update "last used" tracking or similar if implemented
        # Prepare messages
        # Inject User Preferences into System Prompt if present
        final_messages = []
        system_content = ""
        
        # Extract existing system prompt if any
        for m in messages:
            if m["role"] == "system":
                system_content += str(m["content"]) + "\n"
        
        # Add User Preferences
        prefs_context = self.user_prefs.get_system_prompt_context()
        if prefs_context:
            system_content += f"\n{prefs_context}"
            
        if system_content:
             # Check if we already have a system message to replace or add new
             has_system = any(m["role"] == "system" for m in messages)
             if has_system:
                 final_messages = []
                 for m in messages:
                     if m["role"] == "system":
                         # Replace strictly? Or append?
                         # Current logic above extracted content. Let's create a unified system message.
                         pass
                     else:
                         final_messages.append(m)
                 final_messages.insert(0, {"role": "system", "content": system_content})
             else:
                 final_messages = [{"role": "system", "content": system_content}] + messages
        else:
                  final_messages = messages
        
        # 2. Check Cache
        # Only cache deterministic calls (temp=0)
        cache_key_prompt = json.dumps(final_messages, sort_keys=True, default=str)
        if not bypass_cache and temperature == 0.0:
            cached_data = self.cache_manager.get(cache_key_prompt, model, temperature)
            if cached_data:
                logger.info(f"Cache Hit for {model}")
                # Reconstruct LLMResponse
                return LLMResponse(**cached_data)


        # Multi-modal handling happened before validation, but we can do it here/provider level.
        # But wait, Provider impls take `messages`. We should pass `final_messages`.
        
        try:
            response = await provider.complete(
                messages=final_messages,
                model=model, 
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
            
            # Cache the response result if deterministic
            if temperature == 0.0:
                # Convert LLMResponse to dict for storage
                self.cache_manager.set(
                    cache_key_prompt, 
                    model, 
                    asdict(response), 
                    temperature
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
            "response_content": response.content if response else None,
            "thinking_record": response.thinking if response else None
        }
        
        try:
            with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")