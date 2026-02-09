# CLI Command Specifications

This document outlines the command‑line interface for interacting with the domain‑specific AI Code Orchestrator.  The CLI wraps the internal API and enforces argument schemas.

## Commands

### run

Execute a complete workflow (analysis → architecture → planning → tasks → implementation → testing → compliance) for a natural language requirement.

```bash
aiorchestrator run --requirement "Add customer onboarding feature" [--mode greenfield] [--context-type backend]
```

Arguments:

| Argument | Type | Required | Description |
|---|---|---|---|
| `--requirement` | string | ✔ | Natural language description of the feature or change. |
| `--mode` | enum |  | Workflow mode: `greenfield`, `incremental`, `refactor`, `migration`.  Defaults to `greenfield`. |
| `--context-type` | enum |  | Context retrieval type: `backend`, `frontend`, or `full`.  Defaults to `full`. |

### query

Retrieve the structured domain context for a requirement without running the full workflow.

```bash
aiorchestrator query --requirement "Add login form" [--top-k-entities 5] [--top-k-components 8]
```

Arguments:

| Argument | Type | Required | Description |
|---|---|---|---|
| `--requirement` | string | ✔ | Natural language description of the feature or change. |
| `--top-k-entities` | integer |  | Number of database entities to retrieve (default 5). |
| `--top-k-components` | integer |  | Number of UI components to retrieve (default 8). |

