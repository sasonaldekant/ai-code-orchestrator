"""
Test script to send JSON-to-Form generation request to the orchestrator.
"""
import asyncio
import requests
import json

async def test_json_to_form():
    url = "http://localhost:8000/orchestrate"
    
    request_text = """
Pročitaj JSON fajl na putanji `examples/insurance-system/frontend/components/fizicko-lice.json` i generiši mi React komponentu koja renderuje ovu formu koristeći moje postojeće komponente iz biblioteke.

Pravila mapiranja:
- `type: "text"` → koristi komponentu za text input
- `type: "radio"` → koristi komponentu za radio button group  
- `type: "date"` → koristi komponentu za date picker
- `type: "tel"` → koristi komponentu za telephone input
- `type: "email"` → koristi komponentu za email input

Uključi:
1. Svu validaciju definisanu u JSON-u (required, pattern, minLength, maxLength)
2. Error handling sa porukama iz `errorMessage` polja
3. Responsive layout
4. Submit handler koji loguje podatke

Generiši kompletan .tsx fajl spreman za upotrebu.
"""
    
    payload = {
        "request": request_text,
        "mode": "standard",
        "deep_search": False,
        "retrieval_strategy": "local",
        "auto_fix": False,
        "consensus_mode": False,
        "review_strategy": "basic"
    }
    
    print("Sending request to orchestrator...")
    print(f"Request: {request_text[:100]}...")
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("\n✅ Request accepted!")
        print("Check the GUI for real-time progress and thinking stream.")
        result = response.json()
        print(f"\nResult preview: {json.dumps(result, indent=2)[:500]}...")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    asyncio.run(test_json_to_form())
