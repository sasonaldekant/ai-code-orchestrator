"""
Demo: Code Reviewer V2 Specialist
Verifies the CodeReviewerV2 in simulation mode.
"""

import sys
import asyncio
import logging

sys.path.insert(0, ".")

from agents.specialist_agents.code_reviewer_v2 import CodeReviewerV2
from core.simulation.mock_llm import MockLLMClient

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ReviewV2Demo")

async def run_demo():
    print("🚀 Starting Code Reviewer V2 Demo...")
    
    # 1. Initialize Mock LLM
    mock_llm = MockLLMClient()
    
    # 2. Initialize Agent
    reviewer = CodeReviewerV2(llm_client=mock_llm)
    
    # 3. Simulate Code Review
    code_sample = """
    def get_user(user_id):
        query = "SELECT * FROM users WHERE id = " + user_id
        cursor.execute(query)
        return cursor.fetchall()
    """
    
    print("\n[1] Reviewing Code...")
    print(f"Code:\n{code_sample}")
    
    report = await reviewer.review_code(code_sample, context="User authentication module")
    
    print("\n=== Review Report ===")
    print(f"Score: {report.score}/1.0")
    print(f"Passed: {report.passed}")
    print(f"Summary: {report.summary}")
    print("\nIssues:")
    for issue in report.issues:
        print(f"[{issue.severity.upper()}] {issue.type}: {issue.message}")
        print(f"   Line {issue.line}: {issue.suggestion}")
    
    print("\n✅ Demo Complete!")

if __name__ == "__main__":
    asyncio.run(run_demo())
