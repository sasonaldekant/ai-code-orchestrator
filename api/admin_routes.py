
"""
Admin API Routes for Orchestrator Configuration and Management.

Provides endpoints for:
- Configuration read/write (YAML configs)
- Knowledge base management (collections)
- RAG ingestion with validation
- Local file system browsing
- Knowledge Graph visualization and building
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
from dataclasses import asdict

from rag.vector_store import ChromaVectorStore, Document
from domain_knowledge.ingestion.database_schema_ingester import DatabaseSchemaIngester
from domain_knowledge.ingestion.component_library_ingester import ComponentLibraryIngester
from core.chunking.engine import ChunkingEngine
from core.graph.schema import KnowledgeGraph
from core.graph.ingester import GraphIngester
from domain_knowledge.ingestion.database_content_ingester import DatabaseContentIngester
from core.external_integration import ExternalIntegration
from api.shared import orchestrator_instance

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

# Base paths
CONFIG_DIR = Path("config")
PROJECT_ROOT = Path(".")

# Global Knowledge Graph Instance (In-Memory MVP)
knowledge_graph = KnowledgeGraph()

from core.cascade_metrics import CascadeMetrics

@router.get("/cascade-metrics", summary="Get model cascading statistics")
async def get_cascade_metrics():
    """
    Returns usage stats for the 5-tier model cascade system.
    """
    try:
        return CascadeMetrics().get_stats()
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        return {"tier_usage": {}, "error": str(e)}

@router.get("/models", summary="Get supported LLM models")
async def get_supported_models():
    """
    Returns supported models with pricing from CostManager.
    """
    from core.cost_manager import CostManager
    # Return full pricing info for UI display
    return {
        "models": CostManager.get_supported_models(),
        "pricing": {k: asdict(v) for k, v in CostManager.PRICING.items()}
    }


# ============== Pydantic Models ==============

class ConfigUpdateRequest(BaseModel):
    """Request to update a config file."""
    content: Dict[str, Any]


class IngestionValidateRequest(BaseModel):
    """Request to validate ingestion before executing."""
    type: str  # database, component_library, project_codebase, etc.
    path: str
    tier: int = 3  # Default to Tier 3
    category: str = "generic"
    models_dir: Optional[str] = None
    collection: Optional[str] = None
    chunk_size: int = 800
    chunk_overlap: int = 120


class IngestionExecuteRequest(IngestionValidateRequest):
    """Request to execute ingestion."""
    pass


class ContentIngestRequest(BaseModel):
    """Request to ingest database content (rows)."""
    mode: str = "json"  # 'json' or 'sql'
    
    # Common
    table_name: str
    collection_name: str = "database_content"
    
    # JSON specific
    file_path: Optional[str] = None
    
    # SQL specific
    connection_string: Optional[str] = None
    query: Optional[str] = "SELECT * FROM {table_name}"


class PromptGenRequest(BaseModel):
    query: str
    context_files: List[str]  # List of file paths
    target_model: str = "generic"

class ExternalIngestRequest(BaseModel):
    question: str
    answer: str
    source: str = "external_ai"


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
    
    elif req.type == "project_codebase" or req.type == "instruction_docs" or req.type == "specialization_rules":
        # Ingest existing project source code or documentation for context
        if source_path.is_dir():
            # Count source files by type
            if req.type == "instruction_docs":
                code_extensions = ["*.md", "*.txt", "*.pdf"]
            elif req.type == "specialization_rules":
                code_extensions = ["*.yaml", "*.yml", "*.json"]
            else:
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
                try:
                    sample_content = filtered_files[0].read_text(errors="ignore")[:2000]
                    recs = chunker.get_recommendations(sample_content, str(filtered_files[0]))
                    warnings.extend([r for r in recs])
                except Exception:
                    pass
            
            # Estimate based on files and average size
            info["estimated_documents"] = len(filtered_files) * 3  # ~3 chunks per file
            info["estimated_tokens"] = info["estimated_documents"] * 500
            info["estimated_cost_usd"] = round(info["estimated_tokens"] * 0.0001 / 1000, 4)
        else:
            errors.append(f"{req.type.replace('_', ' ').capitalize()} path must be a directory")
    else:
        errors.append(f"Unknown type: {req.type}. Use 'database', 'component_library', 'project_codebase', 'instruction_docs', or 'specialization_rules'")
    
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
            "tier": req.tier,
            "category": req.category,
            "collection": req.collection or f"tier{req.tier}_{req.category}"
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
        
        elif req.type in ["project_codebase", "instruction_docs", "specialization_rules"]:
            if not collection_name:
                collection_name = req.type
            
            # Simple generic ingestion - read source files and chunk them
            source_path = Path(req.path)
            
            if req.type == "instruction_docs":
                code_extensions = ["*.md", "*.txt", "*.pdf"]
            elif req.type == "specialization_rules":
                code_extensions = ["*.yaml", "*.yml", "*.json"]
            else:
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
                            id=f"tier{req.tier}_{req.category}_{content_hash}_{len(documents)}",
                            text=chunk.content,
                            metadata={
                                **chunk.metadata,
                                "tier": req.tier,
                                "category": req.category,
                                "full_path": str(file_path.resolve()),
                                "file": str(rel_path),
                                "type": file_path.suffix,
                                "source": req.type,
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


@router.post("/ingest/content")
async def ingest_content(req: ContentIngestRequest):
    """
    Ingest actual data rows from JSON or SQL.
    """
    try:
        ingester = DatabaseContentIngester()
        documents = []
        
        if req.mode == "json":
            if not req.file_path:
                raise HTTPException(status_code=400, detail="file_path required for json mode")
            documents = ingester.ingest_from_json(req.file_path, req.table_name)
            
        elif req.mode == "sql":
            if not req.connection_string:
                raise HTTPException(status_code=400, detail="connection_string required for sql mode")
            
            # Safe basic query formatting
            final_query = req.query
            if "{table_name}" in final_query:
                final_query = final_query.format(table_name=req.table_name)
                
            documents = ingester.ingest_from_sql(req.connection_string, final_query, req.table_name)
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown mode: {req.mode}")
            
        if documents:
            store = ChromaVectorStore(collection_name=req.collection_name)
            store.add_documents(documents)
            
        return {
            "status": "success",
            "count": len(documents),
            "collection": req.collection_name,
            "mode": req.mode
        }
        
    except Exception as e:
        logger.error(f"Content ingestion failed: {e}")
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

# ============== Knowledge Graph Endpoints (Phase 12) ==============

@router.post("/graph/build")
async def build_knowledge_graph(path: str = ".", background_tasks: BackgroundTasks = None):
    """
    Trigger a full rebuild of the Knowledge Graph.
    """
    try:
        # In a real app, use background tasks for large codebases
        # For MVP, we do it synchronously or via simple background task
        
        target_path = Path(path).resolve()
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")

        # Reset graph
        global knowledge_graph
        knowledge_graph = KnowledgeGraph()
        ingester = GraphIngester(knowledge_graph)

        logger.info(f"Building Knowledge Graph from {target_path}...")
        
        # Simple recursive walk
        count = 0
        for file_path in target_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".py", ".cs", ".ts", ".js"]:
                if "node_modules" in str(file_path) or "__pycache__" in str(file_path):
                    continue
                    
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    ingester.process_file(str(file_path), content)
                    count += 1
                except Exception as e:
                    logger.warning(f"Failed to ingest {file_path}: {e}")
        
        return {
            "status": "success",
            "message": f"Graph built from {count} files.",
            "stats": {
                "nodes": len(knowledge_graph.nodes),
                "edges": len(knowledge_graph.edges)
            }
        }
    except Exception as e:
        logger.error(f"Graph build failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/graph")
async def get_knowledge_graph_data():
    """
    Get the current Knowledge Graph in JSON format.
    """
    return knowledge_graph.to_json()


# ============== Swarm Monitoring Endpoints (Phase 19) ==============

@router.get("/swarm/dag")
async def get_swarm_dag():
    """
    Get the current Swarm Task DAG from the blackboard.
    """
    swarm_manager = getattr(orchestrator_instance.orchestrator, "swarm_manager", None)
    if not swarm_manager:
         raise HTTPException(status_code=404, detail="Swarm Manager not initialized in orchestrator.")
         
    return await swarm_manager.blackboard.get_dag()

@router.get("/swarm/observations")
async def get_swarm_observations():
    """
    Get all observations from the swarm blackboard.
    """
    swarm_manager = getattr(orchestrator_instance.orchestrator, "swarm_manager", None)
    if not swarm_manager:
         raise HTTPException(status_code=404, detail="Swarm Manager not initialized in orchestrator.")
         
    return await swarm_manager.blackboard.get_observations()


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

@router.post("/tools/generate-prompt")
async def generate_external_prompt(req: PromptGenRequest):
    """
    Generate a prompt for external Pro models (ChatGPT o1, Perplexity).
    """
    try:
        # 1. Gather context
        context_data = []
        for file_path_str in req.context_files:
            path = Path(file_path_str)
            if path.exists() and path.is_file():
                content = path.read_text(encoding="utf-8", errors="ignore")
                context_data.append({"path": str(path), "content": content})
            else:
                logger.warning(f"File not found for context: {path}")

        # 2. Generate Prompt
        integration = ExternalIntegration()
        prompt = integration.generate_prompt(req.query, context_data, req.target_model)
        
        return {"prompt": prompt}
    except Exception as e:
        logger.error(f"Prompt generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/advise-complexity")
async def advise_complexity(req: PromptGenRequest):
    """
    Check if a task is too complex for local models.
    """
    try:
        # 1. Gather context
        context_data = []
        for file_path_str in req.context_files:
            path = Path(file_path_str)
            if path.exists() and path.is_file():
                content = path.read_text(encoding="utf-8", errors="ignore")
                context_data.append({"path": str(path), "content": content})
            
        # 2. Analyze
        integration = ExternalIntegration()
        advice = integration.detect_task_complexity(req.query, context_data)
        
        return advice
    except Exception as e:
        logger.error(f"Advisor error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest/external-response")
async def ingest_external_response(req: ExternalIngestRequest):
    """
    Ingest an answer from an external AI tool.
    """
    try:
        store = ChromaVectorStore(collection_name="external_knowledge")
        integration = ExternalIntegration(vector_store=store)
        
        doc_id = integration.ingest_response(req.question, req.answer, req.source)
        
        return {"status": "success", "doc_id": doc_id}
    except Exception as e:
        logger.error(f"External ingestion error: {e}")
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
