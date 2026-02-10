# Phase 20: Model Context Protocol (MCP) Integration Specification

## 1. Overview

The **Model Context Protocol (MCP)** is an open standard that enables AI models (like Claude) to securely interact with local data and tools. By implementing an MCP Server interface for the AI Code Orchestrator, we allow external applications (Claude Desktop, Cursor, Zed) to leverage our **Swarm Intelligence** and **Specialist Agents** directly.

This means a user can type `"Refactor the auth module"` in Claude Desktop, and Claude will use the `run_swarm_task` tool provided by our server to execute the complex logic using our orchestrated agents, without the user moving files or using our CLI directly.

## 2. Architecture

We will implement an **MCP Server** that runs locally (stdio or SSE).

```mermaid
graph LR
    User[User (Claude Desktop)] -- MCP Protocol (JSON-RPC) --> MCPServer[MCP Server (core/mcp_server.py)]
    MCPServer -- Dispatches --> Orchestrator[LifecycleOrchestrator]
    Orchestrator -- Manages --> Swarm[Swarm Manager]
    Orchestrator -- Uses --> RAG[RAG System]
    MCPServer -- Returns --> User
```

## 3. Exposed Tools

We will expose high-level capabilities, not low-level functions.

| Tool Name          | Description                                                                                      | Arguments                                    | Maps To                                 |
| :----------------- | :----------------------------------------------------------------------------------------------- | :------------------------------------------- | :-------------------------------------- |
| `run_swarm_task`   | Decomposes and executes a complex software development task using a swarm of specialized agents. | `request` (str), `context_files` (list[str]) | `SwarmManagerAgent.run_swarm`           |
| `deep_search`      | Performs a semantic search across the codebase and knowledge base to answer questions.           | `query` (str)                                | `RetrievalAgent.search`                 |
| `auto_fix`         | Attempts to automatically fix a reported error or linting issue.                                 | `error_context` (str)                        | `RepairAgent.fix`                       |
| `get_architecture` | Retrieves the high-level system architecture and relationships.                                  | `focus_area` (str, optional)                 | `Blackboard.get_dag` (Visual/Structure) |

## 4. Exposed Resources

We can expose internal state as read-only resources.

| Resource URI                | Description                       | Content Source                      |
| :-------------------------- | :-------------------------------- | :---------------------------------- |
| `orchestrator://swarm/dag`  | The current Swarm Task DAG (JSON) | `SwarmManager.blackboard.get_dag()` |
| `orchestrator://logs/audit` | Recent audit logs                 | `AuditLogger.get_recent()`          |

## 5. Implementation Details

### 5.1 Dependencies

We will use the standard python SDK if available, or a lightweight implementation of the JSON-RPC spec over Stdio.

- Package: `mcp` (pip install mcp)

### 5.2 Server Class (`core/mcp_server.py`)

```python
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent

class OrchestratorMCPServer:
    def __init__(self, orchestrator: LifecycleOrchestrator):
        self.app = Server("ai-code-orchestrator")
        self.orchestrator = orchestrator
        self.setup_handlers()

    def setup_handlers(self):
        @self.app.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="run_swarm_task",
                    description="Execute complex coding tasks...",
                    inputSchema={...}
                ),
                # ... other tools
            ]

        @self.app.call_tool()
        async def call_tool(name: str, arguments: dict):
            if name == "run_swarm_task":
                return await self.handle_swarm(arguments)
            # ...
```

### 5.3 Transport

We will use **StdioServerTransport** for efficient local integration with Claude Desktop.

```python
async def main():
    # ... setup orchestrator ...
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())
```

## 6. Integration Guide (Claude Desktop)

Users will simply add this to their `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "orchestrator": {
      "command": "python",
      "args": ["-m", "core.mcp_server"]
    }
  }
}
```

## 7. Security Considerations

- **Local Only**: This server is designed for local use.
- **Confirmation**: High-impact tools (like `run_swarm_task` which edits files) should ideally require confirmation, but currently MCP delegates trust to the client UI (Claude Desktop asks user for approval).

## 8. Verification Plan

1.  **Unit Tests**: `tests/verify_phase20_mcp.py` will mock a client and send JSON-RPC messages.
2.  **Manual Verification**: Connect real Claude Desktop instance to the running code.
