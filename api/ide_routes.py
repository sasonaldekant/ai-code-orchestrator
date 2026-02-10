from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from pathlib import Path

from core.llm_client_v2 import LLMClientV2
from core.cost_manager import CostManager

router = APIRouter(prefix="/ide", tags=["ide"])
logger = logging.getLogger(__name__)

class IDEActionRequest(BaseModel):
    file_path: str
    selection: str
    action: str # EXPLAIN, FIX, REFACTOR, DOCSTRING, TEST
    context: Optional[str] = None

class IDEActionResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None

@router.post("/context-action", response_model=IDEActionResponse)
async def context_action(req: IDEActionRequest):
    try:
        # Initialize Dependencies
        cost_manager = CostManager()
        llm_client = LLMClientV2(cost_manager)
        
        # Prepare Prompt based on Action
        system_prompt = "You are an expert AI coding assistant."
        user_prompt = ""
        
        file_context = f"File: {req.file_path}\n"
        if req.context:
            file_context += f"Context: {req.context}\n"
            
        if req.action.upper() == "EXPLAIN":
             system_prompt = "You are an expert tech lead and teacher."
             user_prompt = f"{file_context}\nExplain the following code selection clearly and concisely:\n\n```\n{req.selection}\n```"
             
        elif req.action.upper() == "FIX":
             system_prompt = "You are an expert debugger."
             user_prompt = f"{file_context}\nAnalyze and fix the bug in the following code selection. Return ONLY the fixed code block without markdown.\n\n```\n{req.selection}\n```"
             if req.context:
                 user_prompt += f"\nError/Issue: {req.context}"

        elif req.action.upper() == "REFACTOR":
             system_prompt = "You are a clean code expert."
             user_prompt = f"{file_context}\nRefactor the following code selection for better readability and performance. Return ONLY the refactored code block without markdown.\n\n```\n{req.selection}\n```"

        elif req.action.upper() == "DOCSTRING":
             system_prompt = "You are a documentation specialist."
             user_prompt = f"{file_context}\nGenerate a Python docstring (or appropriate comment block) for the following code selection. Return ONLY the docstring.\n\n```\n{req.selection}\n```"
             
        elif req.action.upper() == "TEST":
             system_prompt = "You are a QA automation engineer."
             user_prompt = f"{file_context}\nGenerate a unit test for the following code selection. Return ONLY the test code.\n\n```\n{req.selection}\n```"
             
        else:
            return IDEActionResponse(success=False, error=f"Unknown action: {req.action}")

        # Execute
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Use gpt-4o for quality
        response = await llm_client.complete(messages, model="gpt-4o", temperature=0.2)
        
        return IDEActionResponse(success=True, result=response.content)

    except Exception as e:
        logger.error(f"IDE Action Failed: {e}")
        return IDEActionResponse(success=False, error=str(e))
