
from dotenv import load_dotenv

# Load environment variables BEFORE creating orchestrator
load_dotenv()

from core.lifecycle_orchestrator import LifecycleOrchestrator

# Global Orchestrator Instance shared across routes
orchestrator_instance = LifecycleOrchestrator()
