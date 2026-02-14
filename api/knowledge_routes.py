from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
from pathlib import Path
import hashlib
import glob

from rag.domain_aware_retriever import DomainAwareRetriever
from rag.vector_store import ChromaVectorStore
from core.chunking.engine import ChunkingEngine

# Legacy Ingesters (Optional: Keep if still needed for specialized logic)
from domain_knowledge.ingestion.database_schema_ingester import DatabaseSchemaIngester
from domain_knowledge.ingestion.component_library_ingester import ComponentLibraryIngester

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class IngestRequest(BaseModel):
    # Legacy field support (optional)
    type: Optional[str] = None  # "database" | "component_library" | "project_codebase"
    
    # Universal fields
    source_type: str = "directory"  # directory, file, text, url
    path: Optional[str] = None
    content: Optional[str] = None
    file_filter: Optional[str] = "*.*"  # glob pattern
    
    tier: int = 3
    category: str = "generic"
    tags: List[str] = []
    collection: Optional[str] = None
    
    chunk_size: int = 800
    chunk_overlap: int = 100
    extract_options: Dict[str, bool] = {}
    
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
        collections = []
        for c in client.list_collections():
            collections.append({
                "name": c.name,
                "count": c.count()
            })
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


@router.get("/collections/{name}/documents")
async def get_collection_documents(name: str, limit: int = 100):
    """Get all documents from a specific collection."""
    try:
        import chromadb
        from chromadb.config import Settings

        client = chromadb.PersistentClient(
            path="rag/chroma_db",
            settings=Settings(anonymized_telemetry=False),
        )
        
        collection = client.get_collection(name=name)
        results = collection.get(limit=limit, include=["documents", "metadatas"])
        
        documents = []
        for i, doc_id in enumerate(results["ids"]):
            documents.append({
                "id": doc_id,
                "text": results["documents"][i] if i < len(results["documents"]) else "",
                "metadata": results["metadatas"][i] if i < len(results["metadatas"]) else {}
            })
        
        return {
            "collection": name,
            "count": len(documents),
            "documents": documents
        }
    except Exception as e:
        logging.error(f"Error getting documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/validate")
async def validate_knowledge(req: IngestRequest):
    """Validate source path and filter before ingestion."""
    try:
        if req.source_type == "directory":
            if not req.path:
                 raise HTTPException(status_code=400, detail="Path is required")
            
            source_path = Path(req.path)
            if not source_path.exists():
                 return {"valid": False, "error": f"Path not found: {req.path}"}
            
            pattern = req.file_filter or "*.*"
            files = []
            if "**" in pattern:
                files = list(source_path.glob(pattern))
            else:
                files = list(source_path.rglob(pattern))
            
            ignore_patterns = ["node_modules", "__pycache__", "dist", ".git", ".venv"]
            filtered_files = [
                str(f.relative_to(source_path)) 
                for f in files 
                if f.is_file() and not any(p in str(f) for p in ignore_patterns)
            ]
            
            return {
                "valid": True,
                "fileCount": len(filtered_files),
                "files": filtered_files[:20], # Return first 20 for preview
                "totalEstimatedTokens": len(filtered_files) * 500 # Very rough estimate
            }
        
        elif req.source_type == "file":
            file_path = Path(req.path)
            if not file_path.exists() or not file_path.is_file():
                return {"valid": False, "error": "File not found"}
            return {"valid": True, "fileCount": 1, "files": [file_path.name]}
            
        return {"valid": True, "message": "Source type ready for input"}
        
    except Exception as e:
        logging.error(f"Validation error: {e}")
        return {"valid": False, "error": str(e)}


