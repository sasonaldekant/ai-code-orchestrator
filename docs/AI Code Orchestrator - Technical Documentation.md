# AI Code Orchestrator — Technical Documentation

**Version:** 4.0.0 (Bleeding Edge)
**Last updated:** 2026-02-10

---

## 1. Overview

The **AI Code Orchestrator v4.0** represents a paradigm shift from a "Stateless Executor" to a "Cognitive Learning Agent". It introduces a centralized **System Cortex** for dynamic tool discovery, persistent **Cognitive Memory** for learning from user preferences and past mistakes, and **Multi-Modal Capabilities** for vision-based tasks.

### Key Enhancements in v4.0

| Feature                     | Description                                                                                                                                              |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **System Cortex**           | A centralized `CapabilityRegistry` and `SemanticRouter` that dynamically maps user intent (text) to executable tools (functions) using LLM reasoning.    |
| **Cognitive Memory**        | **Episodic Memory** stores user preferences (`UserPreferences`). **Experience Memory** (`ExperienceDB`) stores successful bug fixes for self-correction. |
| **Autonomous Self-Healing** | The `RepairAgent` automatically investigates validation failures, generates fixes, and re-verifies them without user intervention.                       |
| **Multi-Modal Vision**      | The `VisionManager` allows the system to analyze images (screenshots, diagrams) and use them as context for coding tasks.                                |
| **IDE Bridge**              | A REST API (`/ide/*`) allowing external IDEs (VS Code, Cursor) to request context-aware actions like "Fix", "Explain", or "Refactor".                    |

---

## 2. Architecture

v4.0 introduces the "Cortex" layer above the Orchestrator.

```
┌──────────────────────────────────────────────────────────────┐
│                    IDE / CLI / Nexus GUI                     │
└───────────────┬──────────────────────────────┬───────────────┘
                │                              │
         ┌──────▼─────────┐             ┌──────▼─────────┐
         │   API Gateway  │             │   IDE Bridge   │
         └──────┬─────────┘             └──────┬─────────┘
                │                              │
         ┌──────▼──────────────────────────────▼─────────┐
         │                System Cortex                  │
         │           (Registry + Semantic Router)        │
         └──────┬──────────────────────┬─────────────────┘
                │                      │
      ┌─────────▼─────────┐    ┌───────▼─────────┐
      │   Cognitive Memory│    │  Orchestrator   │
      │  - User Prefs     │◄──►│  - Agents       │
      │  - Experience DB  │    │  - RAG          │
      └───────────────────┘    └─────────────────┘
```

### 2.1 The System Cortex (`core/registry.py`, `core/router.py`)

- **Registry:** A singleton that stores all available tools (`@register_tool`).
- **Router:** Uses an LLM to analyze a user request and select the best tool from the Registry.

### 2.2 Cognitive Memory

- **User Preferences:** Stored in `user_prefs.json`. Injected into the System Prompt of `LLMClientV2`.
- **Experience DB:** SQLite database (`experience.db`). Maps `error_pattern` -> `fix_strategy`. Used by `RepairAgent`.

---

## 3. New Components

### 3.1 Repair Agent (Auto-Fixer)

- **File:** `core/agents/specialist_agents/repair_agent.py`
- **Role:** Debugger and Patcher.
- **Workflow:**
  1. Receives error log.
  2. Queries `ExperienceDB` for similar past errors.
  3. Uses `RetrievalAgent` to investigate code.
  4. Generates a fix plan.
  5. Applies fix and re-runs verification.

### 3.2 Vision Manager

- **File:** `core/vision_manager.py`
- **Role:** Image Analysis.
- **Model:** GPT-4o / Gemini 1.5 Pro.
- **Input:** URL or Base64 Data URI.

### 3.3 IDE Bridge

- **File:** `api/ide_routes.py`
- **Endpoints:**
  - `POST /ide/context_action`: Executes actions like `FIX`, `EXPLAIN`.

---

## 4. References

- [User Guide v4.0](USER_GUIDE_v4.md)
- [IDE Integration Guide](IDE_INTEGRATION_GUIDE.md)
