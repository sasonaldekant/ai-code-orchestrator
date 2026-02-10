"""
Benchmark Runner for AI Code Orchestrator v3.0

This module runs standardized benchmarks to evaluate the model's coding performance.
"""

from __future__ import annotations

import asyncio
import logging
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path

from core.code_executor import CodeExecutor
from core.code_evaluator import CodeEvaluator

logger = logging.getLogger(__name__)

@dataclass
class BenchmarkCase:
    """A single benchmark problem."""
    id: str
    prompt: str
    canonical_solution: str
    test_code: str
    language: str

@dataclass
class BenchmarkResult:
    """Result of a benchmark run."""
    case_id: str
    passed: bool
    execution_time: float
    evaluation_score: float
    details: Dict[str, Any]

class BenchmarkRunner:
    """Runs benchmarks against the orchestrator or specific models."""
    
    def __init__(self, benchmarks_dir: str = "evals/benchmarks"):
        self.benchmarks_dir = Path(benchmarks_dir)
        self.executor = CodeExecutor()
        self.evaluator = CodeEvaluator()
        
    def load_benchmark(self, suite_name: str) -> List[BenchmarkCase]:
        """Load benchmark cases from a suite directory."""
        suite_path = self.benchmarks_dir / suite_name
        cases = []
        
        # Load cases from JSONL or individual files (placeholder logic)
        # In reality, we'd parse Humaneval JSONL or similar
        return cases

    async def run_suite(self, suite_name: str, model_func: Any) -> Dict[str, Any]:
        """
        Run a full benchmark suite.
        
        Args:
            suite_name: Name of the benchmark suite
            model_func: Async function that takes prompt -> returns code
            
        Returns:
            Aggregate results
        """
        cases = self.load_benchmark(suite_name)
        results = []
        
        for case in cases:
            # Generate code
            generated_code = await model_func(case.prompt)
            
            # Execute tests
            test_run = await self.executor.execute_python(
                f"{generated_code}\n{case.test_code}"
            )
            
            # Evaluate quality
            quality = self.evaluator.evaluate(generated_code, case.language)
            
            results.append(BenchmarkResult(
                case_id=case.id,
                passed=test_run.passed,
                execution_time=test_run.execution_time_ms,
                evaluation_score=quality["overall_score"],
                details={
                    "test_output": test_run.stdout,
                    "quality_issues": quality["details"]
                }
            ))
            
        return self._aggregate_results(results)

    def _aggregate_results(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Calculate aggregate metrics."""
        total = len(results)
        if total == 0:
            return {}
            
        passed = len([r for r in results if r.passed])
        avg_score = sum(r.evaluation_score for r in results) / total
        
        return {
            "total": total,
            "passed": passed,
            "pass_rate": passed / total,
            "avg_quality_score": avg_score
        }
