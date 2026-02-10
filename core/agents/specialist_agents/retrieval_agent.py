"""
Retrieval Agent ("The Investigator") for deep codebase exploration.
Uses a ReAct-style loop to actively search and read files.
"""

import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import os

from core.llm_client import LLMClient
from core.registry import register_tool

logger = logging.getLogger(__name__)

class RetrievalAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.max_steps = 10
        self.root_dir = Path(os.getcwd())

    @register_tool(
        name="deep_search",
        description="Investigates the codebase to answer complex questions using a multi-step plan.",
        category="research"
    )
    async def run(self, query: str, context: Optional[Dict] = None, initial_plan: Optional[str] = None) -> str:
        """
        Executes the investigation loop.
        """
        history = []
        history.append(f"Task: {query}")
        
        if initial_plan:
            history.append(f"Recommended Plan (Follow this strictly):\n{initial_plan}")
            
        history.append("Available Tools: search_code(query), read_file(path), list_dir(path)")
        
        for step in range(self.max_steps):
            # 1. Plan
            prompt = self._build_prompt(history)
            
            # Use LLMClientV2 interface
            resp_obj = await self.llm.complete(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4o", 
                temperature=0
            )
            response = resp_obj.content
            
            history.append(f"Thought: {response}")
            
            # 2. Parse Action
            action = self._parse_action(response)
            
            if action['type'] == 'finish':
                return action['content']
            
            # 3. Execute
            observation = self._execute_tool(action)
            history.append(f"Observation: {observation}")
            
        return "Max steps reached. Investigation incomplete."

    def _build_prompt(self, history: List[str]) -> str:
        return "\n".join(history) + "\n\nNext Thought (or 'FINAL ANSWER: ...'):"

    def _parse_action(self, response: str) -> Dict[str, Any]:
        if "FINAL ANSWER:" in response:
            return {"type": "finish", "content": response.split("FINAL ANSWER:")[1].strip()}
        
        # Simple parsing for demo (robust parsing would use Regex or JSON mode)
        # Expected format: Action: tool_name(args)
        if "Action:" in response:
            try:
                line = [l for l in response.split('\n') if "Action:" in l][0]
                cmd = line.split("Action:")[1].strip()
                tool_name = cmd.split("(")[0]
                args = cmd.split("(")[1].rstrip(")")
                return {"type": "tool", "name": tool_name, "args": args}
            except:
                return {"type": "error", "content": "Failed to parse action."}
        
        return {"type": "finish", "content": response} # Fallback

    def _execute_tool(self, action: Dict) -> str:
        if action['type'] == 'error':
            return action['content']
            
        name = action['name']
        args = action['args']
        
        try:
            if name == "search_code":
                # Security: simplistic check
                if ";" in args or "|" in args: return "Security Error: Illegal characters"
                # Use ripgrep or grep
                result = subprocess.run(["grep", "-r", args, "."], cwd=self.root_dir, capture_output=True, text=True)
                return result.stdout[:2000] # Truncate
            
            elif name == "read_file":
                path = (self.root_dir / args.strip("'").strip('"')).resolve()
                if not path.is_file(): return "File not found."
                return path.read_text(encoding='utf-8')[:3000] # Truncate
            
            elif name == "list_dir":
                path = (self.root_dir / args.strip("'").strip('"')).resolve()
                if not path.is_dir(): return "Directory not found."
                files = [f.name for f in path.iterdir()]
                return ", ".join(files[:50])
                
            else:
                return f"Unknown tool: {name}"
        except Exception as e:
            return f"Tool Error: {e}"
