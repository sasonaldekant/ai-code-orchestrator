"""
Mock LLM Client for Simulation Mode to test the orchestrator without API costs.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import random

logger = logging.getLogger(__name__)

@dataclass
class MockResponse:
    """Simulates an LLM response object."""
    content: str
    usage: Dict[str, int] = None
    model: str = "mock-model"
    provider: str = "mock-provider"

    def __post_init__(self):
        if self.usage is None:
            self.usage = {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150, "prompt": 100, "completion": 50}
            
    @property
    def tokens_used(self) -> Dict[str, int]:
        return self.usage
        
    def __getitem__(self, key):
        return getattr(self, key)

class MockLLMClient:
    """
    A mock client that returns predefined responses based on the prompt content/role.
    """
    
    def __init__(self, cost_manager: any = None):
        self.cost_manager = cost_manager
        
    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.0,
        json_mode: bool = False,
        **kwargs
    ) -> MockResponse:
        """
        Simulate an LLM completion.
        """
        # Try to use system prompt for more accurate role detection
        system_content = ""
        prompt = messages[-1]["content"]
        
        for m in messages:
            if m["role"] == "system":
                system_content = m["content"].lower()
                break
                
        prompt_lower = prompt.lower()
        
        if model == "doc_specialist" or "generate openapi" in prompt_lower or "generate a comprehensive readme" in prompt_lower:
             return self._mock_doc_response(prompt)
             
        if model == "reviewer_v2":
             return self._mock_review_v2_response(prompt)
             
        if model == "refactoring_specialist":
             return self._mock_refactoring_response(prompt)
             
        if model == "migration_specialist":
             return self._mock_migration_response(prompt)
        
        # Analyze prompt/system to determine phase/intent
        if "analyst" in system_content or "analyst" in prompt_lower:
            return self._mock_analyst_response(prompt)
        elif "architect" in system_content: # Stricter check for architect
            return self._mock_architect_response()
        elif "developer" in system_content or "implementation" in prompt_lower:
            return self._mock_implementation_response(prompt)
        elif "quality assurance" in system_content or "reviewer" in prompt_lower:
             return self._mock_review_response()
        elif "tester" in system_content or "testgeneratoragent" in prompt_lower:
             return self._mock_test_response()
        
        # Fallback to loose matching if system prompt ambiguous
        if "requirements" in prompt_lower:
            return self._mock_analyst_response(prompt)
        elif "architecture" in prompt_lower and "implement" not in prompt_lower:
            return self._mock_architect_response()
        elif "implement" in prompt_lower:
            return self._mock_implementation_response(prompt) # Pass prompt for error injection
            
        return MockResponse(content="I am a mock LLM.")

    def _mock_analyst_response(self, prompt: str) -> MockResponse:
        """Return fake requirements."""
        response = {
            "functional_requirements": [
                "The system shall accept a CSV file input.",
                "The system shall parse the CSV using pandas.",
                "The system shall output summary statistics.",
                "The system shall handle empty files gracefully."
            ],
            "non_functional_requirements": [
                "Performance: Process 1MB file < 1s",
                "Reliability: Handle malformed CSVs"
            ],
            "constraints": ["Must use Python 3.9+"],
            "assumptions": ["CSV has headers"]
        }
        return MockResponse(content=json.dumps(response, indent=2))

    def _mock_architect_response(self) -> MockResponse:
        """Return fake architecture."""
        response = {
            "architecture_overview": "A simple Python script using pandas.",
            "components": [
                {
                    "name": "CsvAnalyzer",
                    "description": "Main class for analyzing CSVs",
                    "dependencies": ["pandas"]
                }
            ],
            "data_flow": "Input File -> Parser -> Analyzer -> Output",
            "file_structure": {
                "main.py": "Main entry point",
                "analyzer.py": "Class definition",
                "utils.py": "Helper functions"
            }
        }
        return MockResponse(content=json.dumps(response, indent=2))

    def _mock_implementation_response(self, prompt: str = "") -> MockResponse:
        """Return working Python code dynamically based on context."""
        
        # Scenario: Force Hallucination (Guardrail Test)
        if "FORCE_HALLUCINATION" in prompt:
            code = """
import pndas as pd # Spelling error to trigger hallucination detector
import os

def analyze(filepath):
    df = pd.read_csv(filepath)
    return df.describe()
"""
            response = {
                "files": [{"path": "analyzer.py", "content": code}],
                "explanation": "Implemented analyzer with a typo in imports."
            }
            return MockResponse(content=json.dumps(response, indent=2))

        # Scenario: Force Syntax Error (Verification Test)
        if "FORCE_SYNTAX_ERROR" in prompt:
            code = """
import pandas as pd

