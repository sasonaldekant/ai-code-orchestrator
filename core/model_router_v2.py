"""
Model router for intelligent LLM selection based on task characteristics.

Reads configuration from YAML and routes requests to the optimal model
considering reasoning requirements, cost constraints, context limits,
and consensus needs.

Version: 3.0.0
"""

from __future__ import annotations

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    model: str
    provider: str
    temperature: float
    max_tokens: int
    tier: int = 1
    reasoning: Optional[str] = None
    consensus_mode: bool = False
    producer_reviewer_loop: bool = False
    max_iterations: int = 1
    quality_threshold: float = 8.0
    context_aware: bool = False
    context_sources: List[str] = field(default_factory=list)
    specialization: Optional[str] = None


@dataclass
class ConsensusConfig:
    """Configuration for consensus mode with multiple models."""
    primary: ModelConfig
    secondary: ModelConfig
    tertiary: Optional[ModelConfig] = None
    synthesis_model: str = "gpt-5.2"
    weight_primary: float = 0.5
    weight_secondary: float = 0.3
    weight_tertiary: float = 0.2
    reasoning: Optional[str] = None


class ModelRouterV2:
    """
    Route LLM requests to optimal models based on task characteristics.
    
    The router supports:
    - Phase-based routing (analyst, architect, implementer, tester, reviewer)
    - Specialty routing (backend, frontend, documentation, etc.)
    - Consensus mode (multiple models vote)
    - Producer-reviewer loops
    """
    
    def __init__(self, config_path: str = "config/model_mapping.yaml"):
        # Default to model_mapping.yaml instead of v2 to align with new spec
        self.config_path = Path(config_path)
        self.config = self._load_config()
        logger.info(f"Model router initialized from {config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load and parse YAML configuration."""
        if not self.config_path.exists():
            logger.warning(f"Config file {self.config_path} not found, using defaults")
            return self._get_default_config()
        
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if YAML not found."""
        return {
            "default": {
                "model": "gpt-5-mini",
                "temperature": 0.0,
                "max_tokens": 8000,
                "provider": "openai"
            }
        }
    
    def get_model_for_phase(self, phase: str) -> ModelConfig:
        """
        Get model configuration for a specific phase.
        """
        routing = self.config.get("routing", {})
        # Support both 'phases' and 'phase' for backward compatibility
        phase_config = routing.get("phases", {}).get(phase) or routing.get("phase", {}).get(phase)
        
        if not phase_config:
            # Fall back to default
            default = self.config.get("default", {})
            return ModelConfig(
                model=default.get("model", "gpt-5-mini"),
                provider=default.get("provider", "openai"),
                temperature=default.get("temperature", 0.0),
                max_tokens=default.get("max_tokens", 8000)
            )
        
        # Check for consensus mode
        if phase_config.get("consensus_mode"):
            # Return primary model but flag consensus mode
            models = phase_config.get("models", {})
            # Handle list vs dict in config
            if isinstance(phase_config.get("secondary"), list):
                primary_model = phase_config["model"]
                primary_provider = phase_config["provider"]
            else:
                primary = models.get("primary", {})
                primary_model = primary.get("model", phase_config.get("model"))
                primary_provider = primary.get("provider", phase_config.get("provider"))

            return ModelConfig(
                model=primary_model,
                provider=primary_provider,
                temperature=phase_config.get("temperature", 0.1),
                max_tokens=phase_config.get("max_tokens", 8000),
                consensus_mode=True,
                reasoning=phase_config.get("reasoning", "")
            )
        
        # Standard single-model routing
        return ModelConfig(
            model=phase_config["model"],
            provider=phase_config["provider"],
            tier=phase_config.get("tier", 1),
            temperature=phase_config.get("temperature", 0.0),
            max_tokens=phase_config.get("max_tokens", 8000),
            producer_reviewer_loop=phase_config.get("producer_reviewer_loop", False),
            max_iterations=phase_config.get("max_iterations", 1),
            quality_threshold=phase_config.get("quality_threshold", 8.0),
            reasoning=phase_config.get("reasoning", "")
        )
    
    def get_model_for_specialty(
        self,
        category: str,
        specialty: str
    ) -> ModelConfig:
        """
        Get model for a specialty task.
        """
        routing = self.config.get("routing", {})
        # Support both 'specialties' and 'specialty'
        specialty_config = (
            (routing.get("specialties", {}) or routing.get("specialty", {}))
            .get(category, {})
            .get(specialty)
        )
        
        if not specialty_config:
            # Fallback to category default or global default
            category_default = (routing.get("specialties", {}) or routing.get("specialty", {})).get(category, {})
            if isinstance(category_default, dict) and "model" in category_default:
                specialty_config = category_default
            else:
                default = self.config.get("default", {})
                return ModelConfig(
                    model=default.get("model", "gpt-5-mini"),
                    provider=default.get("provider", "openai"),
                    temperature=default.get("temperature", 0.0),
                    max_tokens=default.get("max_tokens", 8000)
                )
        
        return ModelConfig(
            model=specialty_config["model"],
            provider=specialty_config["provider"],
            temperature=specialty_config.get("temperature", 0.0),
            max_tokens=specialty_config.get("max_tokens", 8000),
            context_aware=specialty_config.get("context_aware", False),
            context_sources=specialty_config.get("context_sources", []),
            specialization=specialty_config.get("specialization", "")
        )
    
    def get_consensus_models(self, phase: str) -> ConsensusConfig:
        """
        Get all models for consensus mode.
        """
        routing = self.config.get("routing", {})
        phase_config = routing.get("phases", {}).get(phase) or routing.get("phase", {}).get(phase)
        
        if not phase_config or not phase_config.get("consensus_mode"):
            raise ValueError(f"Phase {phase} not configured for consensus mode")
        
        # New format (architect)
        if "secondary" in phase_config and isinstance(phase_config["secondary"], list):
            primary = ModelConfig(
                model=phase_config["model"],
                provider=phase_config["provider"],
                temperature=0.1,
                max_tokens=8000
            )
            # Take first secondary
            sec_model_name = phase_config["secondary"][0]
            secondary = ModelConfig(
                model=sec_model_name,
                provider="anthropic" if "claude" in sec_model_name.lower() else "openai",
                temperature=0.1,
                max_tokens=8000
            )
            return ConsensusConfig(
                primary=primary,
                secondary=secondary,
                synthesis_model="gpt-5.2"
            )

        # Old format
        models = phase_config.get("models", {})
        primary_cfg = models.get("primary", {})
        primary = ModelConfig(
            model=primary_cfg.get("model", phase_config.get("model")),
            provider=primary_cfg.get("provider", phase_config.get("provider")),
            temperature=0.1,
            max_tokens=8000
        )
        
        secondary_cfg = models.get("secondary", {})
        secondary = ModelConfig(
            model=secondary_cfg.get("model", "claude-opus-4.6"),
            provider=secondary_cfg.get("provider", "anthropic"),
            temperature=0.1,
            max_tokens=8000
        )
        
        tertiary = None
        if "tertiary" in models:
            tertiary_cfg = models["tertiary"]
            tertiary = ModelConfig(
                model=tertiary_cfg["model"],
                provider=tertiary_cfg["provider"],
                temperature=0.1,
                max_tokens=8000
            )
        
        return ConsensusConfig(
            primary=primary,
            secondary=secondary,
            tertiary=tertiary,
            synthesis_model=phase_config.get("synthesis_model", "gpt-5.2"),
            weight_primary=primary_cfg.get("weight", 0.5),
            weight_secondary=secondary_cfg.get("weight", 0.3),
            weight_tertiary=models.get("tertiary", {}).get("weight", 0.2),
            reasoning=phase_config.get("reasoning", "")
        )
    
    def get_cost_limits(self) -> Dict[str, float]:
        """Get cost management configuration."""
        return self.config.get("cost_management", {}).get("budgets", {})
    
    def should_enable_cache(self) -> bool:
        """Check if caching is enabled in configuration."""
        caching = self.config.get("caching")
        if caching:
            return caching.get("enabled", True)
        return self.config.get("cost_management", {}).get("optimization", {}).get("enable_cache", True)
    
    def get_cache_ttl(self) -> int:
        """Get cache TTL in seconds."""
        caching = self.config.get("caching")
        if caching:
            # Return first rule's ttl or default
            rules = caching.get("tier_1_rules", {})
            return rules.get("ttl_seconds", 3600)
        return self.config.get("cost_management", {}).get("optimization", {}).get("cache_ttl_seconds", 3600)