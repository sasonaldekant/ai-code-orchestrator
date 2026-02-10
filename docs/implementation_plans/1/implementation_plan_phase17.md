# Implementation Plan - Phase 17: Cognitive Memory & System Cortex

## Goal

Transform the Orchestrator from a "Stateless Executor" to a "Learner" with a unified Tool Registry ("The Cortex") and Persistent Memory.

## 1. API Registry ("The Cortex")

**Goal:** Centralized definition of all system capabilities to enable dynamic tool selection.

### 1.1 `core/registry.py`

- **Pattern:** Singleton Registry with Decorators.
- **Features:**
  - `@register_tool(name, description, input_schema)`
  - `Registry.get_tools()` -> List of JSON schemas (for LLM).
  - `Registry.get_tool(name)` -> Callable.

### 1.2 `core/router.py`

- **Logic:** Semantic Intent Router.
- **Workflow:**
  1. Receive User Request ("Fix the bug in the currently selected file").
  2. Query `Registry` for available tools.
  3. LLM decides: "Call `ide_fix_selection`".
  4. Router invokes the tool.

## 2. Episodic Memory (User Preferences)

**Goal:** Remember user rules across sessions.

### 2.1 `core/memory/user_prefs.py`

- **Storage:** `chromadb` (collection: `user_prefs`) or simple JSON if rules are few.
- **Schema:** `{ "rule": "Always use Tailwind", "category": "frontend", "timestamp": "..." }`
- **Integration:** Inject relevant rules into `LLMClientV2` system prompt.

## 3. Experience Database (Self-Correction)

**Goal:** Avoid repeating mistakes.

### 3.1 `core/memory/experience_db.py`

- **Storage:** SQLite (`metrics.db` table: `experiences`).
- **Schema:**
  - `id`: PK
  - `error_pattern`: textual description or embedding.
  - `fix_strategy`: what worked.
  - `context_hash`: unique ID of the error context.

## 4. Execution Steps

### Step 1: The Cortex (Registry)

1. Create `core/registry.py`.
2. Refactor `VisionManager`, `RepairAgent`, `RetrievalAgent` to use `@register_tool`.
3. Create `core/router.py`.

### Step 2: Memory

1. Create `core/memory/user_prefs.py`.
2. Update `LLMClientV2` to load prefs.

### Step 3: Experience

1. Create `core/memory/experience_db.py`.
2. Hook `RepairAgent` to save/load experiences.
