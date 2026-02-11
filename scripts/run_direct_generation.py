import asyncio
import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from core.lifecycle_orchestrator import LifecycleOrchestrator
from api.event_bus import bus, EventType

async def main():
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
        
    print("Starting direct orchestration...")
    orchestrator = LifecycleOrchestrator()
    
    request_text = """
Pročitaj JSON fajl na putanji `examples/insurance-system/frontend/components/fizicko-lice.json` 
i generiši mi React komponentu koja renderuje ovu formu koristeći moje postojeće komponente iz biblioteke.

Pravila mapiranja:
- type: 'text' -> koristi DynInput
- type: 'radio' -> koristi RadioGroup
- type: 'date' -> koristi DatePicker
- type: 'tel' -> koristi DynInput sa type='tel'
- type: 'email' -> koristi DynInput sa type='email'

Uključi:
1. Svu validaciju definisanu u JSON-u (required, pattern, minLength, maxLength)
2. Error handling sa porukama iz 'errorMessage' polja
3. Responsive layout
4. Submit handler koji loguje podatke

Generiši kompletan .tsx fajl.
"""
    
    try:
        print("Executing request...")
        result = await orchestrator.execute_request(
            request_text,
            mode="standard"
        )
        
        output_path = "outputs/fizicko_lice_form_result.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        
        print(f"\n[SUCCESS] All result data saved to {output_path}")
        
    except Exception as e:
        print(f"\n[ERROR] Execution script failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
