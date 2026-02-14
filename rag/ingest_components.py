
import os
import argparse
import logging
from pathlib import Path
from domain_knowledge.ingestion.component_library_ingester import ComponentLibraryIngester
from rag.embeddings_store import EmbeddingStore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Ingest Component Library")
    parser.add_argument("--components", required=True, help="Path to components directory")
    parser.add_argument("--store", required=True, help="Path to output store JSON")
    
    args = parser.parse_args()
    
    components_dir = Path(args.components)
    store_path = Path(args.store)
    
    if not components_dir.exists():
        logger.error(f"Components directory not found: {components_dir}")
        return
        
    logger.info(f"Ingesting components from {components_dir}...")
    
    ingester = ComponentLibraryIngester(str(components_dir))
    documents = ingester.ingest()
    
    if not documents:
        logger.warning("No documents generated.")
        return
        
    logger.info(f"Generated {len(documents)} documents.")
    
    # Save to store
    store = EmbeddingStore(store_path)
    
    for doc in documents:
        # Use component name as ID and the generated text description as content
        # store.add expects (id, text)
        component_name = doc.metadata.get('component', doc.id)
        store.add(id=component_name, text=doc.text)
        
    store.save()
    logger.info(f"Saved {len(documents)} components to {store_path}")

if __name__ == "__main__":
    main()
