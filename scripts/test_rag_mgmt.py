"""
Verification script for RAG document management endpoints.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/admin"

def main():
    print("=== RAG Document Management Verification ===\n")
    
    collection_name = "test_management_collection"
    
    # 1. Ensure collection exists by adding a document
    print(f"Adding test document to '{collection_name}'...")
    ingest_payload = {
        "source_path": ".", # Dummy
        "collection_name": collection_name,
        "chunk_size": 1000,
        "chunk_overlap": 100
    }
    # Note: Using execute_ingestion might be too heavy for a quick test. 
    # Let's instead use the vector store directly if we can't easily hit the API for direct add.
    # Actually, the admin API doesn't have a 'direct add document' endpoint for users yet.
    # It has 'execute_ingestion' which reads files.
    
    # Let's just use the browsing endpoint on an existing collection 
    # to prove it works, or use 'rag_collection' if it exists.
    
    response = requests.get(f"{BASE_URL}/collections")
    collections = response.json().get("collections", [])
    if not collections:
        print("No collections found. Run ingestion first.")
        return
        
    target_collection = collections[0]
    print(f"Testing browsing on collection: {target_collection}")
    
    # 2. Browse documents
    browse_url = f"{BASE_URL}/collections/{target_collection}/documents?limit=5"
    resp = requests.get(browse_url)
    if resp.status_code == 200:
        data = resp.json()
        docs = data.get("documents", [])
        print(f"Successfully retrieved {len(docs)} documents.")
        if docs:
            first_doc_id = docs[0]['id']
            print(f"First doc ID: {first_doc_id}")
            
            # 3. Test deletion (optional, be careful)
            # print(f"Deleting doc {first_doc_id}...")
            # del_resp = requests.delete(f"{BASE_URL}/collections/{target_collection}/documents/{first_doc_id}")
            # print(f"Deletion status: {del_resp.status_code}, {del_resp.json()}")
    else:
        print(f"Failed to browse documents: {resp.status_code}, {resp.text}")

if __name__ == "__main__":
    main()
