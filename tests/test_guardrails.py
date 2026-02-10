"""
Test script for Guardrails module.
"""
import sys
import unittest
sys.path.insert(0, '.')

from core.guardrails import GuardrailMonitor, CircuitBreaker, Action

class TestGuardrails(unittest.TestCase):
    def setUp(self):
        self.monitor = GuardrailMonitor()
        self.cb = CircuitBreaker(max_retries=3, max_cost=1.0)

    def test_hallucination_detection(self):
        # Good code
        good_code = """
import os
import sys
from datetime import datetime
x = 1
"""
        violations = self.monitor.validate_code(good_code, "python")
        self.assertEqual(len(violations), 0)

        # Bad code (hallucinated package)
        bad_code = """
import non_existent_package_xyz
import os
"""
        violations = self.monitor.validate_code(bad_code, "python")
        self.assertTrue(len(violations) > 0)
        self.assertEqual(violations[0].rule_id, "hallucinated_import")
        self.assertEqual(violations[0].severity, "critical")

    def test_circuit_breaker(self):
        # Normal execution
        self.assertEqual(self.cb.check_execution(1, 0.1), Action.CONTINUE)
        self.assertEqual(self.cb.check_execution(2, 0.1), Action.CONTINUE)
        
        # Max retries exceeded
        self.assertEqual(self.cb.check_execution(4, 0.1), Action.ABORT)
        self.assertTrue(self.cb.is_open)
        
        self.cb.reset()
        self.assertFalse(self.cb.is_open)
        
        # Cost limit exceeded
        self.assertEqual(self.cb.check_execution(1, 1.5), Action.ABORT)
        self.assertTrue(self.cb.is_open)

if __name__ == "__main__":
    unittest.main()
