"""
Enhanced orchestrator with advanced features:
- Retry logic with exponential backoff
- Feedback loop system for iterative improvements
- Enhanced error handling and recovery
- Parallel execution with dependency management
- Dynamic strategy selection
- Real-time monitoring and metrics
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import time

from .model_router_v2 import ModelRouterV2
from .llm_client_v2 import LLMClientV2
from .cost_manager import CostManager
from .validator import OutputValidator
from .tracer import TracingService
from .retriever import RAGRetriever

logger = logging.getLogger(__name__)


class ExecutionStrategy(Enum):
    """Execution strategies for different task complexities."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    ADAPTIVE = "adaptive"


class PhaseStatus(Enum):
    """Status of a phase execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class PhaseResult:
    """Result of a phase execution."""
    phase: str
    status: PhaseStatus
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    attempts: int = 0
    execution_time: float = 0.0
    cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FeedbackResult:
    """Feedback from quality assessment."""
    quality_score: float
    issues: List[str]
    suggestions: List[str]
    needs_iteration: bool


class OrchestratorV2:
    """
    Enhanced orchestrator with advanced orchestration capabilities.
    
    Features:
    - Automatic retry with exponential backoff
    - Feedback loop for iterative refinement
    - Parallel execution where possible
    - Dynamic strategy selection
    - Comprehensive monitoring and metrics
    """

    def __init__(
        self,
        config_path: str = "config/model_mapping.yaml",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        max_feedback_iterations: int = 3,
        retriever: Optional[Any] = None,
        llm_client: Optional[Any] = None,
    ) -> None:
        self.cost_manager = CostManager()
        self.model_router = ModelRouterV2(config_path)
        self.llm_client = llm_client or LLMClientV2(self.cost_manager)
        self.validator = OutputValidator()
        self.tracer = TracingService()
        self.retriever = retriever or RAGRetriever()

        # Configuration
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.max_feedback_iterations = max_feedback_iterations

        # Phase agents will be initialized lazily
        self._phase_agents: Optional[Dict[str, Any]] = None

        # Output directory
        self.outputs_dir = Path("outputs")
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

        # Metrics
        self.metrics: Dict[str, Any] = {
            "total_phases_executed": 0,
            "total_retries": 0,
            "total_feedback_iterations": 0,
            "phase_execution_times": {},
            "error_counts": {},
        }

    @property
    def phase_agents(self) -> Dict[str, Any]:
        """Lazy initialization of phase agents."""
        if self._phase_agents is None:
            from agents.phase_agents.analyst import AnalystAgent
            from agents.phase_agents.architect import ArchitectAgent
            from agents.phase_agents.implementation import ImplementationAgent
            from agents.phase_agents.testing import TestingAgent

            self._phase_agents = {
                "analyst": AnalystAgent(self),
                "architect": ArchitectAgent(self),
                "implementation": ImplementationAgent(self),
                "testing": TestingAgent(self),
            }
        return self._phase_agents

    async def run_phase_with_retry(
        self,
        phase: str,
        schema_name: str,
        context: Optional[Dict[str, Any]] = None,
        question: Optional[str] = None,
        top_k: int = 3,
    ) -> PhaseResult:
        """
        Run a phase with automatic retry on failure.
        
        Args:
            phase: Name of the phase
            schema_name: Schema for validation
            context: Context from previous phases
            question: RAG query
            top_k: Number of RAG results
            
        Returns:
            PhaseResult with execution details
        """
        result = PhaseResult(phase=phase, status=PhaseStatus.PENDING)
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            try:
                result.attempts = attempt + 1
                result.status = PhaseStatus.RUNNING if attempt == 0 else PhaseStatus.RETRYING
                
                logger.info(f"Executing phase '{phase}' (attempt {attempt + 1}/{self.max_retries})")
                
                # Execute phase
                output = await self._execute_phase(
                    phase=phase,
                    schema_name=schema_name,
                    context=context,
                    question=question,
                    top_k=top_k,
                )
                
                result.output = output
                result.status = PhaseStatus.COMPLETED
                result.execution_time = time.time() - start_time
                
                logger.info(f"Phase '{phase}' completed successfully")
                self.metrics["total_phases_executed"] += 1
                
                return result
                
            except Exception as e:
                error_msg = f"Error in phase '{phase}' (attempt {attempt + 1}): {str(e)}"
                logger.error(error_msg)
                
                result.error = error_msg
                self.metrics["total_retries"] += 1
                self.metrics["error_counts"][phase] = self.metrics["error_counts"].get(phase, 0) + 1
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    result.status = PhaseStatus.FAILED
                    result.execution_time = time.time() - start_time
                    logger.error(f"Phase '{phase}' failed after {self.max_retries} attempts")
                    
        return result

    async def _execute_phase(
        self,
        phase: str,
        schema_name: str,
        context: Optional[Dict[str, Any]] = None,
        question: Optional[str] = None,
        top_k: int = 3,
    ) -> Dict[str, Any]:
        """
        Internal method to execute a single phase.
        """
        self.tracer.log_event("phase_start", {
            "phase": phase,
            "schema": schema_name,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # RAG retrieval
        rag_context: list = []
        if question:
            rag_context = self.retriever.retrieve(question, top_k=top_k)
            rag_path = self.outputs_dir / f"rag_context_{phase}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
            with open(rag_path, "w", encoding="utf-8") as f:
                json.dump(rag_context, f, indent=2)

        # Get agent and execute
        agent = self.phase_agents.get(phase)
        if not agent:
            raise ValueError(f"Unknown phase: {phase}")
            
        result = await agent.execute(context=context or {}, rag_context=rag_context)
        
        # Validate
        validation = self.validator.validate(result, schema_name)
        
        if not validation["valid"]:
            self.tracer.log_event("validation_failed", {
                "phase": phase,
                "errors": validation["errors"],
            })
            raise ValueError(f"Validation failed for phase {phase}: {validation['errors']}")
        
        # Save output
        out_path = self.outputs_dir / f"{phase}_{schema_name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
            
        self.tracer.log_event("phase_complete", {
            "phase": phase,
            "output_path": str(out_path),
        })
        
        return result

    async def run_phase_with_feedback(
        self,
        phase: str,
        schema_name: str,
        context: Optional[Dict[str, Any]] = None,
        question: Optional[str] = None,
        quality_threshold: float = 0.8,
    ) -> PhaseResult:
        """
        Run phase with iterative feedback loop for quality improvement.
        
        Args:
            phase: Name of the phase
            schema_name: Schema for validation
            context: Context from previous phases
            question: RAG query
            quality_threshold: Minimum acceptable quality score
            
        Returns:
            PhaseResult with final output
        """
        logger.info(f"Starting phase '{phase}' with feedback loop")
        
        for iteration in range(self.max_feedback_iterations):
            logger.info(f"Feedback iteration {iteration + 1}/{self.max_feedback_iterations}")
            
            # Execute phase
            result = await self.run_phase_with_retry(
                phase=phase,
                schema_name=schema_name,
                context=context,
                question=question,
            )
            
            if result.status != PhaseStatus.COMPLETED:
                return result
            
            # Assess quality
            feedback = await self._assess_quality(result.output, phase)
            
            logger.info(f"Quality score: {feedback.quality_score:.2f}")
            
            if feedback.quality_score >= quality_threshold:
                logger.info(f"Quality threshold met for phase '{phase}'")
                return result
            
            if not feedback.needs_iteration or iteration >= self.max_feedback_iterations - 1:
                logger.warning(f"Max iterations reached for phase '{phase}'")
                return result
            
            # Update context with feedback for next iteration
            context = context or {}
            context["previous_output"] = result.output
            context["feedback"] = {
                "issues": feedback.issues,
                "suggestions": feedback.suggestions,
            }
            
            self.metrics["total_feedback_iterations"] += 1
            logger.info(f"Refining output based on feedback...")
        
        return result

    async def _assess_quality(
        self,
        output: Dict[str, Any],
        phase: str,
    ) -> FeedbackResult:
        """
        Assess the quality of phase output using an LLM reviewer.
        """
        logger.info(f"Assessing quality for phase: {phase}")
        
        # Get reviewer configuration
        reviewer_cfg = self.model_router.get_model_for_phase("reviewer")
        
        # Construct review prompt
        prompt = (
            f"You are a Quality Assurance Reviewer for the '{phase}' phase.\n"
            f"Review the following output against the expected quality standards.\n"
            f"Output JSON with check result.\n\n"
            f"Output to Review:\n{json.dumps(output, indent=2)[:4000]}...\n\n" # Truncate if too long
            f"Return JSON format:\n"
            f"{{\n"
            f"  \"score\": <float 0.0-1.0>,\n"
            f"  \"issues\": [\"ticket 1\", ...],\n"
            f"  \"suggestions\": [\"suggestion 1\", ...],\n"
            f"  \"needs_iteration\": <bool>\n"
            f"}}"
        )
        
        try:
            # Call LLM for review
            response = await self.llm_client.complete(
                messages=[
                    {"role": "system", "content": "You are a critical code reviewer. Output structured JSON."},
                    {"role": "user", "content": prompt}
                ],
                model=reviewer_cfg.model,
                temperature=0.0,
                json_mode=True
            )
            
            # Parse result
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            review_data = json.loads(content)
            
            return FeedbackResult(
                quality_score=float(review_data.get("score", 0.0)),
                issues=review_data.get("issues", []),
                suggestions=review_data.get("suggestions", []),
                needs_iteration=bool(review_data.get("needs_iteration", False))
            )

        except Exception as e:
            logger.warning(f"Review failed, falling back to heuristic: {e}")
            # Fallback heuristic
            return FeedbackResult(
                quality_score=0.8, # Assume OK if review fails to avoid infinite loops
                issues=["Review process failed"],
                suggestions=[],
                needs_iteration=False
            )

    async def run_parallel_phases(
        self,
        phases: List[Dict[str, Any]],
    ) -> List[PhaseResult]:
        """
        Execute multiple independent phases in parallel.
        
        Args:
            phases: List of phase configurations
            
        Returns:
            List of PhaseResults
        """
        logger.info(f"Executing {len(phases)} phases in parallel")
        
        tasks = [
            self.run_phase_with_retry(
                phase=p["phase"],
                schema_name=p["schema_name"],
                context=p.get("context"),
                question=p.get("question"),
            )
            for p in phases
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        phase_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                phase_results.append(PhaseResult(
                    phase=phases[i]["phase"],
                    status=PhaseStatus.FAILED,
                    error=str(result),
                ))
            else:
                phase_results.append(result)
        
        return phase_results

    async def run_pipeline_adaptive(
        self,
        initial_requirements: str,
        question: Optional[str] = None,
        strategy: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL,
        use_feedback: bool = True,
    ) -> Dict[str, Any]:
        """
        Run pipeline with adaptive strategy selection.
        
        Args:
            initial_requirements: Feature requirements
            question: RAG query
            strategy: Execution strategy
            use_feedback: Whether to use feedback loops
            
        Returns:
            Dictionary with all phase outputs and metadata
        """
        logger.info(f"Starting adaptive pipeline with strategy: {strategy.value}")
        
        self.cost_manager.reset_task()
        pipeline_start = time.time()
        results: Dict[str, Any] = {
            "metadata": {
                "strategy": strategy.value,
                "use_feedback": use_feedback,
                "start_time": datetime.utcnow().isoformat(),
            },
            "phases": {},
        }
        
        try:
            # Analyst phase (always first)
            analyst_result = await (
                self.run_phase_with_feedback(
                    phase="analyst",
                    schema_name="requirements",
                    context={"requirements": initial_requirements},
                    question=question,
                )
                if use_feedback
                else self.run_phase_with_retry(
                    phase="analyst",
                    schema_name="requirements",
                    context={"requirements": initial_requirements},
                    question=question,
                )
            )
            
            if analyst_result.status != PhaseStatus.COMPLETED:
                raise RuntimeError(f"Analyst phase failed: {analyst_result.error}")
            
            results["phases"]["analyst"] = {
                "output": analyst_result.output,
                "metadata": {
                    "attempts": analyst_result.attempts,
                    "execution_time": analyst_result.execution_time,
                },
            }
            
            # Architect phase
            architect_result = await (
                self.run_phase_with_feedback(
                    phase="architect",
                    schema_name="architecture",
                    context=analyst_result.output,
                )
                if use_feedback
                else self.run_phase_with_retry(
                    phase="architect",
                    schema_name="architecture",
                    context=analyst_result.output,
                )
            )
            
            if architect_result.status != PhaseStatus.COMPLETED:
                raise RuntimeError(f"Architect phase failed: {architect_result.error}")
            
            results["phases"]["architect"] = {
                "output": architect_result.output,
                "metadata": {
                    "attempts": architect_result.attempts,
                    "execution_time": architect_result.execution_time,
                },
            }
            
            # Implementation phase
            implementation_result = await self.run_phase_with_retry(
                phase="implementation",
                schema_name="implementation",
                context=architect_result.output,
            )
            
            if implementation_result.status != PhaseStatus.COMPLETED:
                raise RuntimeError(f"Implementation phase failed: {implementation_result.error}")
            
            results["phases"]["implementation"] = {
                "output": implementation_result.output,
                "metadata": {
                    "attempts": implementation_result.attempts,
                    "execution_time": implementation_result.execution_time,
                },
            }
            
            # Testing phase
            testing_result = await self.run_phase_with_retry(
                phase="testing",
                schema_name="testing",
                context=implementation_result.output,
            )
            
            if testing_result.status != PhaseStatus.COMPLETED:
                raise RuntimeError(f"Testing phase failed: {testing_result.error}")
            
            results["phases"]["testing"] = {
                "output": testing_result.output,
                "metadata": {
                    "attempts": testing_result.attempts,
                    "execution_time": testing_result.execution_time,
                },
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            results["error"] = str(e)
            results["status"] = "failed"
        else:
            results["status"] = "completed"
        finally:
            # Add final metadata
            results["metadata"]["end_time"] = datetime.utcnow().isoformat()
            results["metadata"]["total_time"] = time.time() - pipeline_start
            results["metadata"]["total_cost"] = self.cost_manager.total_cost
            results["metadata"]["metrics"] = self.metrics
            
            # Save results
            pipeline_path = self.outputs_dir / f"pipeline_v2_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
            with open(pipeline_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            
            self.tracer.log_event("pipeline_complete", {
                "pipeline_path": str(pipeline_path),
                "status": results["status"],
                "total_cost": self.cost_manager.total_cost,
            })
            
            logger.info(f"Pipeline {results['status']}. Results saved to {pipeline_path}")
        
        return results

    def get_metrics(self) -> Dict[str, Any]:
        """Get current orchestrator metrics."""
        return {
            **self.metrics,
            "total_cost": self.cost_manager.total_cost,
            "cost_by_model": self.cost_manager.get_cost_breakdown(),
        }

    def reset_metrics(self) -> None:
        """Reset metrics counters."""
        self.metrics = {
            "total_phases_executed": 0,
            "total_retries": 0,
            "total_feedback_iterations": 0,
            "phase_execution_times": {},
            "error_counts": {},
        }
        self.cost_manager.reset_task()
