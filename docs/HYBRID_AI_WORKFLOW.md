# Hybrid AI Workflow: Orchestrator + Pro Tools 🤝

This document defines the strategy for leveraging external "Pro" AI tools (ChatGPT Plus/o1, Perplexity Pro, Antigravity Pro) alongside the AI Code Orchestrator to maximize efficiency and minimize token costs.

## 🎯 Philosophy: "Delegate & Ingest"

The Orchestrator is the **Context Manager** and **Executor**. The Pro Tools are the **Heavy Lifters** and **Researchers**.

1.  **Orchestrator**: Knows the codebase, gathers context, executes code.
2.  **Pro Tools**: Solve complex reasoning problems, generate massive content, or research up-to-date info.
3.  **Loop**: The Orchestrator prepares the "package" for the Pro Tool, and ingests the "result" back into its brain.

---

## 🛠️ When to Delegate?

| Scenario                        | Tool                             | Why?                                                                             |
| :------------------------------ | :------------------------------- | :------------------------------------------------------------------------------- |
| **Complex Architecture Design** | **ChatGPT o1 / Antigravity Pro** | Requires deep reasoning and "thinking" time that smaller models lack.            |
| **Unknown Error / New Lib**     | **Perplexity Pro**               | Requires live web search to find recent GitHub issues or documentation.          |
| **Massive Refactoring**         | **ChatGPT Plus (Canvas)**        | large context window and interactive editing are superior for 500+ line changes. |
| **Security Audit**              | **Antigravity Pro / GPT-4**      | Specialized reasoning to find subtle vulnerabilities.                            |
| **Documentation (Full Site)**   | **ChatGPT Plus**                 | Can generate 10 pages of markdown in one go, saving local tokens.                |

---

## 🔄 The Workflow

### Step 1: Context Gathering (Orchestrator)

The Orchestrator uses RAG and Knowledge Graph to find all relevant files for the problem.

- _Action:_ User clicks **"Generate Prompt for Pro AI"**.
- _Output:_ A highly structured prompt containing:
  - **Role**: "You are a Senior Architect..."
  - **Task**: "Refactor class X to allow Y..."
  - **Context**: Complete content of `file_a.py`, `file_b.py`, and graph relationships.
  - **Constraint**: "Output specifically in format Z..."

### Step 2: Execution (External Tool)

User pastes the prompt into ChatGPT/Perplexity.

- _Action:_ User interacts with the Pro Tool to refine the solution.

### Step 3: Ingestion (Orchestrator)

User takes the final code/answer and feeds it back.

- _Action:_ User clicks **"Ingest External Response"** or pastes into a specific "Apply Patch" window.
- _Result:_ The orchestrator saves this into `knowledge_base` (VectorDB) or applies the code changes directly.

---

## 🤖 Prompt Engineering Strategy

The Orchestrator generates prompts optimized for specific models using the **Pro Prompt Gen** tab in the Admin Panel:

### For ChatGPT o1 (Reasoning)

```markdown
<context_dump>
[File: main.py] ...
[File: utils.py] ...
</context_dump>

<objective>
Analyze the race condition in `main.py`.
Think step-by-step.
Output the fixed code block suitable for copy-pasting.
</objective>
```

### For Perplexity (Research)

```
SEARCH QUERY: "Python generated generic repository pattern with SQLAlchemy 2.0 async"
CONTEXT: We are using FastApi and SQLModel.
TASK: Find the best practice for implementing X.
```

---

## 🚀 Implementation Status (Completed in Phase 14)

1.  **Pro Prompt Generator**: Available in the "Prompt Gen" tab of the Admin Panel.
    - Generates context-rich prompts for o1/DeepSeek.
2.  **External Knowledge Ingestion**: Available in the "Ingest Response" tab.
    - Parses and saves answers from external AIs into the Vector Database.
