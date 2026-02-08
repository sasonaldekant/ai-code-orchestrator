#!/usr/bin/env python3
"""
Example demonstrating Advanced RAG usage.

Shows how to:
1. Initialize the RAG system
2. Index documents
3. Perform searches
4. Use with context manager
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.retriever_v2 import EnhancedRAGRetriever
from core.context_manager_v2 import EnhancedContextManager


def example_1_basic_indexing():
    """Example 1: Basic document indexing and retrieval."""
    print("\n" + "="*60)
    print("Example 1: Basic Indexing and Retrieval")
    print("="*60)
    
    # Initialize retriever
    retriever = EnhancedRAGRetriever(
        collection_name="example_docs",
        persist_directory="./example_chroma_db",
    )
    
    # Reset collection for clean start
    retriever.reset_collection()
    
    # Sample documents
    documents = [
        {
            "content": """
            # Authentication Guide
            
            Our API uses JWT tokens for authentication.
            
            ## Getting Started
            
            1. Register a user account
            2. Login to receive JWT token
            3. Include token in Authorization header
            
            ## Example
            
            ```python
            headers = {
                'Authorization': f'Bearer {token}'
            }
            response = requests.get('/api/users', headers=headers)
            ```
            """,
            "metadata": {
                "source": "auth_guide.md",
                "topic": "authentication",
                "type": "documentation",
            },
            "id": "auth_guide",
        },
        {
            "content": """
            def authenticate_user(username: str, password: str) -> dict:
                '''Authenticate user and return JWT token.'''
                user = db.query(User).filter_by(username=username).first()
                
                if not user or not verify_password(password, user.password_hash):
                    raise AuthenticationError("Invalid credentials")
                
                token = generate_jwt_token(user.id)
                return {"token": token, "user_id": user.id}
            
            def verify_jwt_token(token: str) -> int:
                '''Verify JWT token and return user ID.'''
                try:
                    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                    return payload["user_id"]
                except jwt.InvalidTokenError:
                    raise AuthenticationError("Invalid token")
            """,
            "metadata": {
                "source": "auth.py",
                "topic": "authentication",
                "language": "python",
                "type": "code",
            },
            "id": "auth_code",
        },
        {
            "content": """
            # Database Setup
            
            ## PostgreSQL Configuration
            
            Set up connection string in environment:
            
            ```
            DATABASE_URL=postgresql://user:password@localhost:5432/mydb
            ```
            
            ## Migrations
            
            Run migrations using Alembic:
            
            ```bash
            alembic upgrade head
            ```
            """,
            "metadata": {
                "source": "database_setup.md",
                "topic": "database",
                "type": "documentation",
            },
            "id": "db_setup",
        },
    ]
    
    # Index documents
    print("\nIndexing documents...")
    total_chunks = retriever.add_documents_batch(
        documents=documents,
        chunking_strategy="text",
    )
    print(f"✓ Indexed {len(documents)} documents -> {total_chunks} chunks")
    
    # Perform semantic search
    print("\nSearching: 'How to implement user authentication?'")
    results = retriever.retrieve(
        query="How to implement user authentication?",
        top_k=3,
    )
    
    print(f"\nFound {len(results)} results:")
    for idx, result in enumerate(results, 1):
        print(f"\n[{idx}] Score: {result.score:.3f}")
        print(f"Source: {result.metadata.get('source', 'unknown')}")
        print(f"Content preview: {result.content[:150]}...")


def example_2_hybrid_search():
    """Example 2: Hybrid search (semantic + keyword)."""
    print("\n" + "="*60)
    print("Example 2: Hybrid Search")
    print("="*60)
    
    retriever = EnhancedRAGRetriever(
        collection_name="example_docs",
        persist_directory="./example_chroma_db",
    )
    
    # Hybrid search for specific implementation
    print("\nHybrid search: 'JWT token verification code'")
    results = retriever.hybrid_retrieve(
        query="JWT token verification code",
        top_k=2,
        semantic_weight=0.7,  # 70% semantic, 30% keyword
    )
    
    print(f"\nFound {len(results)} results:")
    for idx, result in enumerate(results, 1):
        print(f"\n[{idx}] Score: {result.score:.3f}")
        print(f"Type: {result.metadata.get('type', 'unknown')}")
        print(f"Source: {result.metadata.get('source', 'unknown')}")
        print(f"Content:\n{result.content[:300]}...")


def example_3_metadata_filtering():
    """Example 3: Search with metadata filtering."""
    print("\n" + "="*60)
    print("Example 3: Metadata Filtering")
    print("="*60)
    
    retriever = EnhancedRAGRetriever(
        collection_name="example_docs",
        persist_directory="./example_chroma_db",
    )
    
    # Search only in code files
    print("\nSearching in code files only...")
    results = retriever.retrieve(
        query="authentication implementation",
        top_k=3,
        filter_metadata={"type": "code"},
    )
    
    print(f"\nFound {len(results)} code results:")
    for idx, result in enumerate(results, 1):
        print(f"\n[{idx}] {result.metadata.get('source', 'unknown')}")
        print(f"Language: {result.metadata.get('language', 'N/A')}")
        print(f"Preview:\n{result.content[:200]}...")
    
    # Search only in documentation
    print("\n" + "-"*60)
    print("Searching in documentation only...")
    results = retriever.retrieve(
        query="authentication setup",
        top_k=3,
        filter_metadata={"type": "documentation"},
    )
    
    print(f"\nFound {len(results)} documentation results:")
    for idx, result in enumerate(results, 1):
        print(f"\n[{idx}] {result.metadata.get('source', 'unknown')}")
        print(f"Preview:\n{result.content[:200]}...")


def example_4_context_manager():
    """Example 4: Using RAG with Context Manager."""
    print("\n" + "="*60)
    print("Example 4: Context Manager Integration")
    print("="*60)
    
    # Initialize context manager with RAG
    retriever = EnhancedRAGRetriever(
        collection_name="example_docs",
        persist_directory="./example_chroma_db",
    )
    
    context_mgr = EnhancedContextManager(
        retriever=retriever,
        enable_rag=True,
    )
    
    # Build enriched context
    print("\nBuilding enriched context for query...")
    context = context_mgr.build_context(
        phase="implementation",
        specialty="backend",
        user_query="Create secure login endpoint with JWT authentication",
        top_k_docs=3,
        filter_metadata={"topic": "authentication"},
    )
    
    # Format for LLM prompt
    prompt_context = context.to_prompt_context(max_docs=2)
    
    print("\nEnriched Context for LLM:")
    print("="*60)
    print(prompt_context)
    print("="*60)
    
    # RAG statistics
    stats = context_mgr.get_rag_stats()
    print(f"\nRAG Stats:")
    print(f"  Enabled: {stats['enabled']}")
    print(f"  Collection: {stats['collection_name']}")
    print(f"  Documents: {stats['document_count']}")


def example_5_code_chunking():
    """Example 5: Code-specific chunking."""
    print("\n" + "="*60)
    print("Example 5: Code Chunking Strategy")
    print("="*60)
    
    retriever = EnhancedRAGRetriever(
        collection_name="code_example",
        persist_directory="./example_chroma_db",
    )
    
    # Reset for clean example
    retriever.reset_collection()
    
    # Sample Python code
    python_code = """
    class UserService:
        '''Service for user management operations.'''
        
        def __init__(self, db_session):
            self.db = db_session
        
        def create_user(self, username: str, email: str, password: str) -> User:
            '''Create a new user account.'''
            password_hash = hash_password(password)
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
            )
            self.db.add(user)
            self.db.commit()
            return user
        
        def get_user(self, user_id: int) -> User:
            '''Retrieve user by ID.'''
            return self.db.query(User).filter_by(id=user_id).first()
        
        def update_user(self, user_id: int, **kwargs) -> User:
            '''Update user information.'''
            user = self.get_user(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            for key, value in kwargs.items():
                setattr(user, key, value)
            
            self.db.commit()
            return user
        
        def delete_user(self, user_id: int) -> bool:
            '''Delete user account.'''
            user = self.get_user(user_id)
            if not user:
                return False
            
            self.db.delete(user)
            self.db.commit()
            return True
    """
    
    # Index with code chunking
    print("\nIndexing code with 'code' strategy...")
    chunks_count = retriever.add_document(
        content=python_code,
        metadata={
            "source": "user_service.py",
            "language": "python",
            "type": "code",
        },
        doc_id="user_service",
        chunking_strategy="code",
    )
    
    print(f"✓ Created {chunks_count} chunks from code")
    
    # Search for specific method
    print("\nSearching: 'How to update user information?'")
    results = retriever.hybrid_retrieve(
        query="How to update user information?",
        top_k=2,
    )
    
    for idx, result in enumerate(results, 1):
        print(f"\n[{idx}] Score: {result.score:.3f}")
        print(f"Content:\n{result.content}")


def main():
    """Run all examples."""
    print("\n" + "#"*60)
    print("#  Advanced RAG Examples")
    print("#"*60)
    
    try:
        example_1_basic_indexing()
        example_2_hybrid_search()
        example_3_metadata_filtering()
        example_4_context_manager()
        example_5_code_chunking()
        
        print("\n" + "="*60)
        print("All examples completed successfully! ✓")
        print("="*60)
        
    except Exception as exc:
        print(f"\n❌ Error: {exc}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
