"""
Unified LLM client with offline stub and cost tracking.

This module provides a single entry point for generating text via
different providers (OpenAI, Anthropic, Google).  When API keys are
not available or `OFFLINE_LLM` is set, it falls back to a deterministic
offline stub.  It returns token usage estimates and integrates with
`CostManager` to update cost budgets.
"""

from __future__ import annotations

import os
import time
from typing import Dict, Any, Tuple
import logging
import asyncio

import json

from .cost_manager import CostManager

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified interface for LLM calls with optional offline fallback."""

    def __init__(self, cost_manager: CostManager) -> None:
        self.cost_manager = cost_manager
        self.offline = os.getenv("OFFLINE_LLM", "1") == "1"
        # API keys
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_key = os.getenv("GOOGLE_API_KEY")

        # Lazy import so local environment does not require these packages
        self._openai = None
        self._anthropic = None
        self._google = None

    async def generate(
        self,
        prompt: str,
        model_cfg: Dict[str, Any],
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> Dict[str, Any]:
        """
        Generate a response from the selected model.

        Parameters
        ----------
        prompt : str
            The prompt to send to the LLM.
        model_cfg : dict
            Configuration containing keys: `model`, `provider`, `temperature`, `max_tokens`.
        max_tokens : int, optional
            Override max_tokens from config.
        temperature : float, optional
            Override temperature from config.

        Returns
        -------
        dict
            Contains keys: `content`, `tokens_in`, `tokens_out`, `cost`, `model`.
        """
        model = model_cfg.get("model")
        provider = model_cfg.get("provider", "openai")
        temp = temperature if temperature is not None else model_cfg.get("temperature", 0.0)
        max_toks = max_tokens if max_tokens is not None else model_cfg.get("max_tokens", 4000)

        # offline stub fallback
        if self.offline or not self._has_credentials(provider):
            return self._generate_offline(prompt, model, provider)
        # In a real implementation, call the provider's async API here.
        try:
            if provider == "openai":
                return await self._call_openai(prompt, model, temp, max_toks)
            elif provider == "anthropic":
                return await self._call_anthropic(prompt, model, temp, max_toks)
            elif provider == "google":
                return await self._call_google(prompt, model, temp, max_toks)
            else:
                logger.warning(f"Unknown provider {provider}, using offline stub")
                return self._generate_offline(prompt, model, provider)
        except Exception as exc:
            logger.warning(f"LLM call failed: {exc}; falling back to offline stub")
            return self._generate_offline(prompt, model, provider)

    def _has_credentials(self, provider: str) -> bool:
        if provider == "openai":
            return bool(self.openai_key)
        if provider == "anthropic":
            return bool(self.anthropic_key)
        if provider == "google":
            return bool(self.google_key)
        return False

    async def _call_openai(self, prompt: str, model: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
        """Call OpenAI's async API (stubbed if not installed)."""
        if self._openai is None:
            import importlib
            try:
                self._openai = importlib.import_module("openai").AsyncOpenAI(api_key=self.openai_key)
            except Exception:
                return self._generate_offline(prompt, model, "openai")
        start = time.time()
        response = await self._openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        duration_ms = int((time.time() - start) * 1000)
        # Estimate cost; usage fields available on response
        tokens_in = response.usage.prompt_tokens
        tokens_out = response.usage.completion_tokens
        should_continue, cost = self.cost_manager.check_and_update(model, tokens_in, tokens_out)
        return {
            "content": response.choices[0].message.content,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost": cost,
            "model": model,
            "provider": "openai",
            "latency_ms": duration_ms,
            "continue": should_continue,
        }

    async def _call_anthropic(self, prompt: str, model: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
        if self._anthropic is None:
            import importlib
            try:
                anthropic_module = importlib.import_module("anthropic")
                self._anthropic = anthropic_module.AsyncAnthropic(api_key=self.anthropic_key)
            except Exception:
                return self._generate_offline(prompt, model, "anthropic")
        start = time.time()
        response = await self._anthropic.messages.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        duration_ms = int((time.time() - start) * 1000)
        tokens_in = response.usage.input_tokens
        tokens_out = response.usage.output_tokens
        should_continue, cost = self.cost_manager.check_and_update(model, tokens_in, tokens_out)
        return {
            "content": response.content[0].text if hasattr(response, "content") else "",
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost": cost,
            "model": model,
            "provider": "anthropic",
            "latency_ms": duration_ms,
            "continue": should_continue,
        }

    async def _call_google(self, prompt: str, model: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
        if self._google is None:
            import importlib
            try:
                genai = importlib.import_module("google.generativeai")
                genai.configure(api_key=self.google_key)
                self._google = genai.GenerativeModel(model)
            except Exception:
                return self._generate_offline(prompt, model, "google")
        start = time.time()
        response = await asyncio.get_event_loop().run_in_executor(
            None, lambda: self._google.generate_content(prompt, temperature=temperature, max_output_tokens=max_tokens)
        )
        duration_ms = int((time.time() - start) * 1000)
        # Google's API does not provide token counts; estimate by char count
        tokens_in = len(prompt) // 4
        tokens_out = len(response.text) // 4 if hasattr(response, "text") else 0
        should_continue, cost = self.cost_manager.check_and_update(model, tokens_in, tokens_out)
        return {
            "content": response.text if hasattr(response, "text") else "",
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost": cost,
            "model": model,
            "provider": "google",
            "latency_ms": duration_ms,
            "continue": should_continue,
        }

    def _generate_offline(self, prompt: str, model: str, provider: str) -> Dict[str, Any]:
        """Return a deterministic stub without calling external APIs."""
        # Estimate token usage heuristically: 1 token per 4 characters
        tokens_in = len(prompt) // 4
        # generate a simple echo or JSON stub
        content = {
            "prompt_length": len(prompt),
            "model": model,
            "provider": provider,
            "message": "offline stub: no API call",
        }
        text = json.dumps(content, indent=2)
        tokens_out = len(text) // 4
        _, cost = self.cost_manager.check_and_update(model, tokens_in, tokens_out)
        return {
            "content": text,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost": cost,
            "model": model,
            "provider": provider,
            "latency_ms": 0,
            "continue": True,
        }