def analyze(filepath):
    df = pd.read_csv(filepath
    return df.describe() # Missing closing parenthesis
"""
            response = {
                "files": [{"path": "analyzer.py", "content": code}],
                "explanation": "Implemented analyzer with syntax error."
            }
            return MockResponse(content=json.dumps(response, indent=2))

        # Scenario: Force Security Violation (Guardrail Test)
        if "FORCE_SECURITY_VIOLATION" in prompt:
            code = """
import pandas as pd
import os

AWS_KEY = "AKIA1234567890SECRETKEY" # Hardcoded secret

def analyze(filepath):
    # Connect to S3 using secret
    pass
"""
            response = {
                "files": [{"path": "analyzer.py", "content": code}],
                "explanation": "Implemented analyzer with hardcoded credentials."
            }
            return MockResponse(content=json.dumps(response, indent=2))
            
        # Default Success Scenario
        # Simple working code that passes tests (using csv module for dependency-free execution)
        code = """
import csv
import os
from typing import Dict, Any

class CsvAnalyzer:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def analyze(self) -> Dict[str, Any]:
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"File not found: {self.filepath}")
            
        try:
            with open(self.filepath, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                rows = list(reader)
                
            return {
                "rows": len(rows),
                "columns": len(headers),
                "summary": {"headers": headers}
            }
        except Exception as e:
            raise ValueError(f"Error parsing CSV: {e}")

if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 1:
        analyzer = CsvAnalyzer(sys.argv[1])
        print(analyzer.analyze())
"""
        response = {
            "files": [
                {
                    "path": "analyzer.py",
                    "content": code
                }
            ],
            "explanation": "Implemented CsvAnalyzer class using standard csv module."
        }
        return MockResponse(content=json.dumps(response, indent=2))

    def _mock_review_response(self) -> MockResponse:
        """Return a passing review."""
        response = {
            "score": 0.95,
            "issues": [],
            "suggestions": ["Consider handling larger files with streaming"],
            "needs_iteration": False
        }
        return MockResponse(content=json.dumps(response, indent=2))
        
    def _mock_test_response(self) -> MockResponse:
         """Return unit tests."""
         code = """
import pytest
from analyzer import CsvAnalyzer
import os

def test_analyze_valid_csv(tmp_path):
    d = tmp_path / "subdir"
    d.mkdir()
    p = d / "test.csv"
    p.write_text("a,b\\n1,2", encoding="utf-8")
    
    analyzer = CsvAnalyzer(str(p))
    result = analyzer.analyze()
    assert result["rows"] == 1
    assert result["columns"] == 2
    # Simplified assertion to avoid strict equality issues in demo
    assert "headers" in result["summary"]

def test_file_not_found():
    analyzer = CsvAnalyzer("non_existent.csv")
    with pytest.raises(FileNotFoundError):
        analyzer.analyze()
"""
         return MockResponse(content=code)

    def _mock_doc_response(self, prompt: str) -> MockResponse:
        """Return mock documentation."""
        if "OpenAPI" in prompt:
             content = """
```yaml
openapi: 3.0.0
info:
  title: CSV Analyzer API
  version: 1.0.0
paths:
  /analyze:
    post:
      summary: Analyze a CSV file
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
      responses:
        '200':
          description: Analysis result
          content:
            application/json:
              schema:
                type: object
                properties:
                  rows:
                    type: integer
                  columns:
                    type: integer
```"""
        else: # README
             content = """
```markdown
# CsvAnalyzer Project

## Overview
Automated CSV analysis tool.

## Features
- Parse CSV files
- Generate summary statistics
- Handle errors gracefully

## Installation
```bash
pip install pandas
```

## Usage
```python
from analyzer import CsvAnalyzer
repo = CsvAnalyzer("data.csv")
```
```"""
        return MockResponse(content=content)

    def _mock_review_v2_response(self, prompt: str) -> MockResponse:
        """Return detailed review v2."""
        response = {
            "score": 0.85,
            "summary": "Code is solid but has a security concern.",
            "issues": [
                {
                    "type": "security",
                    "severity": "high",
                    "line": 10,
                    "message": "Potential SQL Injection in query construction.",
                    "suggestion": "Use parameterized queries."
                },
                {
                    "type": "performance",
                    "severity": "medium",
                    "line": 15,
                    "message": "Inefficient loop over large dataset.",
                    "suggestion": "Use list comprehension or map()."
                }
            ]
        }
        return MockResponse(content=json.dumps(response, indent=2))

    def _mock_refactoring_response(self, prompt: str) -> MockResponse:
        """Return a simulated multi-file refactoring plan."""
        # Scenario: Dependency Analysis
        if "Analyze the dependencies" in prompt:
            return MockResponse(content=json.dumps(["core/utils.py", "api/routes.py"]))
            
        # Scenario: Refactoring Plan
        response = {
            "description": "Refactor CsvAnalyzer to handle streaming.",
            "affected_files": ["analyzer.py", "main.py"],
            "steps": [
                {
                    "file": "analyzer.py",
                    "description": "Update CsvAnalyzer to use generators.",
                    "code": "# Refactored analyzer code..."
                },
                {
                    "file": "main.py",
                    "description": "Update entry point to handle stream output.",
                    "code": "# Refactored main code..."
                }
            ],
            "rollback_strategy": "Restore backups created by FileWriter."
        }
        return MockResponse(content=json.dumps(response, indent=2))

    def _mock_migration_response(self, prompt: str) -> MockResponse:
        """Return a simulated migration plan or breaking change analysis."""
        # Scenario: Breaking Change Analysis
        if "Analyze the following code versions" in prompt:
            changes = [
                "Function 'process_data' renamed to 'execute_pipeline'",
                "Parameter 'strict_mode' removed from 'Analyzer.init'",
                "Return type of 'get_stats' changed from Dict to List"
            ]
            return MockResponse(content=json.dumps(changes, indent=2))
            
        # Scenario: Migration Plan
        response = {
            "description": "Migrate core logic to v2.0 API.",
            "breaking_changes": [
                "Rename process_data -> execute_pipeline",
                "Update config schema"
            ],
            "steps": [
                {
                    "file": "main.py",
                    "description": "Rename function calls.",
                    "original_code_snippet": "process_data(data)",
                    "new_code_snippet": "execute_pipeline(data, version='2.0')",
                    "rationale": "API v2.0 requires explicit versioning."
                },
                {
                    "file": "config.json",
                    "description": "Update schema version.",
                    "original_code_snippet": '{"version": 1}',
                    "new_code_snippet": '{"version": 2, "features": []}',
                    "rationale": "New features require v2 schema."
                }
            ],
            "risk_level": "Medium"
        }
        return MockResponse(content=json.dumps(response, indent=2))
