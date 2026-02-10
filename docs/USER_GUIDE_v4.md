# AI Code Orchestrator v4.0 - User Guide

This guide provides instructions on how to use the AI Code Orchestrator v4.0 (Bleeding Edge). This major release introduces **Autonomous Self-Healing**, **Multi-Modal Vision**, **IDE Integration**, and **Cognitive Memory** ("The Cortex").

## Table of Contents

1. [Installation](#1-installation)
2. [Configuration](#2-configuration)
3. [Running the Orchestrator](#3-running-the-orchestrator)
4. [Nexus GUI](#4-nexus-gui)
5. [Autonomous Self-Healing (Auto-Fixer)](#5-autonomous-self-healing-auto-fixer)
6. [Vision Capabilities](#6-vision-capabilities)
7. [IDE Bridge API](#7-ide-bridge-api)
8. [Cognitive Memory (The Cortex)](#8-cognitive-memory-the-cortex)
9. [Swarm Intelligence (Multi-Agent)](#9-swarm-intelligence-multi-agent)
10. [Advanced Features](#10-advanced-features)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Installation

### Prerequisites

- Python 3.10+
- Node.js 18+ (for GUI)
- API Keys for OpenAI, Anthropic, Google Gemini, or **Perplexity** (for Deep Research).

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

   _Note: v4.0 requires `pillow` for image processing and `chromadb` for memory._

3. Set up environment variables in `.env`:

   ```bash
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   GOOGLE_API_KEY=...
   PERPLEXITY_API_KEY=pplx-...
   ```

4. Start the system:

   ```bash
   # Terminal 1: Backend
   python manage.py start-api

   # Terminal 2: Frontend (Nexus GUI)
   cd ui && npm run dev
   ```

---

## 2. Configuration

### Domain Configuration (`config/domain_config.yaml`)

Define your specific domain knowledge sources here (Database, Component Library, etc.).

### Cost Management

Set budgets in `config/limits.yaml`. Default per-task budget is $0.50.

---

## 3. Running the Orchestrator

### Using Nexus GUI (Recommended)

1. Start the GUI: `http://localhost:5173`
2. Enter your request in the chat input.
3. Toggle "Auto-Fix" if you want autonomous debugging.
4. Click **"Execute"**.

### Using CLI

```bash
python manage.py run "Refactor the authentication middleware." --auto-fix
```

---

## 4. Nexus GUI

The Nexus GUI has been updated with:

- **Vision Upload**: Drag & Drop images for analysis.
- **Auto-Fix Toggle**: Enable/Disable self-healing.
- **Deep Search Toggle**: Switch between fast embedding search and agentic investigation.
- **Hybrid Delegation**: Dynamically routes complex tasks to specialized external reasoning models (o1/DeepSeek).
- **Delegate to Pro AI**: Generate optimized prompts for external reasoning models (o1/DeepSeek).
- **Thought Stream**: Visualizes `RepairAgent` and `VisionManager` actions.

---

## 5. Autonomous Self-Healing (Auto-Fixer)

**Feature:** The Orchestrator can now detect and fix bugs automatically during the Verification phase.

- **How it works:**
  1. Orchestrator generates code.
  2. Verification verifies code (tests).
  3. If verification fails and **Auto-Fix** is ON:
     - The `RepairAgent` analyzes the error log.
     - It investigates the codebase to understand the root cause.
     - It applies a fix (modifies the file).
     - It re-runs verification.

- **Usage:** Toggle the "Wrench" icon in the UI or pass `--auto-fix` in CLI.

---

## 6. Vision Capabilities

**Feature:** The Orchestrator can now "see" images.

- **Use Cases:**
  - "Make the UI look like this screenshot."
  - "Explain this architecture diagram."
  - "Debug this error screenshot."

- **Usage:**
  - **GUI:** Click the "Image" icon to upload a file or paste an image URL.
  - **API:** Use the `/vision/analyze` endpoint.

---

## 7. IDE Bridge API

**Feature:** Connect your IDE (VS Code, Cursor, JetBrains) directly to the Orchestrator.

The Orchestrator exposes endpoints for context-aware actions:

- `POST /ide/context_action`: Perform actions on selected code.
  - Actions: `EXPLAIN`, `FIX`, `REFACTOR`, `DOCSTRING`, `TEST`.

**Integration Guide:** See [docs/IDE_INTEGRATION_GUIDE.md](IDE_INTEGRATION_GUIDE.md) for details on building extensions.

---

## 8. Cognitive Memory (The Cortex)

**Feature:** The system learns from you and improves over time.

### 8.1 API Registry ("The Cortex")

The system uses a semantic router to dynamically select the right tool (`auto_fix`, `analyze_image`, `deep_search`) based on your intent.

### 8.2 User Preferences (Episodic Memory)

The system remembers your coding style and rules.

- **Example:** "Always use functional components."
- **Storage:** `core/memory/user_prefs.py`
- **Effect:** Rules are injected into every prompt.

### 8.3 Self-Correction (Experience DB)

The system remembers how it fixed bugs in the past.

- **Logic:** Before fixing a bug, the `RepairAgent` checks the **Experience Database** (`experience.db`) for similar past errors and successful fixes.

---

## 9. Swarm Intelligence (Multi-Agent)

**Feature:** Run complex requests through a coordinated "swarm" of agents that work in parallel.

- **How it works:**
  1. The **Swarm Manager** reads your request and breaks it into independent sub-tasks.
  2. Tasks are assigned to the most capable specialists (Analyst, Architect, C# Specialist, etc.).
  3. Specialized nodes execute **concurrently** via the `Blackboard` memory system.
  4. The manager synthesizes the final result.

- **Usage:**
  - **GUI:** Toggle the "Swarm" icon (Beta) in the Nexus control bar.
  - **CLI:**
    ```bash
    python manage.py run "Build a multi-tenant auth system with SQLite" --mode swarm
    ```

---

- **Perplexity Deep Research**: Integrated via API for the `code_research` specialty. It provides up-to-date information on libraries, security patches, and community best practices by searching the live web.
- **RAG Ingestion**: Ingest knowledge using `python manage.py ingest`.
- **Domain-Aware Retrieval**: Context-aware context building.
- **Producer-Reviewer Loop**: Automated code review.
- **Cost Tracking**: Real-time budget monitoring.

---

## 10. Troubleshooting

- **Logs:** Check `outputs/logs/` and `outputs/audit_logs/`.
- **Experience DB:** If fixes are stale, you can delete `experience.db` to reset self-correction memory.
- **Preferences:** Reset preferences by deleting `user_prefs.json`.
