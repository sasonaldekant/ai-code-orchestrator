"""
Capability Registry ("The Cortex")
Central repository for all system tools and capabilities.
Allows dynamic discovery and schema generation for LLM routing.
"""

import inspect
import json
import logging
from typing import Callable, Dict, Any, List, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel

logger = logging.getLogger(__name__)

@dataclass
class ToolDefinition:
    name: str
    description: str
    func: Callable
    parameters: Dict[str, Any]
    category: str = "general"

class CapabilityRegistry:
    _instance = None
    _tools: Dict[str, ToolDefinition] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CapabilityRegistry, cls).__new__(cls)
        return cls._instance

    @classmethod
    def register_tool(cls, name: str, description: str, category: str = "general"):
        """
        Decorator to register a function as a tool.
        Automatic schema generation from type hints (if pydantic model or simple types).
        """
        def decorator(func: Callable):
            # Extract parameters using inspect
            sig = inspect.signature(func)
            params = {}
            required = []
            
            for param_name, param in sig.parameters.items():
                if param_name == "self": continue
                
                param_type = "string" # default
                if param.annotation == int: param_type = "integer"
                elif param.annotation == bool: param_type = "boolean"
                elif param.annotation == float: param_type = "number"
                elif param.annotation == dict: param_type = "object"
                elif param.annotation == list: param_type = "array"
                
                # Handle Pydantic models as annotations deep inspection? 
                # For now keep it simple: generic object or simple types.
                # If complex Pydantic model is passed, we might need to export its schema.
                
                params[param_name] = {
                    "type": param_type,
                    "description": f"Parameter {param_name}" # ideally parse docstring
                }
                if param.default == inspect.Parameter.empty:
                    required.append(param_name)

            tool_def = ToolDefinition(
                name=name,
                description=description,
                func=func,
                parameters={
                    "type": "object",
                    "properties": params,
                    "required": required
                },
                category=category
            )
            
            cls._tools[name] = tool_def
            logger.info(f"Registered tool: {name}")
            return func
        return decorator

    @classmethod
    def get_tool(cls, name: str) -> Optional[ToolDefinition]:
        return cls._tools.get(name)

    @classmethod
    def get_tools_schema(cls) -> List[Dict[str, Any]]:
        """
        Returns the list of tool definitions in OpenAI 'functions' or 'tools' format.
        """
        schemas = []
        for name, tool in cls._tools.items():
            schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            })
        return schemas

    @classmethod
    def list_tools(cls) -> List[str]:
        return list(cls._tools.keys())

# Global Decorator alias
register_tool = CapabilityRegistry.register_tool
