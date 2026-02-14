# Implementation Plan: Solution Completion & Testing

## Goal

Finalize the "AI Code Orchestrator" by integrating the advanced `ProducerReviewerLoop` into the core orchestration engine and ensuring the CLI/API integration is robust enough for a full end-to-end test.

## User Review Required

> [!IMPORTANT]
> **Refactoring Core Logic**: I will be replacing the ad-hoc feedback loop in `OrchestratorV2` with the specialized `ProducerReviewerLoop` class. This centralizes quality control.

## Proposed Changes

### Core Orchestration

#### [MODIFY] [orchestrator_v2.py](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/core/orchestrator_v2.py)

- Import `ProducerReviewerLoop`.
- Update `run_phase_with_feedback` to instantiate and use `ProducerReviewerLoop`.
- Remove internal `_assess_quality` method (redundant).

### API & CLI

#### [MODIFY] [cli_commands.py](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/api/cli_commands.py)

- Add `--auto-fix` flag to `run` command.
- Add `--deep-search` flag to `run` command.
- Ensure `ingest` command handles default paths gracefully.

### GUI Implementation

#### [MODIFY] [OrchestratorUI.tsx](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/ui/src/components/OrchestratorUI.tsx)

- The "Run" tab already has `Auto-Fix` and `Deep Search` toggles.
- **[NEW] Knowledge Tab**: Add a new tab/modal for "Knowledge Management".
  - Allow users to trigger ingestion via GUI (`/ingest` endpoint).
  - Show Ingestion Status.

## Verification Plan

### Automated Tests

- **Unit Tests**:
  - Check `ProducerReviewerLoop` integration (mock LLM).
- **Manual Verification**:
  1. **Ingestion**:
     - CLI: `python api/cli_commands.py ingest database ./examples/pos-system/backend --collection pos_db`
     - GUI: Verify "Ingest" button works in new Knowledge tab.
  2. **Retrieval**: `python api/cli_commands.py query "login controller"`
  3. **Execution**:
     - CLI: `python api/cli_commands.py run "Create a UserProfile controller with Get and Update methods" --auto-fix`
     - GUI: Toggle "Auto-Fix" and run a request.
