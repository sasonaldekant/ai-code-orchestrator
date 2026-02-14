# Task: Scaling & Bug Fixing

## Checklist

- [x] Investigate Anthropic API model availability
- [x] Update model configuration files
- [x] Test updated configuration
- [x] Fix Analyst-Orchestrator protocol mismatch
    - Update `LifecycleOrchestrator._parse_plan` to support `implementation_plan` key
    - Ensure logical task phase assignment
- [x] Configure Custom Claude Models
    - Update configs with `claude-sonnet-4-5-20250929`
    - Restart server
- [/] Verify query handling
- [x] Configure Custom Claude Models
    - Attempted `claude-sonnet-4-5-20250929` (Invalid/Unavailable)
    - Reverted to `gpt-4o` for stability
- [/] Verify query handling
    - Test "How many components do we have?"
    - Expecting text answer using GPT-4o
- [ ] Fix Missing Analyst Schema
    - Create `schemas/phase_schemas/analyst_output.json` (Solved by mapping to `requirements.json`)
- [x] Fix JSON Serialization Error
    - `ExecutionStatus` is not serializable (Solved by adding `str` inheritance)
    - Convert Enum to string in responses
- [x] Increase Request Timeout
    - Updated `timeout_seconds` to 120 to prevent premature termination of complex tasks
- [x] Fix Execution Error Loop
    - Improve phase detection heuristics
    - Harden code extraction
- [x] Fix Q&A Flow (Hallucination)
    - Analyst prompt was forcing requirements even for simple questions
    - Updated prompt to support `answer` field
- [x] Fix Q&A Flow (Hallucination)
    - Analyst prompt was forcing requirements even for simple questions
    - Updated prompt to support `answer` field
    - Updated Orchestrator to bypass execution if `answer` is present
    - Injected project structure into `ContextManager` to allow answering questions like "how many components"
    - Aligned `LifecycleOrchestrator` keys with `Analyst` prompt (`requirements`, `domain_context`)
- [x] Fix Empty Request Loop
    - Added validation in `api/app.py` to reject empty requests
- [x] Fix Schema Validation (Architect)
    - Updated `architecture.json` to accept object type instead of string
- [x] Fix Schema Validation (Testing)
    - Updated `TestingAgent` to output `test_plan` as required by schema

