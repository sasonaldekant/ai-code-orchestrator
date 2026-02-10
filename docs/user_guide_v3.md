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
5. [Nexus GUI](#nexus-gui)
6. [Admin Panel](#admin-panel)
7. [Best Practices & Guidelines](#best-practices--guidelines)
8. [Lessons Learned System](#lessons-learned-system)
9. [Advanced Features](#advanced-features)
10. [Troubleshooting](#troubleshooting)

---

## 1. Installation

### Prerequisites

- Python 3.10+
- Node.js 18+ (for React component parsing and GUI)
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
   cd ui && npm install
   ```

   _Note: v3.0 introduces new dependencies: `chromadb`, `sentence-transformers`, `tiktoken`._

3. Set up environment variables:
   Copy `.env.example` to `.env` and fill in your API keys:

   ```bash
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   GOOGLE_API_KEY=...
   ```

4. Start the system:

   ```bash
   # Terminal 1: Backend
   cd api && uvicorn app:app --reload --port 8000

   # Terminal 2: Frontend (Nexus GUI)
   cd ui && npm run dev
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

  - type: "existing_codebase" # NEW in v3.0
    source_format: "dotnet_solution"
    path: "/path/to/existing/project"
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

### Using CLI

```bash
# Ingest your database schema (C# EF Core)
python manage.py ingest database ./path/to/backend/Data --models-dir ./path/to/backend/Data/Models

# Ingest your component library (React TypeScript)
python manage.py ingest component_library ./path/to/frontend/src/components

# NEW: Ingest existing project codebase
python manage.py ingest project_codebase ./path/to/existing/project

# Ingest generic files (Documentation, Scripts, etc.)
python scripts/build_rag_index.py --directory ./docs --collection "project_docs"
```

### Using Admin Panel (Recommended)

1. Open Nexus GUI → Click **"Admin Settings"** (bottom-left)
2. Navigate to **"RAG Ingestion"** tab
3. Select type, configure paths, click **Validate** then **Ingest**

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

### Using CLI

```bash
# The orchestrator will plan, architect, implement, and test the feature
python manage.py run "Add a loyalty points redemption feature to the checkout summary."
```

### Using Nexus GUI (Recommended)

1. Start the GUI: `cd ui && npm run dev`
2. Enter your request in the chat input
3. Click **"Execute"** and watch the Thought Stream

### Programmatic Usage

```python
import asyncio
from core.lifecycle_orchestrator import LifecycleOrchestrator

async def main():
    orchestrator = LifecycleOrchestrator()
    request = "Add a loyalty points redemption feature to the checkout summary."
    result = await orchestrator.execute_request(request)
    print("Execution Result:", result["status"])

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 5. Nexus GUI

### Overview

Nexus is the graphical interface for AI Code Orchestrator. Access it at `http://localhost:5173` after starting the frontend.

### Main Features

| Feature                | Description                                  |
| ---------------------- | -------------------------------------------- |
| **Thought Stream**     | Real-time visualization of AI reasoning      |
| **Orchestration Plan** | Interactive task list with status indicators |
| **Artifact Workshop**  | Live code generation with Monaco Editor      |
| **Cost HUD**           | Real-time token and cost tracking            |

### Starting Nexus

```bash
# Terminal 1 - Backend
cd api && uvicorn app:app --reload --port 8000

# Terminal 2 - Frontend
cd ui && npm run dev
```

---

## 6. Admin Panel

Access Admin Panel by clicking **"Admin Settings"** button in Nexus GUI.

### 6.1 RAG Ingestion

#### Ingestion Types

| Type                  | Purpose                     | When to Use                         |
| --------------------- | --------------------------- | ----------------------------------- |
| **Database Schema**   | Parse C# DbContext/Entities | Initial setup, after migrations     |
| **Component Library** | Parse React/TSX components  | When integrating design system      |
| **Project Codebase**  | Scan existing source code   | Before refactoring, incremental dev |

#### Configuration Parameters

| Parameter           | Default | Description                       |
| ------------------- | ------- | --------------------------------- |
| **Path**            | -       | Directory containing source files |
| **Collection Name** | auto    | Name for vector DB collection     |
| **Chunk Size**      | 800     | Characters per RAG document       |
| **Chunk Overlap**   | 120     | Overlap between chunks            |

#### Workflow

1. Select ingestion type
2. Browse and select path
3. Click **Validate** - review file counts and costs
4. Click **Ingest** - wait for completion
5. Verify in **Knowledge Explorer**

### 6.2 Model Configuration

#### Phase-Specific Models

| Phase       | Recommended Model | Reason                                        |
| ----------- | ----------------- | --------------------------------------------- |
| Analyst     | Claude 3.5 Sonnet | Best for requirements analysis                |
| Architect   | Consensus Mode    | Critical decisions need multiple perspectives |
| Implementer | GPT-4o            | Strong C# and .NET performance                |
| Tester      | GPT-4o-mini       | Cost-effective for test generation            |
| Reviewer    | Claude 3.5 Sonnet | Best code review capabilities                 |

#### Consensus Mode

For critical phases (like Architecture), enable Consensus Mode:

- Multiple models work independently
- Synthesis model combines best ideas
- Higher quality but ~3x token cost

### 6.3 Budget & Limits

| Setting           | Description             | Recommended |
| ----------------- | ----------------------- | ----------- |
| Max Input Tokens  | Context limit per call  | 6000-12000  |
| Max Output Tokens | Response limit          | 1000-4000   |
| Top-K Results     | RAG documents retrieved | 4-6         |
| Max Workers       | Parallel LLM calls      | 2-4         |

### 6.4 Knowledge Explorer (Enhanced)

The Knowledge Explorer has been upgraded with document-level management capabilities:

- **Browse Documents**: View a paginated list of all text chunks currently indexed in a collection.
- **Inspect Metadata**: See exactly what source file and line range each chunk originated from.
- **Delete Specific Documents**: Identify "dirty" or unnecessary documents and remove them without needing to reset the entire collection.

#### How to use:

1. Navigate to **"Knowledge Explorer"** in the Admin Panel.
2. Select a collection from the dropdown.
3. Click **"Browse Documents"** to view individual chunks.
4. Use the **"Delete"** icon next to a document to remove it permanently.

### 6.5 Auto-Chunking & Optimization (Phase 10)

The system now uses a `ChunkingEngine` that understands code structure.

#### Benefits:

- **Higher Accuracy**: Instead of splitting randomly, the AI keeps functions and classes together.
- **Lower Cost**: The **Optimization Advisor** warns you if you are indexing redundant files (like `.g.cs`) and suggests exclusion patterns.

#### Configuration in UI:

- **Strategic Mode**: Automatically enabled for supported file types (`.py`, `.cs`, `.ts`, etc.).
- **Validation Report**: Before ingestion, review the advisor's recommendations to save tokens.

---

## 7. Best Practices & Guidelines

### 7.1 What SHOULD Go Into RAG

| Content Type      | Example                         | Benefit                   |
| ----------------- | ------------------------------- | ------------------------- |
| Database Schema   | Entities, tables, relationships | AI understands data model |
| API Endpoints     | Controllers, routes             | AI knows existing APIs    |
| Component Library | DynButton, DynTable             | AI reuses your components |
| Existing Codebase | Services, repositories          | Context for refactoring   |
| Coding Standards  | Naming conventions              | Consistent style          |

### 7.2 What Should NOT Go Into RAG

| Content Type   | Reason              | Alternative           |
| -------------- | ------------------- | --------------------- |
| Credentials    | Security risk       | Use .env files        |
| API Keys       | Exposure risk       | Environment variables |
| Binary Files   | Cannot parse        | Link in docs          |
| Generated Code | Not source of truth | Ignore \*.g.cs, dist/ |
| node_modules   | Too much noise      | Auto-ignored          |
| Test Data      | May confuse AI      | Use only if relevant  |
| Log Files      | Unnecessary         | Never ingest          |

### 7.3 RAG Collection Naming

Use consistent naming convention:

```
{project_name}_{content_type}
```

Examples:

- `wiwa_database_schema`
- `wiwa_backend_codebase`
- `dynui_component_library`

### 7.4 Chunking Recommendations

| Project Size              | Chunk Size | Overlap |
| ------------------------- | ---------- | ------- |
| Small (<50 files)         | 1000       | 150     |
| Medium (50-200 files)     | 800        | 120     |
| Large (>200 files)        | 600        | 100     |
| Long classes (>500 lines) | 500        | 80      |

### 7.5 When to Re-Ingest

**Required:**

- After database migrations
- When adding new components
- After major refactoring

**Optional:**

- When AI doesn't recognize recent changes
- If retrieval returns outdated data

---

## 8. Lessons Learned System

### 8.1 Overview (Planned)

The Lessons Learned system will:

1. Track error patterns across sessions
2. Automatically detect repeated mistakes (after 2-3 occurrences)
3. Create prevention rules
4. Inject relevant lessons into future prompts

### 8.2 Common Errors & Prevention

| Error                 | Cause             | Prevention                         |
| --------------------- | ----------------- | ---------------------------------- |
| AI ignores components | Stale collection  | Re-ingest component library        |
| Wrong DB structure    | Outdated schema   | Refresh database_schema collection |
| Inconsistent style    | Missing standards | Add coding standards to RAG        |
| High costs            | Large context     | Reduce Top-K, optimize chunks      |
| Slow execution        | Too many workers  | Reduce Max Workers to 2            |

### 8.3 Guardrails (Planned)

Automatic protection mechanisms:

- **Circuit Breaker**: Stop after 3 repeated errors
- **Cost Guard**: Pause if task exceeds budget
- **Validation Guard**: Escalate if output fails schema

---

## 9. Advanced Features

### Domain-Aware Retrieval

The system understands code structure:

- **Entities**: Knows `Order` relates to `Customer`
- **Components**: Knows `SummaryCard` uses `Button` and `Icon`

### Producer-Reviewer Loop

Critical phases enable feedback loop where a second AI model reviews output, iterating until quality thresholds are met.

### Cost Tracking

Real-time tracking enabled by default. Check `outputs/cost_report.json` for breakdown.

### LLM Audit Log

Every LLM interaction logged to `outputs/audit_logs/llm_audit.jsonl`:

- Timestamp and duration
- Model and provider
- Full prompt and response
- Cost and token usage
- Error details (if any)

---

## 10. Code Verification

The orchestrator automatically verifies generated code by running tests.

### How It Works

```
Implementation → CodeExecutor → TestGenerator → Tests →
    ├── Pass → Continue to FileWriter
    └── Fail → Retry (max 3 attempts)
```

### Components

| Component            | File                                         | Purpose                    |
| -------------------- | -------------------------------------------- | -------------------------- |
| `CodeExecutor`       | `core/code_executor.py`                      | Executes Python/TS/C# code |
| `TestGeneratorAgent` | `agents/specialist_agents/test_generator.py` | Generates tests            |
| `VerificationLoop`   | `core/code_executor.py`                      | Retry logic with feedback  |

### Supported Languages

| Language   | Executor         | Test Framework |
| ---------- | ---------------- | -------------- |
| Python     | Direct execution | pytest         |
| TypeScript | ts-node          | Jest           |
| C#         | dotnet CLI       | xUnit          |

---

## 11. File Writing

After verification, generated code is written to your project.

### FileWriter Features

| Feature             | Description                       |
| ------------------- | --------------------------------- |
| **Diff Preview**    | See changes before writing        |
| **Backup**          | Automatic backup before overwrite |
| **Rollback**        | Restore from backup if tests fail |
| **Git Integration** | Optional branch/commit            |

### Usage

```python
from core.file_writer import FileWriter

writer = FileWriter(project_root="E:/Projects/MyApp")

# Preview changes
diff = writer.preview("src/utils.py", new_code)
print(diff.unified_diff)

# Write with backup
result = writer.write("src/utils.py", new_code)

# Rollback if needed
if not tests_pass:
    writer.rollback(result.backup_path, result.file_path)
```

### Write Modes

| Mode        | Description                      |
| ----------- | -------------------------------- |
| `CREATE`    | Create new file (fail if exists) |
| `OVERWRITE` | Replace entire file              |
| `APPEND`    | Add to end of file               |
| `PATCH`     | Apply specific changes           |

### Backups

Backups are stored in `.orchestrator/backups/` with format:

```
filename.20260209_210500.bak
```

---

## 12. VS Code Integration

The orchestrator works seamlessly with VS Code.

### Recommended Setup

1. **Open project in VS Code**

   ```bash
   code E:/Projects/MyApp
   ```

2. **Enable Auto-Save** (optional)
   - File → Preferences → Settings
   - Search "Auto Save" → Set to "afterDelay"

3. **Watch for changes**
   - VS Code automatically detects file changes
   - Modified files appear in Source Control

### Git Workflow

When FileWriter has Git integration enabled:

```
1. Create feature branch: orchestrator/feature-xyz
2. Write generated files
3. Create commit: "feat: Add loyalty points feature"
4. Ready for PR review
```

---

---

## 14. Lessons Learned System (Phase 3)

The system automatically learns from errors to prevent future mistakes.

### Components

| Component            | Function                                                     |
| -------------------- | ------------------------------------------------------------ |
| **Error Tracker**    | Logs every failure with context to `outputs/error_tracking/` |
| **Pattern Detector** | Finds recurring issues (e.g., "Missing Import" x3)           |
| **Best Practices**   | Injects prevention rules into prompts                        |

### Best Practices Configuration

Located in `config/best_practices.yaml`. You can add custom rules:

```yaml
languages:
  python:
    rules:
      - id: "docstring_required"
        description: "Public functions must have docstrings."
      - id: "type_hints"
        description: "Use type hints for function arguments."
```

### Automatic Error Analysis

When 3+ similar errors occur, the Pattern Detector generates a suggestion:

> **Pattern Detected:** `NameError: name 'X' is not defined`
> **Suggestion:** "Check if module X is imported."

This suggestion is automatically injected into future prompts to guide the AI.

---

---

## 15. Guardrails & Reliability (Phase 4)

Safety mechanisms prevent the AI from making dangerous or costly mistakes.

### Safety Checks

| Guardrail                  | Trigger                        | Action             |
| -------------------------- | ------------------------------ | ------------------ |
| **Circuit Breaker**        | Cost > $1.00 or Retries > 3    | 🛑 Abort Task      |
| **Hallucination Detector** | Importing non-existent package | 🚫 Block Execution |
| **Recursive Loop**         | Tasks generating same tasks    | 🛑 Stop Branch     |

### Configuration

You can adjust limits in `config/guardrails.yaml` (future) or via environment variables:

- `MAX_TASK_RETRIES=3`
- `MAX_TASK_COST=1.0`

---

## 16. Troubleshooting

### Common Issues

| Problem               | Solution                                             |
| --------------------- | ---------------------------------------------------- |
| "No documents found"  | Re-ingest RAG collection or check Knowledge Explorer |
| "Connection refused"  | Start backend on port 8000                           |
| "Cost limit exceeded" | Increase budget in Admin Panel                       |
| "Validation failed"   | Check Advisor report in ingestion tab                |
| "Slow response"       | Reduce Max Workers, check API rate limits            |
| "Verification failed" | Check test output in logs                            |
| "Write failed"        | Check file permissions and path                      |
| "Safety Violation"    | Fix imports or simplify task complexity              |

### Getting Help

1. Check `outputs/logs/` for detailed error messages
2. Review `outputs/error_tracking/error_history.jsonl` for full error history
3. Review `outputs/audit_logs/llm_audit.jsonl` for LLM issues
4. Check `.orchestrator/backups/` for file recovery
5. Open GitHub issue with reproduction steps

---

**Questions?** Contact: mgasic (GitHub: https://github.com/mgasic)

**Repository:** https://github.com/mgasic/ai-code-orchestrator

**License:** MIT
