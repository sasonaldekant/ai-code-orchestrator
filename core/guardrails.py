"""
Guardrails Module for AI Code Orchestrator v3.0

This module provides safety mechanisms to prevent:
- Infinite loops / excessive retries
- Runaway costs
- Hallucinated imports/apis
"""

from __future__ import annotations

import logging
import importlib
import pkgutil
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class Action(Enum):
    CONTINUE = "continue"
    RETRY = "retry"
    ABORT = "abort"
    ESCALATE = "escalate" # Ask user

@dataclass
class GuardrailViolation:
    rule_id: str
    message: str
    severity: str # "warning", "critical"
    context: Dict[str, Any]

class HallucinationDetector:
    """Checks for references to non-existent modules or attributes."""
    
    def __init__(self):
        self._installed_packages = {
            name for _, name, _ in pkgutil.iter_modules()
        }
        # Add stdlib modules (approximation)
        import sys
        self._installed_packages.update(sys.builtin_module_names)
        
    def check_imports(self, code: str) -> List[GuardrailViolation]:
        """Detect imports of non-existent packages."""
        violations = []
        import ast
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        root_pkg = name.name.split('.')[0]
                        if not self._is_package_available(root_pkg):
                            violations.append(GuardrailViolation(
                                rule_id="hallucinated_import",
                                message=f"Package '{root_pkg}' may not be installed or exists.",
                                severity="critical",
                                context={"package": root_pkg, "line": node.lineno}
                            ))
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        root_pkg = node.module.split('.')[0]
                        if not self._is_package_available(root_pkg):
                            violations.append(GuardrailViolation(
                                rule_id="hallucinated_import",
                                message=f"Package '{root_pkg}' may not be installed.",
                                severity="critical",
                                context={"package": root_pkg, "line": node.lineno}
                            ))
        except SyntaxError:
            pass # Syntax errors handled elsewhere
            
        return violations

    def _is_package_available(self, package_name: str) -> bool:
        """Check if a package is importable."""
        if package_name in self._installed_packages:
            return True
        try:
            importlib.util.find_spec(package_name)
            return True
        except ImportError:
            return False
        except ValueError:
            return True # Relative import

class CircuitBreaker:
    """Prevents runaway processes."""
    
    def __init__(self, max_retries: int = 3, max_cost: float = 1.0):
        self.max_retries = max_retries
        self.max_cost = max_cost
        self.current_retries = 0
        self.current_cost = 0.0
        self.is_open = False # Open means breaker tripped (stop execution)
        
    def check_execution(self, retry_count: int, cost_delta: float) -> Action:
        """
        Check if execution should proceed.
        
        Args:
            retry_count: Current retry number
            cost_delta: Cost incurred in last step
            
        Returns:
            Action enum
        """
        if self.is_open:
            return Action.ABORT
            
        self.current_cost += cost_delta
        
        if retry_count > self.max_retries:
            logger.warning("Circuit breaker tripped: Max retries exceeded")
            self.is_open = True
            return Action.ABORT
            
        if self.current_cost > self.max_cost:
            logger.warning(f"Circuit breaker tripped: Cost check failed (${self.current_cost} > ${self.max_cost})")
            self.is_open = True
            return Action.ABORT
            
        return Action.CONTINUE

    def reset(self):
        self.current_retries = 0
        self.current_cost = 0.0
        self.is_open = False

class GuardrailMonitor:
    """Central monitor for all safety checks."""
    
    def __init__(self):
        self.hallucination_detector = HallucinationDetector()
        # Map task_id -> CircuitBreaker
        self.breakers: Dict[str, CircuitBreaker] = {}
        
    def get_breaker(self, task_id: str) -> CircuitBreaker:
        if task_id not in self.breakers:
            self.breakers[task_id] = CircuitBreaker()
        return self.breakers[task_id]
        
    def validate_code(self, code: str, language: str = "python") -> List[GuardrailViolation]:
        """Run all static checks on code."""
        violations = []
        
        if language == "python":
            violations.extend(self.hallucination_detector.check_imports(code))
            
        return violations

    def check_runtime(self, task_id: str, retry_count: int, cost: float) -> Action:
        """Check runtime constraints."""
        breaker = self.get_breaker(task_id)
        return breaker.check_execution(retry_count, cost)
