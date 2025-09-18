"""Orchestrator entrypoint with model routing, validation, tracing."""
from dataclasses import dataclass, asdict
from pathlib import Path
import json, argparse
from .context_manager import build_context
from .model_router import route
from .output_validator import validate
from .llm_client import call
from .tracing import log

@dataclass
class Result:
    ok: bool
    message: str

def run(phase: str, schema_path: str, specialty: str | None = None, extra_context: str | None = None) -> Result:
    ctx = build_context(phase=phase, specialty=specialty, schema_path=Path(schema_path))
    model = route(phase, specialty)
    log("orchestrator.context", {"phase": phase, "specialty": specialty, "schema": Path(schema_path).name, "model": asdict(model)})
    # Build prompt with optional RAG context (truncate to ~2000 chars for safety)
ctx_snippet = (extra_context or "")[:2000]
prompt = (
    f"Generate JSON valid to provided schema for phase={phase}, specialty={specialty}. "
    "Output only JSON. "
    + (f"Context:\n{ctx_snippet}" if ctx_snippet else "")
)
    resp = call(model.name, prompt, temperature=model.temperature)
    ok, err = validate(resp.text, ctx.schema)
    log("orchestrator.validate", {"ok": ok, "error": err})
    if not ok:
        return Result(ok=False, message=f"Validation failed: {err}\nRaw: {resp.text[:200]}...")
    return Result(ok=True, message="Run succeeded with model %s" % model.name)

def main():
    ap = argparse.ArgumentParser(description="AI Code Orchestrator")
    ap.add_argument("--phase", required=True, help="analyst|architect|tester|...")
    ap.add_argument("--schema", required=True, help="Path to JSON schema")
    ap.add_argument("--specialty", required=False, help="css|react|typescript|dotnet|...")
    args = ap.parse_args()
    res = run(phase=args.phase, schema_path=args.schema, specialty=args.specialty)
    print(("OK: " if res.ok else "FAIL: ") + res.message)

if __name__ == "__main__":
    main()
