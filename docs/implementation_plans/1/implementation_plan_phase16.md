# Phase 16: Autonomous Evolution & Connectivity

## Goal

To evolve the AI Code Orchestrator from a passive assistant to an **autonomous partner** capable of self-healing and multi-modal understanding, and to expand its accessibility via a dedicated IDE API.

## User Review Required

> [!IMPORTANT]
> **Autonomy Risks**: The `RepairAgent` will have the ability to modifying code autonomously. We must ensure it runs in a sandboxed environment (Docker) or has strict revert capabilities. For this phase, we will implement it with a **"Human-in-the-Loop"** approval step by default.

## Proposed Changes

### 16.1 Autonomous Self-Healing ("The Auto-Fixer")

We will create a `RepairAgent` that orchestrates the following loop:

1.  **Trigger**: Test failure or Runtime Exception.
2.  **Investigate**: Use `RetrievalAgent` to locate the source code and error context.
3.  **Plan**: Use LLM to generate a fix hypothesis.
4.  **Action**: Use `RefactoringAgent` or simple file writer to apply the fix.
5.  **Verify**: Re-run the specific test case.

#### [NEW] `core/agents/specialist_agents/repair_agent.py`

- Class `RepairAgent`
- Method `auto_fix(error_log: str, test_command: str) -> bool`

#### [MODIFY] `core/orchestrator_v2.py`

- Add `auto_fix` toggle to `run_pipeline`.
- If `Verification` fails and `auto_fix=True`, invoke `RepairAgent`.

### 16.2 Multi-Modal Capabilities (Vision)

Enabling the LLM to "see" the UI allows for frontend auditing and generation from wireframes.

#### [MODIFY] `core/llm_client_v2.py`

- Update `Message` schema to support `image_url` content blocks (OpenAI format).

#### [NEW] `core/vision_manager.py`

- Helper to process images (resize, base64 encode).

#### [NEW] `api/vision_routes.py`

- `POST /tools/analyze-image`: Proxies image + prompt to LLM.

### 16.3 IDE Bridge (API)

A streamlined API for external tools.

#### [MODIFY] `api/app.py`

- Register `ide_routes`.

#### [NEW] `api/ide_routes.py`

- `POST /ide/status`: Returns current orchestrator state.
- `POST /ide/fix`: specific endpoint for "Quick Fix" actions.

## Verification Plan

### Automated

1.  **Auto-Fix Simulation**: Create a test file with a known syntax error, run `RepairAgent`, and assert the file is fixed and tests pass.
2.  **Vision Test**: Mock the LLM vision response and verify the API handles base64 images correctly.

### Manual

1.  **UI**: Upload a screenshot to the new "Vision" tab (to be added) and ask for a critique.
