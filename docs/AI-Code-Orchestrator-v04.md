# AI Code Orchestrator v4.0 --- Functional Specification

**Version:** 4.0.0 (Bleeding Edge)
**Last updated:** 2026-02-10
**Evolution:** From "Domain-Agnostic Framework" to **"Cognitive Learning Agent"**

---

## 1. Executive Summary

The **AI Code Orchestrator v4.0** represents the pinnacle of local, autonomous software development. It builds upon the **domain-agnostic** foundation of v3.0—which solved the problem of understanding heterogeneous codebases via Advanced RAG—and elevates the system to a **Cognitive Agent** capable of perception, memory, and self-correction.

### Core Philosophy: "The Cognitive Loop"

Unlike v3.0, which was a linear executor, v4.0 operates in a continuous cognitive loop:
**Perceive (Vision/IDE) → Route (Cortex) → Remember (Memory) → Execute (Agents/Swarm) → Learn (Experience DB)**

### Key Enhancements in v4.0

## ,ReplacementChunks:[{AllowMultiple:false,EndLine:27,ReplacementContent:

## 2. Architecture Overview

The architecture has evolved to include the **Cortex Layer** which mediates all interaction between inputs (User/IDE) and execution (Agents).

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       Inputs (CLI, GUI, IDE Bridge)                     │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                          ┌───────▼───────┐
                          │ System Cortex │ ◀── NEW: Semantic Router & Registry
                          └───────┬───────┘
                                  │
          ┌───────────────────────┼────────────────────────┐
          │                       │                        │
     ┌────▼────┐             ┌────▼────┐              ┌────▼────┐
     │Cognitive│ ◀── NEW     │ Orchest-│              │  RAG    │
     │ Memory  │             │  rator  │              │ System  │
     └────┬────┘             └────┬────┘              └────┬────┘
          │                       │                        │
     ┌────▼────┐             ┌────▼────┐              ┌────▼────┐
     │User Pref│             │ Agents  │              │ Domain  │
     │Exp DB   │             │(Fix,Vis)│              │Knowledge│
     └─────────┘             └─────────┘              └─────────┘
```

---

## 3. The System Cortex & Memory

### 3.1 The Cortex (Registry & Router)

The Cortex is the decision-making layer.

- **Capability Registry**: A live catalog of all available "Tools" (functions decorated with `@register_tool`).
- **Semantic Router**: An LLM-based decision engine that analyzes user prompts + active context to select the precise tool for the job.

#### Tool Registry Schema

Tools are registered with semantic metadata to aid the Router.

```python
@register_tool(
    name="auto_fix",
    category="debugging",
    description="Investigates validation errors and applies patches to code."
)
async def auto_fix(error_log: str, ...): ...
```

### 3.2 Cognitive Memory Systems

#### A. Episodic Memory (User Preferences)

Persists stylistic rules across sessions.

- **Problem:** In v3, the AI "forgot" your style preferences between sessions.
- **Solution:** v4 persists preferences and injects them into the **System Prompt** of every agent.
- **Storage:** `user_prefs.json`
- **Example:** "Always use Python 3.9 type hinting."

#### B. Experience Memory (Self-Correction)

Persists successful bug fixes.

- **Problem:** The AI repeated the same mistakes.
- **Solution:** The **Experience DB** stores successful fix patterns.
- **Storage:** `experience.db` (SQLite)
- **Schema:** `Error Pattern` -> `Fix Strategy`

---

## 4. Domain Configuration (Enhanced)

v4.0 allows configuration of both the **Domain Knowledge** (what the AI knows) and the **Cognitive System** (how the AI thinks).

### 4.1 Configuration Structure

```yaml
domain:
  name: "wiwa-insurance-system"
  description: "Property and risk insurance management platform"

# --- Knowledge Sources (v3 Standard) ---
knowledge_sources:
  - type: "database"
    source_format: "sql_ddl"
    path: "./data/WIWA_DB.sql"
    bounded_contexts:
      policies: ["Concerns", "ConcernRisks"]

  - type: "existing_codebase"
    source_format: "dotnet_solution"
    path: "./backend"
    analysis_depth: "deep"
    focus_areas:
      - "api_endpoints"
      - "data_models"
      - "business_logic"

  - type: "component_library"
    source_format: "react_tsx"
    path: "./frontend/components"
    component_groups:
      basic: ["DynButton", "DynInput"]
      layout: ["DynGrid", "DynFlex"]

