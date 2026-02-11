from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

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
        import chromadb
        from chromadb.config import Settings

        client = chromadb.PersistentClient(
            path="rag/chroma_db",
            settings=Settings(anonymized_telemetry=False),
        )
        collections = [c.name for c in client.list_collections()]
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
            "collection": collection_name,
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
        else:
            # Use the existing domain-aware retriever which might query multiple
            retriever = DomainAwareRetriever()
            raw_results = retriever.retrieve(req.query, top_k=req.top_k)
            results = [
                {
                    "text": item.get("text") or item.get("content") or "",
                    "metadata": item.get("metadata", {}),
                    "score": item.get("score", 0.0),
                }
                for item in raw_results
            ]
            return {"results": results}

        return {
            "results": [
                {
                    "text": r.document.text,
                    "metadata": r.document.metadata,
                    "score": r.score,
                }
                for r in results
            ]
        }
    except Exception as e:
        logging.error(f"Error querying: {e}")
        raise HTTPException(status_code=500, detail=str(e))
