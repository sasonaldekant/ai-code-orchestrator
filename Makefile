.PHONY: init test run rag-ingest rag-query docker-build docker-run
init:
	python -m venv .venv && . .venv/bin/activate && pip install -e .[dev] && pip install jsonschema pyyaml
test:
	pytest -q
run:
	python -m pipeline
rag-ingest:
	python -m rag.ingest --src rag/domain_docs --store rag/store.json
rag-query:
	python -m rag.query --store rag/store.json --q "frontend accessibility" --k 2
docker-build:
	docker build -t ai-orchestrator:dev .
docker-run:
	docker run --rm ai-orchestrator:dev

api-run:
	uvicorn api.app:app --host 0.0.0.0 --port 8000

api-docker-build:
	docker build -t ai-orchestrator-api:dev -f Dockerfile.api .

api-docker-run:
	docker run --rm -p 8000:8000 -e OFFLINE_LLM=1 ai-orchestrator-api:dev

compose-up:
	docker compose up -d --build

compose-down:
	docker compose down -v

api-ingest:
	python -m rag.ingest --src rag/domain_docs --store rag/store.json

api-run-rag:
	curl -s -X POST http://localhost:8000/run -H "Content-Type: application/json" -d '{"phase":"analyst","schema_name":"requirements","question":"frontend accessibility","top_k":2}' | jq .

api-query:
	curl -s -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"question":"OpenAPI health checks","top_k":3}' | jq .