# --- System Settings (v4 New) ---
system:
  # Cognitive Memory Settings
  memory:
    episodic:
      enabled: true
      storage_path: "user_prefs.json"
    experience:
      enabled: true
      db_path: "experience.db"

  # Autonomous Behavior
  autonomy:
    auto_fix_enabled: true
    max_repair_retries: 3

  # Perception
  vision:
    model: "gpt-4o"
    max_resolution: "high"
```

---

## 5. Domain Knowledge Ingestion

v4.0 relies on the robust ingestion pipeline established in v3.0 to ground its cognition in reality.

### 5.1 Database Schema Ingestion

**Goal:** Teach the AI the data model.
**Process:** Parse SQL DDL -> Extract Tables/FKs -> Vectorize.

**Output Document Example:**

```json
{
  "id": "table_concerns",
  "type": "database_table",
  "content": "Table: Concerns\nPK: ConcernID (int)\nColumns: InsuredSum (decimal), CurrencyID (smallint FK)...",
  "metadata": {
    "table_name": "Concerns",
    "bounded_context": "policies",
    "relationships": ["ConcernRisks", "ConcernMarks"]
  }
}
```

### 5.2 Codebase Ingestion (.NET / Python / TS)

**Goal:** Teach the AI existing patterns.
**Process:** AST Parsing -> Logic-Aware Chunking.

**Output Document Example:**

```json
{
  "id": "endpoint_questionnaires_get",
  "type": "api_endpoint",
  "content": "GET /api/questionnaires/{id}\nController: QuestionnairesController\nService: IQuestionnaireService",
  "metadata": {
    "file": "Controllers/QuestionnairesController.cs",
    "endpoint_route": "GET /api/questionnaires/{id}",
    "return_type": "ActionResult<QuestionnaireDto>"
  }
}
```

### 5.3 Component Library Ingestion

**Goal:** Enable UI component reuse.
**Process:** TypeScript AST -> Prop Extraction.

**Output Document Example:**

```json
{
  "id": "component_dyn_table",
  "type": "ui_component",
  "content": "Component: DynTable\nProps: columns (ColumnDef[]), data (T[]), pagination (boolean)",
  "metadata": {
    "component_name": "DynTable",
    "category": "data",
    "props": ["columns", "data", "pagination"]
  }
}
```

---

## 6. Multi-Collection RAG Strategy

The Cortex uses a **Domain-Aware Retriever** to pull context from the right memory banks.

### 6.1 Collection Architecture and Strategy

The retrieval logic dynamically selects collections based on the active intent.

```python
class DomainAwareRetriever:
    def retrieve(self, query: str, context_type: str):
        if context_type == "full_stack_feature":
            return {
                "backend": self.query("existing_backend", query, n=3),
                "frontend": self.query("existing_frontend", query, n=3),
                "database": self.query("database_schema", query, n=5),
                "components": self.query("component_library", query, n=2)
            }
        elif context_type == "bug_fix":
             # New in v4: Check Experience DB first
            return {
                "experience": self.query("experience_db", query, n=1),
                "codebase": self.query("existing_backend", query, n=5)
            }
