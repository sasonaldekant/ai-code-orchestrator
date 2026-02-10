import asyncio
import os
import sys
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any

# Add project root to path
sys.path.append(str(Path.cwd()))

from core.agents.specialist_agents.repair_agent import RepairAgent

# Setup Test Environment
TEST_FILE = Path("broken_math.py")
TEST_CONTENT = """
def add_numbers(a, b):
    # This function has a syntax error
    return a + b +
"""

@dataclass
class MockResponse:
    content: str

class TestMockLLM:
    async def complete(self, messages: List[Dict], model: str, **kwargs):
        prompt = messages[-1]["content"]
        
        if "Find the file and line number" in prompt:
            return MockResponse(content="The error is in broken_math.py line 4. It's a SyntaxError.")
            
        if "You are a Senior Debugger" in prompt:
            # Return the fix plan
            fix_plan = {
                "analysis": "Syntax error due to trailing +",
                "file_path": "broken_math.py",
                "fixed_content": "def add_numbers(a, b):\n    # Fixed syntax error\n    return a + b\n"
            }
            return MockResponse(content=json.dumps(fix_plan))
            
        return MockResponse(content="Unknown prompt")

async def run_verification():
    print(">>> Starting Phase 16.1 Verification (RepairAgent) <<<")
    
    # 1. Create broken file
    TEST_FILE.write_text(TEST_CONTENT, encoding="utf-8")
    print(f"[Setup] Created {TEST_FILE} with syntax error.")

    # 2. Initialize Agent with Mock LLM
    llm_client = TestMockLLM() 
    agent = RepairAgent(llm_client)
    
    # 3. Simulate Error Log (as if from Python execution)
    error_log = f"""
      File "{TEST_FILE.absolute()}", line 4
        return a + b +
                     ^
    SyntaxError: invalid syntax
    """
    
    print(f"[Action] Triggering auto_fix...")
    
    # 4. Run Auto-Fix
    result = await agent.auto_fix(error_log, f"python {TEST_FILE}")
    
    # 5. Verify Result
    print(f"[Result] Success: {result['success']}")
    print(f"[Result] Summary: {result['summary']}")
    
    if result['success']:
        new_content = TEST_FILE.read_text(encoding="utf-8")
        print("\n[Fixed Content]:")
        print(new_content)
        
        if "return a + b" in new_content and "return a + b +" not in new_content:
            print("\n>>> VERIFICATION PASSED: File was fixed! <<<")
        else:
            print("\n>>> VERIFICATION FAILED: Content does not look fixed. <<<")
    else:
        print("\n>>> VERIFICATION FAILED: Agent returned failure. <<<")

    # Cleanup
    if TEST_FILE.exists():
        os.remove(TEST_FILE)

if __name__ == "__main__":
    asyncio.run(run_verification())
