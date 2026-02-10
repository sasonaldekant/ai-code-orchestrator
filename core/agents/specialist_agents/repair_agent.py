"""
Repair Agent ("The Auto-Fixer")
Autonomous agent that attempts to fix code errors by analyzing logs, 
investigating the codebase, and applying patches.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path

from core.llm_client_v2 import LLMClientV2
from core.agents.specialist_agents.retrieval_agent import RetrievalAgent
from core.registry import register_tool
from core.memory.experience_db import ExperienceDB

logger = logging.getLogger(__name__)

class RepairAgent:
    def __init__(self, llm_client: LLMClientV2):
        self.llm = llm_client
        self.investigator = RetrievalAgent(llm_client) # Use shared LLM
        self.experience_db = ExperienceDB()

    @register_tool(
        name="auto_fix",
        description="Autonomous agent that investigates error logs and applies fixes to code.",
        category="debugging"
    )
    async def auto_fix(self, error_log: str, test_command: str) -> Dict[str, Any]:
        """
        Attempts to fix the error described in the log.
        Returns: { "success": bool, "summary": str, "diff": str }
        """
        logger.info(f"Starting Auto-Fix for error in: {test_command}")
        
        # 1. Investigate Root Cause
        investigation_query = f"""
        I have a test failure or runtime error.
        Command: {test_command}
        Error Log:
        {error_log[:2000]}
        
        Task: Find the file and line number causing this error. Explain the root cause.
        """
        
        findings = await self.investigator.run(investigation_query)
        logger.info(f"Investigation Findings: {findings[:200]}")
        
        # Prepare Prompt with Experience
        past_fixes = self.experience_db.find_similar_error(error_log[:500]) # truncated for search key efficiency
        
        experience_context = ""
        if past_fixes:
            experience_context = "\n\n[PAST SUCCESSFUL FIXES FOR SIMILAR ERRORS]:\n"
            for exp in past_fixes:
                experience_context += f"- Error: {exp['error_pattern'][:100]}...\n  Fix Strategy: {exp['fix_strategy']}\n"

        fix_prompt = f"""
        }}
        """
        
        try:
            response_obj = await self.llm.complete(
                messages=[{"role": "user", "content": fix_prompt}],
                model="gpt-4o",
                json_mode=True
            )
            import json
            plan = json.loads(response_obj.content)
            
            target_file = Path(plan["file_path"])
            if not target_file.exists():
                # Try to fuzzy match or use absolute path if provided
                 return {"success": False, "summary": f"Target file not found: {plan['file_path']}"}
            
            # 3. Apply Fix (Safety: Write to file)
            # In a real system, we might want to create a branch or patch file.
            # For this MVP, we overwrite.
            original_content = target_file.read_text(encoding='utf-8')
            
            # Simple safety check: don't overwrite with empty string
            if len(plan["fixed_content"]) < 10:
                return {"success": False, "summary": "Generated fix was too short/empty."}
                
            target_file.write_text(plan["fixed_content"], encoding='utf-8')
            
            return {
                "success": True, 
                "summary": f"Fixed {target_file}. Analysis: {plan['analysis']}",
                "original_content": original_content # usable for rollback
            }
            
        except Exception as e:
            logger.error(f"Auto-Fix failed: {e}")
            return {"success": False, "summary": f"Error during fix generation: {str(e)}"}