```

### 6.2 Context Formatting (JSON)

Token-optimized JSON format is used to feed the LLM.

```json
{
  "context_type": "incremental",
  "query": "Add export to Excel",
  "existing_backend": [
    {
      "route": "GET /api/questionnaires",
      "file": "QuestionnairesController.cs"
    }
  ],
  "existing_frontend": [{ "name": "QuestionnaireList", "uses": "DynTable" }],
  "database_tables": [
    { "table": "Questionnaires", "columns": ["ID", "Title", "CreatedAt"] }
  ],
  "reusable_components": [
    { "name": "DynExportButton", "props": ["data", "filename", "format"] }
  ]
}
```

---

## 7. Autonomous Workflows

v4.0 supports three primary autonomous loops: Auto-Healing, Incremental Development, and Visual Implementation.

### 7.1 The Self-Healing Loop (Auto-Fixer)

**Goal:** Fix bugs without human intervention.

1.  **Orchestrator** generates code.
2.  **Verification** runs tests -> **FAIL**.
3.  **Repair Agent** activates:
    - Reads error log.
    - Queries **Experience Memory** for past fixes.
    - Investigates code via **Retrieval Agent**.
    - Generates and applies patch.
4.  **Verification** re-runs -> **PASS**.
5.  **Experience Memory** records the successful fix.

### 7.2 The Visual Implementation Loop (New in v4)

**Goal:** Convert design to code.

1.  **User** uploads UI screenshot.
2.  **Vision Manager** analyzes image -> Generates distinct visual spec JSON.
3.  **Frontend Agent** retrieves `component_library`.
4.  **Frontend Agent** implements code matching the spec using existing components, strictly adhering to the visual constraints.

### 7.3 The Incremental Development Loop (v3 Enhanced)

**Goal:** Safely modify existing systems.

**Request:** "Add two-factor authentication to login flow"

**Step 1: Analysis (Analyst Agent)**

```json
{
  "affected_backend_files": [
    "Controllers/AuthController.cs",
    "Services/AuthService.cs"
  ],
  "db_changes": {
    "alter_table": "Users",
    "add_column": "TwoFactorEnabled bit, TwoFactorSecret nvarchar(255)"
  },
  "new_dependencies": ["OtpNet (NuGet)"]
}
```

**Step 2: Implementation (Developer Agent)**

```json
{
  "file_changes": [
    { "file": "Controllers/AuthController.cs", "change_type": "modify" },
    { "file": "Services/AuthService.cs", "change_type": "modify" },
    { "file": "Services/TwoFactorService.cs", "change_type": "create" }
  ]
}
```

**Step 3: Frontend Implementation (Frontend Agent)**

```json
{
  "file_changes": [
    { "file": "src/pages/Login.tsx", "change_type": "modify" },
    { "file": "src/components/TwoFactorModal.tsx", "change_type": "create" }
  ]
}
```

---

## 8. Usage Examples

v4.0 extends the CLI allows for both standard and autonomous operation modes.

### 8.1 Setup Domain

```bash
# Ingest knowledge sources defined in yaml
python -m domain_knowledge.cli ingest --config my-project/domain_config.yaml
```

### 8.2 Standard Execution (Greenfield)

```bash
python -m core.orchestrator \
  --mode greenfield \
  --domain-config my-project/domain_config.yaml \
  --request "Create REST API for products" \
  --bounded-context products
```

### 8.3 Autonomous Execution (Auto-Fix enabled)

```bash
python -m core.orchestrator \
  --mode incremental \
  --domain-config my-project/domain_config.yaml \
  --request "Refactor the Auth middleware" \
  --auto-fix  # Enables RepairAgent loop
```

### 8.4 Visual Task

```bash
python -m core.orchestrator \
  --mode incremental \
  --image ./mockups/dashboard_v2.png \
  --request "Update the Dashboard Layout to match this mockup"
```

---

## 9. IDE Bridge API

The **IDE Bridge** allows external tools to tap into the Cortex.

### 9.1 API Contract

**Base URL:** `http://localhost:8000/ide`

| Endpoint          | Method | Action                                                       |
| ----------------- | ------ | ------------------------------------------------------------ |
| `/context_action` | POST   | Execute generic action on selection (FIX, EXPLAIN, REFACTOR) |

### 9.2 Integration Example (VS Code Extension)

```typescript
// VS Code Extension Logic
vscode.commands.registerCommand("ai.fixThis", async () => {
  const selection = editor.selection;
  const response = await fetch("http://localhost:8000/ide/context_action", {
    method: "POST",
    body: JSON.stringify({
      action: "FIX",
      selection: selection.text,
      file_path: editor.document.fileName,
    }),
  });
  applyEdit(response.patch);
});
```

---

## 10. Comprehensive Comparison

| Feature                | v3.0 (Legacy) | v4.0 (Cognitive)             | Feature Gain                            |
| ---------------------- | ------------- | ---------------------------- | --------------------------------------- |
| **Context Routing**    | Static Rules  | **Semantic Router (LLM)**    | Dynamic, intent-based tool selection    |
| **Memory**             | Stateless     | **Episodic + Experience**    | Learn from preferences & mistakes       |
| **Error Handling**     | Retry Loop    | **Autonomous Repair**        | Intelligent investigation & patching    |
| **Input Modality**     | Text Only     | **Text + Vision**            | "See" designs and bugs                  |
| **Code Understanding** | RAG (Basic)   | **RAG (Strategic)**          | AST-aware chunking & retrieval          |
| **Integration**        | CLI / Web GUI | **CLI / GUI / IDE Bridge**   | Deep workflow integration               |
| **Domain Config**      | YAML          | **YAML + System Prefs**      | Enhanced configurability                |
| **Swarm Intelligence** | N/A           | **Multi-Agent Coordination** | Parallel task decomposition & execution |

---

## 11. Troubleshooting & Patterns

Common scenarios encountered when running v4.0.

### 11.1 Auto-Fix Loops

**Symptom:** The `RepairAgent` enters an infinite loop trying to fix the same error.
**Cause:** The error message is ambiguous, or the test case is flawed.
**Resolution:**

