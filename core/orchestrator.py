from dataclasses import dataclass
from pathlib import Path
import json

from .model_router import route
from .output_validator import validate
from .llm_client import call

# Optional tracing: fall back to no-op if not present
try:
    from .tracing import log as _trace_log
except Exception:  # pragma: no cover
    def _trace_log(*args, **kwargs):
        return None

@dataclass
class Result:
    ok: bool
    message: str

def _extract_text(resp) -> str:
    """Handle several possible response shapes from llm_client.call."""
    if resp is None:
        return ""
    if isinstance(resp, str):
        return resp
    # dict-like
    if isinstance(resp, dict):
        return str(resp.get("text", resp))
    # object with .text
    text = getattr(resp, "text", None)
    if text is not None:
        return str(text)
    return str(resp)

def _build_prompt(phase: str, specialty: str | None, schema: dict, extra_context: str | None):
    parts = [
        "You are a micro-specialized code agent.",
        f"Phase: {phase}",
        f"Specialty: {specialty or 'generic'}",
        "Produce ONLY valid JSON matching the provided JSON Schema.",
        "DO NOT include any prose outside the JSON value.",
    ]
    if extra_context:
        parts.append("Context:\n" + extra_context)
    parts.append("JSON Schema:\n" + json.dumps(schema))
    return "\n\n".join(parts)

def run(phase: str, schema_path: str, specialty: str | None = None, extra_context: str | None = None) -> Result:
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    model = route(phase, specialty)
    prompt = _build_prompt(phase, specialty, schema, extra_context)
    resp = call(model.name, prompt, temperature=model.temperature)
    text = _extract_text(resp)

    ok, err = validate(text, schema)

    _trace_log("orchestrator.run", {
        "phase": phase, "specialty": specialty, "model": model.name, "ok": ok
    })

    if not ok:
        return Result(ok=False, message=f"Validation failed: {err}\nRaw: {text[:200]}...")

    out_dir = Path("outputs"); out_dir.mkdir(exist_ok=True)
    out = out_dir / f"{phase}-{(specialty or 'generic')}.json"
    out.write_text(text, encoding="utf-8")
    return Result(ok=True, message=f"Run succeeded with model {model.name}")
