"""
Semantic Router
Routing engine that uses LLMs to map natural language intents to registered tools.
"""

import json
import logging
from typing import Dict, Any, Optional

from core.llm_client_v2 import LLMClientV2
from core.registry import CapabilityRegistry
from core.cost_manager import CostManager

logger = logging.getLogger(__name__)

class SemanticRouter:
    def __init__(self, llm_client: Optional[LLMClientV2] = None):
        self.llm_client = llm_client or LLMClientV2(CostManager())
        self.registry = CapabilityRegistry()

    async def route_intent(self, user_request: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyzes the user request and selects the best tool to call.
        Returns a dict with 'tool_name' and 'arguments'.
        """
        tools_schema = self.registry.get_tools_schema()
        
        if not tools_schema:
            return {"error": "No tools registered."}

        system_prompt = """You are an intelligent Intent Router for an AI Code Orchestrator.
Your goal is to select the most appropriate tool to fulfill the user's request.
Analyze the request and available tools.
Return a JSON object with:
- "tool_name": The name of the tool to call.
- "arguments": The arguments to pass to the tool.
- "reasoning": Brief explanation of your choice.

If no tool matches, return "tool_name": null.
"""

        user_content = f"User Request: {user_request}\n"
        if context:
            user_content += f"Context: {context}\n"
            
        user_content += f"\nAvailable Tools Schema:\n{json.dumps(tools_schema, indent=2)}"

        try:
            response = await self.llm_client.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                model="gpt-4o", # Use smart model for routing
                temperature=0.0,
                json_mode=True
            )
            
            return json.loads(response.content)
            
        except Exception as e:
            logger.error(f"Routing failed: {e}")
            return {"error": str(e)}

    async def execute_route(self, route_result: Dict[str, Any]) -> Any:
        """
        Executes the tool specified in the route result.
        """
        tool_name = route_result.get("tool_name")
        if not tool_name:
            return {"status": "skipped", "reason": "No matching tool found."}
            
        tool_def = self.registry.get_tool(tool_name)
        if not tool_def:
             return {"error": f"Tool {tool_name} not found in registry."}
             
        args = route_result.get("arguments", {})
        
        try:
            logger.info(f"Executing tool: {tool_name} with args: {args}")
            # If the tool is async, await it
            if  logging.getLevelName(logger.level) == "DEBUG":
                 print(f"DEBUG: Executing {tool_name}")

            # Check if async
            import inspect
            if inspect.iscoroutinefunction(tool_def.func):
                result = await tool_def.func(**args)
            else:
                result = tool_def.func(**args)
                
            return result
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {"error": str(e)}
