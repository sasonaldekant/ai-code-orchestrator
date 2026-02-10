
import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock
from core.mcp_server import OrchestratorMCPServer, FastMCP

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_tool_registration():
    logger.info("Testing Tool Registration...")
    
    server = OrchestratorMCPServer(MagicMock())
    tools = server.mcp.list_tools()
    
    tool_names = [t.__name__ for t in tools]
    assert "run_swarm_task" in tool_names
    assert "deep_search" in tool_names
    assert "auto_fix" in tool_names
    
    logger.info("✓ Tool Registration passed.")

async def test_run_swarm_task():
    logger.info("Testing run_swarm_task...")
    
    # Mock Orchestrator and Swarm
    mock_orch = MagicMock()
    mock_orch.orchestrator = MagicMock()
    mock_orch.orchestrator.swarm_manager = MagicMock()
    
    # Mock return value
    mock_orch.orchestrator.run_swarm = AsyncMock(return_value={"status": "success", "tasks": []})
    
    server = OrchestratorMCPServer(mock_orch)
    
    # Call the tool directly (as FastMCP wrapper does)
    result_json = await server.run_swarm_task("Test Request", ["file1.py"])
    
    assert '"status": "success"' in result_json
    mock_orch.orchestrator.run_swarm.assert_called_once()
    
    logger.info("✓ run_swarm_task passed.")

async def test_deep_search():
    logger.info("Testing deep_search...")
    
    mock_orch = MagicMock()
    mock_orch.orchestrator = MagicMock()
    mock_orch.orchestrator.run_phase = AsyncMock(return_value="Search Result")
    
    server = OrchestratorMCPServer(mock_orch)
    
    result = await server.deep_search("How does auth work?")
    
    assert result == "Search Result"
    mock_orch.orchestrator.run_phase.assert_called_with(
        phase="analyst",
        question="How does auth work?",
        context={}
    )
    
    logger.info("✓ deep_search passed.")

async def test_auto_fix():
    logger.info("Testing auto_fix...")
    
    mock_orch = MagicMock()
    mock_orch.orchestrator = MagicMock()
    mock_orch.orchestrator.run_pipeline = AsyncMock(return_value={"status": "fixed"})
    
    server = OrchestratorMCPServer(mock_orch)
    
    result = await server.auto_fix("Error on line 10")
    
    assert '"status": "fixed"' in result
    mock_orch.orchestrator.run_pipeline.assert_called_with(
        goal="Fix this error: Error on line 10",
        mode="incremental"
    )
    
    logger.info("✓ auto_fix passed.")

async def main():
    try:
        await test_tool_registration()
        await test_run_swarm_task()
        await test_deep_search()
        await test_auto_fix()
        logger.info("\nALL PHASE 20 MCP VERIFICATION TESTS PASSED!")
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
