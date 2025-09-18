from dataclasses import dataclass
from pathlib import Path
import json, yaml

@dataclass
class Context:
    phase: str
    specialty: str | None
    rules: dict
    schema: dict
    extra: dict

def load_yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8"))

def load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))

def build_context(phase: str, specialty: str | None, schema_path: Path, rules_path: Path | None = None) -> Context:
    rules = load_yaml(rules_path) if rules_path and rules_path.exists() else {}
    schema = load_json(schema_path)
    return Context(phase=phase, specialty=specialty, rules=rules, schema=schema, extra={})
