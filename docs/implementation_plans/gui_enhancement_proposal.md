# GUI Enhancement Proposal: "Nexus Control Center"

This document outlines a plan to expose advanced Orchestrator settings and functionalities primarily through the GUI, moving away from file-based configuration for day-to-day usage.

## 1. Categorization

### A. Global Settings (Configuration)

These are persistent settings that affect how the system behaves across all runs.
_Location: New "Settings" Modal (triggered by Sidebar Gear Icon)_

| Setting Group          | Parameters                                                               | UI Element                                 |
| :--------------------- | :----------------------------------------------------------------------- | :----------------------------------------- |
| **Model Intelligence** | Model selection per phase (Analyst, Architect, Dev, Reviewer)            | Dropdowns (GPT-4o, Claude 3.5, Gemini 2.5) |
| **Orchestration**      | `Max Retries` (1-5), `Quality Threshold` (0.1-1.0), `Max Feedback Loops` | Sliders & Number Inputs                    |
| **Performance**        | `Consensus Mode` (Enable/Disable), `Parallel Execution` (Limit workers)  | Toggles & Inputs                           |
| **Secrets**            | API Keys (OpenAI, Anthropic, Google)                                     | Masked Input Fields                        |

### B. Run-Time Functionalities (Per-Request)

These are options that customize a specific execution task.
_Location: Main Input Area (Expandable "Advanced Options")_

| Feature              | Description                                                     | UI Element           |
| :------------------- | :-------------------------------------------------------------- | :------------------- |
| **Budget Limit**     | Max cost for this specific run (e.g., $2.00)                    | Number Input ($)     |
| **Review Intensity** | How strict the reviewer should be (Lenient vs. Strict)          | Segmented Control    |
| **Output Format**    | Force specific output (Code only, Plan only, Full Report)       | Multi-select Chips   |
| **Agent Constraint** | Force specific specialist agents (e.g., "Use React Agent only") | multiselect Dropdown |

### C. Knowledge & Data Management

Enhancements to the existing "Manage Knowledge" tab.
_Location: `KnowledgeTab`_

| Feature           | Description                               | Improvement                            |
| :---------------- | :---------------------------------------- | :------------------------------------- |
| **Live Status**   | View actual collections in Vector DB      | Fetch & Display real-time doc counts   |
| **Domain Config** | Visual editor for `domain_config.yaml`    | Form-based editor for Bounded Contexts |
| **Reset/Prune**   | Clear specific collections or flush cache | Destructive Action Buttons             |

---

## 2. Proposed UI Architecture

### 1. The "Settings" Modal

A centralized modal accessible via the sidebar "Admin Settings" button.

- **Tabs**: General, Models, API Keys.
- **Action**: "Save Configuration" (Writes to `config/model_mapping.yaml` and `.env`).

### 2. Enhanced Input Widget

Upgrade the main chat input to support an "Advanced" drawer.

```text
[ Attach Image ] [ Deep Search ] [ Auto-Fix ]
--------------------------------------------------
[ Text Input Area                                ]
--------------------------------------------------
[ > Advanced Options ] (Collapsible)
   | Budget: [$ 5.00]  Review: [Strict]
   | Models: [Default (Optimized)] v
   | Consensus: [ON]
[ SEND ]
```

### 3. Agent Registry View (New Tab)

A new tab alongside "Thought Stream" and "Manage Knowledge".

- **Purpose**: Visualize active agents and their tools.
- **Interaction**: Enable/Disable specific tools (e.g., "Disable CLI Execution" for safety).

---

## 3. Implementation Priorities

1.  **Phase 1 (Quick Wins)**:
    - Implement "Advanced Options" collapsible in `OrchestratorUI`.
    - Add `Quality Threshold` and `Max Iterations` to the UI (passed to API).

2.  **Phase 2 (Configuration)**:
    - Create the "Settings Modal".
    - Create API endpoint `GET/POST /config` to read/write `model_mapping.yaml`.

3.  **Phase 3 (Observability)**:
    - Implement "Agent Registry" tab.
    - Connect "Knowledge Tab" to real Vector DB stats.
