# AI Code Orchestrator — Technical Documentation
*Version:* 0.1.0  
*Last updated:* 2025-09-18 20:39:52Z

---


## 1) Overview
The **AI Code Orchestrator** is a scaffolded system for micro‑specialized agent orchestration with:
- **Phase agents** (analyst, architect, implementer, tester placeholders)
- **Specialist agents** (frontend: CSS/TS/React; backend: .NET; integration; DevOps)
- **Schema‑driven outputs** (JSON Schema validation across phases & specialties)
- **Prompt templates** (universal/spec templates + phase/specialist prompts)
- **RAG layer** (deterministic embeddings + ingest/query pipeline)
- **CLI & E2E pipeline** (dry‑run that validates all outputs end‑to‑end)
- **REST API** (FastAPI) with **auth**, **rate limiting**, **Prometheus metrics**
- **Tracing/Audit** (JSONL), **evals**, **CI artifacts**, **Docker/Compose**, **devcontainer**
- **Versioned artifacts** (outputs written to `outputs/v<semver>/<UTC-TS>/`)

This documentation consolidates **all iterations** and explains installation, usage, APIs, and design decisions.

---

## 2) Repository Structure (key folders/files)
```
core/
  orchestrator.py         # routing + validation + tracing
  context_manager.py      # loads schema/rules & builds runtime context
  model_router.py         # simple heuristic model selection
  output_validator.py     # JSON Schema validation
  llm_client.py           # LLM call (offline stub + optional OpenAI SDK, retry/backoff, tracing)
  tracing.py              # JSONL audit logs
  versioning.py           # writes versioned artifacts
agents/
  phase_agents/           # analyst/architect/implementer/tester (stubs)
  specialist_agents/      # frontend/backend/integration roles (stubs)
schemas/
  phase_schemas/          # requirements.json, architecture.json, test_report.json
  specialist_schemas/     # css_output.json, typescript_types.json, react_component.json, dotnet_api.json, microservice_config.json
prompts/
  templates/              # universal_template.yaml, specialist_template.yaml
  phase_prompts/          # analyst_prompts.yaml, architect_prompts.yaml
  specialist_prompts/     # css_prompts.yaml, typescript_prompts.yaml, react_prompts.yaml, dotnet_prompts.yaml
rag/
  embeddings_store.py     # toy embeddings + cosine similarity
  ingest.py               # ingest .md files into store
  query.py                # top‑k query against store
  domain_docs/            # example domain docs (frontend/backend/devops)
api/
  app.py                  # FastAPI app: /health, /metrics, /ingest, /query, /run (with RAG-in-prompt)
evals/
  specialist_evals/       # css_quality_eval.py, typescript_eval.py, react_best_practices.py, dotnet_standards.py
tests/
  test_validator.py       # schema validator unit tests
  test_orchestrator_cli.py# CLI smoke test
  test_rag.py             # ingest + query test
examples/
  requirements.sample.json
docs/
  GET_STARTED.md
VERSION
cli.py                    # CLI entrypoint
pipeline.py               # E2E dry‑run pipeline (writes versioned outputs)
Dockerfile                # pipeline image
Dockerfile.api            # API image
docker-compose.yml        # API + Qdrant (stub)
Makefile                  # helpful tasks
.devcontainer/            # VS Code devcontainer
.github/workflows/ci.yml  # CI pipeline (tests + E2E + artifact upload)
.github/ISSUE_TEMPLATE/*  # issue templates
.github/PULL_REQUEST_TEMPLATE.md
.github/CODEOWNERS
pyproject.toml            # project metadata & deps
README.md
```

---