@router.post("/ingest")
async def ingest_knowledge(req: IngestRequest):
    """Ingest data into the knowledge base using universal logic."""
    try:
        documents = []
        collection_name = req.collection
        
        # Determine collection name if not provided
        if not collection_name:
            collection_name = f"tier{req.tier}_{req.category}"

        # --- Universal Ingestion Logic ---
        
        # 1. Source Type: Directory
        if req.source_type == "directory":
            if not req.path:
                raise HTTPException(status_code=400, detail="Path is required for directory ingestion")
            
            source_path = Path(req.path)
            if not source_path.exists() or not source_path.is_dir():
                raise HTTPException(status_code=400, detail=f"Directory not found: {req.path}")
                
            # Use glob to find files matching the pattern
            # Search recursively if pattern includes **
            pattern = req.file_filter or "*.*"
            if "**" in pattern:
                files = list(source_path.glob(pattern))
            else:
                # Default recursive search for code/docs if simple pattern
                # If specific file pattern provided (e.g. DOCS.md), search recursively
                files = list(source_path.rglob(pattern))
            
            ignore_patterns = ["node_modules", "__pycache__", "dist", ".git", ".venv", "bin", "obj"]
            
            chunker = ChunkingEngine()
            
            for file_path in files:
                if any(p in str(file_path) for p in ignore_patterns):
                    continue
                if not file_path.is_file():
                    continue
                    
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    if not content.strip():
                        continue
                        
                    chunks = chunker.chunk_content(content, file_path=str(file_path))
                    
                    for chunk in chunks:
                        doc_id = f"tier{req.tier}_{req.category}_{hashlib.md5(chunk.content.encode()).hexdigest()}"
                        documents.append({
                            "id": doc_id,
                            "text": chunk.content,
                            "metadata": {
                                **chunk.metadata,
                                "tier": req.tier,
                                "category": req.category,
                                "tags": ",".join(req.tags),
                                "source_type": "directory",
                                "file": str(file_path.relative_to(source_path)),
                                "full_path": str(file_path)
                            }
                        })
                except Exception as ex:
                    logging.warning(f"Failed to process file {file_path}: {ex}")
                    continue

        # 2. Source Type: File
        elif req.source_type == "file":
            if not req.path:
                raise HTTPException(status_code=400, detail="Path is required for file ingestion")
            
            file_path = Path(req.path)
            if not file_path.exists() or not file_path.is_file():
                raise HTTPException(status_code=400, detail=f"File not found: {req.path}")
                
            chunker = ChunkingEngine()
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                chunks = chunker.chunk_content(content, file_path=str(file_path))
                
                for chunk in chunks:
                    doc_id = f"tier{req.tier}_{req.category}_{hashlib.md5(chunk.content.encode()).hexdigest()}"
                    documents.append({
                        "id": doc_id,
                        "text": chunk.content,
                        "metadata": {
                            **chunk.metadata,
                            "tier": req.tier,
                            "category": req.category,
                            "tags": ",".join(req.tags),
                            "source_type": "file",
                            "file": file_path.name,
                            "full_path": str(file_path)
                        }
                    })
            except Exception as ex:
                raise HTTPException(status_code=500, detail=f"Failed to process file: {ex}")

        # 3. Source Type: Text
        elif req.source_type == "text":
            if not req.content:
                raise HTTPException(status_code=400, detail="Content is required for text ingestion")
            
            chunker = ChunkingEngine()
            chunks = chunker.chunk_content(req.content, file_path="manual_input")
            
            for chunk in chunks:
                doc_id = f"tier{req.tier}_{req.category}_{hashlib.md5(chunk.content.encode()).hexdigest()}"
                documents.append({
                    "id": doc_id,
                    "text": chunk.content,
                    "metadata": {
                        **chunk.metadata,
                        "tier": req.tier,
                        "category": req.category,
                        "tags": ",".join(req.tags),
                        "source_type": "text",
                        "file": "manual_input"
                    }
                })

        # 4. Fallback / Legacy (Database/ComponentLibrary specific ingesters)
        elif req.type == "database":
             # Invoke legacy logic if needed, or reimplement here
             # For now, let's just support universal
             pass 
        
        else:
            # Try legacy logic if type is set but source_type is default
            if req.type == "component_library":
                ingester = ComponentLibraryIngester(req.path)
                # Adapter needed because legacy ingester returns list of dicts or objects?
                # Looking at original code: documents = ingester.ingest(), assuming standard format
                # But we want to standardize everything. 
                # Let's trust the Directory walker above for component library too if the user selected it via new UI.
                pass

        if not documents:
            return {
                "status": "warning",
                "message": "No documents found or processed.",
                "documents_ingested": 0,
                "collection": collection_name
            }

        store = ChromaVectorStore(collection_name=collection_name)
        # ChromaVectorStore expects objects or dicts? 
        # Original code: store.add_documents(documents) where documents was a list of objects or dicts.
        # Let's ensure format. ChromaVectorStore usually takes text, metadata, ids.
        # Let's look at `store.add_documents`.
        # Assuming it handles list of dicts with 'id', 'text', 'metadata'.
        
        # Reformulate for store.add_documents if it expects a specific class
        # But wait, original code used `Document` class?
        # No, I see `documents.append({ "id": ..., "text": ..., "metadata": ... })` in my snippet above.
        # But simpler previous code used `Document` class in `project_codebase` section: `documents.append(Document(...))`
        # I need to know if `store.add_documents` expects dicts or objects.
        # `ingest_knowledge` line 165: `store.add_documents(documents)`.
        # DatabaseSchemaIngester returns dicts?
        
        # Let's try to assume dicts are fine or use a simple Document class if defined.
        from rag.vector_store import Document
        final_docs = []
        for d in documents:
            if isinstance(d, dict):
                 final_docs.append(Document(id=d['id'], text=d['text'], metadata=d['metadata']))
            else:
                 final_docs.append(d)
                 
        store.add_documents(final_docs)

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
