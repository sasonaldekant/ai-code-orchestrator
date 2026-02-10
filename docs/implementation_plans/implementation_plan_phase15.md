# Implementation Plan - Phase 15: Agentic Retrieval ("The Investigator")

## Goal

Implement a "Retrieval Agent" that can actively explore the codebase using tools, rather than relying on a single-shot vector search. This enables multi-hop reasoning (e.g., "Find usage of X, then see how Y uses it").

## User Review Required

> [!IMPORTANT]
> This phase introduces an autonomous loop that can read files. While read-only, it may consume more tokens per query than standard RAG.

## Proposed Changes

### 1. Core Logic (`core/agents/specialist_agents/retrieval_agent.py`)

- **New Class**: `RetrievalAgent`
- **Dependencies**: `LangChain` (or custom ReAct loop), `FileSystem` access.
- **Tools**:
  - `search_code(query: str, path: str = ".")`: Uses `grep` or `find` to locate code.
  - `read_file(path: str, start_line: int, end_line: int)`: Reads file content.
  - `list_dir(path: str)`: Lists files for exploration.
  - `get_definition(symbol: str)`: Uses the Graph (from Phase 12) to find definitions.

### 2. Strategy Selection & Cost Estimation (New)

- **Logic**: Before running the agent, the Orchestrator runs `detect_task_complexity`.
- **UI Interaction**:
  - If `complexity > High`: Show "Strategy Selection" Modal.
  - **Option A (Local)**: Run `RetrievalAgent` loop. (Estimated Cost: $$)
  - **Option B (External)**: Generate "Investigation Prompt" for ChatGPT/Perplexity. (Estimated Cost: $0 - User Subscription)
  - **Option C (Hybrid)**: Agent runs but asks External Pro for "Search Strategy" first.

### 3. Integration (`core/orchestrator.py`)

- **Modification**: Update `run_phase` (specifically for 'analyst') to accept a `deep_search=True` flag.
- **Logic**:
  - If `deep_search` is enabled, check complexity.
  - If complex, prompt user for strategy (via UI event or default config).
  - Execute chosen strategy.
  - Append findings to `rag_context`.

### 4. UI Updates (`ui/src/components/OrchestratorUI.tsx`)

- **New Toggle**: "Deep Search (Agentic)" in the Chat input area.
- **Feedback**: Show a "Investigating..." spinner distinct from normal "Thinking...".
- **Modal**: Strategy Selection Modal when complexity is high.

## Verification Plan

### Automated Tests

- `pytest tests/agents/test_retrieval_agent.py`
  - Test tool execution (mocked filesystem).
  - Test reasoning loop (mocked LLM).

### Manual Verification

- Ask a complex questions: "How does the `CostManager` handle token pricing for different models?"
- Verify the agent searches, reads `cost_manager.py`, and formulates an answer.
