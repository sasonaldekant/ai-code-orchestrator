from __future__ import annotations
import os
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Limits:
    top_k: int = 4
    max_input_tokens: int = 6000
    max_output_tokens: int = 1000
    concurrency: int = 2

def load_limits() -> Limits:
    # from YAML if present
    cfg = {}
    p = Path(__file__).resolve().parent.parent / "config" / "limits.yaml"
    if p.exists():
        import yaml  # project already uses PyYAML
        cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    budgets = cfg.get("budgets", {})
    retr = cfg.get("retrieval", {})
    conc = cfg.get("concurrency", {})
    return Limits(
        top_k = int(os.getenv("ACORCH_TOP_K", retr.get("top_k", 4))),
        max_input_tokens = int(os.getenv("ACORCH_MAX_INPUT_TOKENS", budgets.get("max_input_tokens", 6000))),
        max_output_tokens = int(os.getenv("ACORCH_MAX_OUTPUT_TOKENS", budgets.get("max_output_tokens", 1000))),
        concurrency = int(os.getenv("ACORCH_CONCURRENCY", conc.get("max_workers", 2))),
    )

def get_dynui_path() -> Path:
    """Returns the absolute path to the DynUI project."""
    path_str = os.getenv("DYNUI_PROJECT_PATH", "../dyn-ui-main-v01")
    return Path(path_str).resolve()

def resolve_path(metadata_path: str | None) -> str | None:
    """
    Resolves a file path, attempting to 'heal' it if the absolute path from 
    RAG metadata doesn't exist on the current machine.
    """
    if not metadata_path:
        return None
        
    p = Path(metadata_path)
    
    # 1. If it already exists, use it
    if p.exists():
        return str(p.absolute())
        
    # 2. Try to re-anchor it using the current DynUI project path
    # Look for the project folder name in the path to extract the relative part
    dynui_root = get_dynui_path()
    project_folder_name = dynui_root.name # e.g. "dyn-ui-main-v01"
    
    parts = p.parts
    if project_folder_name in parts:
        idx = parts.index(project_folder_name)
        relative_part = Path(*parts[idx+1:])
        healed_path = dynui_root / relative_part
        if healed_path.exists():
            return str(healed_path.absolute())
            
    # 3. Fallback: Check if it's just a filename in the DynUI root (recursive)
    filename = p.name
    for found_path in dynui_root.rglob(filename):
        return str(found_path.absolute())
        
    return metadata_path # Return original if all else fails
