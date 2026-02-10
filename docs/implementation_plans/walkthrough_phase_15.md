# Phase 15: Agentic Retrieval ("The Investigator") Walkthrough

## Overview

Phase 15 introduced "The Investigator," an autonomous agent capable of actively exploring the codebase to answer complex queries. This moves the system beyond passive RAG (Retrieval-Augmented Generation) to active, multi-hop reasoning. We also implemented a "Hybrid Strategy" to leverage external Pro models (like ChatGPT o1) for high-level planning while keeping execution local and cost-effective.

## Features Implemented

### 1. Retrieval Agent ("The Investigator")

- **Active Exploration**: Can search code, read files, and list directories autonomously.
- **ReAct Loop**: Uses a detailed Thought-Action-Observation loop to navigate the codebase.
- **Tools**:
  - `search_code(query)`: Greps the codebase.
  - `read_file(path)`: Reads file content.
  - `list_dir(path)`: Explores directory structure.

### 2. Hybrid Delegation Strategy

- **Concept**: Use an external "Pro" model (e.g., ChatGPT via API) to generate a high-quality investigation _plan_, then execute that plan using the local Investigator agent.
- **Benefit**: Combines the reasoning power of SOTA models with the low latency and zero-data-exfiltration of local execution.
- **Implementation**:
  - `ExternalIntegration.generate_search_plan`: Generates a step-by-step plan from a user query.
  - `RetrievalAgent.run(initial_plan=...)`: Accepts this plan to guide its actions.

### 3. Orchestrator Integration

- **Deep Search Toggle**: Added `deep_search` parameter to `OrchestratorV2` and `LifecycleOrchestrator`.
- **Strategy Selector**: Supports `local` (pure local agent), `hybrid` (external plan + local agent), and `external` (full delegation - placeholder for future).
- **Execution Flow**:
  1. User requests a feature.
  2. If `Deep Search` is ON:
     - (Hybrid) Fetch plan from External AI.
     - `RetrievalAgent` executes investigation.
     - Findings are added to RAG Context.
  3. Standard phases (Analyst, Architect, IMPL) proceed with deeper context.

### 4. UI Updates

- **Toolbar**: Added "Deep Search" toggle and "Strategy" options (Local/Hybrid/Pro) to the Chat Interface.

## Verification

We verified the implementation using a custom regression script `tests/verify_phase15.py`.

### Verification Steps

1. **Agent Logic**: Validated that `RetrievalAgent` can use tools and return findings.
2. **Orchestrator Integration**: Verified `OrchestratorV2` correctly calls the agent when `deep_search=True`.
3. **API & UI**: Confirmed the new parameters are exposed via `api/app.py` and the Frontend.

### Test Output

The verification script confirmed:

- Successful instantiation of `RetrievalAgent`.
- Correct handling of `deep_search` and `retrieval_strategy` in `OrchestratorV2`.
- Execution of the investigation loop (simulated in mocks).

## Next Steps

- Refine the `ExternalIntegration` to support more providers.
- Improve `RetrievalAgent` with more advanced tools (e.g., LSP integration / Go To Definition).
- Benchmarking the tokens saved by the Hybrid Strategy vs Full External Delegation.
