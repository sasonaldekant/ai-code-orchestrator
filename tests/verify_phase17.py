import asyncio
import os
import sys
import json
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

# Add project root to path
sys.path.append(str(Path.cwd()))

from core.registry import CapabilityRegistry, register_tool
from core.memory.user_prefs import UserPreferences
from core.memory.experience_db import ExperienceDB
from core.llm_client_v2 import LLMClientV2

# --- Test Data ---
TEST_PREF_RULE = "Always use Python 3.9 type hinting"
TEST_ERROR = "IndexError: list index out of range"
TEST_FIX = "Added check for len(list) > index"

async def run_verification():
    print(">>> Starting Phase 17 Verification (Memory & Cortex) <<<")

    # 1. Verify Registry
    print("\n[Test 1] Capability Registry")
    registry = CapabilityRegistry()
    tools = registry.list_tools()
    print(f"Registered Tools: {tools}")
    
    # Check if our agents registered themselves (by importing them)
    # We need to import the modules for decorators to run
    from core.agents.specialist_agents.repair_agent import RepairAgent
    from core.vision_manager import VisionManager
    
    if "auto_fix" in registry.list_tools() and "analyze_image" in registry.list_tools():
        print(">>> PASSED: Agents registered successfully <<<")
    else:
        print(">>> FAILED: Agents not registered <<<")

    # 2. Verify User Preferences
    print("\n[Test 2] User Preferences")
    prefs = UserPreferences()
    # Reset for test
    prefs.rules = [] 
    prefs.add_rule(TEST_PREF_RULE, "coding_style")
    
    context = prefs.get_system_prompt_context()
    print(f"Preference Context:\n{context}")
    
    if TEST_PREF_RULE in context:
        print(">>> PASSED: User Preference stored and retrieved <<<")
    else:
        print(">>> FAILED: User Preference missing <<<")

    # 3. Verify Experience DB
    print("\n[Test 3] Experience DB")
    exp_db = ExperienceDB()
    # Clean up test DB entry if exists
    conn = sqlite3.connect(exp_db.db_path)
    conn.execute("DELETE FROM experiences WHERE error_pattern = ?", (TEST_ERROR,))
    conn.commit()
    conn.close()

    # Record
    exp_db.record_fix(TEST_ERROR, TEST_FIX, "test_context")
    
    # Retrieve
    matches = exp_db.find_similar_error(TEST_ERROR)
    print(f"Matches found: {len(matches)}")
    if matches and matches[0]['fix_strategy'] == TEST_FIX:
        print(">>> PASSED: Experience recorded and retrieved <<<")
    else:
        print(f">>> FAILED: Experience not found {matches} <<<")

    # 4. Verify LLMClient Integration (Mocked)
    print("\n[Test 4] LLMClient Integration")
    # Setup Client
    client = LLMClientV2(MagicMock())
    
    # Mock the provider directly in the dictionary
    mock_provider = MagicMock()
    mock_provider.complete = AsyncMock(return_value=MagicMock(content="OK", tokens_used={"prompt": 0, "completion": 0}))
    client.providers["openai"] = mock_provider
    client.providers["anthropic"] = mock_provider
    client.providers["google"] = mock_provider
    
    # Run complete
    await client.complete([{"role": "user", "content": "Hello"}], "gpt-4o")
    
    # Check calling args
    call_args = mock_provider.complete.call_args
    if call_args:
         messages = call_args.kwargs.get('messages', [])
         system_msg = next((m for m in messages if m['role'] == 'system'), None)
         if system_msg and TEST_PREF_RULE in system_msg['content']:
             print(">>> PASSED: User preferences injected into System Prompt <<<")
         else:
             print(f">>> FAILED: System prompt missing preferences. Msg: {system_msg} <<<")
    else:
         print(">>> FAILED: Provider not called <<<")

    # Clean up
    if Path("user_prefs.json").exists():
        os.remove("user_prefs.json")
    # Don't delete experience.db, valuable data potentially (though just test data here)

if __name__ == "__main__":
    asyncio.run(run_verification())
