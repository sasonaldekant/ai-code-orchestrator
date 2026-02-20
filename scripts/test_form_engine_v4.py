import sys
import logging
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.form_engine.orchestrator import FormEngineOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_test():
    orchestrator = FormEngineOrchestrator()
    
    # Test Data Sample to Project
    data_sample = {
        "userId": "usr_123",
        "username": "mgasic",
        "email": "test@example.com",
        "age": 28,
        "isPremium": True,
        "joinedDate": "2024-02-15",
        "preferences": ["dark_mode", "email_notifications"],
        "bio": "Software engineer and AI enthusiast."
    }
    
    project_name = "data-inferred-user"
    
    logger.info(f"--- Testing Data to Project: {project_name} ---")
    path = await orchestrator.generate_from_data(data_sample, project_name)
    logger.info(f"DONE! Project created at: {path}")

if __name__ == "__main__":
    asyncio.run(run_test())
