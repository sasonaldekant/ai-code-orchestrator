# AI Code Orchestrator v3.0 - User Guide

This guide provides instructions on how to set up, configure, and use the AI Code Orchestrator v3.0. This major release introduces a domain-agnostic architecture, advanced RAG capabilities, and multi-model orchestration.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
   - [Domain Configuration](#domain-configuration)
   - [Model Routing](#model-routing)
   - [Cost Management](#cost-management)
3. [Ingesting Knowledge](#ingesting-knowledge)
4. [Running the Orchestrator](#running-the-orchestrator)
5. [Advanced Features](#advanced-features)

---

## 1. Installation

### Prerequisites

- Python 3.10+
- Node.js (for React component parsing)
- API Keys for OpenAI, Anthropic, or Google Gemini.

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/mgasic/ai-code-orchestrator.git
   cd ai-code-orchestrator
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   _Note: v3.0 introduces new dependencies: `chromadb`, `sentence-transformers`, `tiktoken`._

3. Set up environment variables:
   Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   GOOGLE_API_KEY=...
   ```

---

## 2. Configuration

### Domain Configuration (`config/domain_config.yaml`)

Define your specific domain knowledge sources here. The orchestrator uses this to understand your codebase and database.

```yaml
domain:
  name: "POS System"
  description: "Retail Point of Sale Application"

knowledge_sources:
  - type: "database"
    source_format: "ef_core"
    path: "/path/to/backend/Data"
    bounded_contexts:
      ordering: ["Orders", "OrderItems"]

  - type: "component_library"
    source_format: "react_tsx"
    path: "/path/to/frontend/src/components"
```

### Model Routing (`config/model_mapping_v2.yaml`)

Configure which AI model handles which phase of development. v3.0 supports routing based on task complexity and model strengths (e.g., Claude 3.5 Sonnet for architecture, GPT-4o for implementation).

### Cost Management (`core/cost_manager.py`)

Set budgets in `config/limits.yaml` (or via constructor) to prevent runaway costs.

- **Per-Task Budget**: Limit cost for a single feature request (default: $0.50).
- **Daily Budget**: Limit total daily consumption (default: $40.00).

---

## 3. Ingesting Knowledge

Before running the orchestrator, you must ingest your domain knowledge into the vector store.

### Using CLI (Recommended)

```bash
# Ingest your database schema (C# EF Core)
python manage.py ingest database ./path/to/backend/Data --models-dir ./path/to/backend/Data/Models

# Ingest your component library (React TypeScript)
# Ingest your component library (React TypeScript)
python manage.py ingest component_library ./path/to/frontend/src/components

# Ingest generic files (Documentation, Scripts, etc.)
python scripts/build_rag_index.py --directory ./docs --collection "project_docs"
```

### Programmatic Usage

```python
from domain_knowledge.ingestion.database_schema_ingester import DatabaseSchemaIngester
from rag.vector_store import ChromaVectorStore

# Ingest Database Schema
db_ingester = DatabaseSchemaIngester("/path/to/dbcontext", "/path/to/models")
documents = db_ingester.ingest()

# Store in Vector DB
vector_store = ChromaVectorStore(collection_name="pos_database_schema")
vector_store.add_documents(documents)
```

---

## 4. Running the Orchestrator

To start a new feature request using the Lifecycle Orchestrator:

### Using CLI

```bash
# The orchestrator will plan, architect, implement, and test the feature
python manage.py run "Add a loyalty points redemption feature to the checkout summary."
```

### Programmatic Usage

```python
import asyncio
from core.lifecycle_orchestrator import LifecycleOrchestrator

async def main():
    # Initialize
    orchestrator = LifecycleOrchestrator()

    # Submit request
    request = "Add a loyalty points redemption feature to the checkout summary."
    result = await orchestrator.execute_request(request)

    print("Execution Result:", result["status"])

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 5. Daily Operations

### Querying Knowledge Base

Ask questions about your ingested domain knowledge to verify what the system knows or for quick lookups.

```bash
python manage.py query "How does the Order entity relate to Customer?"
```

### Cost Monitoring

View usage and cost reports for your current session.

```bash
python manage.py cost
```

---

## 6. Advanced Features

### Domain-Aware Retrieval

The system doesn't just search for text; it understands code structure.

- **Entities**: It knows `Order` has a relationship with `Customer`.
- **Components**: It knows `SummaryCard` uses `Button` and `Icon`.

### Generic File Ingestion

You can ingest any code or documentation directory using the utility script:

```bash
# Index a directory recursively
python scripts/build_rag_index.py --directory ./src/utils --collection "utils"

# Index a single file
python scripts/build_rag_index.py --file ./README.md --collection "docs"
```

This uses smart chunking strategies automatically based on file type (Python/TS/C# vs Markdown vs Text).

### Producer-Reviewer Loop

Critical phases (like Architecture and Security) optionally enable a feedback loop where a second AI model reviews the output of the first, iterating until quality thresholds are met.

### Cost Tracking

Real-time cost tracking is enabled by default. Check `outputs/cost_report.json` after execution for a breakdown of tokens and costs by model.

### LLM Audit Log

For detailed auditing and debugging, every interaction with an LLM provider is logged to `outputs/audit_logs/llm_audit.jsonl`. This log includes:

- **Timestamp** and duration
- **Model** and provider
- **Full Prompt** sent to the model
- **Full Response** received from the model
- **Cost** and token usage
- **Error** details (if any)

This is useful for analyzing model behavior, debugging prompts, and verifying expenses.
