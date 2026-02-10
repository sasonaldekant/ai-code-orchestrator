import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(name, path, method="GET", data=None):
    print(f"Testing {name} [{method} {path}]...", end=" ", flush=True)
    try:
        if method == "GET":
            resp = requests.get(f"{BASE_URL}{path}")
        else:
            resp = requests.post(f"{BASE_URL}{path}", json=data)
        
        if resp.ok:
            print("âœ… SUCCESS")
            return resp.json()
        else:
            print(f"â Œ FAILED ({resp.status_code})")
            print(f"   Response: {resp.text}")
            return None
    except Exception as e:
        print(f"â Œ ERROR: {e}")
        return None

def verify_all():
    print("=== Nexus v3.0 API Verification ===\n")
    
    # 1. Health
    test_endpoint("Health Check", "/health")
    
    # 2. Config
    config = test_endpoint("Global Settings", "/config/settings")
    if config:
        print(f"   Models found: {len(config.get('models', {}))}")
    
    # 3. Agents
    agents = test_endpoint("Agent Registry", "/agents/")
    if agents:
        print(f"   Agents registered: {len(agents.get('agents', []))}")
        for a in agents['agents']:
            print(f"     - {a['name']} ({a['role']})")

    # 4. Knowledge
    knowledge = test_endpoint("Knowledge Collections", "/knowledge/collections")
    if knowledge:
        print(f"   Collections found: {knowledge.get('collections', [])}")

if __name__ == "__main__":
    verify_all()
