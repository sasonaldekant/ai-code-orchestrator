"""
Code Evaluator Module for AI Code Orchestrator v3.0

This module provides tools for objectively measuring code quality using:
- Static Analysis (linting, style checks)
- Complexity Analysis (cyclomatic complexity)
- Security Scanning (SAST)
- Functional Correctness (via test execution results)
"""

from __future__ import annotations

import ast
import subprocess
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class EvaluationMetric:
    """A single metric result."""
    name: str           # e.g., "cyclomatic_complexity"
    value: float        # e.g., 5.0
    threshold: float    # e.g., 10.0
    status: str         # "pass", "fail", "warning"
    details: str = ""

@dataclass
class EvaluationResult:
    """Result of an evaluation run."""
    evaluator_name: str
    metrics: List[EvaluationMetric]
    issues: List[Dict[str, Any]] = field(default_factory=list)
    score: float = 0.0  # 0.0 to 1.0

class Evaluator(ABC):
    """Abstract base class for code evaluators."""
    
    @abstractmethod
    def evaluate(self, code: str, language: str) -> EvaluationResult:
        pass

class ComplexityEvaluator(Evaluator):
    """Evaluates code complexity (Cyclomatic Complexity)."""
    
    def evaluate(self, code: str, language: str) -> EvaluationResult:
        if language == "python":
            return self._evaluate_python(code)
        # TODO: Implement for other languages
        return EvaluationResult(
            evaluator_name="Complexity",
            metrics=[],
            issues=[],
            score=1.0 # Default pass for unsupported languages
        )

    def _evaluate_python(self, code: str) -> EvaluationResult:
        try:
            tree = ast.parse(code)
            
            # Simple cyclomatic complexity approximation
            # Count branches: if, for, while, and, or, except, with, assert
            complexity = 1  # Base complexity
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.With, ast.AsyncWith, ast.Assert)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
            
            status = "pass"
            if complexity > 15:
                status = "fail"
            elif complexity > 10:
                status = "warning"
                
            return EvaluationResult(
                evaluator_name="Complexity",
                metrics=[EvaluationMetric(
                    name="cyclomatic_complexity",
                    value=float(complexity),
                    threshold=10.0,
                    status=status,
                    details=f"Cyclomatic complexity is {complexity}"
                )],
                issues=[],
                score=max(0.0, 1.0 - (max(0, complexity - 5) / 20.0))
            )
        except Exception as e:
            logger.error(f"Complexity evaluation failed: {e}")
            return EvaluationResult("Complexity", [], [{"error": str(e)}])

class StaticAnalysisEvaluator(Evaluator):
    """Evaluates code style and potential errors using static analysis tools."""
    
    def evaluate(self, code: str, language: str) -> EvaluationResult:
        # Since we don't want to install tools in this environment yet,
        # we'll implement a basic AST-based linter for Python as a proof-of-concept
        if language == "python":
            return self._evaluate_python(code)
        return EvaluationResult("StaticAnalysis", [], [], 1.0)
        
    def _evaluate_python(self, code: str) -> EvaluationResult:
        issues = []
        metrics = []
        
        try:
            tree = ast.parse(code)
            
            # 1. Check for docstrings in functions and classes
            missing_docstrings = 0
            total_defs = 0
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    total_defs += 1
                    if not ast.get_docstring(node):
                        missing_docstrings += 1
                        issues.append({
                            "type": "style",
                            "message": f"Missing docstring in {node.name}",
                            "line": node.lineno
                        })
            
            # 2. Check for broad except clauses (Pokemon catching)
            broad_excepts = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None or (isinstance(node.type, ast.Name) and node.type.id == "Exception"):
                        broad_excepts += 1
                        issues.append({
                            "type": "warning",
                            "message": "Broad exception catch found",
                            "line": node.lineno
                        })

            # Calculate score
            score = 1.0
            if total_defs > 0:
                score -= (missing_docstrings / total_defs) * 0.2
            score -= (broad_excepts * 0.1)
            score = max(0.0, score)
            
            metrics.append(EvaluationMetric(
                name="docstring_coverage",
                value=(1.0 - (missing_docstrings/total_defs)) * 100 if total_defs else 100.0,
                threshold=80.0,
                status="pass" if score > 0.8 else "warning",
                details=f"Missing {missing_docstrings} docstrings out of {total_defs} definitions"
            ))
            
            return EvaluationResult(
                evaluator_name="StaticAnalysis",
                metrics=metrics,
                issues=issues,
                score=score
            )
            
        except SyntaxError as e:
            return EvaluationResult("StaticAnalysis", [], [{"error": f"Syntax Error: {e}"}], 0.0)
        except Exception as e:
             logger.error(f"Static analysis failed: {e}")
             return EvaluationResult("StaticAnalysis", [], [{"error": str(e)}], 0.0)

class SecurityEvaluator(Evaluator):
    """Evaluates code for security vulnerabilities."""
    
    def evaluate(self, code: str, language: str) -> EvaluationResult:
        if language == "python":
            return self._evaluate_python(code)
        return EvaluationResult("Security", [], [], 1.0)
    
    def _evaluate_python(self, code: str) -> EvaluationResult:
        issues = []
        score = 1.0
        
        # Simple pattern matching for known dangerous functions (Proof of Concept)
        # In production, use Bandit or Semgrep
        dangerous_functions = ["eval(", "exec(", "subprocess.call(", "input(", "pickle.load("]
        
        for func in dangerous_functions:
            if func in code:
                issues.append({
                    "type": "security",
                    "message": f"Potentially dangerous function usage: {func[:-1]}"
                })
                score -= 0.2
        
        # Check for hardcoded secrets (very basic)
        if "api_key" in code.lower() and "=" in code and '"' in code:
             issues.append({
                "type": "security",
                "message": "Potential hardcoded API key found"
            })
             score -= 0.5
             
        score = max(0.0, score)
        
        status = "pass"
        if score < 0.8: status = "warning"
        if score < 0.5: status = "fail"
        
        return EvaluationResult(
            evaluator_name="Security",
            metrics=[EvaluationMetric("security_score", score * 100, 80.0, status)],
            issues=issues,
            score=score
        )

class CodeEvaluator:
    """Main entry point for code evaluation."""
    
    def __init__(self):
        self.evaluators: List[Evaluator] = [
            ComplexityEvaluator(),
            StaticAnalysisEvaluator(),
            SecurityEvaluator()
        ]
        
    def evaluate(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Run all evaluators on the code.
        
        Args:
            code: Source code to evaluate
            language: Programming language
            
        Returns:
            Dictionary containing aggregated results
        """
        results = {}
        total_score = 0.0
        
        for evaluator in self.evaluators:
            result = evaluator.evaluate(code, language)
            results[result.evaluator_name] = {
                "score": result.score,
                "metrics": [asdict(m) for m in result.metrics],
                "issues": result.issues
            }
            total_score += result.score
            
        avg_score = total_score / len(self.evaluators) if self.evaluators else 0.0
        
        return {
            "overall_score": avg_score,
            "status": "pass" if avg_score > 0.7 else "fail",
            "details": results
        }
