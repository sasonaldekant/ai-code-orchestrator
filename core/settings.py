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
