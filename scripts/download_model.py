
import os
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_model():
    """Download sentence-transformer model to local directory."""
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        logger.error("huggingface_hub not installed. Run: pip install huggingface_hub")
        return

    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    project_root = Path(__file__).parent.parent
    local_dir = project_root / "rag" / "models" / "all-MiniLM-L6-v2"
    
    logger.info(f"Downloading {model_name} to {local_dir}...")
    
    try:
        snapshot_download(
            repo_id=model_name,
            local_dir=str(local_dir),
            local_dir_use_symlinks=False,
            ignore_patterns=["*.msgpack", "*.h5", "*.ot"] # Ignore non-PyTorch weights if possible to save space
        )
        logger.info("Download complete.")
        logger.info(f"Model saved to: {local_dir}")
        print(f"\nSUCCESS: Model downloaded to {local_dir}")
        print(f"You can now point the embeddings provider to this path.")
        
    except Exception as e:
        logger.error(f"Download failed: {e}")

if __name__ == "__main__":
    download_model()
