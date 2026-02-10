import asyncio
import logging
import json
from typing import List, Optional, Dict, Any

try:
    from mcp.server.fastmcp import FastMCP
    from mcp.types import Tool, TextContent, ImageContent, FileResource
except ImportError:
    # Fallback for environments without 'mcp' installed, purely for structure
    # In a real scenario, we would enforce installation.
    class FastMCP:
        def __init__(self, name): 
            self.name = name
            self.tools = []
            self.resources = []
        def tool(self, func=None):
            def decorator(f):
                self.tools.append(f)
                return f
            return decorator(func) if func else decorator
        def resource(self, uri_pattern):
            def decorator(f):
                self.resources.append((uri_pattern, f))
                return f
            return decorator
        def list_tools(self): return self.tools

from core.lifecycle_orchestrator import LifecycleOrchestrator

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCPServer")

class OrchestratorMCPServer:
    """
    Exposes AI Code Orchestrator capabilities via the Model Context Protocol (MCP).
    This allows tools like Claude Desktop to directly drive the Orchestrator.
    """

    def __init__(self, orchestrator: LifecycleOrchestrator):
        logger.info(f"DEBUG: MCP Server init with orchestrator: {type(orchestrator)}")
        if hasattr(orchestrator, "orchestrator"):
             logger.info(f"DEBUG: Inner orchestrator: {type(orchestrator.orchestrator)}")
             
        self.orchestrator = orchestrator
        # Initialize FastMCP service
        self.mcp = FastMCP("AI Code Orchestrator")
        
        # Register Tools
        self.mcp.tool()(self.run_swarm_task)
        self.mcp.tool()(self.deep_search)
        self.mcp.tool()(self.auto_fix)
        
        # Register Resources
        self.mcp.resource("orchestrator://swarm/dag")(self.get_swarm_dag)
        self.mcp.resource("orchestrator://logs/audit")(self.get_audit_logs)

    async def run_swarm_task(self, request: str, context_files: List[str] = []) -> str:
        """
        Decomposes and executes a complex software development task using a swarm of specialized agents.
        Use this for big features, refactoring, or architectural changes.
        """
        logger.info(f"MCP: run_swarm_task('{request}')")
        try:
            # Check if Swarm Manager is available
            if not hasattr(self.orchestrator.orchestrator, "swarm_manager"):
                return "Error: Swarm Manager not initialized in Orchestrator."
                
            # Execute Swarm
            result = await self.orchestrator.orchestrator.run_swarm(
                request=request,
                context={"files": context_files}
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"MCP Error: {e}")
            return f"Error executing task: {str(e)}"

    async def deep_search(self, query: str) -> str:
        """
        Performs a semantic search across the codebase and knowledge base to answer questions.
        Use this when you need to understand how something works before changing it.
        """
        logger.info(f"MCP: deep_search('{query}')")
        try:
            # Use RetrievalAgent directly if available, or orchestrator phase
            # For now, we reuse the 'analyst' phase which does retrieval
            result = await self.orchestrator.orchestrator.run_phase(
                phase="analyst",
                question=query,
                context={}
            )
            return str(result)
        except Exception as e:
            return f"Error searching: {str(e)}"

    async def auto_fix(self, error_context: str) -> str:
        """
        Attempts to automatically fix a reported error or linting issue.
        Provide the full error message and stack trace.
        """
        logger.info(f"MCP: auto_fix(...)")
        try:
            # Trigger Repair Agent via Orchestrator
            # Note: We might need a direct methods on LifecycleOrchestrator for this
            # For now, we simulate a "fix" request
            result = await self.orchestrator.orchestrator.run_pipeline(
                goal=f"Fix this error: {error_context}",
                mode="incremental" # Assumes incremental fix
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error fixing: {str(e)}"

    async def get_swarm_dag(self) -> str:
        """Resource: Returns the current Swarm Task DAG as JSON."""
        if hasattr(self.orchestrator.orchestrator, "swarm_manager"):
             dag = await self.orchestrator.orchestrator.swarm_manager.blackboard.get_dag()
             return json.dumps(dag, indent=2)
        return "{}"

    async def get_audit_logs(self) -> str:
        """Resource: Returns recent audit logs."""
        # This assumes AuditLogger has a get_recent method (added in Phase 8)
        # return json.dumps(AuditLogger.get_recent(), indent=2)
        return "[]" # Placeholder until AuditLogger is fully linked

    def run_stdio(self):
        """Runs the MCP server over Stdio."""
        self.mcp.run(transport="stdio")

if __name__ == "__main__":
    # Entry point for running as a standalone process
    # Initialize the real orchestrator here
    # This part requires the full environment to be loaded
    from api.shared import orchestrator_instance
    
    server = OrchestratorMCPServer(orchestrator_instance)
    server.run_stdio()
