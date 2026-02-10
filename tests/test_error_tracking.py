"""
Test script for ErrorTracker and PatternDetector modules.
"""
import sys
import unittest
import shutil
from pathlib import Path

sys.path.insert(0, '.')

from core.error_tracker import ErrorTracker
from core.pattern_detector import PatternDetector

class TestErrorTracking(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/temp_error_tracking"
        self.tracker = ErrorTracker(storage_dir=self.test_dir)
        self.detector = PatternDetector()

    def tearDown(self):
        import time
        # Give disk a moment to release locks
        time.sleep(0.1)
        if Path(self.test_dir).exists():
            try:
                shutil.rmtree(self.test_dir)
            except PermissionError:
                time.sleep(0.5)
                try:
                    shutil.rmtree(self.test_dir)
                except Exception as e:
                    print(f"Warning: Failed to cleanup test dir: {e}")

    def test_log_and_retrieve_error(self):
        error_id = self.tracker.log_error(
            phase="implementation",
            error=ValueError("Invalid input data"),
            context={"file": "utils.py"}
        )
        
        errors = self.tracker.get_recent_errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, error_id)
        self.assertEqual(errors[0].error_type, "ValueError")
        self.assertIn("Invalid input data", errors[0].message)

    def test_pattern_detection(self):
        # Log similar errors 3 times
        for _ in range(3):
            self.tracker.log_error(
                phase="execution",
                error=NameError("name 'pd' is not defined"),
                context={}
            )
            
        # Log a different error
        self.tracker.log_error(
            phase="execution",
            error=SyntaxError("invalid syntax"),
            context={}
        )

        # Convert logs to dicts for detector
        logs = [e.to_dict() for e in self.tracker.session_errors]
        patterns = self.detector.analyze_errors(logs)
        
        # Should detect the recurring NameError
        self.assertTrue(len(patterns) >= 1)
        name_error_pattern = next((p for p in patterns if "missing_import" in p.description), None)
        
        if not name_error_pattern:
             # Fallback if regex didn't catch it exactly as expected, check generic clustering
             name_error_pattern = next((p for p in patterns if "NameError" in p.description), None)

        self.assertIsNotNone(name_error_pattern)
        self.assertEqual(name_error_pattern.frequency, 3)
        self.assertIn("Check if module is imported", name_error_pattern.suggested_fix)

if __name__ == "__main__":
    unittest.main()
