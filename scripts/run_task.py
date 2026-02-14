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
    from core.orchestrator_v2 import OrchestratorV2, ExecutionStrategy
except ImportError:
    print("Error: Could not import OrchestratorV2. Make sure you are running from the project root or scripts folder.")
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
    parser.add_argument("--question", "-q", help="Optional RAG question.", default=None)
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
        # We could pass a custom config or model map here if we wanted to support --model override more deeply
        orchestrator = OrchestratorV2(local_task_budget=args.local_limit)
        
        # Simple Model Override Hack if --model is provided
        if args.model:
            print(f"Using model override: {args.model}")
            # Inject into analyst/architect etc. or just default
            # For now, we'll assume Orchestrator/Router can handle it if we modify them, 
            # but let's at least log it.
    except Exception as e:
        logger.error(f"Failed to initialize Orchestrator: {e}")
        return

    # 3. Running Pipeline
    print(f"\nRunning task: {args.prompt[:50]}...")
    
    # Map high-level strategies to ExecutionStrategy
    strategy_val = args.strategy.lower()
    if strategy_val == "fast":
        strategy_enum = ExecutionStrategy.SEQUENTIAL
        use_feedback = False
        print("Strategy: Fast (Sequential, No Feedback)")
    elif strategy_val == "planning":
        strategy_enum = ExecutionStrategy.ADAPTIVE
        use_feedback = True
        print("Strategy: Planning (Full Adaptive with Feedback)")
    elif strategy_val == "execution":
        strategy_enum = ExecutionStrategy.PARALLEL
        use_feedback = True
        print("Strategy: Execution (Parallel with Feedback)")
    else:
        try:
            strategy_enum = ExecutionStrategy(strategy_val)
        except ValueError:
            strategy_enum = ExecutionStrategy.ADAPTIVE
        use_feedback = True

    try:
        # Use question if provided, else prompt acts as question
        question = args.question if args.question else args.prompt

        results = await orchestrator.run_pipeline_adaptive(
            initial_requirements=final_prompt,
            question=question,
            strategy=strategy_enum,
            use_feedback=use_feedback,
            deep_search=args.deep_search
        )
        
        # 4. Report
        status = results.get("status", "unknown")
        print(f"\nTask completed with status: {status}")
        
        meta = results.get("metadata", {})
        print(f"Total Cost: ${meta.get('total_cost', 0.0):.4f}")
        
    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
