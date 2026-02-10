import requests

BASE_URL = "http://localhost:8000/admin"

def test():
    print("Listing collections...")
    collections_resp = requests.get(f"{BASE_URL}/collections")
    if collections_resp.status_code != 200:
        print(f"Error: {collections_resp.status_code}")
        return
    
    collections = collections_resp.json().get("collections", [])
    if not collections:
        print("No collections found.")
        return
    
    col = collections[0]
    print(f"Browsing collection: {col}")
    docs_resp = requests.get(f"{BASE_URL}/collections/{col}/documents?limit=1")
    if docs_resp.status_code == 200:
        docs = docs_resp.json().get("documents", [])
        print(f"Found {len(docs)} documents.")
        if docs:
            print(f"Sample Doc ID: {docs[0]['id']}")
    else:
        print(f"Browse error: {docs_resp.status_code} - {docs_resp.text}")

if __name__ == "__main__":
    test()
