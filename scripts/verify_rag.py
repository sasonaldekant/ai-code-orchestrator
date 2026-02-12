
import sys
import logging
from pathlib import Path
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from rag.domain_aware_retriever import DomainAwareRetriever

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_retrieval():
    logger.info("Initializing DomainAwareRetriever...")
    try:
        retriever = DomainAwareRetriever(
            components_collection="code_docs", # Must match ingestion
            persist_dir="rag/store_data"
        )
    except Exception as e:
        logger.error(f"Failed to initialize retriever: {e}")
        return

    # Test Case 1: DynBox (Component)
    query = "How do I use the DynBox grid system?"
    logger.info(f"\n--- Test Query 1: '{query}' ---")
    context = retriever.retrieve_domain_context(query, top_k_components=1, top_k_docs=1)
    
    if context.components:
        comp = context.components[0]
        logger.info(f"[SUCCESS] Found Component: {comp['name']}")
        logger.info(f"Snippet: {comp['content'][:100]}...")
    else:
        logger.error("[FAILURE] Did not find DynBox component.")

    if context.documentation:
        doc = context.documentation[0]
        logger.info(f"[SUCCESS] Found Doc: {doc['name']}")
    else:
        logger.warning("[WARNING] Did not find relevant documentation.")

    # Test Case 2: Design Token (Primary Color)
    query = "primary color token"
    logger.info(f"\n--- Test Query 2: '{query}' ---")
    context = retriever.retrieve_domain_context(query, top_k_tokens=3)
    
    if context.design_tokens:
        token = context.design_tokens[0]
        logger.info(f"[SUCCESS] Found Token: {token['name']}")
        logger.info(f"Content: {token['content'][:100]}...")
    else:
        logger.error("[FAILURE] Did not find design tokens.")

    # Test Case 3: Global Stats
    logger.info("\n--- Collection Stats ---")
    logger.info(f"Total UI Components: {context.total_ui_count}")
    
    if context.total_ui_count > 0:
        logger.info("VERIFICATION PASSED: RAG is populated.")
    else:
        logger.error("VERIFICATION FAILED: Collection is empty.")

if __name__ == "__main__":
    verify_retrieval()
