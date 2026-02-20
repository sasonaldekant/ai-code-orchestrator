import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.form_engine.orchestrator import FormEngineOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_generation():
    orchestrator = FormEngineOrchestrator()
    
    # Test 1: Simple Login
    login_template = Path("examples/form_templates/login_simple.json")
    if login_template.exists():
        logger.info("Testing Login Simple generation...")
        project_path = orchestrator.generate_from_file(str(login_template), "login-project")
        logger.info(f"Login project generated: {project_path}")
    
    # Test 2: Contact Minimal
    contact_template = Path("examples/form_templates/contact_minimal.json")
    if contact_template.exists():
        logger.info("Testing Contact Minimal generation...")
        project_path = orchestrator.generate_from_file(str(contact_template), "contact-project")
        logger.info(f"Contact project generated: {project_path}")

if __name__ == "__main__":
    test_generation()
