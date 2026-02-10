from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any, Optional
import yaml
import os
from pathlib import Path

router = APIRouter(prefix="/config", tags=["config"])

CONFIG_PATH = Path("config/model_mapping_v2.yaml")
ENV_PATH = Path(".env")

class ModelConfig(BaseModel):
    model: str
    provider: str
    temperature: float = 0.0
    max_tokens: int = 4000

class GlobalSettings(BaseModel):
    models: Dict[str, Any]
    api_keys: Optional[Dict[str, str]] = None

def load_yaml_config():
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_yaml_config(data: Dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

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
        if not value or value.strip() == "": continue
        
        # Masked value check (don't save if it's ****)
        if "*" in value: continue

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
        
        # Return masked API keys existence check
        api_keys = {
            "OPENAI_API_KEY": "sk-****" if os.getenv("OPENAI_API_KEY") else "",
            "ANTHROPIC_API_KEY": "sk-****" if os.getenv("ANTHROPIC_API_KEY") else "",
            "GOOGLE_API_KEY": "AIza****" if os.getenv("GOOGLE_API_KEY") else "",
            "PERPLEXITY_API_KEY": "pplx-****" if os.getenv("PERPLEXITY_API_KEY") else ""
        }
        
        return {
            "models": config,
            "api_keys": api_keys
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/settings")
async def update_settings(settings: GlobalSettings):
    try:
        # 1. Save YAML config
        save_yaml_config(settings.models)
        
        # 2. Update .env if keys provided
        if settings.api_keys:
            update_env_file(settings.api_keys)
            
        return {"status": "success", "message": "Settings updated. Restart may be required for API keys."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
