import asyncio
import argparse
from pathlib import Path
import sys
import logging
from datetime import datetime
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from core.orchestrator_v2 import ExecutionStrategy
    from core.lifecycle_orchestrator import LifecycleOrchestrator
except ImportError:
    print("Error: Could not import LifecycleOrchestrator. Make sure you are running from the project root or scripts folder.")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    # Load .env from project root
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"Loaded environment from {env_path}")
    else:
        print(f"Warning: .env file not found at {env_path}")
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables might not be loaded.")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    parser = argparse.ArgumentParser(description="Run a task with the AI Code Orchestrator.")
    parser.add_argument("prompt", help="The task description or requirement.")
    parser.add_argument("--context", "-c", action="append", help="Path to a file to include as context.", default=None)
    parser.add_argument("--strategy", "-s", default="adaptive", help="Execution strategy (adaptive, sequential, parallel, fast, planning).")
    parser.add_argument("--model", "-m", help="Primary model override.", default=None)
    parser.add_argument("--mode", default="standard", help="Execution mode (standard, question).")
    parser.add_argument("--auto-fix", action="store_true", help="Enable automatic self-healing.")
    parser.add_argument("--skip-validation", action="store_true", help="Skip domain validation.")
    parser.add_argument("--local-limit", type=float, default=None, help="Local session cost limit (USD).")
    parser.add_argument("--deep-search", action="store_true", help="Enable deep search (Agentic Retrieval).")
    
    args = parser.parse_args()
    
    # 0. Domain Validation (New)
    if not args.skip_validation:
        try:
            from core.domain_validator import DomainValidator
            validator = DomainValidator()
            print("Validating project scope...")
            validation = await validator.validate(args.prompt)
            
            if not validation.get("in_scope", True):
                print(f"\n[Scope Warning]: {validation.get('reason')}")
                if validation.get("suggested_action") == "reject" and validation.get("confidence", 1.0) > 0.8:
                    print("\n[CRITICAL]: This prompt is considered out of scope or nonsense. Stopping execution.")
                    print("Please provide a clearer task related to React, C#, or .NET.")
                    sys.exit(1)
                elif validation.get("confidence", 1.0) > 0.8:
                    print("This prompt seems to be outside the project's technical scope (React/C#/.NET).")
                    print("Proceeding anyway, but results might be suboptimal.\n")
        except Exception as e:
            logger.warning(f"Could not run domain validation: {e}")

    # 1. Build Context
    context_str = ""
    if args.context:
        print(f"Loading {len(args.context)} context files...")
        for file_path in args.context:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"Context file not found: {path}")
                continue
            
            try:
                content = path.read_text(encoding="utf-8")
                context_str += f"\n\n[Context from {path.name}]:\n{content}\n"
                print(f"  - Loaded {path.name} ({len(content)} chars)")
            except Exception as e:
                logger.error(f"Failed to read {path}: {e}")

    final_prompt = f"{args.prompt}\n{context_str}"
    
    # 2. Initialize Orchestrator
    try:
        orchestrator = LifecycleOrchestrator()
        
        if args.model:
            print(f"Using model override: {args.model}")
            # The LifecycleOrchestrator/OrchestratorV2 will need logic to use this override globally.
            # For now, it stays as a placeholder log.
    except Exception as e:
        logger.error(f"Failed to initialize LifecycleOrchestrator: {e}")
        return

    # 3. Running Pipeline
    print(f"\nRunning task: {args.prompt[:50]}... Mode: {args.mode}")
    
    try:
        results = await orchestrator.execute_request(
            user_request=final_prompt,
            mode=args.mode,
            deep_search=args.deep_search,
            auto_fix=args.auto_fix,
            budget_limit=args.local_limit
        )
        
        # 4. Report
        status = results.get("status", "unknown")
        print(f"\nTask completed with status: {status}")
        
        if "answer" in results:
            print(f"\n[ANSWER]:\n{results['answer']}")
        
        total_cost = 0.0
        # If it's a Lifecycle result, cost might be in orchestrator instance
        total_cost = orchestrator.orchestrator.cost_manager.total_cost
        print(f"Total Cost: ${total_cost:.4f}")
        
    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
