
import asyncio
import argparse
import sys
import logging
import json
from pathlib import Path
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Lazy Loading to provide better error messages and startup speed
def get_orchestrator():
    try:
        from core.lifecycle_orchestrator import LifecycleOrchestrator
        return LifecycleOrchestrator
    except ImportError as e:
        logger.error(f"Failed to import core dependencies: {e}")
        return None

def get_ingesters():
    try:
        from domain_knowledge.ingestion.database_schema_ingester import DatabaseSchemaIngester
        from domain_knowledge.ingestion.component_library_ingester import ComponentLibraryIngester
        from rag.vector_store import ChromaVectorStore
        return DatabaseSchemaIngester, ComponentLibraryIngester, ChromaVectorStore
    except ImportError as e:
        logger.error(f"Failed to import ingestion dependencies: {e}")
        return None, None, None

def get_retriever():
    try:
        from rag.domain_aware_retriever import DomainAwareRetriever
        return DomainAwareRetriever
    except ImportError as e:
        logger.error(f"Failed to import retriever dependencies: {e}")
        return None

def get_cost_manager():
    try:
        from core.cost_manager import CostManager
        return CostManager
    except ImportError as e:
        logger.error(f"Failed to import cost manager: {e}")
        return None

async def run_request(request: str, enable_rag: bool = True, deep_search: bool = False, auto_fix: bool = False, retrieval_strategy: str = "local"):
    """Execute a feature request workflow."""
    LifecycleOrchestrator = get_orchestrator()
    if not LifecycleOrchestrator:
        return

    logger.info(f"Running request: {request}")
    
    orchestrator = LifecycleOrchestrator()
    result = await orchestrator.execute_request(
        user_request=request,
        deep_search=deep_search,
        retrieval_strategy=retrieval_strategy,
        auto_fix=auto_fix
    )
    
    print("\n=== Execution Result ===")
    print(f"Status: {result.get('status', 'unknown')}")
    if "error" in result:
        print(f"Error: {result['error']}")
    
    if "plan" in result:
        print("\n--- Plan ---")
        print(json.dumps(result["plan"], indent=2))
        
    if "results" in result:
        print("\n--- Milestone Results ---")
        for m_id, m_res in result["results"].items():
            print(f"\nMilestone {m_id}:")
            if "error" in m_res:
                print(f"  Error: {m_res['error']}")
            else:
                for t_id, t_res in m_res.items():
                    print(f"  Task {t_id}: {t_res.get('status', 'completed')}")
    
    # Save full output
    output_path = Path("outputs") / f"execution_result_{hash(request)}.json"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"\nFull result saved to {output_path}")


def ingest_knowledge(source_type: str, path: str, collection_name: Optional[str] = None, models_dir: Optional[str] = None):
    """Ingest domain knowledge into vector store."""
    DatabaseSchemaIngester, ComponentLibraryIngester, ChromaVectorStore = get_ingesters()
    if not DatabaseSchemaIngester:
        return

    if not collection_name:
        if source_type == "database":
            collection_name = "pos_database_schema"
        elif source_type == "component_library":
            collection_name = "pos_component_library"
        else:
            collection_name = "domain_knowledge"
            
    logger.info(f"Ingesting {source_type} from {path} into {collection_name}")
    
    documents = []
    if source_type == "database":
        if not models_dir:
            # Default to same directory as DbContext if not provided
            models_dir = str(Path(path).parent)
            logger.info(f"Models directory not specified, defaulting to {models_dir}")
            
        ingester = DatabaseSchemaIngester(path, models_dir)
        documents = ingester.ingest()
    elif source_type == "component_library":
        ingester = ComponentLibraryIngester(path)
        documents = ingester.ingest()
    else:
        logger.error(f"Unknown source type: {source_type}")
        return

    logger.info(f"Generated {len(documents)} documents. Storing in vector database...")
    
    store = ChromaVectorStore(collection_name=collection_name)
    store.add_documents(documents)
    
    logger.info("Ingestion complete.")


def query_knowledge(query_text: str, top_k: int = 5):
    """Query the domain knowledge base."""
    DomainAwareRetriever = get_retriever()
    if not DomainAwareRetriever:
        return

    logger.info(f"Querying: {query_text}")
    
    retriever = DomainAwareRetriever()
    results = retriever.retrieve(query_text, top_k=top_k)
    
    print(f"\nFound {len(results)} matches:")
    for i, res in enumerate(results):
        print(f"\n--- Match {i+1} (Score: {res.get('score', 'N/A')}) ---")
        content = res.get('content', '')
        meta = res.get('metadata', {})
        print(f"Type: {meta.get('type', 'unknown')}")
        print(f"Name: {meta.get('name', 'unknown')}")
        print(f"Preview: {content[:200]}...")


def generate_cost_report(days: int = 7):
    """Generate cost usage report."""
    CostManager = get_cost_manager()
    if not CostManager:
        return

    manager = CostManager(enable_history=True)
    # Just print current session report for now as history loading is simplistic
    report = manager.generate_report()
    
    print("\n=== Cost Report (Session) ===")
    print(f"Total Cost: ${report.total_cost:.4f}")
    print(f"Total Tokens: {report.total_tokens}")
    print("\nBy Model:")
    for model, stats in report.by_model.items():
        print(f"  {model}: ${stats['cost']:.4f} ({stats['tokens']} tokens)")
    
    print("\nBy Provider:")
    for provider, stats in report.by_provider.items():
        print(f"  {provider}: ${stats['cost']:.4f}")


def main():
    parser = argparse.ArgumentParser(description="AI Code Orchestrator CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Run Command
    run_parser = subparsers.add_parser("run", help="Run a feature request")
    run_parser.add_argument("request", help="The feature request description")
    run_parser.add_argument("--no-rag", action="store_true", help="Disable RAG retrieval")
    run_parser.add_argument("--auto-fix", action="store_true", help="Enable autonomous self-healing")
    run_parser.add_argument("--deep-search", action="store_true", help="Enable agentic deep search")
    run_parser.add_argument("--strategy", choices=["local", "hybrid", "external"], default="local", help="Retrieval strategy")
    
    # Ingest Command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest domain knowledge")
    ingest_parser.add_argument("type", choices=["database", "component_library"], help="Type of source")
    ingest_parser.add_argument("path", nargs="?", default=".", help="Path to source code/schema (default: current dir)")
    ingest_parser.add_argument("--collection", help="Vector DB collection name (defaults based on type)")
    ingest_parser.add_argument("--models-dir", help="Directory containing entity models (for database ingestion)")
    
    # Query Command
    query_parser = subparsers.add_parser("query", help="Query domain knowledge")
    query_parser.add_argument("text", help="Query text")
    query_parser.add_argument("--k", type=int, default=5, help="Number of results")
    
    # Cost Report Command
    subparsers.add_parser("cost", help="Show cost report")
    
    args = parser.parse_args()
    
    if args.command == "run":
        asyncio.run(run_request(
            request=args.request, 
            enable_rag=not args.no_rag,
            deep_search=args.deep_search,
            auto_fix=args.auto_fix,
            retrieval_strategy=args.strategy
        ))
    elif args.command == "ingest":
        ingest_knowledge(args.type, args.path, args.collection, args.models_dir)
    elif args.command == "query":
        query_knowledge(args.text, args.k)
    elif args.command == "cost":
        generate_cost_report()
    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Failed to run command: {e}")
        sys.exit(1)
