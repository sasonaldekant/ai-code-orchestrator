# Phase 20: MCP Integration - Implementation Plan

## Goal

Implement a Model Context Protocol (MCP) Server to expose AI Code Orchestrator capabilities to external tools like Claude Desktop.

## User Review Required

> [!IMPORTANT]
> This implementation assumes the `mcp` python package is available or can be mocked if not present in the environment. All tests will use a mock client to avoid external dependencies during verification.

## Proposed Changes

### Core System

#### [NEW] [core/mcp_server.py](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/core/mcp_server.py)

- **Class**: `OrchestratorMCPServer`
- **Dependencies**: `mcp`, `LifecycleOrchestrator`
- **Methods**:
  - `list_tools()`: Registers `run_swarm_task`, `deep_search`, `auto_fix`.
  - `call_tool()`: Routes requests to the appropriate agent within `LifecycleOrchestrator`.
  - `list_resources()`: Registers `orchestrator://swarm/dag` and `orchestrator://logs/audit`.
  - `read_resource()`: Fetches data for the requested resource.

### Verification Plan

### Automated Tests

#### [NEW] [tests/verify_phase20_mcp.py](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/tests/verify_phase20_mcp.py)

- **Test 1**: Verify `list_tools` returns correct schema.
- **Test 2**: Verify `call_tool("run_swarm_task")` triggers `SwarmManagerAgent`.
- **Test 3**: Verify `read_resource` returns valid JSON.

### Manual Verification

- Connect a local instance of Claude Desktop to the server using the configuration generated in the Spec.
