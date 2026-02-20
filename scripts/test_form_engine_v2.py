import sys
import logging
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.form_engine.orchestrator import FormEngineOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_test():
    orchestrator = FormEngineOrchestrator()
    
    # 1. Test Simple Login (Should be "standard" or "tabs" depending on heuristics)
    logger.info("--- Testing Simple Login ---")
    await orchestrator.generate_ui_project(
        "examples/form_templates/login_simple.json", 
        "v2-login-project"
    )
    
    # 2. Test Complex Onboarding (Should be "stepper")
    logger.info("--- Testing Complex Onboarding (Stepper) ---")
    await orchestrator.generate_ui_project(
        "examples/form_templates/onboarding_complex.json", 
        "v2-onboarding-stepper"
    )

if __name__ == "__main__":
    asyncio.run(run_test())
