
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import logging
import json
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from core.lifecycle_orchestrator import LifecycleOrchestrator
from rag.domain_aware_retriever import DomainAwareRetriever
from domain_knowledge.ingestion.database_schema_ingester import DatabaseSchemaIngester
from domain_knowledge.ingestion.component_library_ingester import ComponentLibraryIngester
from rag.vector_store import ChromaVectorStore
from api.admin_routes import router as admin_router
from api.vision_routes import router as vision_router
from api.ide_routes import router as ide_router
from api.config_routes import router as config_router
from api.agent_routes import router as agent_router

# Basic auth helper
import os

API_KEY = os.getenv("API_KEY")

def check_auth(req: Request):
    if API_KEY:
        if req.headers.get("x-api-key") != API_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized")

app = FastAPI(title="AI Code Orchestrator API v3.0", version="3.0.0")

# Include admin routes
from api.knowledge_routes import router as knowledge_router

app.include_router(admin_router)
app.include_router(vision_router)
app.include_router(ide_router)
app.include_router(config_router)
app.include_router(agent_router)
app.include_router(knowledge_router)

# Enable CORS for local UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Metrics
REQS = Counter("aio_requests_total", "Total API requests", ["path", "method", "status"])
LAT = Histogram("aio_request_seconds", "Request latency seconds", ["path", "method"])


class RunRequest(BaseModel):
    request: str
    context: Optional[Dict[str, Any]] = None
    deep_search: bool = False
    retrieval_strategy: str = "local"
    auto_fix: bool = False
    budget_limit: Optional[float] = None
    consensus_mode: bool = False
    review_strategy: str = "basic"

class IngestRequest(BaseModel):
    type: str # database, component_library
    path: str
    collection: Optional[str] = None
    models_dir: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@app.get("/health")
def health():
    return {"status": "ok", "version": "3.0.0"}

@app.get("/metrics")
def metrics():
    return (generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST})


@app.get("/stream/logs")
async def stream_logs(request: Request):
    """
    SSE Endpoint for streaming orchestration events to the UI.
    """
    async def event_generator():
        q = bus.subscribe()
        try:
            while True:
                if await request.is_disconnected():
                    break
                
                # Wait for event
                event = await q.get()
                
                # SSE Format: "data: {json}\n\n"
                yield f"data: {event.to_json()}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            bus.unsubscribe(q)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


from api.shared import orchestrator_instance

@app.post("/run")
async def run_feature(req: RunRequest, request: Request):
    # check_auth(request) # Optional for local UI mode
    
    # Notify start
    await bus.publish(Event(type=EventType.LOG, agent="API", content=f"Starting request: {req.request}"))

    try:
        # Use global instance to preserve state for monitoring
        global orchestrator_instance
        
        result = await orchestrator_instance.execute_request(
            req.request,
            deep_search=req.deep_search,
            retrieval_strategy=req.retrieval_strategy,
            auto_fix=req.auto_fix,
            budget_limit=req.budget_limit,
            consensus_mode=req.consensus_mode,
            review_strategy=req.review_strategy
        )
        
        await bus.publish(Event(type=EventType.DONE, agent="Orchestrator", content=result))
        return result
    except Exception as e:
        logging.error(f"Error running request: {e}")
        await bus.publish(Event(type=EventType.ERROR, agent="Orchestrator", content=str(e)))
        raise HTTPException(status_code=500, detail=str(e))

# Knowledge endpoints moved to api/knowledge_routes.py
