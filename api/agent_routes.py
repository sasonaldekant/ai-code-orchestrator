from fastapi import APIRouter
from typing import Dict, Any, List
from api.shared import orchestrator_instance
from core.registry import CapabilityRegistry
from core.agents.specialist_agents.retrieval_agent import RetrievalAgent

router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("/")
async def get_agents():
    """
    Get all active agents and their capabilities.
    """
    agents_list = []
    
    # 1. Phase Agents from OrchestratorV2
    # Ensure initialization
    try:
        # LifecycleOrchestrator -> OrchestratorV2
        core_orchestrator = orchestrator_instance.orchestrator
        phase_agents_dict = core_orchestrator.phase_agents
        
        for key, agent in phase_agents_dict.items():
            agents_list.append({
                "id": key,
                "name": getattr(agent, "name", key.capitalize()),
                "description": getattr(agent, "description", "Phase Agent"),
                "role": getattr(agent, "role", key),
                "tools": getattr(agent, "tools", []),
                "type": "phase",
                "status": "active"
            })
            
        # 2. Specialist Agents
        # Instantiate strictly for metadata retrieval (lightweight)
        if core_orchestrator.llm_client:
             investigator = RetrievalAgent(core_orchestrator.llm_client)
             agents_list.append({
                "id": "investigator",
                "name": getattr(investigator, "name", "Investigator"),
                "description": getattr(investigator, "description", "Deep Search Agent"),
                "role": getattr(investigator, "role", "researcher"),
                "tools": getattr(investigator, "tools", []),
                "type": "specialist",
                "status": "on_demand"
             })
             
    except Exception as e:
        print(f"Error fetching agents: {e}")
        
    return {"agents": agents_list}

@router.get("/tools")
async def get_tools():
    """
    Get all registered tools in the Cortex Registry.
    """
    tools = []
    tool_names = CapabilityRegistry.list_tools()
    
    for name in tool_names:
        tool_def = CapabilityRegistry.get_tool(name)
        if tool_def:
            tools.append({
                "name": tool_def.name,
                "description": tool_def.description,
                "category": tool_def.category,
                "parameters": tool_def.parameters
            })
            
    return {"tools": tools}
