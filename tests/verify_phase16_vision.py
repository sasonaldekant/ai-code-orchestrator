import asyncio
import os
import sys
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any, Union

# Add project root to path
sys.path.append(str(Path.cwd()))

from core.vision_manager import VisionManager
from core.llm_client_v2 import LLMClientV2

@dataclass
class MockResponse:
    content: str
    model: str = "mock-gpt-4o"
    tokens_used: Dict[str, int] = None

class TestMockLLM:
    async def complete(self, messages: List[Dict], model: str, **kwargs):
        # Verify content structure
        user_msg = messages[1]
        content = user_msg["content"]
        
        # Check if we received image content
        has_image = False
        prompt_text = ""
        
        if isinstance(content, list):
            for block in content:
                if block.get("type") == "image_url":
                    has_image = True
                if block.get("type") == "text":
                    prompt_text = block.get("text")
        
        if not has_image:
            return MockResponse(content="Error: No image received in prompt")
            
        if "Analyze this UI" in prompt_text:
            return MockResponse(content="I see a button and a text input. The layout looks clean.")
            
        return MockResponse(content="Analysis complete.")

async def run_verification():
    print(">>> Starting Phase 16.2 Verification (VisionManager) <<<")
    
    # 1. Setup Mock
    llm_client = TestMockLLM()
    manager = VisionManager(llm_client)
    
    # 2. Test Data URI
    print("[Test] Testing Data URI...")
    data_uri = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    
    result = await manager.analyze_image(data_uri, "Analyze this UI")
    
    print(f"[Result] Success: {result['success']}")
    if result.get("analysis") == "I see a button and a text input. The layout looks clean.":
        print(">>> VERIFICATION PASSED: Data URI handled correctly <<<")
    else:
        print(f">>> VERIFICATION FAILED: Unexpected response: {result} <<<")

    # 3. Test Local File (Optional, but good to check path handling)
    print("\n[Test] Testing Local File...")
    test_img = Path("test_image.png")
    test_img.write_bytes(b"fake image data") # Not valid image but good enough for path check
    
    try:
        # We expect a failure in _encode_local_image regarding base64 encoding if it reads invalid binary? 
        # actually base64 just encodes bytes, so it should work fine even if it's not a real png.
        # But our MockLLM doesn't care about the base64 content validity.
        result_file = await manager.analyze_image(str(test_img), "Analyze this UI")
        if result_file['success']:
             print(">>> VERIFICATION PASSED: Local file handled correctly <<<")
        else:
             print(f">>> VERIFICATION FAILED: Local file error: {result_file} <<<")
             
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if test_img.exists():
            os.remove(test_img)

if __name__ == "__main__":
    asyncio.run(run_verification())
