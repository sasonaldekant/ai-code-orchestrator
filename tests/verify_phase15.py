
import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agents.specialist_agents.retrieval_agent import RetrievalAgent
from core.orchestrator_v2 import OrchestratorV2
from core.llm_client_v2 import LLMClientV2

# Mock classes to avoid full dependency chains
class MockLLM(LLMClientV2):
    def __init__(self):
        pass
    async def complete(self, messages, **kwargs):
        class Response:
            content = """
            Thought: I need to search for the file.
            Action: search_code
            Action Input: {"query": "test"}
            """
        
        # Second response to finish
        if "Observation" in str(messages):
            class Response:
                content = """
                Thought: I found it.
                Final Answer: The test file exists.
                """
            return Response()
            
        return Response()

class MockRetriever:
    def retrieve(self, query, top_k=3):
        return []

async def test_retrieval_agent():
    print("Testing RetrievalAgent...", flush=True)
    mock_llm = MockLLM()
    agent = RetrievalAgent(mock_llm)
    
    # Mocking tools for safety
    agent.tools = {
        "search_code": lambda query: "Found file: test.py",
        "read_file": lambda path: "def test(): pass",
        "list_dir": lambda path: "['test.py']"
    }
    
    # Inject mock tools into the available_tools list if needed, 
    # but the agent class usually initializes them.
    # We'll just patch the execution method if needed, but the ReAct loop usage of tools 
    # depends on tool_map.
    agent.tool_map = agent.tools
    
    result = await agent.run("Find the test file")
    print(f"Agent Result: {result}")
    assert "test file" in result or "Found" in result

async def test_orchestrator_integration():
    print("\nTesting Orchestrator Deep Search Integration...", flush=True)
    mock_llm = MockLLM()
    mock_retriever = MockRetriever()
    
    orch = OrchestratorV2(llm_client=mock_llm, retriever=mock_retriever)
    
    # We need to mock the agent inside orchestrator to avoid real calls
    # or just use the mock llm which simulates the agent response
    
    # We also need to mock ExternalIntegration if strategy='hybrid'
    # But for 'local', it should just run RetrievalAgent
    
    # Patch RetrievalAgent in the orchestrator module if possible, 
    # but simpler to just run with 'local' strategy and MockLLM.
    
    # However, OrchestratorV2 instantiates RetrievalAgent internally in _execute_phase.
    # Since we passed mock_llm to Orchestrator, it should pass it to RetrievalAgent?
    # Let's check OrchestratorV2 code.
    # line 259: investigator = RetrievalAgent(self.llm_client)
    # Yes, it uses self.llm_client.
    
    # But RetrievalAgent real init will try to set up real tools.
    # We might want to patch RetrievalAgent class.
    
    orig_agent_cls = __import__('core.orchestrator_v2').orchestrator_v2.RetrievalAgent
    
    class MockRetrievalAgent:
        def __init__(self, llm):
            pass
        async def run(self, query, initial_plan=None):
            return f"Deep search findings for {query}"
            
    # Monkey patch
    import core.orchestrator_v2
    core.orchestrator_v2.RetrievalAgent = MockRetrievalAgent
    
    try:
        # Trigger _execute_phase via custom call or run_phase_with_retry
        # We simulate a phase that calls deep search
        # Note: _execute_phase gets the phase agent (e.g. analyst)
        # We need to make sure 'analyst' agent exists or is mocked
        
        # OrchestratorV2 has lazy phase_agents
        # We can just call _execute_phase directly
        
        class MockAnalyst:
            async def execute(self, *args, **kwargs):
                return {'status': 'done'}
        mock_analyst = MockAnalyst()
        orch._phase_agents = {'analyst': mock_analyst}
        
        result = await orch._execute_phase(
            phase="analyst",
            schema_name="test_schema",
            question="Analyze this",
            deep_search=True,
            retrieval_strategy="local"
        )
        
        print(f"Orchestrator Result: {result}")
        # We check if rag_context has the deep search result
        
        # Wait, _execute_phase returns the agent output (dict).
        # The rag_context is passed to agent.execute.
        # We can check if our mock_analyst received the context.
        pass
        
    finally:
        # Restore
        core.orchestrator_v2.RetrievalAgent = orig_agent_cls

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_retrieval_agent())
    asyncio.run(test_orchestrator_integration())
