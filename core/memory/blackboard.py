"""
Blackboard memory for swarm coordination.
Provides a shared state for multiple agents to collaborate and share information.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class Blackboard:
    """
    Shared memory system for Swarm Intelligence.
    Allows agents to coordinate tasks, share observations, and track progress.
    """

    def __init__(self) -> None:
        self._shared_context: Dict[str, Any] = {}
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._observations: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def update_context(self, key: str, value: Any) -> None:
        """Add or update a piece of shared information."""
        async with self._lock:
            self._shared_context[key] = value
            logger.info(f"Blackboard: Updated context '{key}'")

    async def get_context(self, key: str) -> Optional[Any]:
        """Retrieve shared information from the blackboard."""
        async with self._lock:
            return self._shared_context.get(key)

    async def register_task(self, task_id: str, description: str, assigned_to: Optional[str] = None, depends_on: Optional[List[str]] = None) -> None:
        """Register a new sub-task for the swarm."""
        async with self._lock:
            self._tasks[task_id] = {
                "id": task_id,
                "description": description,
                "status": "pending",
                "assigned_to": assigned_to,
                "depends_on": depends_on or [],
                "result": None,
                "created_at": datetime.utcnow().isoformat(),
            }
            logger.info(f"Blackboard: Registered task '{task_id}' -> {description} (Depends on: {depends_on})")

    async def update_task_status(self, task_id: str, status: str, result: Any = None) -> None:
        """Update the status and optional result of a task."""
        async with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = status
                if result is not None:
                    self._tasks[task_id]["result"] = result
                self._tasks[task_id]["updated_at"] = datetime.utcnow().isoformat()
                logger.info(f"Blackboard: Task '{task_id}' status updated to '{status}'")
            else:
                logger.warning(f"Blackboard: Attempted to update non-existent task '{task_id}'")

    async def add_observation(self, agent_name: str, observation: str) -> None:
        """Add a general observation or insight from an agent."""
        async with self._lock:
            self._observations.append({
                "agent": agent_name,
                "content": observation,
                "timestamp": datetime.utcnow().isoformat()
            })
            logger.info(f"Blackboard: Agent '{agent_name}' added observation.")

    async def get_all_tasks(self) -> Dict[str, Any]:
        """Return all tasks and their current states."""
        async with self._lock:
            return self._tasks.copy()

    async def get_summary(self) -> Dict[str, Any]:
        """Return a summary of the current state of the blackboard."""
        async with self._lock:
            return {
                "task_count": len(self._tasks),
                "completed_tasks": len([t for t in self._tasks.values() if t["status"] == "completed"]),
                "observations_count": len(self._observations),
                "last_update": datetime.utcnow().isoformat()
            }

    async def get_dag(self) -> Dict[str, Any]:
        """Return the task list formatted as a DAG for UI visualization."""
        async with self._lock:
            nodes = []
            links = []
            for tid, tinfo in self._tasks.items():
                nodes.append({
                    "id": tid,
                    "label": tinfo["description"][:30] + "..." if len(tinfo["description"]) > 30 else tinfo["description"],
                    "status": tinfo["status"],
                    "agent": tinfo["assigned_to"]
                })
                for dep in tinfo.get("depends_on", []):
                    links.append({"source": dep, "target": tid})
            
            return {"nodes": nodes, "links": links}

    async def get_observations(self) -> List[Dict[str, Any]]:
        """Return all observations."""
        async with self._lock:
            return self._observations.copy()
