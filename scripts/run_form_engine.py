import asyncio
import argparse
import sys
import logging
import json
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.form_engine.orchestrator import FormEngineOrchestrator

# Load environment
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

async def main():
    parser = argparse.ArgumentParser(description="Run the DynUI Form Engine.")
    parser.add_argument("prompt", help="Natural language description of the form.")
    parser.add_argument("--name", default="generated-form", help="Name of the project to generate.")
    
    args = parser.parse_args()
    
    orchestrator = FormEngineOrchestrator()
    
    # Check if input is JSON data or natural language
    input_str = args.prompt.strip()
    is_json = input_str.startswith("{") and input_str.endswith("}")
    
    try:
        project_name = args.name.lower().replace(" ", "-")
        # Ensure project name is safe
        project_name = "".join(c for c in project_name if c.isalnum() or c == "-")
        
        if is_json:
            try:
                data_sample = json.loads(input_str)
                print(f":::STEP: {{\"text\": \"Inferring form from JSON data sample...\", \"type\": \"running\", \"tier\": 3}}")
                path = await orchestrator.generate_from_data(data_sample, project_name)
            except json.JSONDecodeError:
                # If it looked like JSON but failed, treat as prompt
                print(f":::STEP: {{\"text\": \"Analyzing requirement: {args.prompt[:30]}...\", \"type\": \"running\", \"tier\": 3}}")
                path = await orchestrator.generate_from_prompt(args.prompt, project_name)
        else:
            print(f":::STEP: {{\"text\": \"Analyzing requirement: {args.prompt[:30]}...\", \"type\": \"running\", \"tier\": 3}}")
            path = await orchestrator.generate_from_prompt(args.prompt, project_name)
        
        print(f"\n:::STEP: {{\"text\": \"Form project generated successfully!\", \"type\": \"done\", \"tier\": 3}}")
        print(f"\n[Generated Path]: {path}")
        print(f"\nTo run the form:\ncd {path}\nnpm install\nnpm run dev")
        
    except Exception as e:
        logger.error(f"\n[Error]: {str(e)}")
        print(f":::STEP: {{\"text\": \"Generation failed: {str(e)}\", \"type\": \"failed\", \"tier\": 3}}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
