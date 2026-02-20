import json
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add project root to sys.path
sys.path.append(os.getcwd())

from core.form_engine.orchestrator import FormEngineOrchestrator

async def main():
    orchestrator = FormEngineOrchestrator()
    base_dir = Path.cwd()
    
    projects_to_regen = [
        ("kreditni-zahtev", base_dir / "examples" / "form_templates" / "approved_kreditni-zahtev.json"),
        ("korisni-ka-registracija", base_dir / "examples" / "form_templates" / "approved_korisni-ka-registracija.json")
    ]
    
    for proj_name, template_path in projects_to_regen:
        template_path_str = str(template_path)
        if not os.path.exists(template_path_str):
            # Try finding another variant
            temp = str(base_dir / "examples" / "form_templates" / "01_basic_registration.json") if "korisni-ka" in proj_name else template_path_str
            if os.path.exists(temp):
                 template_path_str = temp
            else:
                print(f"Error: {template_path_str} not found.")
                continue
            
        print(f"Regenerating project: {proj_name} from {template_path_str}")
        project_path = await orchestrator.generate_ui_project(template_path_str, proj_name)
        print(f"Success: Project updated at {project_path}\n")

if __name__ == "__main__":
    asyncio.run(main())
