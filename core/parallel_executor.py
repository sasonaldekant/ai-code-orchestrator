"""
Parallel execution engine for concurrent task processing.

This module enables parallel execution of independent tasks to reduce
end-to-end latency. For example, backend and frontend implementation
can run concurrently, reducing total pipeline time by ~40%.

Features:
- Task dependency resolution
- Concurrent execution with asyncio.gather
- Resource pooling and limits
- Error handling with partial results
- Progress tracking

Version: 2.0.0
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of a task in the execution pipeline."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Task:
    """
    A single task to be executed.
    
    Attributes
    ----------
    id : str
        Unique task identifier.
    name : str
        Human-readable task name.
    executor : callable
        Async function to execute the task.
    dependencies : list
        Task IDs that must complete before this task.
    priority : int
        Execution priority (higher = sooner).
    timeout : int
        Maximum execution time in seconds.
    """
    id: str
    name: str
    executor: Callable[..., Any]
    kwargs: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    priority: int = 0
    timeout: int = 300  # 5 minutes default
    allow_failure: bool = False


@dataclass
class TaskResult:
    """Result of a single task execution."""
    task_id: str
    task_name: str
    status: TaskStatus
    output: Any
    error: Optional[str]
    start_time: float
    end_time: float
    duration: float
    tokens_used: int = 0
    cost: float = 0.0


@dataclass
class ExecutionPlan:
    """
    Execution plan with resolved dependencies.
    
    Tasks are organized into batches where each batch contains
    tasks that can run in parallel.
    """
    batches: List[List[Task]]
    total_tasks: int
    max_parallelism: int


@dataclass
class ExecutionResult:
    """Overall result of parallel execution."""
    task_results: Dict[str, TaskResult]
    total_duration: float
    successful_tasks: int
    failed_tasks: int
    total_tokens: int
    total_cost: float
    speedup_factor: float  # Compared to sequential execution


class ParallelExecutor:
    """
    Execute tasks in parallel with dependency resolution.
    
    The executor:
    1. Resolves task dependencies
    2. Groups tasks into parallel batches
    3. Executes each batch concurrently
    4. Handles errors and collects results
    5. Tracks metrics and progress
    
    Example
    -------
    >>> executor = ParallelExecutor(max_concurrent=3)
    >>> 
    >>> async def implement_backend(**kwargs):
    ...     # Implementation logic
    ...     return "Backend code"
    >>> 
    >>> async def implement_frontend(**kwargs):
    ...     # Implementation logic
    ...     return "Frontend code"
    >>> 
    >>> tasks = [
    ...     Task(
    ...         id="backend",
    ...         name="Backend Implementation",
    ...         executor=implement_backend,
    ...         kwargs={"spec": backend_spec}
    ...     ),
    ...     Task(
    ...         id="frontend",
    ...         name="Frontend Implementation",
    ...         executor=implement_frontend,
    ...         kwargs={"spec": frontend_spec}
    ...     )
    ... ]
    >>> 
    >>> result = await executor.execute(tasks)
    >>> print(f"Speedup: {result.speedup_factor:.1f}x")
    """
    
    def __init__(
        self,
        max_concurrent: int = 5,
        cost_manager: Optional[Any] = None
    ):
        self.max_concurrent = max_concurrent
        self.cost_manager = cost_manager
        self._semaphore = asyncio.Semaphore(max_concurrent)
    
    async def execute(
        self,
        tasks: List[Task],
        fail_fast: bool = False
    ) -> ExecutionResult:
        """
        Execute tasks with dependency resolution and parallelism.
        
        Parameters
        ----------
        tasks : list
            List of Task objects to execute.
        fail_fast : bool
            If True, stop execution on first failure.
        
        Returns
        -------
        ExecutionResult
            Aggregated results from all tasks.
        """
        logger.info(f"Starting parallel execution of {len(tasks)} tasks")
        start_time = time.time()
        
        # Build execution plan
        plan = self._build_execution_plan(tasks)
        logger.info(
            f"Execution plan: {len(plan.batches)} batches, "
            f"max parallelism: {plan.max_parallelism}"
        )
        
        # Execute batches sequentially, tasks within batch in parallel
        task_results = {}
        completed_tasks = set()
        
        for batch_num, batch in enumerate(plan.batches, 1):
            logger.info(f"Executing batch {batch_num}/{len(plan.batches)} ({len(batch)} tasks)")
            
            batch_results = await self._execute_batch(
                batch=batch,
                completed_tasks=completed_tasks,
                all_results=task_results
            )
            
            # Update results and completed set
            task_results.update(batch_results)
            completed_tasks.update(batch_results.keys())
            
            # Check for failures in fail_fast mode
            if fail_fast:
                failed = [
                    r for r in batch_results.values()
                    if r.status == TaskStatus.FAILED
                ]
                if failed:
                    logger.error(f"Fail-fast triggered: {len(failed)} tasks failed")
                    # Mark remaining tasks as skipped
                    for task in tasks:
                        if task.id not in task_results:
                            task_results[task.id] = TaskResult(
                                task_id=task.id,
                                task_name=task.name,
                                status=TaskStatus.SKIPPED,
                                output=None,
                                error="Skipped due to fail-fast",
                                start_time=time.time(),
                                end_time=time.time(),
                                duration=0.0
                            )
                    break
        
        # Aggregate results
        total_duration = time.time() - start_time
        
        successful = sum(
            1 for r in task_results.values()
            if r.status == TaskStatus.COMPLETED
        )
        failed = sum(
            1 for r in task_results.values()
            if r.status == TaskStatus.FAILED
        )
        
        total_tokens = sum(r.tokens_used for r in task_results.values())
        total_cost = sum(r.cost for r in task_results.values())
        
        # Calculate speedup (sequential time vs parallel time)
        sequential_duration = sum(r.duration for r in task_results.values())
        speedup = sequential_duration / total_duration if total_duration > 0 else 1.0
        
        logger.info(
            f"Execution complete: {successful}/{len(tasks)} successful, "
            f"speedup: {speedup:.2f}x, duration: {total_duration:.1f}s"
        )
        
        return ExecutionResult(
            task_results=task_results,
            total_duration=total_duration,
            successful_tasks=successful,
            failed_tasks=failed,
            total_tokens=total_tokens,
            total_cost=total_cost,
            speedup_factor=speedup
        )
    
    def _build_execution_plan(self, tasks: List[Task]) -> ExecutionPlan:
        """
        Resolve dependencies and organize tasks into parallel batches.
        
        Uses topological sorting to ensure dependencies are satisfied.
        """
        task_map = {task.id: task for task in tasks}
        batches = []
        remaining = set(task_map.keys())
        completed = set()
        
        while remaining:
            # Find tasks with satisfied dependencies
            ready = [
                task_id for task_id in remaining
                if all(dep in completed for dep in task_map[task_id].dependencies)
            ]
            
            if not ready:
                # Circular dependency or orphaned tasks
                logger.error(f"Cannot resolve dependencies for: {remaining}")
                # Add them anyway to avoid infinite loop
                ready = list(remaining)
            
            # Sort by priority
            ready.sort(key=lambda tid: task_map[tid].priority, reverse=True)
            
            batch = [task_map[tid] for tid in ready]
            batches.append(batch)
            
            remaining -= set(ready)
            completed.update(ready)
        
        max_parallelism = max(len(batch) for batch in batches) if batches else 0
        
        return ExecutionPlan(
            batches=batches,
            total_tasks=len(tasks),
            max_parallelism=max_parallelism
        )
    
    async def _execute_batch(
        self,
        batch: List[Task],
        completed_tasks: Set[str],
        all_results: Dict[str, TaskResult]
    ) -> Dict[str, TaskResult]:
        """Execute all tasks in a batch concurrently."""
        # Create coroutines for each task
        coroutines = [
            self._execute_task(task, all_results)
            for task in batch
        ]
        
        # Execute in parallel
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # Map results back to task IDs
        batch_results = {}
        for task, result in zip(batch, results):
            if isinstance(result, Exception):
                # Execution raised an exception
                batch_results[task.id] = TaskResult(
                    task_id=task.id,
                    task_name=task.name,
                    status=TaskStatus.FAILED,
                    output=None,
                    error=str(result),
                    start_time=time.time(),
                    end_time=time.time(),
                    duration=0.0
                )
            else:
                batch_results[task.id] = result
        
        return batch_results
    
    async def _execute_task(
        self,
        task: Task,
        all_results: Dict[str, TaskResult]
    ) -> TaskResult:
        """Execute a single task with timeout and error handling."""
        logger.info(f"Starting task: {task.name} (ID: {task.id})\n")
        start_time = time.time()
        
        # Acquire semaphore to limit concurrency
        async with self._semaphore:
            try:
                # Check cost budget if cost manager available
                if self.cost_manager and not self.cost_manager.can_proceed():
                    return TaskResult(
                        task_id=task.id,
                        task_name=task.name,
                        status=TaskStatus.FAILED,
                        output=None,
                        error="Cost budget exceeded",
                        start_time=start_time,
                        end_time=time.time(),
                        duration=time.time() - start_time
                    )
                
                # Inject dependency results into kwargs
                task_kwargs = task.kwargs.copy()
                for dep_id in task.dependencies:
                    if dep_id in all_results:
                        task_kwargs[f"{dep_id}_result"] = all_results[dep_id].output
                
                # Execute with timeout
                output = await asyncio.wait_for(
                    task.executor(**task_kwargs),
                    timeout=task.timeout
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                # Extract tokens/cost if available
                tokens_used = 0
                cost = 0.0
                if isinstance(output, dict):
                    tokens_used = output.get("tokens_used", 0)
                    cost = output.get("cost", 0.0)
                
                logger.info(
                    f"Task completed: {task.name} in {duration:.1f}s "
                    f"({tokens_used} tokens, ${cost:.4f})"
                )
                
                return TaskResult(
                    task_id=task.id,
                    task_name=task.name,
                    status=TaskStatus.COMPLETED,
                    output=output,
                    error=None,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    tokens_used=tokens_used,
                    cost=cost
                )
            
            except asyncio.TimeoutError:
                logger.error(f"Task timed out: {task.name} (>{task.timeout}s)")
                return TaskResult(
                    task_id=task.id,
                    task_name=task.name,
                    status=TaskStatus.FAILED,
                    output=None,
                    error=f"Timeout after {task.timeout}s",
                    start_time=start_time,
                    end_time=time.time(),
                    duration=time.time() - start_time
                )
            
            except Exception as e:
                logger.error(f"Task failed: {task.name} - {e}", exc_info=True)
                
                if task.allow_failure:
                    logger.warning(f"Task failure allowed: {task.name}")
                
                return TaskResult(
                    task_id=task.id,
                    task_name=task.name,
                    status=TaskStatus.FAILED,
                    output=None,
                    error=str(e),
                    start_time=start_time,
                    end_time=time.time(),
                    duration=time.time() - start_time
                )
    
    def get_metrics(self, result: ExecutionResult) -> Dict[str, Any]:
        """Extract metrics from execution result."""
        return {
            "total_tasks": len(result.task_results),
            "successful_tasks": result.successful_tasks,
            "failed_tasks": result.failed_tasks,
            "success_rate": result.successful_tasks / len(result.task_results) if result.task_results else 0,
            "total_duration_seconds": result.total_duration,
            "speedup_factor": result.speedup_factor,
            "total_tokens": result.total_tokens,
            "total_cost_usd": result.total_cost,
            "avg_task_duration": sum(
                r.duration for r in result.task_results.values()
            ) / len(result.task_results) if result.task_results else 0
        }


class BatchLLMProcessor:
    """
    Specialized processor for batch LLM operations using ParallelExecutor.
    Optimized for bulk content generation using cost-effective models (e.g. Haiku).
    """
    def __init__(
        self, 
        llm_client: Any, 
        model: str = "claude-3-5-haiku",
        max_concurrent: int = 10
    ):
        self.llm_client = llm_client
        self.model = model
        self.executor = ParallelExecutor(max_concurrent=max_concurrent)

    async def process_batch(
        self,
        items: List[Any],
        processing_function: Callable[[Any], List[Dict]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        id_prefix: str = "batch_task"
    ) -> List[Any]:
        """
        Process a batch of items in parallel using LLM.
        
        Args:
            items: List of items to process (e.g. file paths, code snippets)
            processing_function: Function that takes an item and returns LLM messages
            system_prompt: Optional override for system prompt
            temperature: LLM temperature
            id_prefix: Prefix for task IDs
            
        Returns:
            List of results in same order as items.
        """
        if not items:
            return []
            
        tasks = []
        for i, item in enumerate(items):
            messages = processing_function(item)
            
            # Prepend system prompt if provided
            final_messages = []
            if system_prompt:
                final_messages.append({"role": "system", "content": system_prompt})
            
            # Append other messages
            for m in messages:
                if m["role"] == "system" and system_prompt:
                    continue # Skip existing system if overridden? Or append? Simple override here.
                final_messages.append(m)
                
            tasks.append(
                Task(
                    id=f"{id_prefix}_{i}",
                    name=f"Batch {id_prefix} #{i}",
                    executor=self._safe_llm_call,
                    kwargs={
                        "messages": final_messages,
                        "model": self.model,
                        "temperature": temperature
                    }
                )
            )
            
        logger.info(f"Batch processing {len(tasks)} items with model {self.model}...")
        result = await self.executor.execute(tasks)
        
        # Extract outputs in order based on index
        ordered_outputs = []
        for i in range(len(items)):
            task_id = f"{id_prefix}_{i}"
            res = result.task_results.get(task_id)
            
            output_content = None
            if res and res.status == TaskStatus.COMPLETED:
                # Handle LLMResponse object or raw dict
                if hasattr(res.output, "content"):
                    output_content = res.output.content
                elif isinstance(res.output, dict) and "content" in res.output:
                    output_content = res.output["content"]
                else:
                    output_content = str(res.output)
            else:
                error = res.error if res else "Unknown error"
                logger.error(f"Task {task_id} failed: {error}")
                output_content = None
                
            ordered_outputs.append(output_content)
                
        return ordered_outputs

    async def _safe_llm_call(self, messages, model, temperature):
        """Wrapper for LLM call that fits Task executor signature."""
        return await self.llm_client.complete(
            messages=messages,
            model=model,
            temperature=temperature
        )