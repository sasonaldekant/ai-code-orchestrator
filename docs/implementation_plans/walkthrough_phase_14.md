# Walkthrough - Phase 14: External AI Delegation Strategy

## Goal

Integrate external Pro AI tools (ChatGPT Plus, Perplexity Pro) into the AI Code Orchestrator's workflow to handle complex reasoning and research tasks, optimizing token usage and leveraging specialized models.

## Changes

### 1. Backend: External Integration Logic

- **`core/external_integration.py`**: Added `ExternalIntegration` class.
  - `generate_prompt(query, context, model)`: Creates optimized prompts with role, context, and model-specific instructions.
  - `detect_task_complexity(query, context)`: Analyzes token count and query keywords to suggest if delegation is needed.
  - `ingest_response(question, answer, source)`: Saves external AI responses into the `external_knowledge` vector store.

### 2. Backend: API Endpoints

- **`api/admin_routes.py`**:
  - `POST /tools/generate-prompt`: Generates a prompt package from user query and files.
  - `POST /tools/advise-complexity`: Checks if a task is too complex for local models.
  - `POST /ingest/external-response`: Ingests the answer back into the system.

### 3. Frontend: Developer Tools Panel

- **`ui/src/components/admin/DeveloperToolsPanel.tsx`**:
  - **Tab: Pro Prompt Gen**:
    - Input for Problem/Query and Context Files.
    - **Proactive Advisor**: Automatically checks complexity as you type and suggests "Delegate to ChatGPT o1" or "Perplexity" if the task is heavy.
    - "Generate Prompt Package" button to create the full prompt.
  - **Tab: Ingest Response**:
    - Form to paste the Question, Answer, and select Source (ChatGPT, Perplexity, etc.).
    - "Ingest to Knowledge Base" button to save it.

## Verification

- **Complexity Advisor**: Verified that typing a long query or adding many files triggers the advisor to suggest delegation.
- **Prompt Generation**: Confirmed that prompts are generated with the correct structure and context.
- **Ingestion**: Confirmed that responses are saved and returned with a Document ID.

## Next Steps

- Use the strategies defined in `docs/HYBRID_AI_WORKFLOW.md`.
- Monitor the usage of external tools vs local models.
