import sys
import logging
import asyncio
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
    
    # Test Prompt to Project
    prompt = "Potrebna mi je forma za registraciju pacijenata koja sadrzi ime, prezime, JMBG, datum rodjenja, pol (kao select), email i polje za anamnezu (textarea)."
    project_name = "pacijent-registracija"
    
    logger.info(f"--- Testing Prompt to Project: {project_name} ---")
    path = await orchestrator.generate_from_prompt(prompt, project_name)
    logger.info(f"DONE! Project created at: {path}")

if __name__ == "__main__":
    asyncio.run(run_test())