1.  Check `max_repair_retries` in `config.yaml` (default: 3).
2.  Inspect `experience.db` for incorrect fix patterns using the admin CLI: `python -m core.cli memory inspect`.
3.  Manually correct the test case.

### 11.2 Vision Hallucinations

**Symptom:** The Vision Manager invents non-existent CSS classes.
**Cause:** The model (e.g., GPT-4o) defaults to standard Tailwind, but the project uses a custom config.
**Resolution:**

- Ensure `tailwind.config.js` is part of the ingested context.
- Add a "Project Style Guide" to the `knowledge_sources` to ground the vision model.

---

## 12. Migration Guide (v3.0 -> v4.0)

Steps to upgrade an existing v3 project to v4.

### 12.1 Configuration

1.  **Backup:** specific `domain_config.yaml`.
2.  **Update:** Add the `system:` block (see Section 4.1).
3.  **Drivers:** Ensure you have the new `vision_model` keys in `.env`.

### 12.2 Database

1.  **Initialize Memory:** Run `python -m core.memory.init_db` to create `experience.db` and `user_prefs.json`.
2.  **Re-Ingest:** Run `python -m domain_knowledge.cli ingest` to refresh the vector store with v4-compatible metadata.

### 12.3 Custom Agents

If you wrote custom agents in v3:

1.  **Decorate:** Add `@register_tool` to your agent's `run` method so the Cortex can find it.
2.  **Inherit:** Update class to inherit from `BaseAgentV4` to get automatic memory injection.

---

## 13. File Structure

```
ai-code-orchestrator/
├── core/
│   ├── registry.py          # Cortex: Tool Registry (NEW)
│   ├── router.py            # Cortex: Semantic Router (NEW)
│   ├── memory/              # Memory Systems (NEW)
│   │   ├── user_prefs.py    # Episodic
│   │   └── experience_db.py # Experience
│   ├── vision_manager.py    # Perception (NEW)
│   └── orchestrator.py      # Execution Engine
├── agents/
│   └── specialist_agents/
│       ├── repair_agent.py  # Auto-Healer (NEW)
│       └── retrieval_agent.py
├── domain_knowledge/        # Ingestion Engine
├── rag/                     # Vector Store
├── api/
│   └── ide_routes.py        # IDE Bridge (NEW)
└── content/                 # Knowledge Sources
```

---

## 14. Implementation Roadmap (Completed)

### 14.1 Phase 14: External AI Delegation

- [x] Hybrid Delegation Strategy
- [x] Proactive Advisor (`detect_task_complexity`)

### 14.2 Phase 15: Agentic Retrieval

- [x] `RetrievalAgent` (Deep Search)
- [x] Hybrid ReAct Loop

### 14.3 Phase 16: Autonomous Evolution

- [x] Auto-Fixer Loop (`RepairAgent`)
- [x] Multi-Modal Vision (`VisionManager`)
- [x] IDE Bridge API

### 14.4 Phase 17: Cognitive Systems

- [x] System Cortex (Registry/Router)
- [x] Episodic Memory (User Preferences)
- [x] Experience Database (Self-Correction)

### 14.5 Phase 18: Swarm Intelligence

- [x] `SwarmManagerAgent` (Task Decomposition)
- [x] Parallel Execution Engine (`asyncio` nodes)
- [x] `Blackboard` (Shared State Memory)

---

## 15. Conclusion & Next Steps

v4.0 is not just an update; it is a transformation. By adding **Sight**, **Memory**, **Autonomy**, and **Swarm Collaboration**, the AI Code Orchestrator has evolved from a sophisticated calculator into a true **Distributed Engineering Team** peer.

**Next Steps:**

1.  **Swarm GUI:** Add a visual DAG of agent activity to the Nexus Admin Panel.
2.  **IDE Plugins:** Build native VS Code / JetBrains extensions consuming the Bridge API.
3.  **Reasoning scaling:** Dynamically scale model power based on swarm-detected complexity.

## 16. Phase 20: MCP Server Integration (In Progress)

### Goal

Integrate the **Model Context Protocol (MCP)** to allow external AI tools (Claude Desktop, Cursor, Zed) to natively drive the Orchestrator.

### Features

- **Native Tool Exposition**: `run_swarm_task`, `deep_search`, and `auto_fix` available as MCP Tools.
- **Resource Access**: Read-only access to the Swarm DAG and Audit Logs.
- **Stdio Transport**: Efficient, secure local communication with desktop apps.

This phase effectively turns the AI Code Orchestrator into a "Super Plugin" for any MCP-compliant IDE.
