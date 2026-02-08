"""
Model routing logic.

This module reads a YAML configuration that describes which large language
model should be used for each agent phase or speciality.  A small helper
provides the appropriate model configuration for a given agent type
and task complexity.  The configuration is stored in `config/model_mapping.yaml`.

Example YAML structure:

```
version: "2.0"
default:
  model: gpt-4o-mini
  temperature: 0.0
  max_tokens: 4000
  provider: openai

routing:
  phase:
    analyst:
      model: claude-3-5-sonnet
      temperature: 0.1
      max_tokens: 8000
      provider: anthropic
    architect:
      model: claude-3-5-sonnet
      temperature: 0.1
      max_tokens: 16000
      provider: anthropic
      consensus_mode: true
      consensus_models:
        - claude-3-5-sonnet
        - gpt-4o
        - gemini-2.5-pro
    implementation:
      model: gpt-4o
      temperature: 0.0
      max_tokens: 8000
      provider: openai
    testing:
      model: gpt-4o-mini
      temperature: 0.0
      max_tokens: 4000
      provider: openai
```
"""

from __future__ import annotations

import yaml
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ModelRouter:
    """Selects model configuration based on agent type and task complexity."""

    def __init__(self, config_path: str = "config/model_mapping.yaml") -> None:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        except Exception as exc:
            logger.error(f"Failed to load model mapping config: {exc}")
            self.config = {}

    def _get_default(self) -> Dict[str, Any]:
        return self.config.get("default", {})

    def get_model_config(self, agent_type: str, category: str = "phase") -> Dict[str, Any]:
        """
        Get the model configuration for the given agent.

        Parameters
        ----------
        agent_type: str
            Name of the agent (e.g. "analyst", "architect", "backend", etc.).
        category: str
            Either "phase" or "speciality" depending on where the agent belongs.

        Returns
        -------
        Dict[str, Any]
            A dictionary describing the model, temperature, max_tokens, provider
            and optional consensus settings.  If no explicit mapping exists,
            values from the `default` section are returned.
        """
        routing = self.config.get("routing", {})
        cat_map: Dict[str, Any] = routing.get(category, {})
        agent_cfg = cat_map.get(agent_type, {})
        # Merge with defaults
        cfg = self._get_default().copy()
        cfg.update(agent_cfg)
        return cfg
