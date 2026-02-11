from core.context_manager_v3 import ContextManagerV3
import os

print(f"CWD: {os.getcwd()}")
cm = ContextManagerV3(enable_rag=False)
structure = cm._get_project_structure()
print(f"Structure length: {len(structure)}")
print("First 500 chars:")
print(structure[:500])
