"""
Verification script for ChunkingEngine.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.chunking.engine import ChunkingEngine

def main():
    print("=== ChunkingEngine Verification ===\n")
    engine = ChunkingEngine()
    
    # 1. Test Code Chunking (Python)
    print("Testing Code Chunking (.py):")
    code_content = """
class Database:
    def __init__(self):
        self.connected = False
        
    def connect(self):
        print("Connecting...")
        self.connected = True

class User:
    def __init__(self, name):
        self.name = name
        
    def greet(self):
        return f"Hello, {self.name}"

def global_helper():
    return 42
"""
    chunks = engine.chunk_content(code_content, file_path="db.py", chunk_size=100)
    print(f"Produced {len(chunks)} chunks.")
    for i, c in enumerate(chunks):
        print(f"--- Chunk {i} ({c.metadata['type']}) ---")
        print(c.content)
    
    # 2. Test Text Chunking
    print("\nTesting Text Chunking (.txt):")
    text_content = "Word " * 100 # 500 characters
    chunks = engine.chunk_content(text_content, file_path="info.txt", chunk_size=200, overlap=50)
    print(f"Produced {len(chunks)} chunks.")
    for i, c in enumerate(chunks):
        print(f"--- Chunk {i} ---")
        print(f"Length: {len(c.content)}")

if __name__ == "__main__":
    main()
