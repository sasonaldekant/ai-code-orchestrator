# Implementation Plan: Phase 19 - Swarm GUI & Adaptive Scaling

This phase focuses on enhancing the visibility and resilience of the Swarm Intelligence system.

## Proposed Changes

### 1. Swarm GUI (Nexus Frontend) 🖥️

Adding visual clarity to the parallel agent activities.

#### [NEW] [SwarmVis.tsx](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/ui/src/components/admin/SwarmVis.tsx)

- A React component using `react-force-graph-2d` or a similar D3-based library to visualize the Task DAG.
- Each node represents a task (e.g., "Analyst Task 1").
- Node color reflects status: `pending` (grey), `running` (blue), `completed` (green), `failed` (red).

#### [MODIFY] [DeveloperToolsPanel.tsx](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/ui/src/components/admin/DeveloperToolsPanel.tsx)

- Add a "Swarm Monitor" tab.
- Integrate `SwarmVis` into this panel.

### 2. Adaptive Scaling (Backend) ⚖️

Making the swarm smarter about resource allocation and failures.

#### [MODIFY] [swarm_manager.py](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/core/agents/specialist_agents/swarm_manager.py)

- **Complexity Aware Routing:** Implement logic to detect when a sub-task is "high-risk" (e.g., legacy code refactor) and automatically upgrade the model from `gpt-4o-mini` to `o1-preview` or `claude-3-5-sonnet`.
- **Dynamic Re-decomposition:** If a specific task node fails repeatedly, the manager will trigger a "Pivot" action to re-decompose the remaining sub-graph.

#### [MODIFY] [blackboard.py](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/core/memory/blackboard.py)

- Add stream-friendly methods for the UI to poll/subscribe to status changes efficiently.

---

## Verification Plan

### Automated Tests

- `tests/test_adaptive_scaling.py`: Verify that "complex" tasks trigger model upscaling in the swarm config.
- `tests/test_swarm_pivot.py`: Simulate a node failure and verify the graph re-calculation.

### Manual Verification

- Launch Nexus GUI and trigger a swarm request.
- Observe the real-time DAG update in the "Swarm Monitor" tab.
