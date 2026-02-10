
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
from api.event_bus import bus, Event, EventType
from api.admin_routes import router as admin_router

# Basic auth helper
import os

API_KEY = os.getenv("API_KEY")

def check_auth(req: Request):
    if API_KEY:
        if req.headers.get("x-api-key") != API_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized")

app = FastAPI(title="AI Code Orchestrator API v3.0", version="3.0.0")

# Include admin routes
app.include_router(admin_router)

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


@app.post("/run")
async def run_feature(req: RunRequest, request: Request):
    # check_auth(request) # Optional for local UI mode
    
    # Run in background to not block, but for now we await to keep simple
    # Ideally, we return a task ID and stream events
    
    # Notify start
    await bus.publish(Event(type=EventType.LOG, content=f"Starting request: {req.request}", agent="API"))

    try:
        orchestrator = LifecycleOrchestrator()
        # We need to inject the event bus into orchestrator to capture internal logs
        # For now, we assume orchestrator logs to stdout/logger, which we might need to intercept
        # OR we modify Orchestrator to accept an event_callback?
        
        # Temporary: Wrap execution and log result
        result = await orchestrator.execute_request(req.request)
        
        await bus.publish(Event(type=EventType.DONE, content=result, agent="Orchestrator"))
        return result
    except Exception as e:
        logging.error(f"Error running request: {e}")
        await bus.publish(Event(type=EventType.ERROR, content=str(e), agent="Orchestrator"))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest_knowledge(req: IngestRequest, request: Request):
    # check_auth(request)
    
    try:
        documents = []
        collection_name = req.collection
        
        if req.type == "database":
             if not collection_name:
                 collection_name = "pos_database_schema"
             ingester = DatabaseSchemaIngester(req.path, req.models_dir or req.path)
             documents = ingester.ingest()
             
        elif req.type == "component_library":
             if not collection_name:
                 collection_name = "pos_component_library"
             ingester = ComponentLibraryIngester(req.path)
             documents = ingester.ingest()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown type: {req.type}")
            
        store = ChromaVectorStore(collection_name=collection_name)
        store.add_documents(documents)
        
        return {"status": "success", "documents_ingested": len(documents), "collection": collection_name}

    except Exception as e:
        logging.error(f"Error ingesting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_knowledge(req: QueryRequest, request: Request):
    # check_auth(request)
    
    try:
        # Use simpler retrieval for now, or expose domain context
        retriever = DomainAwareRetriever()
        results = retriever.retrieve(req.query, top_k=req.top_k)
        return {"results": results}
    except Exception as e:
        logging.error(f"Error querying: {e}")
        raise HTTPException(status_code=500, detail=str(e))
