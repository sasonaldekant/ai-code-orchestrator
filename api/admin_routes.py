"""
Admin API Routes for Orchestrator Configuration and Management.

Provides endpoints for:
- Configuration read/write (YAML configs)
- Knowledge base management (collections)
- RAG ingestion with validation
- Local file system browsing
"""

from core.audit_logger import AuditLogger
from fastapi import APIRouter, HTTPException, BackgroundTasks, Response, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import yaml
import os
import logging
import hashlib
from pathlib import Path

from rag.vector_store import ChromaVectorStore, Document
from domain_knowledge.ingestion.database_schema_ingester import DatabaseSchemaIngester
from domain_knowledge.ingestion.component_library_ingester import ComponentLibraryIngester
from core.chunking.engine import ChunkingEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

# Base paths
CONFIG_DIR = Path("config")
PROJECT_ROOT = Path(".")


# ============== Pydantic Models ==============

class ConfigUpdateRequest(BaseModel):
    """Request to update a config file."""
    content: Dict[str, Any]


class IngestionValidateRequest(BaseModel):
    """Request to validate ingestion before executing."""
    type: str  # database, component_library
    path: str
    models_dir: Optional[str] = None
    collection: Optional[str] = None
    chunk_size: int = 800
    chunk_overlap: int = 120


class IngestionExecuteRequest(IngestionValidateRequest):
    """Request to execute ingestion."""
    pass


class BrowseResponse(BaseModel):
    """Response for file system browsing."""
    path: str
    items: List[Dict[str, Any]]


# ============== Config Endpoints ==============

@router.get("/config/{config_name}")
async def get_config(config_name: str):
    """
    Read a YAML config file and return as JSON.
    
    Supported configs: model_mapping_v2, limits, domain_config
    """
    allowed_configs = ["model_mapping_v2", "limits", "domain_config", "agent_config"]
    
    if config_name not in allowed_configs:
        raise HTTPException(status_code=400, detail=f"Config '{config_name}' not allowed. Use: {allowed_configs}")
    
    config_path = CONFIG_DIR / f"{config_name}.yaml"
    
    if not config_path.exists():
        raise HTTPException(status_code=404, detail=f"Config file not found: {config_path}")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Handle the case where YAML is wrapped in markdown code blocks
            if content.startswith("```yaml"):
                content = content.replace("```yaml", "").replace("```", "").strip()
            data = yaml.safe_load(content)
        return {"config_name": config_name, "data": data}
    except Exception as e:
        logger.error(f"Error reading config {config_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config/{config_name}")
