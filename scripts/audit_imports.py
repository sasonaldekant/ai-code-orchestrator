import sys
import os
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

print(f"Checking imports from: {project_root}")

modules_to_check = [
    "core.external_integration",
    "core.orchestrator",
    "core.graph.schema",
    "api.admin_routes",
    "rag.vector_store"
]

failed = []

for module in modules_to_check:
    try:
        __import__(module)
        print(f"✅ Import successful: {module}")
    except ImportError as e:
        print(f"❌ Import failed: {module} - {e}")
        failed.append(module)
    except Exception as e:
        print(f"❌ Error loading {module}: {e}")
        failed.append(module)

if failed:
    print(f"\nAudit FAILED. Fix issues in: {failed}")
    sys.exit(1)
else:
    print("\nAudit PASSED. All core modules loadable.")
    sys.exit(0)
