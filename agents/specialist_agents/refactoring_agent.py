"""
Refactoring Agent for coordinating multi-file code changes.
"""

import logging
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from core.llm_client_v2 import LLMClientV2

logger = logging.getLogger(__name__)

@dataclass
class RefactoringPlan:
    """Structure for a proposed refactoring plan."""
    description: str
    affected_files: List[str]
    steps: List[Dict[str, Any]] # Each step: {"file": str, "description": str, "code": str}
    rollback_strategy: str

class RefactoringAgent:
    """
    Analyzes code zavisnosti and orchestrates sweeping refactoring changes.
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        self.llm_client = llm_client or LLMClientV2()
        self.model = "refactoring_specialist"

    async def analyze_dependencies(self, files: List[str], project_context: str = "") -> List[str]:
        """
        Identify files that may be impacted by changes to the input files.
        """
        prompt = f"""
        Analyze the dependencies for the following files: {', '.join(files)}
        Project Context: {project_context}
        
        Identify any other files in the project that depend on these or are tightly coupled.
        Return a JSON list of file paths.
        
        Output format: ["path/to/file1.py", "path/to/file2.py"]
        """
        
        response = await self.llm_client.complete(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            json_mode=True
        )
        
        try:
            impacted = json.loads(response.content)
            return list(set(files + impacted))
        except:
            logger.error("Failed to parse dependency analysis result.")
            return files

    async def plan_refactoring(self, request: str, scope_files: List[str]) -> RefactoringPlan:
        """
        Generate a detailed plan for refactoring.
        """
        prompt = f"""
        Refactoring Request: {request}
        Scope: {', '.join(scope_files)}
        
        Generate a multi-file refactoring plan.
        Provide a JSON output with the following structure:
        {{
            "description": "Short summary",
            "affected_files": ["file1", "file2"],
            "steps": [
                {{
                    "file": "path/to/file",
                    "description": "What to change",
                    "code": "Full new code for this file"
                }}
            ],
            "rollback_strategy": "How to undo if logic fails"
        }}
        """
        
        response = await self.llm_client.complete(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            json_mode=True
        )
        
        data = json.loads(response.content)
        return RefactoringPlan(**data)
