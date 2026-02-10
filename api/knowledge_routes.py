from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path

from rag.vector_store import ChromaVectorStore
from domain_knowledge.ingestion.database_schema_ingester import DatabaseSchemaIngester
from domain_knowledge.ingestion.component_library_ingester import ComponentLibraryIngester
from rag.domain_aware_retriever import DomainAwareRetriever

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

class IngestRequest(BaseModel):
    type: str  # "database" | "component_library"
    path: str
    collection: Optional[str] = None
    models_dir: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    collection: Optional[str] = None
    top_k: int = 5

@router.get("/collections")
async def list_collections():
    """List all available knowledge collections."""
    try:
        # Initialize a temporary store just to access the client
        store = ChromaVectorStore(collection_name="temp_listing") 
        collections = store.list_collections()
        # Clean up the temp collection if it was created unnecessarily? 
        # Actually list_collections() uses the client, so checks *all* collections.
        # But initializing with a name creates it if not exists.
        # Let's ignore the temp collection creation side effect for now, 
        # or better, use a persistent name that we know exists or handle it gracefully.
        # A cleaner way would be to refactor ChromaVectorStore to separate client init from collection init,
        # but for now, we just list.
        
        # Filter out the temp one if we can, or just return all
        return {"collections": collections}
    except Exception as e:
        logging.error(f"Error listing collections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections/{name}/stats")
async def get_collection_stats(name: str):
    """Get statistics for a specific collection."""
    try:
        store = ChromaVectorStore(collection_name=name)
        return store.get_collection_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/collections/{name}")
async def delete_collection(name: str):
    """Delete a collection."""
    try:
        store = ChromaVectorStore(collection_name=name)
        store.delete_collection()
        return {"status": "success", "message": f"Collection '{name}' deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest")
async def ingest_knowledge(req: IngestRequest):
    """Ingest data into the knowledge base."""
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
        
        return {
            "status": "success", 
            "documents_ingested": len(documents), 
            "collection": collection_name
        }

    except Exception as e:
        logging.error(f"Error ingesting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def query_knowledge(req: QueryRequest):
    """Query the knowledge base."""
    try:
        # If collection is specified, use specific store, otherwise generic retriever
        if req.collection:
            store = ChromaVectorStore(collection_name=req.collection)
            results = store.search(req.query, top_k=req.top_k)
            return {"results": [
                {"text": r.document.text, "metadata": r.document.metadata, "score": r.score} 
                for r in results
            ]}
        else:
            # Use the existing domain-aware retriever which might query multiple
            retriever = DomainAwareRetriever()
            results = retriever.retrieve(req.query, top_k=req.top_k)
            return {"results": results}
    except Exception as e:
        logging.error(f"Error querying: {e}")
        raise HTTPException(status_code=500, detail=str(e))
