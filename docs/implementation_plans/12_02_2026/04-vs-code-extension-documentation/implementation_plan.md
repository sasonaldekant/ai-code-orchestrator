# Phase 4: Integration & Validation Plan

## Goal
Verify that the AI Code Orchestrator generates code that strictly adheres to DynUI standards ("Golden Rules") in a realistic scenario.

## User Review Required
> [!NOTE]
> This phase involves running the orchestrator. I will create a script to simulate a user request and validate the output programmatically.

## Proposed Changes

### 1. Create E2E Test Script
Create `scripts/test_dynui_compliance.py` to:
1.  **Simulate User Request**: "Create a responsive User Profile form with fields for Name, Email, and a 'Save Preferences' button."
2.  **Run Orchestrator**: Execute the pipeline (Analyst -> Architect -> Implementation).
3.  **Validate Output**:
    *   **Architect**: Check for `DynInput`, `DynButton`, `DynBox` in the component list.
    *   **Frontend**: Check for imports from `@dyn-ui/react`.
    *   **Tokens**: Check for usage of `var(--dyn-...)` CSS variables.
    *   **Grid**: Check for `display="grid"` or `DynBox` grid props.

### 2. Execution Strategy
-   I will use the `OrchestratorV2` class directly.
-   I might need to mock the LLM if I want deterministic results for *testing* the *mechanism*, but for *validation* of the *prompts*, I actually need the real LLM (or a simulated high-fidelity response).
-   *Decision*: I will run the script using the real `OrchestratorV2` but with a flag to potentially limit the number of steps or use a "dry run" mode if available. Since I want to test the *prompts*, I need the LLM to generate the text.

## Validation Criteria
| Check | Expected Result |
| :--- | :--- |
| **Component Usage** | Contains `DynInput`, `DynButton` |
| **No HTML primitives** | No `<input>`, `<button>` (unless wrapped) |
| **Design Tokens** | CSS uses `var(--dyn-spacing-md)`, not `16px` |
| **Grid System** | Uses `DynBox` with `colSpan` or CSS Grid |

## Rollback Plan
If validation fails, I will iterate on the Phase 3 prompts (Analyst/Architect/Implementation) until compliance is met.