async def update_config(config_name: str, req: ConfigUpdateRequest):
    """
    Update a YAML config file from JSON input.
    
    Creates a backup before overwriting.
    """
    allowed_configs = ["model_mapping_v2", "limits", "domain_config", "agent_config"]
    
    if config_name not in allowed_configs:
        raise HTTPException(status_code=400, detail=f"Config '{config_name}' not allowed.")
    
    config_path = CONFIG_DIR / f"{config_name}.yaml"
    backup_path = CONFIG_DIR / f"{config_name}.yaml.bak"
    
    try:
        # Create backup
        if config_path.exists():
            import shutil
            shutil.copy(config_path, backup_path)
        
        # Write new config
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(req.content, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        return {"status": "success", "config_name": config_name, "backup": str(backup_path)}
    except Exception as e:
        logger.error(f"Error writing config {config_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Collections Endpoints ==============

@router.get("/collections")
async def list_collections():
    """
    List all ChromaDB collections with basic stats.
    """
    try:
        import chromadb
        client = chromadb.PersistentClient(path="rag/chroma_db")
        collections = client.list_collections()
        
        result = []
        for col in collections:
            result.append({
                "name": col.name,
                "count": col.count(),
                "metadata": col.metadata or {}
            })
        
        return {"collections": result}
    except Exception as e:
        logger.error(f"Error listing collections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections/{name}/documents")
async def get_collection_documents(name: str, limit: int = 20, offset: int = 0):
    """Browse documents within a collection."""
    try:
        store = ChromaVectorStore(collection_name=name)
        docs = store.get_documents(limit=limit, offset=offset)
        return {
            "documents": [
                {"id": d.id, "text": d.text[:200] + "...", "metadata": d.metadata}
                for d in docs
            ],
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Failed to fetch documents for collection {name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/collections/{name}/documents/{doc_id}")
async def delete_collection_document(name: str, doc_id: str):
    """Delete a specific document from a collection."""
    try:
        store = ChromaVectorStore(collection_name=name)
        store.delete_document(doc_id)
        return {"status": "success", "message": f"Document {doc_id} deleted."}
    except Exception as e:
        logger.error(f"Failed to delete document {doc_id} from collection {name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections/{name}/stats")
async def get_collection_stats(name: str):
    """
    Get detailed statistics for a specific collection.
    """
    try:
        store = ChromaVectorStore(collection_name=name)
        stats = store.get_collection_stats()
        return {"collection": name, "stats": stats}
    except Exception as e:
        logger.error(f"Error getting stats for {name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/collections/{name}")
async def delete_collection(name: str):
    """
    Delete a ChromaDB collection.
    """
    try:
        store = ChromaVectorStore(collection_name=name)
        store.delete_collection()
        return {"status": "deleted", "collection": name}
    except Exception as e:
        logger.error(f"Error deleting collection {name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Ingestion Endpoints ==============

@router.post("/ingest/validate")
async def validate_ingestion(req: IngestionValidateRequest):
    """
    Validate ingestion request without executing.
    
    Returns:
    - Path validation
    - Detected entities/components count
    - Estimated document count
    - Estimated token count
    """
    errors = []
    warnings = []
    info = {}
    
    # Validate path exists
    source_path = Path(req.path)
    if not source_path.exists():
        errors.append(f"Path does not exist: {req.path}")
    else:
        info["path_exists"] = True
        info["is_directory"] = source_path.is_dir()
    
    # Type-specific validation and dynamic recommendations
    chunker = ChunkingEngine()
    
    if req.type == "database":
        if not req.models_dir:
            warnings.append("models_dir not specified, using path as models directory")
        
        models_path = Path(req.models_dir or req.path)
        if not models_path.exists():
            errors.append(f"Models directory does not exist: {models_path}")
        else:
            # Count .cs files and get recommendations
            cs_files = list(models_path.glob("**/*.cs"))
            info["cs_files_found"] = len(cs_files)
            info["estimated_entities"] = len([f for f in cs_files if not f.name.endswith(".g.cs")])
            
            # Get recommendations for a representative sample
            if cs_files:
                sample_content = cs_files[0].read_text(errors="ignore")[:2000]
                recs = chunker.get_recommendations(sample_content, str(cs_files[0]))
                warnings.extend([r for r in recs if "Consider" in r or "Recommend" in r or "Generated" in r])

    elif req.type == "component_library":
        if source_path.is_dir():
            # Count TSX/JSX files
            tsx_files = list(source_path.glob("**/*.tsx")) + list(source_path.glob("**/*.jsx"))
            info["component_files_found"] = len(tsx_files)
            if tsx_files:
                sample_content = tsx_files[0].read_text(errors="ignore")[:2000]
                recs = chunker.get_recommendations(sample_content, str(tsx_files[0]))
                warnings.extend([r for r in recs if "Consider" in r or "Recommend" in r])
        else:
            errors.append("Component library path must be a directory")
    
    elif req.type == "project_codebase":
        # Ingest existing project source code for context
        if source_path.is_dir():
            # Count source files by type
            code_extensions = ["*.py", "*.ts", "*.tsx", "*.js", "*.jsx", "*.cs", "*.java", "*.go", "*.rs", "*.cpp", "*.c", "*.h"]
            all_files = []
            for ext in code_extensions:
                all_files.extend(list(source_path.glob(f"**/{ext}")))
            
            # Filter out common ignore patterns
            ignore_patterns = ["node_modules", "__pycache__", "dist", "build", ".git", "bin", "obj", "venv", ".venv"]
            filtered_files = [f for f in all_files if not any(p in str(f) for p in ignore_patterns)]
            
            info["source_files_found"] = len(filtered_files)
            info["file_types"] = {}
            for f in filtered_files:
                ext = f.suffix
                info["file_types"][ext] = info["file_types"].get(ext, 0) + 1
            
            # Get recommendations for the project
            if filtered_files:
                sample_content = filtered_files[0].read_text(errors="ignore")[:2000]
                recs = chunker.get_recommendations(sample_content, str(filtered_files[0]))
                warnings.extend([r for r in recs])
            
            # Estimate based on files and average size
            info["estimated_documents"] = len(filtered_files) * 3  # ~3 chunks per file
            info["estimated_tokens"] = info["estimated_documents"] * 500
            info["estimated_cost_usd"] = round(info["estimated_tokens"] * 0.0001 / 1000, 4)
        else:
            errors.append("Project codebase path must be a directory")
    else:
        errors.append(f"Unknown type: {req.type}. Use 'database', 'component_library', or 'project_codebase'")
    
    # Estimate documents and tokens (for db/component types)
    if not errors and req.type in ["database", "component_library"]:
        estimated_docs = info.get("estimated_entities", 0) or info.get("component_files_found", 0)
        # Rough estimate: ~2 docs per entity/component, ~400 tokens per doc
        info["estimated_documents"] = estimated_docs * 2
        info["estimated_tokens"] = estimated_docs * 2 * 400
        info["estimated_cost_usd"] = round(info["estimated_tokens"] * 0.0001 / 1000, 4)  # Embedding cost
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "request": {
            "type": req.type,
            "path": req.path,
            "collection": req.collection or f"default_{req.type}"
        }
    }


@router.post("/ingest/execute")
async def execute_ingestion(req: IngestionExecuteRequest):
    """
    Execute ingestion after validation.
    """
    # First validate
    validation = await validate_ingestion(req)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail={"errors": validation["errors"]})
    info = dict(validation.get("info", {}))
    
    try:
        documents = []
        collection_name = req.collection
        
        if req.type == "database":
            if not collection_name:
                collection_name = "database_schema"
            ingester = DatabaseSchemaIngester(req.path, req.models_dir or req.path)
            documents = ingester.ingest()
            
        elif req.type == "component_library":
            if not collection_name:
                collection_name = "component_library"
            ingester = ComponentLibraryIngester(req.path)
            documents = ingester.ingest()
        
        elif req.type == "project_codebase":
            if not collection_name:
                collection_name = "project_codebase"
            
            # Simple generic ingestion - read source files and chunk them
            source_path = Path(req.path)
            code_extensions = ["*.py", "*.ts", "*.tsx", "*.js", "*.jsx", "*.cs", "*.java", "*.go", "*.rs", "*.cpp", "*.c", "*.h"]
            ignore_patterns = ["node_modules", "__pycache__", "dist", "build", ".git", "bin", "obj", "venv", ".venv"]
            
            all_files = []
            for ext in code_extensions:
                all_files.extend(list(source_path.glob(f"**/{ext}")))
            
            filtered_files = [f for f in all_files if not any(p in str(f) for p in ignore_patterns)]
            
            # Create documents from each file
            chunker = ChunkingEngine()
            store = ChromaVectorStore(collection_name=collection_name)
            
            duplicates_skipped = 0
            for file_path in filtered_files:
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    rel_path = file_path.relative_to(source_path)
                    
                    # Use ChunkingEngine for strategic splitting
                    chunks = chunker.chunk_content(
                        content, 
                        file_path=str(file_path),
                        chunk_size=req.chunk_size,
                        overlap=req.chunk_overlap
                    )
                    
                    for chunk in chunks:
                        content_hash = hashlib.md5(chunk.content.encode()).hexdigest()
                        
                        # Check for duplicates (P3 Feature)
                        if store.check_content_exists(content_hash):
                            duplicates_skipped += 1
                            continue
                            
                        documents.append(Document(
                            id=f"code_{content_hash}_{len(documents)}",
                            text=chunk.content,
                            metadata={
                                **chunk.metadata,
                                "file": str(rel_path),
                                "type": file_path.suffix,
                                "source": "project_codebase",
                                "content_hash": content_hash
                            }
                        ))
                except Exception as e:
                    logger.warning(f"Could not read/process file {file_path}: {e}")
            
            info["duplicates_skipped"] = duplicates_skipped
        
        # Store in vector DB
        store = ChromaVectorStore(collection_name=collection_name)
        store.add_documents(documents)
        
        return {
            "status": "success",
            "documents_ingested": len(documents),
            "collection": collection_name,
            "validation": validation["info"]
        }
        
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== File Browser Endpoint ==============

@router.get("/browse")
async def browse_files(
    path: str = Query(default=".", description="Path to browse"),
    filter_ext: Optional[str] = Query(default=None, description="Filter by extension (e.g., .cs,.tsx)")
):
    """
    Browse local file system for path selection.
    
    Security: Restricts to project root and common safe directories.
    """
    try:
        browse_path = Path(path).resolve()
        
        # Security: Only allow browsing within project or common paths
        allowed_roots = [
            Path(".").resolve(),
            Path.home() / "Projects",
            Path("E:/PROGRAMING"),
            Path("C:/Users"),
        ]
        
        is_allowed = any(str(browse_path).startswith(str(root)) for root in allowed_roots)
        if not is_allowed:
            raise HTTPException(status_code=403, detail="Path not allowed for browsing")
        
        if not browse_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        if not browse_path.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")
        
        items = []
        extensions = filter_ext.split(",") if filter_ext else None
        
        for item in sorted(browse_path.iterdir()):
            # Skip hidden files and common ignore patterns
            if item.name.startswith(".") or item.name in ["node_modules", "__pycache__", "bin", "obj"]:
                continue
            
            item_info = {
                "name": item.name,
                "path": str(item),
                "is_dir": item.is_dir(),
            }
            
            if item.is_file():
                item_info["size"] = item.stat().st_size
                item_info["extension"] = item.suffix
                
                # Apply extension filter
                if extensions and item.suffix not in extensions:
                    continue
            
            items.append(item_info)
        
        return BrowseResponse(
            path=str(browse_path),
            items=items
        )
        
    except HTTPException:
        raise
# ============== Tool Endpoints (Phase 7) ==============

from agents.specialist_agents.doc_generator import DocGeneratorAgent
from agents.specialist_agents.code_reviewer_v2 import CodeReviewerV2
from core.simulation.mock_llm import MockLLMClient

class DocGenRequest(BaseModel):
    code: str
    type: str = "openapi" # or 'readme'
    project_name: Optional[str] = "MyProject"
    description: Optional[str] = "A sample project"
    features: Optional[List[str]] = []

class CodeReviewRequest(BaseModel):
    code: str
    context: Optional[str] = "General review"

@router.post("/tools/doc-gen")
async def generate_docs(req: DocGenRequest):
    """
    Generate documentation using DocGeneratorAgent (Simulation).
    """
    try:
        # Initialize simulation stack
        client = MockLLMClient()
        agent = DocGeneratorAgent(llm_client=client)
        
        if req.type == "openapi":
            artifact = await agent.generate_api_docs(req.code)
        else:
            artifact = await agent.generate_readme(
                project_name=req.project_name,
                description=req.description,
                features=req.features
            )
            
        return {
            "status": "success",
            "type": artifact.type,
            "format": artifact.format,
            "content": artifact.content
        }
    except Exception as e:
        logger.error(f"Doc gen error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/code-review")
async def review_code(req: CodeReviewRequest):
    """
    Review code using CodeReviewerV2 (Simulation).
    """
    try:
        # Initialize simulation stack
        client = MockLLMClient()
        reviewer = CodeReviewerV2(llm_client=client)
        
        report = await reviewer.review_code(req.code, context=req.context)
        
        return {
            "status": "success",
            "score": report.score,
            "passed": report.passed,
            "summary": report.summary,
            "issues": [
                {
                    "type": issue.type,
                    "severity": issue.severity,
                    "line": issue.line,
                    "message": issue.message,
                    "suggestion": issue.suggestion
                }
                for issue in report.issues
            ]
        }
    except Exception as e:
        logger.error(f"Code review error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit-report")
async def get_audit_report():
    try:
        logger_audit = AuditLogger()
        report = logger_audit.generate_report()
        return Response(content=report, media_type="text/markdown")
    except Exception as e:
        logger.error(f"Failed to generate audit report: {e}")
        raise HTTPException(status_code=500, detail=str(e))
