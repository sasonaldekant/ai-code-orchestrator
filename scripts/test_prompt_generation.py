
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.phase_agents.analyst import AnalystAgent
from agents.phase_agents.architect import ArchitectAgent
from agents.phase_agents.implementation import ImplementationAgent

def test_prompts():
    print(f"DEBUG: CWD = {os.getcwd()}")
    rag_path = Path("rag")
    if rag_path.exists():
        print(f"DEBUG: rag dir contents: {[p.name for p in rag_path.iterdir()]}")
    else:
        print("DEBUG: rag dir NOT FOUND relative to CWD")

    print("Testing prompt generation...")
    
    # Dummy orchestrator
    orchestrator = MagicMock()
    
    # Context
    context = {"requirements": "Build a login form."}
    rag_context = [{"content": "DynInput component usage..."}]
    
    # 1. Test Analyst
    print("\n--- Testing Analyst Agent ---")
    analyst = AnalystAgent(orchestrator)
    # Mock prompt path to point to real file relative to script execution
    analyst.prompt_path = Path("prompts/phase_prompts/analyst.txt")
    
    prompt = analyst._build_prompt_content(context, rag_context)
    
    if "[PROJECT STANDARDS & RULES]" in prompt or "DynUI" in prompt:
        print("PASS: Analyst prompt contains Golden Rules placeholder/section.")
    else:
        print("FAIL: Analyst prompt MISSING Golden Rules.")
        print(f"DEBUG: Prompt prefix: {prompt[:200]}...")
        
    if "DynInput component usage" in prompt:
         print("PASS: Analyst prompt contains RAG context.")
    else:
         print("FAIL: Analyst prompt MISSING RAG context.")

    # 2. Test Architect
    print("\n--- Testing Architect Agent ---")
    architect = ArchitectAgent(orchestrator)
    architect.prompt_path = Path("prompts/phase_prompts/architect.txt")
    
    prompt = architect._build_prompt_content(context, rag_context)
    
    if "[PROJECT STANDARDS & RULES]" in prompt or "DynUI" in prompt:
        print("PASS: Architect prompt contains Golden Rules placeholder/section.")
    else:
        print("FAIL: Architect prompt MISSING Golden Rules.")

    if "You MUST use existing DynUI components" in prompt:
        print("PASS: Architect prompt contains new instructions.")
    else:
        print("FAIL: Architect prompt MISSING new instructions.")

    # 3. Test Implementation
    print("\n--- Testing Implementation Agent ---")
    implementer = ImplementationAgent(orchestrator)
    # Test Frontend
    implementer.frontend_prompt_path = Path("prompts/phase_prompts/implementation_frontend.txt")
    
    # Need architecture in context
    context["architecture"] = "Frontend Arch"
    context["domain_context"] = "Domain"
    context["milestone"] = "M1"
    context["original_request"] = "Req"
    
    prompt = implementer._build_prompt(
        implementer.frontend_prompt_path,
        context,
        rag_context,
        "Fallback"
    )
    
    if "[PROJECT STANDARDS & RULES]" in prompt or "DynUI" in prompt:
        print("PASS: Frontend prompt contains Golden Rules placeholder/section.")
    else:
        print("FAIL: Frontend prompt MISSING Golden Rules.")
        
    if "STRICTLY FOLLOW the 3-Layer Token System" in prompt:
         print("PASS: Frontend prompt contains strict 3-Layer Token instructions.")
    else:
         print("FAIL: Frontend prompt MISSING strict instructions.")

if __name__ == "__main__":
    test_prompts()
