from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass
class ModelChoice:
    name: str
    temperature: float = 0.0

_cfg = None

def _load_cfg():
    global _cfg
    if _cfg is None:
        cfg_path = Path(__file__).resolve().parent.parent / "config" / "model_mapping.yaml"
        _cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    return _cfg

def route(phase: str, specialty: str | None) -> ModelChoice:
    cfg = _load_cfg()
    d = dict(cfg.get("default", {}))
    # precedence: phase → specialty override
    if phase and phase in cfg.get("routing", {}).get("phase", {}):
        d.update(cfg["routing"]["phase"][phase])
    if specialty and specialty in cfg.get("routing", {}).get("specialty", {}):
        d.update(cfg["routing"]["specialty"][specialty])
    return ModelChoice(name=d["model"], temperature=float(d.get("temperature", 0.0)))
