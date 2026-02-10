# User Guide: MCP Integration (Claude Desktop)

This guide explains how to connect **Claude Desktop** to your local **AI Code Orchestrator** using the Model Context Protocol (MCP).

## Prerequisites

- **Claude Desktop App** installed (macOS or Windows).
- **AI Code Orchestrator** installed and running locally.
- **Python 3.10+** available in your path.

## Configuration

1.  Open your Claude Desktop configuration file:
    - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
    - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

2.  Add the `orchestrator` server to the `mcpServers` section:

    ```json
    {
      "mcpServers": {
        "orchestrator": {
          "command": "python",
          "args": ["-m", "core.mcp_server"],
          "cwd": "e:\\PROGRAMING\\AI_Projects\\ai-code-orchestrator",
          "env": {
            "PYTHONPATH": "e:\\PROGRAMING\\AI_Projects\\ai-code-orchestrator"
          }
        }
      }
    }
    ```

    > **Note**: Adjust the `cwd` and `PYTHONPATH` to match your actual project path.

3.  Restart Claude Desktop.

## Available Tools

Once connected, you can ask Claude to perform advanced tasks directly:

| Tool               | Action                                                      | Example Prompt                                                |
| :----------------- | :---------------------------------------------------------- | :------------------------------------------------------------ |
| **run_swarm_task** | Decomposes and executes complex coding tasks (multi-agent). | "Refactor the authentication module to use JWTs."             |
| **deep_search**    | Semantically searches your codebase and docs.               | "How does the resilience manager handle retry logic?"         |
| **auto_fix**       | Attempts to fix specific errors.                            | "Fix this traceback: `ImportError: no module named core.llm`" |

## Usage Examples

### 1. Architectural Refactoring

> "Refactor the `CostManager` to support per-provider budgets using the `run_swarm_task` tool."

### 2. Bug Investigation

> "Use `deep_search` to find where `LifecycleOrchestrator` is initialized, then explain why the `RepairAgent` might be missing."

### 3. Quick Fix

> "I'm getting a `ValueError` in `app.py`. Can you `auto_fix` it?"
