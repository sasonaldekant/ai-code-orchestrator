from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import yaml
import os
from pathlib import Path

router = APIRouter(prefix="/config", tags=["config"])

CONFIG_PATH = Path("config/model_mapping_v2.yaml")
ENV_PATH = Path(".env")

LIMITS_PATH = Path("config/limits.yaml")

class ModelConfig(BaseModel):
    model: str
    provider: str
    temperature: float = 0.0
    max_tokens: int = 4000


class GlobalConfig(BaseModel):
    temperature: float = 0.0
    max_retries: int = 3
    max_feedback_iterations: int = 3
    deep_search: bool = False
    per_task_budget: float = 0.5
    per_hour_budget: float = 5.0
    per_day_budget: float = 20.0
    strict_mode: bool = True

class GlobalSettings(BaseModel):
    models: Optional[Dict[str, Any]] = None
    limits: Optional[Dict[str, Any]] = None
    api_keys: Optional[Dict[str, str]] = None
    global_config: Optional[GlobalConfig] = None


def load_yaml_config():
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_limits_config():
    if not LIMITS_PATH.exists():
        return {}
    with open(LIMITS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def save_yaml_config(data: Dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def _is_masked_value(value: str) -> bool:
    trimmed = value.strip()
    if not trimmed:
        return True
    if set(trimmed) == {"*"}:
        return True
    return trimmed.endswith("****") and "*" in trimmed


def save_limits_config(data: Dict):
    with open(LIMITS_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False)

def update_env_file(api_keys: Dict[str, str]):
    # Simple .env updater - in production use python-dotenv or similar
    # This reads the file lines, updates found keys, appends new ones
    lines = []
    if ENV_PATH.exists():
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()

    current_keys = {}
    for i, line in enumerate(lines):
        if "=" in line:
            key = line.split("=")[0].strip()
            current_keys[key] = i

    for key, value in api_keys.items():
        if not value or value.strip() == "":
            continue

        # Masked value check (don't save if value is still redacted)
        if _is_masked_value(value):
            continue

        line_content = f"{key}={value}\n"
        if key in current_keys:
            lines[current_keys[key]] = line_content
        else:
            lines.append(line_content)

    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)


@router.get("/settings")
async def get_settings():
    try:
        config = load_yaml_config()
        limits = load_limits_config()
        
        # Extract global config from limits
        global_conf = limits.get("global", {})

        # Return masked API keys existence check
        api_keys = {
            "OPENAI_API_KEY": "sk-****" if os.getenv("OPENAI_API_KEY") else "",
            "ANTHROPIC_API_KEY": "sk-****" if os.getenv("ANTHROPIC_API_KEY") else "",
            "GOOGLE_API_KEY": "AIza****" if os.getenv("GOOGLE_API_KEY") else "",
            "PERPLEXITY_API_KEY": "pplx-****" if os.getenv("PERPLEXITY_API_KEY") else "",
        }
        
        return {
            "models": config,
            "limits": limits,
            "global_config": global_conf,
            "api_keys": api_keys
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/settings")
async def update_settings(settings: GlobalSettings):
    try:
        # 1. Save YAML config
        if settings.models:
            save_yaml_config(settings.models)
        
        # 2. Save Limits config (merge global config)
        current_limits = load_limits_config()
        
        if settings.limits:
            current_limits.update(settings.limits)
            
        if settings.global_config:
            current_limits["global"] = settings.global_config.dict()
            
        save_limits_config(current_limits)
        
        # 2. Update .env if keys provided
        if settings.api_keys:
            update_env_file(settings.api_keys)

        return {
            "status": "success",
            "message": "Settings updated. Restart may be required for API keys.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/client-settings")
async def get_client_settings():
    try:
        limits = load_limits_config()
        global_conf = limits.get("global", {})
        
        # Define model traits statically
        model_traits_catalog = {
            "gpt-5-nano": {"label": "GPT-5 Nano ⚡", "traits": "Ultra Fast, Low Cost", "provider": "openai"},
            "gpt-5-mini": {"label": "GPT-5 Mini 🚀", "traits": "Fast, Cost-Effective", "provider": "openai"},
            "gpt-5.2": {"label": "GPT-5.2 🧠", "traits": "High Intelligence", "provider": "openai"},
            "claude-sonnet-4.5": {"label": "Claude Sonnet 4.5 💡", "traits": "Balanced", "provider": "anthropic"},
            "claude-opus-4.6": {"label": "Claude Opus 4.6 🔬", "traits": "Deep Thinking, Premium", "provider": "anthropic"},
            "gemini-3-flash": {"label": "Gemini 3 Flash ⚡", "traits": "Ultra Fast", "provider": "google"},
            "gemini-3-pro": {"label": "Gemini 3 Pro 📖", "traits": "Mega Context, 1M tokens", "provider": "google"},
            "sonar-deep-research": {"label": "Sonar Deep Research 🌐", "traits": "Web Research", "provider": "perplexity"},
            "sonar": {"label": "Sonar 🔍", "traits": "Fact Checking", "provider": "perplexity"}
        }

        allowed_model_ids = limits.get("allowed_user_models", ["gpt-5-mini", "gpt-5.2"])
        client_models = []
        for mid in allowed_model_ids:
            if mid in model_traits_catalog:
                entry = model_traits_catalog[mid].copy()
                entry["id"] = mid
                client_models.append(entry)

        allowed_options = limits.get("allowed_user_options", {})
        
        from core.cost_manager import CostManager
        cm = CostManager(enable_history=True)

        return {
            "models": client_models,
            "modes": allowed_options.get("modes", ["fast", "thinking", "agentic"]),
            "form_studio_enabled": allowed_options.get("form_studio", True),
            "limits": {
                "per_task_budget": global_conf.get("per_task_budget", 0.25),
                "per_day_budget": global_conf.get("per_day_budget", 2.0)
            },
            "daily_spend": {
                "today_usd": cm.day_cost,
                "limit_usd": global_conf.get("per_day_budget", 2.0)
            },
            "advanced_options": {
                "review_strategy": allowed_options.get("show_review_strategy", False),
                "consensus_mode": allowed_options.get("show_consensus_mode", False),
                "retrieval_mode": allowed_options.get("show_retrieval_mode", False)
            },
            "allowed_rag_tiers": limits.get("allowed_rag_tiers", [3, 4])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/approve")
async def approve_settings(settings: GlobalSettings):
    return await update_settings(settings)
