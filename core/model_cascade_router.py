"""
Model Cascade Router
--------------------
Central decision engine for Model Cascading System.
Routes tasks to the most cost-effective model tier based on complexity.
Handles comprehensive fallback logic and provider availability.
"""

from __future__ import annotations

import logging
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from .model_router_v2 import ModelRouterV2, ModelConfig, ConsensusConfig
from .cascade_metrics import CascadeMetrics

logger = logging.getLogger(__name__)

@dataclass
class CascadeTier:
    level: int
    name: str
    max_cost_input: float
    description: str

TIERS = {
    0: CascadeTier(0, "Gate", 0.08, "Filter, validate, classify (Gemini Flash)"),
    1: CascadeTier(1, "Worker", 0.15, "Standard generation & monitoring (GPT-4o-mini)"),
    2: CascadeTier(2, "Standard", 2.50, "Architecture, reasoning (GPT-4o)"),
    3: CascadeTier(3, "Heavy", 3.00, "Complex fixes, self-healing (Claude Sonnet)"),
    4: CascadeTier(4, "Mega", 1.25, "Massive context analysis (Gemini Pro)")
}

class ModelCascadeRouter:
    def __init__(self, config_path: str = "config/model_mapping_v2.yaml"):
        self.base_router = ModelRouterV2(config_path)
        self.metrics_tracker = CascadeMetrics()
        self.provider_status: Dict[str, bool] = {
            "openai": True,
            "anthropic": True,
            "google": True,
            "perplexity": True
        }
        logger.info("ModelCascadeRouter initialized with 5-tier hierarchy and centralized metrics.")

    def get_model_for_phase(self, phase: str) -> ModelConfig:
        """
        Get model configuration for a specific phase from the base router.
        """
        config = self.base_router.get_model_for_phase(phase)
        return self._record_usage(config)

    def get_cascade_chain(self, phase: str) -> List[ModelConfig]:
        """
        Get the ordered list of models for a phase (primary + fallbacks).
        """
        primary = self.base_router.get_model_for_phase(phase)
        
        # Check if phase has specific cascade config in raw yaml
        phase_conf = self.base_router.config.get("routing", {}).get("phase", {}).get(phase, {})
        cascade_list = phase_conf.get("cascade", [])
        
        chain = [primary]
        
        for item in cascade_list:
            # Parse cascade item into ModelConfig
            model_name = item.get("model")
            provider = item.get("provider")
            # Create config inheriting basic properties
            fallback_cfg = ModelConfig(
                model=model_name,
                provider=provider,
                tier=primary.tier, # Inherit tier or define logic? Fallback usually implies same role so likely same tier or higher cost.
                                   # We should ideally parse tier from item if available, or assume Tier 2 behavior for fallbacks
                temperature=primary.temperature,
                max_tokens=primary.max_tokens,
                reasoning=f"Fallback for {phase}"
            )
            chain.append(fallback_cfg)
            
        return chain

    def select_model(self, phase: str, complexity: str = "simple", context_tokens: int = 0) -> ModelConfig:
        """
        Select optimal model based on phase, complexity, and context size.
        """
        chain = self.get_cascade_chain(phase)
        primary = chain[0]
        
        # Logic for Tier selection dynamic adjustment
        # If context is massive, force Tier 4 (Gemini Pro) if available in chain
        if context_tokens > 100000:
            for cfg in chain:
                if "gemini-1.5-pro" in cfg.model:
                    logger.info(f"Escalating to Tier 4 (Mega) due to context size: {context_tokens}")
                    return self._record_usage(cfg)
        
        # If complexity is high and we have a tiered fallback
        if complexity == "high" and len(chain) > 1:
            # Look for a higher tier model in the chain
            for cfg in chain:
                 # Heuristic: Claude Sonnet or GPT-4o are usually higher tier
                 if "sonnet" in cfg.model or "gpt-4o" in cfg.model:
                     if cfg.model != "gpt-4o-mini":
                        logger.info(f"Escalating to High Compexity model: {cfg.model}")
                        return self._record_usage(cfg)
        
        # [Task 6.2] Adaptive Health Check
        # If primary (Tier 1) is failing frequently, escalate to fallback
        if primary.tier == 1 and not self.check_tier_health(1):
            logger.warning("Tier 1 showing high failure rate. Escalating to fallback.")
            if len(chain) > 1:
                return self._record_usage(chain[1])

        # Default: Return primary checked for availability

        # Default: Return primary checked for availability
        for cfg in chain:
            if self.is_provider_available(cfg.provider):
                return self._record_usage(cfg)
                
        # If all fail, return primary and hope for best (or raise error)
        logger.warning(f"All providers validation failed for phase {phase}. Returning primary.")
        return primary

    def check_tier_health(self, tier: int, threshold: float = 0.90) -> bool:
        """
        Check if a tier is performing above the success threshold.
        Returns False if failure rate > (1 - threshold).
        """
        stats = self.metrics_tracker.get_stats()
        outcomes = stats.get("tier_outcomes", {}).get(str(tier))
        
        if not outcomes:
            return True
            
        success = outcomes.get("success", 0)
        failure = outcomes.get("failure", 0)
        total = success + failure
        
        # Need minimum sample size to judge
        if total < 10:
            return True
            
        success_rate = success / total
        if success_rate < threshold:
            logger.warning(f"Tier {tier} health check failed: {success_rate:.2%} success rate")
            return False
            
        return True

    def is_provider_available(self, provider: str) -> bool:
        """
        Check if provider is marked as available.
        (Real implementation would ping health checkpoints)
        """
        return self.provider_status.get(provider, True)

    def mark_provider_failure(self, provider: str):
        """Temporarily mark provider as down."""
        logger.warning(f"Marking provider {provider} as DOWN.")
        self.provider_status[provider] = False
        # In real-world, spawn a background task to check health and re-enable

    def _record_usage(self, config: ModelConfig) -> ModelConfig:
        self.metrics_tracker.record_selection(config.tier, config.model, config.provider)
        return config

    def get_model_for_specialty(self, category: str, specialty: str) -> ModelConfig:
        """Proxy to base router with metric tracking."""
        config = self.base_router.get_model_for_specialty(category, specialty)
        return self._record_usage(config)

    def get_consensus_models(self, phase: str) -> ConsensusConfig:
        """Proxy to base router."""
        # Note: ConsensusConfig contains ModelConfigs, we should ideally record them too if used
        return self.base_router.get_consensus_models(phase)

    def get_cost_limits(self) -> Dict[str, float]:
        """Proxy to base router."""
        return self.base_router.get_cost_limits()

    def should_enable_cache(self) -> bool:
        """Proxy to base router."""
        return self.base_router.should_enable_cache()

    def get_cache_ttl(self) -> int:
        """Proxy to base router."""
        return self.base_router.get_cache_ttl()

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics_tracker.get_stats()
