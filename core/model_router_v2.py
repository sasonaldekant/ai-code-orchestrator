"""
Model router for intelligent LLM selection based on task characteristics.

Reads configuration from YAML and routes requests to the optimal model
considering reasoning requirements, cost constraints, context limits,
and consensus needs.

Version: 2.0.0
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
    synthesis_model: str = "claude-3-5-sonnet"
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
    
    Example
    -------
    >>> router = ModelRouterV2("config/model_mapping_v2.yaml")
    >>> config = router.get_model_for_phase("analyst")
    >>> print(config.model)  # claude-3-5-sonnet
    >>> print(config.reasoning)  # Best for requirements analysis...
    """
    
    def __init__(self, config_path: str = "config/model_mapping_v2.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        logger.info(f"Model router initialized from {config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load and parse YAML configuration."""
        if not self.config_path.exists():
            logger.warning(f"Config file {self.config_path} not found, using defaults")
            return self._get_default_config()
        
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if YAML not found."""
        return {
            "default": {
                "model": "gpt-4o-mini",
                "temperature": 0.0,
                "max_tokens": 4000
            }
        }
    
    def get_model_for_phase(self, phase: str) -> ModelConfig:
        """
        Get model configuration for a specific phase.
        
        Parameters
        ----------
        phase : str
            Phase name (e.g., "analyst", "architect", "implementer").
        
        Returns
        -------
        ModelConfig
            Configuration for the selected model.
        
        Examples
        --------
        >>> router = ModelRouter()
        >>> config = router.get_model_for_phase("implementer")
        >>> print(f"{config.model} - {config.reasoning}")
        gpt-4o - Strong C# performance (92% HumanEval)
        """
        phase_config = self.config.get("routing", {}).get("phase", {}).get(phase)
        
        if not phase_config:
            # Fall back to default
            default = self.config.get("default", {})
            return ModelConfig(
                model=default.get("model", "gpt-4o-mini"),
                provider="openai",
                temperature=default.get("temperature", 0.0),
                max_tokens=default.get("max_tokens", 4000)
            )
        
        # Check for consensus mode
        if phase_config.get("consensus_mode"):
            # Return primary model but flag consensus mode
            primary = phase_config["models"]["primary"]
            return ModelConfig(
                model=primary["model"],
                provider=primary["provider"],
                temperature=0.1,
                max_tokens=8000,
                consensus_mode=True,
                reasoning=phase_config.get("reasoning", "")
            )
        
        # Standard single-model routing
        return ModelConfig(
            model=phase_config["model"],
            provider=phase_config["provider"],
            temperature=phase_config.get("temperature", 0.0),
            max_tokens=phase_config.get("max_tokens", 4000),
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
        
        Parameters
        ----------
        category : str
            Category (e.g., "backend", "frontend", "integration").
        specialty : str
            Specific specialty (e.g., "dotnet_api", "react", "efcore").
        
        Returns
        -------
        ModelConfig
            Configuration for the selected model.
        
        Examples
        --------
        >>> router = ModelRouter()
        >>> config = router.get_model_for_specialty("backend", "efcore")
        >>> print(config.context_aware)  # True
        >>> print(config.context_sources)  # ['existing_dbcontext', 'migration_history']
        """
        specialty_config = (
            self.config.get("routing", {})
            .get("specialty", {})
            .get(category, {})
            .get(specialty)
        )
        
        if not specialty_config:
            raise ValueError(f"No configuration found for {category}/{specialty}")
        
        return ModelConfig(
            model=specialty_config["model"],
            provider=specialty_config["provider"],
            temperature=specialty_config.get("temperature", 0.0),
            max_tokens=specialty_config.get("max_tokens", 4000),
            context_aware=specialty_config.get("context_aware", False),
            context_sources=specialty_config.get("context_sources", []),
            specialization=specialty_config.get("specialization", "")
        )
    
    def get_consensus_models(self, phase: str) -> ConsensusConfig:
        """
        Get all models for consensus mode.
        
        Parameters
        ----------
        phase : str
            Phase name (e.g., "architect").
        
        Returns
        -------
        ConsensusConfig
            Configuration containing primary, secondary, and tertiary models.
        
        Examples
        --------
        >>> router = ModelRouter()
        >>> consensus = router.get_consensus_models("architect")
        >>> print(consensus.primary.model)  # claude-3-5-sonnet
        >>> print(consensus.secondary.model)  # gpt-4o
        >>> print(consensus.weight_primary)  # 0.5
        """
        phase_config = self.config.get("routing", {}).get("phase", {}).get(phase)
        
        if not phase_config or not phase_config.get("consensus_mode"):
            raise ValueError(f"Phase {phase} not configured for consensus mode")
        
        models = phase_config["models"]
        
        primary_cfg = models["primary"]
        primary = ModelConfig(
            model=primary_cfg["model"],
            provider=primary_cfg["provider"],
            temperature=0.1,
            max_tokens=8000
        )
        
        secondary_cfg = models["secondary"]
        secondary = ModelConfig(
            model=secondary_cfg["model"],
            provider=secondary_cfg["provider"],
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
            synthesis_model=phase_config.get("synthesis_model", "claude-3-5-sonnet"),
            weight_primary=primary_cfg.get("weight", 0.5),
            weight_secondary=secondary_cfg.get("weight", 0.3),
            weight_tertiary=models.get("tertiary", {}).get("weight", 0.2),
            reasoning=phase_config.get("reasoning", "")
        )
    
    def get_cost_limits(self) -> Dict[str, float]:
        """
        Get cost management configuration.
        
        Returns
        -------
        dict
            Cost budgets and thresholds.
        """
        return self.config.get("cost_management", {}).get("budgets", {})
    
    def should_enable_cache(self) -> bool:
        """Check if caching is enabled in configuration."""
        return self.config.get("cost_management", {}).get("optimization", {}).get("enable_cache", True)
    
    def get_cache_ttl(self) -> int:
        """Get cache TTL in seconds."""
        return self.config.get("cost_management", {}).get("optimization", {}).get("cache_ttl_seconds", 3600)