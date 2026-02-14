from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import yaml
import os
from pathlib import Path

router = APIRouter(prefix="/config", tags=["config"])

CONFIG_PATH = Path("config/model_mapping.yaml")
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

class GlobalSettings(BaseModel):
    models: Dict[str, Any]
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
