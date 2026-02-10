import asyncio
import os
import sys
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any, Union

# Add project root to path
sys.path.append(str(Path.cwd()))

from api.ide_routes import IDEActionRequest, context_action
from core.llm_client_v2 import LLMClientV2

@dataclass
class MockResponse:
    content: str
    model: str = "mock-gpt-4o"
    tokens_used: Dict[str, int] = None

class TestMockLLM:
    async def complete(self, messages: List[Dict], model: str, **kwargs):
        system_msg = messages[0]["content"]
        user_msg = messages[1]["content"]
        
        if "expert tech lead" in system_msg:
            return MockResponse(content="This code adds two numbers.")
            
        if "expert debugger" in system_msg:
             return MockResponse(content="def foo():\n    return 1")
             
        return MockResponse(content="Unknown action")

# Monkey patch LLMClientV2 in ide_routes module context? 
# No, `context_action` instantiates `LLMClientV2` inside the function.
# This makes it hard to mock without dependency injection or patching.

# For this test, I will refrain from patching the module and instead trust the integration test 
# if I had a running server. But I don't validly have a running server in this environment.
# 
# Alternative: Modify `ide_routes.py` to accept `llm_client` as dependency?
# FastAPI dependency injection is the way.
# But `ide_routes.py` currently initiates it inside.

# I will use `unittest.mock` to patch `LLMClientV2` in `api.ide_routes`.

from unittest.mock import patch, MagicMock

async def run_verification():
    print(">>> Starting Phase 16.3 Verification (IDE Bridge) <<<")
    
    # Mock the LLMClientV2 class within api.ide_routes
    with patch("api.ide_routes.LLMClientV2") as MockClientClass:
        # Setup mock instance
        mock_instance = MockClientClass.return_value
        mock_instance.complete = MagicMock(side_effect=TestMockLLM().complete)
        
        # Test 1: EXPLAIN
        print("[Test] Testing EXPLAIN action...")
        req = IDEActionRequest(
            file_path="test.py",
            selection="def add(a,b): return a+b",
            action="EXPLAIN"
        )
        resp = await context_action(req)
        
        print(f"[Result] Success: {resp.success}")
        print(f"[Result] Content: {resp.result}")
        
        if resp.success and "This code adds two numbers" in resp.result:
             print(">>> VERIFICATION PASSED: EXPLAIN action worked <<<")
        else:
             print(">>> VERIFICATION FAILED: EXPLAIN action failed <<<")

        # Test 2: FIX
        print("\n[Test] Testing FIX action...")
        req_fix = IDEActionRequest(
            file_path="test.py",
            selection="def foo(): return 1 +",
            action="FIX",
            context="Syntax Error"
        )
        resp_fix = await context_action(req_fix)
        print(f"[Result] Success: {resp_fix.success}")
        if resp_fix.success and "def foo" in resp_fix.result:
             print(">>> VERIFICATION PASSED: FIX action worked <<<")
        else:
             print(">>> VERIFICATION FAILED: FIX action failed <<<")

if __name__ == "__main__":
    asyncio.run(run_verification())
