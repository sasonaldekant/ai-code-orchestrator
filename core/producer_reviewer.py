"""
Producer-Reviewer loop for iterative quality improvement.

This module implements a feedback loop where:
1. A producer model (e.g., GPT-4o-mini) generates initial output
2. A reviewer model (e.g., Claude Sonnet) provides detailed feedback
3. The producer refines the output based on feedback
4. Loop continues until quality threshold is met or max iterations reached

Typical use cases:
- Code generation with quality review
- Architecture refinement
- Documentation improvement
- Test case enhancement

Version: 2.0.0
"""

from __future__ import annotations

import asyncio
import logging
import json
import re
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class QualityDimension(Enum):
    """Dimensions for quality evaluation."""
    CORRECTNESS = "correctness"
    COMPLETENESS = "completeness"
    CLARITY = "clarity"
    BEST_PRACTICES = "best_practices"
    PERFORMANCE = "performance"
    SECURITY = "security"


@dataclass
class ReviewFeedback:
    """Feedback from reviewer model."""
    overall_score: float  # 0.0-10.0
    dimension_scores: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    critical_issues: List[str]
    approved: bool
    reasoning: str


@dataclass
class Iteration:
    """Single iteration of the producer-reviewer loop."""
    number: int
    producer_output: str
    review_feedback: Optional[ReviewFeedback]
    producer_tokens: int
    reviewer_tokens: int
    improvement_delta: float  # Score change from previous iteration


@dataclass
class ProducerReviewerResult:
    """Final result of the producer-reviewer loop."""
    final_output: str
    iterations: List[Iteration]
    final_score: float
    converged: bool
    reason: str  # "threshold_met", "max_iterations", "no_improvement"
    total_tokens: int
    total_cost: float


