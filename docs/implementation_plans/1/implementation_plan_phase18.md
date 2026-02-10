# Phase 18: Swarm Intelligence & Multi-Agent Nodes ("The Hive Mind")

## Goal

Transition from a linear pipeline (Analyst -> Architect -> Developer) to a dynamic **Swarm Architecture** where a central **Swarm Manager** decomposes complex requests and orchestrates a "hive" of specialized agents working in semi-autonomous collaboration.

## Feature Overview

1.  **Swarm Manager (`SwarmManagerAgent`)**: A high-level reasoning agent that analyzes the goal and creates a dynamic Directed Acyclic Graph (DAG) of tasks.
2.  **Parallel Execution**: Ability to run independent tasks (e.g., Backend Refactor + Doc Update) concurrently across different agent "nodes".
3.  **Cross-Agent Communication**: A shared "Blackboard" or context-sharing mechanism for agents to exchange insights during the swarm process.
4.  **Consensus/Review Loop**: Agents can request peer-review from other specialized agents (e.g., Developer requests Reviewer to check a patch).

## Proposed Changes

### [Component] Core Orchestrator

#### [MODIFY] [orchestrator.py](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/core/orchestrator.py)

- Add `run_swarm(request)` method.
- Integrate `SwarmManagerAgent` for initial task decomposition.

### [Component] Specialist Agents

#### [NEW] [swarm_manager.py](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/agents/specialist_agents/swarm_manager.py)

- Logic for task decomposition.
- Management of the "Agent Pool".
- Conflict resolution and result synthesis.

### [Component] Communication Layer

#### [NEW] [blackboard.py](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/core/memory/blackboard.py)

- A shared state object for swarm participants to read/write shared context and sub-task statuses.

---

## Verification Plan

### Automated Tests

- `tests/verify_phase18_swarm.py`: Verify that a complex multi-part request (e.g., "Implement feature X and update the README and add tests") is correctly decomposed and executed by the swarm.

### Manual Verification

- Trigger "Swarm Mode" via CLI/GUI and monitor the "Thought Stream" to see multiple agents collaborating.
