"""
Swarm Manager agent.
Responsible for decomposing complex requests into specialized tasks and coordinating agents via the Blackboard.
"""

from __future__ import annotations

import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from ...memory.blackboard import Blackboard

logger = logging.getLogger(__name__)

class SwarmManagerAgent:
    """
    The central coordinator for swarm activities.
    Decomposes requests and manages agent assignments.
    """

    def __init__(self, orchestrator) -> None:
        self.orchestrator = orchestrator
        self.prompt_path = Path("prompts/specialist_prompts/swarm_manager.txt")
        self.blackboard = Blackboard()

    async def decompose(self, request: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Analyze a request and return a list of tasks.
        """
        # Build prompt
        prompt_template = self._load_prompt()
        prompt = prompt_template.format(
            request=request,
            context=json.dumps(context or {}, indent=2),
            completed_tasks="None" # Initial decomposition
        )

        # Select model (Swarm Manager needs high reasoning, use architect or custom config)
        cfg = self.orchestrator.model_router.get_model_for_phase("architect")

        messages = [
            {"role": "system", "content": "You are the Swarm Manager. Decompose requests into parallelizable tasks. Output strictly JSON."},
            {"role": "user", "content": prompt}
        ]

        logger.info("SwarmManager: Decomposing request...")
        response = await self.orchestrator.llm_client.complete(
            messages=messages,
            model=cfg.model,
            temperature=0.1, # Low temperature for structured output
            json_mode=True
        )

        tasks = self._parse_tasks(response.content)
        
        # Register tasks on Blackboard
        for task in tasks:
            await self.blackboard.register_task(
                task_id=task.get("id"),
                description=task.get("description"),
                assigned_to=task.get("agent"),
                depends_on=task.get("dependencies", [])
            )
        
        return tasks

    async def execute_swarm(self, request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Full swarm execution loop.
        1. Decompose.
        2. Execute tasks in parallel (respecting dependencies).
        3. Synthesize result.
        """
        tasks = await self.decompose(request, context)
        if not tasks:
            return {"status": "error", "message": "Failed to decompose request."}

        # Initialize tracking
        task_map = {t["id"]: t for t in tasks}
        pending_tasks = set(task_map.keys())
        running_tasks = set()
        completed_success = set()
        completed_failed = set()

        logger.info(f"SwarmManager: Starting execution of {len(tasks)} tasks.")

        while pending_tasks or running_tasks:
            # 1. Identify tasks ready to run (all dependencies met)
            ready_to_run = []
            for tid in list(pending_tasks):
                deps = task_map[tid].get("dependencies", [])
                if all(dep_id in completed_success for dep_id in deps):
                    ready_to_run.append(tid)

            # 2. Start ready tasks
            for tid in ready_to_run:
                pending_tasks.remove(tid)
                running_tasks.add(tid)
                asyncio.create_task(self._run_task(tid, task_map[tid], context))

            # 3. Wait for at least one task to complete or a short timeout
            if running_tasks:
                # This is a bit complex for a simple loop, we'll use a queue or event-based approach in a real impl
                # For this version, we'll poll the blackboard for status updates
                await asyncio.sleep(1) 
                
                # Check status from blackboard
                all_status = await self.blackboard.get_all_tasks()
                for tid in list(running_tasks):
                    status = all_status.get(tid, {}).get("status")
                    if status == "completed":
                        running_tasks.remove(tid)
                        completed_success.add(tid)
                        logger.info(f"SwarmManager: Task '{tid}' completed successfully.")
                    elif status == "failed":
                        running_tasks.remove(tid)
                        completed_failed.add(tid)
                        logger.error(f"SwarmManager: Task '{tid}' failed. Triggering pivot.")
                        
                        # [Phase 19] Fail-Safe Pivoting: Re-decompose remaining tasks
                        new_tasks = await self._pivot_swarm(request, context, completed_success, completed_failed)
                        if new_tasks:
                            # Update task_map and pending_tasks with new decomposition
                            for nt in new_tasks:
                                if nt["id"] not in completed_success and nt["id"] not in completed_failed:
                                    task_map[nt["id"]] = nt
                                    pending_tasks.add(nt["id"])
                            logger.info(f"SwarmManager: Swarm pivoted with {len(new_tasks)} updated tasks.")
                        else:
                            logger.warning("SwarmManager: Pivot failed to generate new tasks. Continuing with remaining.")

            if not ready_to_run and running_tasks:
               # Just waiting for current runs to finish
               continue
            
            if not ready_to_run and not running_tasks and pending_tasks:
                logger.error("SwarmManager: Deadlock detected! Some tasks have unmet or failed dependencies.")
                break

        summary = await self.blackboard.get_summary()
        return {
            "status": "completed" if not pending_tasks and not running_tasks and not completed_failed else "partial",
            "summary": summary,
            "tasks_completed": list(completed_success),
            "tasks_failed": list(completed_failed),
            "tasks_unmet": list(pending_tasks)
        }

    async def _run_task(self, task_id: str, task_info: Dict[str, Any], context: Optional[Dict[str, Any]]) -> None:
        """
        Execute a single task using the assigned agent.
        """
        agent_type = task_info.get("agent")
        description = task_info.get("description")
        
        await self.blackboard.update_task_status(task_id, "running")
        
        try:
            logger.info(f"SwarmManager: Executing task '{task_id}' with agent '{agent_type}'")
            
            # [Phase 19] Adaptive Scaling: Detect complexity
            is_complex = self._detect_complexity(description)
            model_override = None
            if is_complex:
                logger.info(f"SwarmManager: High complexity detected for '{task_id}'. Upscaling model.")
                # Upscale to a stronger model (e.g., architect's primary)
                cfg = self.orchestrator.model_router.get_model_for_phase("architect")
                model_override = cfg.model
                await self.blackboard.add_observation(
                    "SwarmManager", 
                    f"Upscaled task '{task_id}' to {model_override} due to detected complexity."
                )

            # Map agent types to Orchestrator phases or specialist agents
            result = None
            if agent_type.lower() in ["analyst", "architect", "implementation", "testing"]:
                # Use standard phase execution
                result = await self.orchestrator.run_phase(
                    phase=agent_type.lower(),
                    schema_name=self._get_schema_for_agent(agent_type),
                    context=context,
                    question=description,
                )
            else:
                logger.warning(f"SwarmManager: Agent type '{agent_type}' execution logic not fully integrated.")
                result = {"status": "unsupported_agent", "info": description}

            await self.blackboard.update_task_status(task_id, "completed", result=result)
        except Exception as e:
            logger.error(f"SwarmManager: Error in task '{task_id}': {e}")
            await self.blackboard.update_task_status(task_id, "failed", result=str(e))

    def _detect_complexity(self, description: str) -> bool:
        """Heuristic-based complexity detection."""
        complex_keywords = [
            "refactor", "migration", "security", "complex", "performance", 
            "breaking change", "multi-threading", "race condition", "auth"
        ]
        desc_lower = description.lower()
        return any(k in desc_lower for k in complex_keywords) or len(description) > 200

    async def _pivot_swarm(self, request: str, context: Optional[Dict[str, Any]], completed_success: set, completed_failed: set) -> List[Dict[str, Any]]:
        """
        Re-decompose the request given the current swarm state (successes/failures).
        """
        logger.info("SwarmManager: Pivoting strategy...")
        
        # Build prompt for re-decomposition
        prompt_template = self._load_prompt()
        status_summary = f"Success: {completed_success}, Failed: {completed_failed}"
        
        prompt = prompt_template.format(
            request=request,
            context=json.dumps(context or {}, indent=2),
            completed_tasks=status_summary
        )

        cfg = self.orchestrator.model_router.get_model_for_phase("architect")
        messages = [
            {"role": "system", "content": "You are the Swarm Manager in Pivot Mode. A task has failed. Re-decompose the remaining work into new tasks. Avoid repeating failed approaches."},
            {"role": "user", "content": prompt}
        ]

        try:
            response = await self.orchestrator.llm_client.complete(
                messages=messages,
                model=cfg.model,
                temperature=0.3, # Slightly higher temperature for "creative" pivoting
                json_mode=True
            )
            new_tasks = self._parse_tasks(response.content)
            
            # Register NEW tasks on Blackboard
            for task in new_tasks:
                if task.get("id") not in completed_success and task.get("id") not in completed_failed:
                    await self.blackboard.register_task(
                        task_id=task.get("id"),
                        description=task.get("description"),
                        assigned_to=task.get("agent"),
                        depends_on=task.get("dependencies", [])
                    )
            
            return new_tasks
        except Exception as e:
            logger.error(f"SwarmManager: Pivot decomposition failed: {e}")
            return []

    def _get_schema_for_agent(self, agent: str) -> str:
        mapping = {
            "analyst": "requirements",
            "architect": "architecture",
            "implementation": "implementation",
            "testing": "testing"
        }
        return mapping.get(agent.lower(), "generic_output")

    def _load_prompt(self) -> str:
        try:
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"SwarmManager prompt not found at {self.prompt_path}")
            return "Decompose: {request}. Context: {context}. Completed: {completed_tasks}"

    def _parse_tasks(self, content: str) -> List[Dict[str, Any]]:
        try:
            # Handle markdown blocks if present
            cleaned = content.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            
            data = json.loads(cleaned)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "tasks" in data:
                return data["tasks"]
            return []
        except json.JSONDecodeError:
            logger.error("SwarmManager: Failed to parse task list.")
            return []