class ProducerReviewerLoop:
    """
    Orchestrate iterative refinement through producer-reviewer feedback.
    
    The loop operates as follows:
    1. Producer generates initial output
    2. Reviewer evaluates and scores the output
    3. If score < threshold, reviewer provides actionable feedback
    4. Producer revises output based on feedback
    5. Repeat until threshold met or max iterations reached
    """
    
    def __init__(self, llm_client: Any, cost_manager: Any):
        self.llm_client = llm_client
        self.cost_manager = cost_manager
    
    async def run(
        self,
        task: str,
        producer_model: str,
        reviewer_model: str,
        quality_threshold: float = 8.0,
        max_iterations: int = 3,
        context: Optional[str] = None,
        evaluation_criteria: Optional[List[QualityDimension]] = None,
        custom_reviewer_prompt: Optional[str] = None
    ) -> ProducerReviewerResult:
        """
        Execute the producer-reviewer loop.
        """
        logger.info(
            f"Starting producer-reviewer loop: {producer_model} → {reviewer_model}, "
            f"threshold={quality_threshold}, max_iter={max_iterations}"
        )
        
        iterations = []
        previous_score = 0.0
        feedback_history = []
        
        for iteration_num in range(1, max_iterations + 1):
            logger.info(f"Iteration {iteration_num}/{max_iterations}")
            
            # Producer generates output
            producer_output, producer_tokens = await self._produce(
                task=task,
                model=producer_model,
                context=context,
                previous_feedback=feedback_history[-1] if feedback_history else None
            )
            
            # Reviewer evaluates output
            review_feedback, reviewer_tokens = await self._review(
                task=task,
                output=producer_output,
                model=reviewer_model,
                evaluation_criteria=evaluation_criteria,
                custom_prompt=custom_reviewer_prompt
            )
            
            # Calculate improvement
            improvement = review_feedback.overall_score - previous_score
            
            # Record iteration
            iteration = Iteration(
                number=iteration_num,
                producer_output=producer_output,
                review_feedback=review_feedback,
                producer_tokens=producer_tokens,
                reviewer_tokens=reviewer_tokens,
                improvement_delta=improvement
            )
            iterations.append(iteration)
            feedback_history.append(review_feedback)
            
            logger.info(
                f"Iteration {iteration_num}: score={review_feedback.overall_score:.1f}, "
                f"improvement={improvement:+.1f}, approved={review_feedback.approved}"
            )
            
            # Check convergence criteria
            if review_feedback.approved and review_feedback.overall_score >= quality_threshold:
                return self._build_result(
                    iterations=iterations,
                    reason="threshold_met",
                    converged=True
                )
            
            # Check for diminishing returns
            if iteration_num > 1 and improvement < 0.5:
                logger.warning("Minimal improvement detected, stopping early")
                return self._build_result(
                    iterations=iterations,
                    reason="no_improvement",
                    converged=False
                )
            
            previous_score = review_feedback.overall_score
        
        # Max iterations reached
        return self._build_result(
            iterations=iterations,
            reason="max_iterations",
            converged=False
        )
    
    async def _produce(
        self,
        task: str,
        model: str,
        context: Optional[str],
        previous_feedback: Optional[ReviewFeedback]
    ) -> tuple[str, int]:
        """Generate or refine output using producer model."""
        messages = []
        
        if context:
            messages.append({
                "role": "system",
                "content": f"Context:\n{context}"
            })
        
        if previous_feedback:
            # Refinement iteration
            feedback_text = self._format_feedback(previous_feedback)
            messages.append({
                "role": "user",
                "content": f"Task: {task}\n\nPrevious output received the following feedback:\n{feedback_text}\n\nPlease revise your output to address all feedback points."
            })
        else:
            # Initial generation
            messages.append({
                "role": "user",
                "content": task
            })
        
        response = await self.llm_client.complete(
            messages=messages,
            model=model,
            temperature=0.0,
            max_tokens=8000
        )
        
        return response.content, response.tokens_used.get("total", 0)
    
    async def _review(
        self,
        task: str,
        output: str,
        model: str,
        evaluation_criteria: Optional[List[QualityDimension]],
        custom_prompt: Optional[str]
    ) -> tuple[ReviewFeedback, int]:
        """Evaluate output using reviewer model."""
        if custom_prompt:
            review_prompt = custom_prompt.format(task=task, output=output)
        else:
            review_prompt = self._build_default_review_prompt(
                task, output, evaluation_criteria
            )
        
        response = await self.llm_client.complete(
            messages=[{"role": "user", "content": review_prompt}],
            model=model,
            temperature=0.0,
            max_tokens=4000
        )
        
        feedback = self._parse_review_response(response.content)
        return feedback, response.tokens_used.get("total", 0)
    
    def _build_default_review_prompt(
        self,
        task: str,
        output: str,
        criteria: Optional[List[QualityDimension]]
    ) -> str:
        """Build default review prompt with evaluation criteria."""
        criteria_list = criteria or [
            QualityDimension.CORRECTNESS,
            QualityDimension.COMPLETENESS,
            QualityDimension.CLARITY,
            QualityDimension.BEST_PRACTICES
        ]
        
        criteria_text = "\n".join([
            f"- {c.value.replace('_', ' ').title()}" for c in criteria_list
        ])
        
        return f"""You are an expert code reviewer. Evaluate the following output.

Task:
{task}

Output to review:
```
{output}
```

Evaluation criteria:
{criteria_text}

Provide your review in JSON format:
{{
  "overall_score": 8.5,  // 0.0-10.0
  "dimension_scores": {{
    "correctness": 9.0,
    "completeness": 8.0,
    "clarity": 9.0,
    "best_practices": 8.0
  }},
  "strengths": ["Point 1", "Point 2"],
  "weaknesses": ["Issue 1", "Issue 2"],
  "suggestions": ["Improvement 1", "Improvement 2"],
  "critical_issues": ["Blocker 1"],  // Empty if none
  "approved": false,  // true if score >= 8.0 and no critical issues
  "reasoning": "Detailed explanation..."
}}
"""
    
    def _parse_review_response(self, content: str) -> ReviewFeedback:
        """Parse reviewer's JSON response into ReviewFeedback object."""
        try:
            # Extract JSON from markdown if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            data = json.loads(content.strip())
            
            return ReviewFeedback(
                overall_score=float(data.get("overall_score", 5.0)),
                dimension_scores=data.get("dimension_scores", {}),
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", []),
                suggestions=data.get("suggestions", []),
                critical_issues=data.get("critical_issues", []),
                approved=data.get("approved", False),
                reasoning=data.get("reasoning", "")
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse review response: {e}")
            # Return low-quality feedback as fallback
            return ReviewFeedback(
                overall_score=5.0,
                dimension_scores={},
                strengths=[],
                weaknesses=["Unable to parse review"],
                suggestions=[],
                critical_issues=["Review parsing failed"],
                approved=False,
                reasoning="Failed to parse structured review"
            )
    
    def _format_feedback(self, feedback: ReviewFeedback) -> str:
        """Format feedback for producer's consumption."""
        lines = [
            f"Overall Score: {feedback.overall_score}/10.0",
            f"Approved: {feedback.approved}",
            ""
        ]
        
        if feedback.critical_issues:
            lines.append("🚨 Critical Issues:")
            for issue in feedback.critical_issues:
                lines.append(f"  - {issue}")
            lines.append("")
        
        if feedback.weaknesses:
            lines.append("⚠️  Weaknesses:")
            for weakness in feedback.weaknesses:
                lines.append(f"  - {weakness}")
            lines.append("")
        
        if feedback.suggestions:
            lines.append("💡 Suggestions:")
            for suggestion in feedback.suggestions:
                lines.append(f"  - {suggestion}")
            lines.append("")
        
        lines.append(f"Reasoning: {feedback.reasoning}")
        
        return "\n".join(lines)
    
    def _build_result(
        self,
        iterations: List[Iteration],
        reason: str,
        converged: bool
    ) -> ProducerReviewerResult:
        """Build final result from iteration history."""
        final_iteration = iterations[-1]
        total_tokens = sum(
            it.producer_tokens + it.reviewer_tokens for it in iterations
        )
        total_cost = self.cost_manager.get_cumulative_cost()
        
        return ProducerReviewerResult(
            final_output=final_iteration.producer_output,
            iterations=iterations,
            final_score=final_iteration.review_feedback.overall_score if final_iteration.review_feedback else 0.0,
            converged=converged,
            reason=reason,
            total_tokens=total_tokens,
            total_cost=total_cost
        )
