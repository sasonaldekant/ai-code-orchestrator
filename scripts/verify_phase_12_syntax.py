
import sys
import os
from pathlib import Path

# Add project root
sys.path.append(str(Path(__file__).parent.parent))

print("Checking api/admin_routes.py syntax...")
try:
    from api import admin_routes
    print("✅ Import successful.")
    
    if hasattr(admin_routes, 'build_knowledge_graph'):
        print("✅ build_knowledge_graph endpoint found.")
    else:
        print("❌ build_knowledge_graph endpoint MISSING.")
        
    if hasattr(admin_routes, 'knowledge_graph'):
        print("✅ Global knowledge_graph instance found.")
    else:
        print("❌ Global knowledge_graph instance MISSING.")

except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Syntax/Runtime error: {e}")
