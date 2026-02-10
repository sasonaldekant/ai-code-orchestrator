# IDE Integration Guide - AI Code Orchestrator v3.0

## Overview

This guide documents the API endpoints available for IDE extensions (VS Code, JetBrains) to interact with the AI Code Orchestrator. This allows developers to use features like "Explain Code," "Fix Bug," and "Refactor" directly from their editor context.

## Base URL

`http://localhost:8000/ide` (Default)

## Endpoints

### 1. Context Action

Trigger an AI action on a selected code block.

- **URL:** `/context-action`
- **Method:** `POST`
- **Content-Type:** `application/json`

#### Request Body

```json
{
  "file_path": "/absolute/path/to/source.py",
  "selection": "def foo():\n    return 1",
  "action": "EXPLAIN",
  "context": "Optional context or error message"
}
```

#### Supported Actions

| Action      | Description                            | Agent/Prompt        |
| :---------- | :------------------------------------- | :------------------ |
| `EXPLAIN`   | Explain the selected code logic.       | Tech Lead / Teacher |
| `FIX`       | Fix bugs in the selection.             | Debugger            |
| `REFACTOR`  | Improve code quality/readability.      | Clean Code Expert   |
| `DOCSTRING` | Generate documentation/docstrings.     | Doc Specialist      |
| `TEST`      | Generate unit tests for the selection. | QA Engineer         |

#### Response

```json
{
  "success": true,
  "result": "Here is the explanation...",
  "error": null
}
```

## Example Usage (Python)

```python
import requests

payload = {
    "file_path": "/src/app.py",
    "selection": "def add(a,b): return a+b",
    "action": "DOCSTRING"
}

resp = requests.post("http://localhost:8000/ide/context-action", json=payload)
print(resp.json()["result"])
# Output: """Adds two numbers and returns the result."""
```

## Future Roadmap

- **Streaming Support:** Streaming responses for long explanations.
- **WebSocket:** Real-time bi-directional context syncing.
- **LSP Integration:** Language Server Protocol proxies.
