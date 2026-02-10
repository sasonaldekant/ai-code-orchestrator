
import sys
import os
from pathlib import Path

# Add project root
sys.path.append(str(Path(__file__).parent.parent))

print("Checking Phase 13 backend components...")
try:
    # Check Ingester presence
    from domain_knowledge.ingestion.database_content_ingester import DatabaseContentIngester
    print("✅ DatabaseContentIngester class found.")
    
    ingester = DatabaseContentIngester()
    if hasattr(ingester, 'ingest_from_sql') and hasattr(ingester, 'ingest_from_json'):
        print("✅ Ingester methods found.")
    else:
        print("❌ Ingester methods MISSING.")

    # Check API Endpoint presence (static check)
    from api import admin_routes
    if hasattr(admin_routes, 'ingest_content'):
         print("✅ ingest_content endpoint found.")
    else:
         print("❌ ingest_content endpoint MISSING.")

except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Syntax/Runtime error: {e}")
