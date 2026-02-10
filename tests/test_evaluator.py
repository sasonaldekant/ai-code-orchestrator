"""
Test script for CodeEvaluator module.
"""
import sys
import unittest
sys.path.insert(0, '.')

from core.code_evaluator import CodeEvaluator

class TestCodeEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = CodeEvaluator()

    def test_clean_code(self):
        code = """
def add(a: int, b: int) -> int:
    \"\"\"Add two numbers.\"\"\"
    return a + b
"""
        result = self.evaluator.evaluate(code, "python")
        print(f"\nClean Code Score: {result['overall_score']:.2f}")
        self.assertGreater(result["overall_score"], 0.9)
        self.assertEqual(len(result["details"]["Security"]["issues"]), 0)

    def test_bad_code(self):
        code = """
def bad_function(x):
    # No docstring
    try:
        if x > 0:
            if x > 1:
                if x > 2:
                    if x > 3:
                        if x > 4:
                            print(x)
                            eval("import os; os.system('rm -rf /')") # Security issue
    except: # Broad except
        pass
"""
        result = self.evaluator.evaluate(code, "python")
        print(f"\nBad Code Score: {result['overall_score']:.2f}")
        
        # Check security issue
        security_issues = result["details"]["Security"]["issues"]
        self.assertTrue(any("eval" in i["message"] for i in security_issues))
        
        # Check static analysis issues (missing docstring, broad except)
        static_issues = result["details"]["StaticAnalysis"]["issues"]
        self.assertTrue(any("docstring" in i["message"]for i in static_issues))
        self.assertTrue(any("Broad exception" in i["message"] for i in static_issues))

        self.assertLessEqual(result["overall_score"], 0.81)

if __name__ == "__main__":
    unittest.main()
