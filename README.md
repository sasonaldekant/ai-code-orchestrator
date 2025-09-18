# ai-code-orchestrator

This scaffold implements the **next step**: filled JSON schemas, prompt templates, a runnable CLI, unit tests, and CI.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
pip install jsonschema pyyaml
python -m cli --phase analyst --schema schemas/phase_schemas/requirements.json
```

## Layout
- `core/` — orchestrator, routing, validation
- `schemas/` — JSON Schemas for phase and specialist outputs
- `prompts/` — universal/spec templates + phase/specialist prompts
- `evals/` — placeholder evaluation scripts
- `rag/` — domain indices placeholders
- `tests/` — unit tests for validator
- `.github/workflows/ci.yml` — CI pipeline


## E2E Dry Run
```
python -m pipeline
ls outputs
```

## RAG (toy) demo
```
make rag-ingest
make rag-query
```

## Docker
```
make docker-build
make docker-run
```

## Tracing & audit
By default tracing is **on** and writes JSONL:
```
export TRACE_JSONL=1
export TRACE_FILE=trace.jsonl
```

## Real LLM (optional)
Set `OFFLINE_LLM=0` and provide `OPENAI_API_KEY`. The client tries OpenAI Responses API:
```
export OFFLINE_LLM=0
export OPENAI_API_KEY=sk-...
python -m cli --phase analyst --schema schemas/phase_schemas/requirements.json
```
If the SDK isn't installed or call fails, it falls back to offline stub and traces the reason.

## REST API
Local:
```
make api-run
# health
curl http://localhost:8000/health
# run orchestrator
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" \  -d '{"phase":"analyst","schema_name":"requirements"}'
```

Docker Compose:
```
make compose-up
# then hit http://localhost:8000/health
make compose-down
```

### API with RAG
Ingest sample domain docs and run with a question to enrich context:
```
make api-run         # terminal A
make api-ingest      # terminal B
curl -X POST http://localhost:8000/run -H "Content-Type: application/json"   -d '{"phase":"analyst","schema_name":"requirements","question":"frontend accessibility","top_k":2}'
# RAG context stored in outputs/rag_context.txt
```

### Query endpoint
```
make api-run           # terminal A
make api-ingest        # terminal B
make api-query         # hits POST /query
```
The `/run` endpoint now merges retrieved text into the LLM prompt (truncated to ~2000 chars). Audit copy is stored in `outputs/rag_context.txt`.
