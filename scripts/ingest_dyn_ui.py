
import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path to specificy rag module
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Attempt to import from local rag module
try:
    from rag.vector_store import ChromaVectorStore, Document
except ImportError:
    # Fallback if running from a different context
    print("Could not import rag.vector_store. Ensure you are running from the project root.")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
DYN_UI_REL_PATH = "../dyn-ui-main-v01"
# Adjust this path based on where the script is run. Assuming run from orchestrator root.
# If project root is ai-code-orchestrator, then DYN_UI is likely ../dyn-ui-main-v01
DYN_UI_ROOT = (PROJECT_ROOT.parent / "dyn-ui-main-v01").resolve()

def ingest_components(store: ChromaVectorStore):
    """Ingest DynUI React components."""
    components_dir = DYN_UI_ROOT / "packages/dyn-ui-react/src/components"
    
    if not components_dir.exists():
        logger.error(f"Components directory not found: {components_dir}")
        return

    documents = []
    
    # Iterate over component directories
    for component_path in components_dir.iterdir():
        if not component_path.is_dir():
            continue
            
        component_name = component_path.name
        if not component_name.startswith("Dyn"):
            continue # Skip non-Dyn components if any
            
        logger.info(f"Processing component: {component_name}")
        
        # Files to ingest
        files_to_read = {
            "tsx": component_path / f"{component_name}.tsx",
            "types": component_path / f"{component_name}.types.ts",
            "stories": component_path / f"{component_name}.stories.tsx",
            "css": component_path / f"{component_name}.module.css"
        }
        
        content_parts = []
        
        # 1. Types (Interfaces) - High Priority
        if files_to_read["types"].exists():
            content_parts.append(f"--- Types ({component_name}.types.ts) ---\n{files_to_read['types'].read_text(encoding='utf-8')}")
            
        # 2. Main Component Logic
        if files_to_read["tsx"].exists():
            content_parts.append(f"--- Component ({component_name}.tsx) ---\n{files_to_read['tsx'].read_text(encoding='utf-8')}")
            
        # 3. Stories (Usage Examples)
        if files_to_read["stories"].exists():
             content_parts.append(f"--- Usage Examples ({component_name}.stories.tsx) ---\n{files_to_read['stories'].read_text(encoding='utf-8')}")

        # 4. CSS (Styles) - For token usage awareness
        if files_to_read["css"].exists():
             content_parts.append(f"--- Styles ({component_name}.module.css) ---\n{files_to_read['css'].read_text(encoding='utf-8')}")

        if content_parts:
            full_text = f"# Component: {component_name}\n\n" + "\n\n".join(content_parts)
            
            doc = Document(
                id=f"dyn_ui_component_{component_name}",
                text=full_text,
                metadata={
                    "type": "ui_component",
                    "name": component_name,
                    "source": "dyn-ui-main-v01",
                    "path": str(component_path)
                }
            )
            documents.append(doc)
    
    if documents:
        store.add_documents(documents)
        logger.info(f"Successfully ingested {len(documents)} components.")
    else:
        logger.warning("No components found to ingest.")

def ingest_tokens(store: ChromaVectorStore):
    """Ingest Design Tokens (Foundations & Themes)."""
    styles_dir = DYN_UI_ROOT / "packages/design-tokens/styles"
    
    if not styles_dir.exists():
        logger.error(f"Styles directory not found: {styles_dir}")
        return

    documents = []
    
    # 1. Foundations
    foundations_dir = styles_dir / "foundations"
    if foundations_dir.exists():
        for token_file in foundations_dir.glob("*.css"):
            content = token_file.read_text(encoding='utf-8')
            doc = Document(
                id=f"dyn_ui_token_foundation_{token_file.stem}",
                text=f"# Design Token: {token_file.stem}\n\n{content}",
                metadata={
                    "type": "design_token",
                    "category": "foundation",
                    "name": token_file.stem,
                    "source": "dyn-ui-main-v01"
                }
            )
            documents.append(doc)
            
    # 2. Themes
    themes_dir = styles_dir / "themes"
    if themes_dir.exists():
        for theme_file in themes_dir.glob("*.css"):
            content = theme_file.read_text(encoding='utf-8')
            doc = Document(
                id=f"dyn_ui_token_theme_{theme_file.stem}",
                text=f"# Design Token Theme: {theme_file.stem}\n\n{content}",
                metadata={
                    "type": "design_token",
                    "category": "theme",
                    "name": theme_file.stem,
                    "source": "dyn-ui-main-v01"
                }
            )
            documents.append(doc)
            
    if documents:
        store.add_documents(documents)
        logger.info(f"Successfully ingested {len(documents)} token files.")
    else:
        logger.warning("No token files found to ingest.")
        
def ingest_documentation(store: ChromaVectorStore):
    """Ingest core documentation files for architectural context."""
    docs_dir = DYN_UI_ROOT / "docs"
    
    if not docs_dir.exists():
        logger.warning(f"Docs directory not found: {docs_dir}")
        return
        
    documents = []
    
    # Critical docs to ingest
    target_docs = [
        "COMPLETE_KNOWLEDGE_BASE.md",
        "COMPONENT_COMPOSITION_GUIDE.md",
        "TECHNICAL_DOCUMENTATION.md",
        "DESIGN_TOKEN_SYSTEM.md"
    ]
    
    for doc_name in target_docs:
        doc_path = docs_dir / doc_name
        if doc_path.exists():
             doc = Document(
                id=f"dyn_ui_docs_{doc_path.stem}",
                text=doc_path.read_text(encoding='utf-8'),
                metadata={
                    "type": "documentation",
                    "name": doc_path.stem,
                    "source": "dyn-ui-main-v01",
                    "category": "architecture"
                }
            )
             documents.append(doc)
             logger.info(f"Processing doc: {doc_name}")
             
    if documents:
        store.add_documents(documents)
        logger.info(f"Successfully ingested {len(documents)} documentation files.")

def main():
    logger.info("Starting DynUI Ingestion...")
    logger.info(f"DynUI Root: {DYN_UI_ROOT}")
    
    if not DYN_UI_ROOT.exists():
        logger.error(f"DynUI Root does not exist! Please check path.")
        sys.exit(1)

    # Initialize Store
    # Use SimplePersistentVectorStore for Python 3.14 compatibility
    from rag.vector_store import SimplePersistentVectorStore
    from rag.embeddings_provider import create_embeddings_provider
    
    # Initialize embeddings (uses local model if available)
    embedding_provider = create_embeddings_provider(
        provider_type="huggingface",
        model="all-MiniLM-L6-v2"
    )
    
    store = SimplePersistentVectorStore(
        collection_name="code_docs",
        persist_directory="rag/store_data",
        embedding_function=embedding_provider.embed_texts
    ) 
    
    # Ingest
    ingest_documentation(store)
    ingest_tokens(store)
    ingest_components(store)
    
    logger.info("Ingestion Complete.")

if __name__ == "__main__":
    main()
