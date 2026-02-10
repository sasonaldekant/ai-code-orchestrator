"""
Migration Agent for AI Code Orchestrator v3.0

Specializes in analyzing breaking changes between software versions and
generating structured migration plans.
"""

from __future__ import annotations

import logging
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from core.llm_client_v2 import LLMClientV2

logger = logging.getLogger(__name__)

@dataclass
class MigrationStep:
    file: str
    description: str
    original_code_snippet: str
    new_code_snippet: str
    rationale: str

@dataclass
class MigrationPlan:
    description: str
    breaking_changes: List[str]
    steps: List[MigrationStep]
    risk_level: str  # "Low", "Medium", "High"

class MigrationAgent:
    """
    Analyzes code differences and orchestrates migration tasks.
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        self.llm_client = llm_client or LLMClientV2()
        self.model = "migration_specialist"

    async def analyze_breaking_changes(self, old_code: str, new_code: str) -> List[str]:
        """
        Compares two snippets/modules to find breaking signature changes.
        """
        prompt = f"""
        Analyze the following code versions and identify BREAKING CHANGES.
        Focus on:
        - Function signature changes (parameters, return types)
        - Removed functions/classes
        - Logic shifts that change expected behavior
        
        OLD CODE:
        ```python
        {old_code}
        ```
        
        NEW CODE:
        ```python
        {new_code}
        ```
        
        Return a JSON list of strings describing each breaking change.
        """
        
        messages = [
            {"role": "system", "content": "You are a Migration Specialist Agent. Output only valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm_client.complete(
            messages=messages,
            model=self.model
        )
        
        try:
            return json.loads(response.content)
        except Exception as e:
            logger.error(f"Failed to parse breaking changes: {e}")
            return ["Error analyzing changes"]

    async def generate_migration_plan(self, request: str, affected_files: List[str]) -> MigrationPlan:
        """
        Generates a detailed plan to migrate codebases to a newer version.
        """
        prompt = f"""
        Create a detailed Migration Plan for the following request: "{request}"
        Affected files: {affected_files}
        
        The plan must be a JSON object with:
        - description: string
        - breaking_changes: list of strings
        - steps: list of objects (file, description, original_code_snippet, new_code_snippet, rationale)
        - risk_level: "Low", "Medium", or "High"
        """
        
        messages = [
            {"role": "system", "content": "You are a Migration Specialist Agent. Output only valid JSON matching the MigrationPlan schema."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.llm_client.complete(
            messages=messages,
            model=self.model
        )
        
        try:
            data = json.loads(response.content)
            steps = [MigrationStep(**s) for s in data.get("steps", [])]
            return MigrationPlan(
                description=data.get("description", "Migration Plan"),
                breaking_changes=data.get("breaking_changes", []),
                steps=steps,
                risk_level=data.get("risk_level", "Medium")
            )
        except Exception as e:
            logger.error(f"Failed to parse migration plan: {e}")
            raise ValueError(f"Invalid migration plan generated: {e}")