## 3) Requirements
- **Python** 3.10+ (dev), CI uses 3.11
- OS: Linux/Mac/Windows
- Optional: **Docker**/**Docker Compose**, **VS Code** (devcontainer), **jq** (for curl)

---

## 4) Installation & Quickstart
```bash
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -e .[dev]
pip install jsonschema pyyaml
```

### 4.1 Offline vs Online LLM
- Offline deterministic stub (default):  
  `export OFFLINE_LLM=1`
- Online (OpenAI Responses API) with retry/backoff + tracing fallback:  
  ```bash
  export OFFLINE_LLM=0
  export OPENAI_API_KEY=sk-...   # if SDK not present or call fails => auto fallback to offline stub
  ```

### 4.2 CLI (single run)
```bash
python -m cli --phase analyst --schema schemas/phase_schemas/requirements.json
```

### 4.3 E2E Dry‑Run Pipeline
```bash
python -m pipeline
# outputs written to: outputs/v<semver>/<UTC-timestamp>/
```

### 4.4 Run Tests
```bash
pytest -q
```

---

## 5) JSON Schemas
**Phase schemas:** `requirements.json`, `architecture.json`, `test_report.json`  
**Specialist schemas:** `css_output.json`, `typescript_types.json`, `react_component.json`, `dotnet_api.json`, `microservice_config.json`

All agent outputs must validate against the corresponding schema; validation is enforced by `core/output_validator.py`.

---

## 6) Prompts
- **Universal template**: `prompts/templates/universal_template.yaml` (schema‑first outputs, deterministic, no placeholders)
- **Specialist template**: `prompts/templates/specialist_template.yaml`
- **Phase prompts**: `analyst_prompts.yaml`, `architect_prompts.yaml`
- **Specialist prompts**: `css_prompts.yaml`, `typescript_prompts.yaml`, `react_prompts.yaml`, `dotnet_prompts.yaml`

---

## 7) RAG (toy) Subsystem
### 7.1 Ingest
```bash
# ingest built-in domain docs into JSON store
python -m rag.ingest --src rag/domain_docs --store rag/store.json
```
### 7.2 Query
```bash
python -m rag.query --store rag/store.json --q "frontend accessibility" --k 3
```
### 7.3 How it works
- Deterministic “hash” embeddings (no external services)
- Cosine similarity ranking
- Used by API `/query` and **merged into** `/run` prompts (truncated ~2000 chars)

---

## 8) Tracing & Audit
- JSONL tracing enabled by default (or set `TRACE_JSONL=1`)
- Configure log path: `TRACE_FILE=trace.jsonl`
- LLM calls, responses, errors, routing decisions and validation outcomes are recorded

```bash
export TRACE_JSONL=1
export TRACE_FILE=trace.jsonl
```

---

## 9) Evaluations
Location: `evals/specialist_evals/*`  
- `css_quality_eval.py`: BEM/WCAG hints, small heuristic score  
- `typescript_eval.py`: presence of core TS constructs  
- `react_best_practices.py`: function components/hooks  
- `dotnet_standards.py`: `/health` endpoint + OpenAPI header  
E2E pipeline writes `outputs/.../eval_summary.json` with scores.

---

## 10) REST API
**Stack:** FastAPI + Uvicorn  

### 10.1 Run Locally
```bash
export OFFLINE_LLM=1
# Optional auth & rate limit:
export API_KEY=secret
export RATE_LIMIT_PER_MIN=120
make api-run
```

### 10.2 Endpoints
- `GET /health` → `{{"status": "ok"}}`
- `GET /metrics` → Prometheus metrics (counters & latency histograms)
- `POST /ingest` → `{{ "src": "...", "store": "..." }}`  
  **Body:** `{{ "src": "rag/domain_docs", "store": "rag/store.json" }}`
- `POST /query` → RAG top‑k results  
  **Body:** `{{ "question": "text", "top_k": 3 }}`
- `POST /run` → Run orchestrator with optional RAG enrichment  
  **Body:**  
  ```json
  {{
    "phase": "analyst",
    "schema_name": "requirements",
    "specialty": null,
    "question": "frontend accessibility",
    "top_k": 2
  }}
  ```
  **Response:** `{{ "ok": true, "message": "Run succeeded with model ..." }}`

### 10.3 Authentication
- If `API_KEY` is set, the server requires header: `X-API-Key: <API_KEY>`

### 10.4 Rate Limiting
- Token bucket per IP. Configure: `RATE_LIMIT_PER_MIN` (default: 60).

### 10.5 RAG‑Enriched Prompts
- If `/run` body includes `question`, the top‑k retrieved chunks are:
  1) saved to `outputs/rag_context.txt` for audit
  2) **merged into the LLM prompt** (truncated ~2000 chars)

---

## 11) Docker & Compose
### 11.1 Pipeline Image
```bash
make docker-build
make docker-run
```
### 11.2 API Image
```bash
make api-docker-build
make api-docker-run
```
### 11.3 Docker Compose (API + Qdrant stub)
```bash
make compose-up    # builds API, runs alongside Qdrant
make compose-down  # stop & remove
```

---

## 12) Devcontainer
- `.devcontainer/devcontainer.json` for quick VS Code setup (Python, Ruff, Docker)

---

## 13) CI (GitHub Actions)
Workflow: `.github/workflows/ci.yml`
- Install deps → run tests → run E2E pipeline
- Upload artifacts: `outputs/*` + `trace.jsonl`

---

## 14) Versioned Outputs
- File: `VERSION` (semantic version for your artifacts)
- Pipeline writes artifacts to: `outputs/v<semver>/<UTC-timestamp>/`
- Bump `VERSION` when changing schemas/prompts/business rules

---

## 15) Makefile Targets
```make
init            # venv + deps
test            # pytest
run             # pipeline
rag-ingest      # ingest rag/domain_docs -> rag/store.json
rag-query       # query store.json
docker-build    # pipeline image
docker-run      # run pipeline container
api-run         # local uvicorn API
api-docker-build
api-docker-run
compose-up      # API + Qdrant
compose-down
api-ingest      # convenience RAG ingest for API
api-run-rag     # curl POST /run with question
api-query       # curl POST /query
```

---

## 16) Configuration (env vars)
- `OFFLINE_LLM` (1|0): offline stub vs SDK
- `OPENAI_API_KEY`: OpenAI Responses API key (when `OFFLINE_LLM=0`)
- `TRACE_JSONL` (1|0), `TRACE_FILE`: tracing on/off and file path
- `API_KEY`: if provided, API requires header `X-API-Key`
- `RATE_LIMIT_PER_MIN`: token bucket per IP (default: 60)

---

## 17) Security Notes
- No secrets in repo; use env vars
- Traces do not record raw secrets; audit files are local by default
- Rate limiting prevents accidental API abuse in demos
- Optional auth via API key (simple but effective for prototypes)

---

## 18) Troubleshooting
- **Schema validation failed**: ensure outputs match required fields; check `schemas/*`
- **OpenAI call fails**: set `OFFLINE_LLM=1` or provide valid `OPENAI_API_KEY`
- **429 Too Many Requests**: raise `RATE_LIMIT_PER_MIN` or back off
- **No RAG results**: run `/ingest` first or adjust query text
- **Artifacts missing**: check `outputs/v<semver>/<UTC-TS>/` and CI artifact uploads

---

## 19) Change Log (by iteration)
1. **Initial scaffold**: repo layout, stubs, config, docs boilerplate  
2. **Filled schemas, prompts, CLI, tests, CI skeleton**  
3. **E2E dry‑run**: requirements → architecture → specialists → test report (validated)  
4. **LLM routing + offline stub**, **RAG ingest/query**, **Dockerfile**, **Makefile**, **devcontainer**  
5. **Tracing (JSONL)**, **eval scripts**, **CI artifacts** upload  
6. **REST API** (FastAPI), **Docker Compose** (with Qdrant stub), GH templates  
7. **API /ingest & RAG**, **/run** enriched with saved context  
8. **/query endpoint** and **in‑prompt** context injection + OpenAPI examples  
9. **Auth (X-API-Key)**, **rate limiting**, **Prometheus metrics**, **versioned outputs**

---

## 20) Roadmap (suggested next steps)
- Replace toy embeddings with a real vector DB (Qdrant client) and semantic chunking
- Add richer evals (linters, unit tests per generated artifact)
- Advanced routing (per‑specialty temperature, cost/latency constraints)
- Persistent run registry endpoint (list/retrieve artifacts & traces)
- CI: caching, coverage reports, SBOM

---

## 21) License & Ownership
Provide your organization’s license and ownership statements here.
