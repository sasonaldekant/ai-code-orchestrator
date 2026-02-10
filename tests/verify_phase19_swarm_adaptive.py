
import asyncio
import json
import logging
from unittest.mock import AsyncMock, MagicMock, patch
from core.memory.blackboard import Blackboard
from core.agents.specialist_agents.swarm_manager import SwarmManagerAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_blackboard_dag():
    logger.info("Testing Blackboard DAG...")
    bb = Blackboard()
    await bb.register_task("t1", "Task 1", "agent1")
    await bb.register_task("t2", "Task 2", "agent2", depends_on=["t1"])
    
    dag = await bb.get_dag()
    assert len(dag["nodes"]) == 2
    assert len(dag["links"]) == 1
    assert dag["links"][0]["source"] == "t1"
    assert dag["links"][0]["target"] == "t2"
    logger.info("✓ Blackboard DAG test passed.")

async def test_complexity_detection():
    logger.info("Testing Complexity Detection...")
    bb = Blackboard()
    orchestrator = MagicMock()
    manager = SwarmManagerAgent(orchestrator)
    
    assert manager._detect_complexity("implement simple function") == False
    assert manager._detect_complexity("comprehensive architectural overhaul with multi-file refactoring") == True
    assert manager._detect_complexity("a" * 201) == True # Length based
    logger.info("✓ Complexity Detection test passed.")

async def test_adaptive_scaling():
    logger.info("Testing Adaptive Scaling (Model Upscaling)...")
    orchestrator = MagicMock()
    orchestrator.model_router = MagicMock()
    mock_cfg = MagicMock()
    mock_cfg.model = "stronger-model"
    orchestrator.model_router.get_model_for_phase.return_value = mock_cfg
    
    orchestrator.run_phase = AsyncMock(return_value={"status": "completed"})
    
    manager = SwarmManagerAgent(orchestrator)
    # Mocking _load_prompt to avoid file IO
    manager._load_prompt = MagicMock(return_value="template")
    
    # Run a complex task
    # We need to mock _run_task or call it
    # _run_task(self, task_id, description, agent_type, context)
    await manager.blackboard.register_task("t1", "comprehensive refactoring of architecture", "implementation")
    await manager._run_task("t1", {"description": "comprehensive refactoring of architecture", "agent": "implementation"}, {})
    
    # Verify run_phase was called WITH model_override
    orchestrator.run_phase.assert_called_once()
    kwargs = orchestrator.run_phase.call_args.kwargs
    assert kwargs["model_override"] == "stronger-model"
    logger.info("✓ Adaptive Scaling test passed.")

async def test_fail_safe_pivoting():
    logger.info("Testing Fail-Safe Pivoting...")
    orchestrator = MagicMock()
    orchestrator.llm_client = AsyncMock()
    orchestrator.model_router = MagicMock()
    orchestrator.model_router.get_model_for_phase.return_value = MagicMock(model="architect")
    
    # Mock LLM response for pivot
    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "status": "success",
        "tasks": [
            {"id": "new_t1", "description": "New Task", "agent": "Analyst", "dependencies": []}
        ]
    })
    orchestrator.llm_client.complete.return_value = mock_response
    
    manager = SwarmManagerAgent(orchestrator)
    manager._load_prompt = MagicMock(return_value="template")
    
    # Mock failing a task in execute_swarm logic
    # We'll test _pivot_swarm directly
    new_tasks = await manager._pivot_swarm("Request", {}, {"prev_ok"}, {"prev_fail"})
    
    assert len(new_tasks) == 1
    assert new_tasks[0]["id"] == "new_t1"
    
    # Check if registered on blackboard
    dag = await manager.blackboard.get_dag()
    assert any(n["id"] == "new_t1" for n in dag["nodes"])
    logger.info("✓ Fail-Safe Pivoting test passed.")

async def main():
    try:
        await test_blackboard_dag()
        await test_complexity_detection()
        await test_adaptive_scaling()
        await test_fail_safe_pivoting()
        logger.info("\nALL PHASE 19 VERIFICATION TESTS PASSED!")
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
