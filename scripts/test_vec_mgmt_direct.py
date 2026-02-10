from rag.vector_store import ChromaVectorStore, Document
import logging

# Disable excessive logging
logging.getLogger("chromadb").setLevel(logging.ERROR)

def test_direct():
    print("=== Direct VectorStore Test ===")
    store = ChromaVectorStore(collection_name="rag_collection")
    
    # 1. Try to get documents
    print("Fetching documents...")
    docs = store.get_documents(limit=5)
    print(f"Found {len(docs)} documents.")
    
    if docs:
        for i, doc in enumerate(docs):
            print(f"[{i}] ID: {doc.id}, Metadata: {doc.metadata}")
            
    # 2. Add and delete a test doc
    print("Testing add/delete...")
    test_id = "test_doc_123"
    test_doc = Document(id=test_id, text="Test content", metadata={"type": "test"})
    store.add_documents([test_doc])
    
    docs_after = store.get_documents(limit=100)
    found = any(d.id == test_id for d in docs_after)
    print(f"Doc added successfully: {found}")
    
    if found:
        store.delete_document(test_id)
        docs_final = store.get_documents(limit=100)
        still_there = any(d.id == test_id for d in docs_final)
        print(f"Doc deleted successfully: {not still_there}")

if __name__ == "__main__":
    test_direct()
