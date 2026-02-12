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
    parser.add_argument("--context", "-c", action="append", help="Path to a file to include as context.", default=None) # default None to check properly
    parser.add_argument("--strategy", "-s", choices=["sequential", "parallel", "adaptive"], default="adaptive", help="Execution strategy.")
    parser.add_argument("--question", "-q", help="Optional RAG question.", default=None)
    
    args = parser.parse_args()
    
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
        orchestrator = OrchestratorV2()
    except Exception as e:
        logger.error(f"Failed to initialize Orchestrator: {e}")
        return

    # 3. Running Pipeline
    print(f"\nRunning task: {args.prompt[:50]}...")
    try:
        strategy_enum = ExecutionStrategy(args.strategy)
    except ValueError:
        strategy_enum = ExecutionStrategy.ADAPTIVE

    try:
        # Use question if provided, else prompt acts as question
        question = args.question if args.question else args.prompt

        results = await orchestrator.run_pipeline_adaptive(
            initial_requirements=final_prompt,
            question=question,
            strategy=strategy_enum,
            use_feedback=True
        )
        
        # 4. Report
        status = results.get("status", "unknown")
        print(f"\nTask completed with status: {status}")
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        # Results are already saved by orchestrator to outputs/pipeline_v2_...
        # We can just print the path if available in metadata
        
        meta = results.get("metadata", {})
        print(f"Total Cost: ${meta.get('total_cost', 0.0):.4f}")
        
    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
