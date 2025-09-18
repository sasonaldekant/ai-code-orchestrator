from __future__ import annotations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from core.orchestrator import run as orchestrate
from rag.ingest import ingest_dir
from rag.query import ask

import os, time, math, threading
from typing import Dict, Tuple
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

REQS = Counter("aio_requests_total", "Total API requests", ["path", "method", "status"])
LAT = Histogram("aio_request_seconds", "Request latency seconds", ["path", "method"])

API_KEY = os.getenv("API_KEY")  # if None, auth disabled
def check_key(req: Request):
    if API_KEY is None:
        return True
    return req.headers.get("x-api-key") == API_KEY

_LIMIT = int(os.getenv("RATE_LIMIT_PER_MIN", "60"))
_refill = _LIMIT / 60.0
_buckets: Dict[str, Tuple[float, float]] = {}
_lock = threading.Lock()

def allow(ip: str) -> bool:
    if _LIMIT <= 0:
        return True
    now = time.time()
    with _lock:
        tokens, last = _buckets.get(ip, (_LIMIT, now))
        delta = now - last
        tokens = min(_LIMIT, tokens + delta * _refill)
        if tokens >= 1.0:
            tokens -= 1.0
            _buckets[ip] = (tokens, now)
            return True
        _buckets[ip] = (tokens, now)
        return False

app = FastAPI(title="AI Code Orchestrator API", version="0.0.1")

SCHEMA_MAP = {
    "requirements": "schemas/phase_schemas/requirements.json",
    "architecture": "schemas/phase_schemas/architecture.json",
    "test_report": "schemas/phase_schemas/test_report.json",
    "css_output": "schemas/specialist_schemas/css_output.json",
    "typescript_types": "schemas/specialist_schemas/typescript_types.json",
    "react_component": "schemas/specialist_schemas/react_component.json",
    "dotnet_api": "schemas/specialist_schemas/dotnet_api.json",
}


class IngestRequest(BaseModel):
    src: str = "rag/domain_docs"
    store: str = "rag/store.json"

class RunRequest(BaseModel):
    phase: str
    schema_name: str
    specialty: str | None = None
    question: str | None = None   # optional RAG question to enrich prompt
    top_k: int = 3

    class Config:
        json_schema_extra = {
            "examples": [{
                "phase": "analyst",
                "schema_name": "requirements",
                "specialty": None,
                "question": "frontend accessibility",
                "top_k": 2
            }]
        }


class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

    class Config:
        json_schema_extra = {
            "examples": [{
                "question": "OpenAPI health checks",
                "top_k": 3
            }]
        }

class QueryHit(BaseModel):
    id: str
    score: float
    text: str

class RunResponse(BaseModel):
    ok: bool
    message: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/query")
def post_query(req: QueryRequest, request: Request):
    if not check_key(request):
        REQS.labels(path="/query", method="POST", status="401").inc()
        raise HTTPException(status_code=401, detail="Unauthorized")
    ip = request.client.host if request and request.client else "unknown"
    if not allow(ip):
        REQS.labels(path="/query", method="POST", status="429").inc()
        raise HTTPException(status_code=429, detail="Too Many Requests")
    import time as _t; _t0 = _t.time()
    hits = ask('rag/store.json', req.question, k=req.top_k)
    LAT.labels(path="/query", method="POST").observe(_t.time()-_t0); REQS.labels(path="/query", method="POST", status="200").inc()
    return [{"id": h[0], "score": h[1], "text": h[2]} for h in hits]

@app.post("/ingest")
def post_ingest(req: IngestRequest, request: Request):
    if not check_key(request):
        REQS.labels(path="/ingest", method="POST", status="401").inc()
        raise HTTPException(status_code=401, detail="Unauthorized")
    ip = request.client.host if request and request.client else "unknown"
    if not allow(ip):
        REQS.labels(path="/ingest", method="POST", status="429").inc()
        raise HTTPException(status_code=429, detail="Too Many Requests")
    import time as _t; _t0 = _t.time()
    ingest_dir(req.src, req.store)
    LAT.labels(path="/ingest", method="POST").observe(_t.time()-_t0); REQS.labels(path="/ingest", method="POST", status="200").inc()
    return {"status": "ok", "store": req.store, "src": req.src}

@app.post("/run", response_model=RunResponse)
def post_run(req: RunRequest, request: Request):
    # Auth, RL, metrics start
    if not check_key(request):
        REQS.labels(path="/run", method="POST", status="401").inc()
        raise HTTPException(status_code=401, detail="Unauthorized")
    ip = request.client.host if request and request.client else "unknown"
    if not allow(ip):
        REQS.labels(path="/run", method="POST", status="429").inc()
        raise HTTPException(status_code=429, detail="Too Many Requests")
    import time as _t; _t0 = _t.time()

    schema_rel = SCHEMA_MAP.get(req.schema_name)
    if not schema_rel:
        REQS.labels(path="/run", method="POST", status="400").inc()
        raise HTTPException(status_code=400, detail=f"Unknown schema_name '{req.schema_name}'")
    schema_path = Path(schema_rel)
    if not schema_path.exists():
        REQS.labels(path="/run", method="POST", status="500").inc()
        raise HTTPException(status_code=500, detail=f"Schema not found at {schema_path}")
    # Optional RAG
    if req.question:
        try:
            hits = ask('rag/store.json', req.question, k=req.top_k)
            ctx_lines = [h[2] for h in hits]
            (Path('outputs')/ 'rag_context.txt').write_text('\n---\n'.join(ctx_lines), encoding='utf-8')
        except Exception:
            ctx_lines = []
    else:
        ctx_lines = []
    res = orchestrate(phase=req.phase, schema_path=str(schema_path), specialty=req.specialty, extra_context='\n'.join(ctx_lines) if ctx_lines else None)
    LAT.labels(path="/run", method="POST").observe(_t.time()-_t0); REQS.labels(path="/run", method="POST", status="200").inc()
    return RunResponse(ok=res.ok, message=res.message)
