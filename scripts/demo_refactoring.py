"""
Demo script for RefactoringAgent in Simulation Mode.
"""

import asyncio
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.specialist_agents.refactoring_agent import RefactoringAgent
from core.simulation.mock_llm import MockLLMClient

async def main():
    print("🚀 Testing RefactoringAgent (Simulation Mode)")
    print("---------------------------------------------")
    
    # Initialize mock client and agent
    mock_client = MockLLMClient()
    agent = RefactoringAgent(llm_client=mock_client)
    
    # 1. Dependency Analysis
    print("\n[Step 1] Analyzing Dependencies for 'analyzer.py'...")
    impacted_files = await agent.analyze_dependencies(["analyzer.py"])
    print(f"Impacted Files: {impacted_files}")
    
    # 2. Refactoring Plan
    print("\n[Step 2] Generating Refactoring Plan for 'Streaming Support'...")
    request = "Enable streaming for CSV analysis to handle large files."
    plan = await agent.plan_refactoring(request, impacted_files)
    
    print("\n✅ Refactoring Plan Generated:")
    print(f"Description: {plan.description}")
    print(f"Affected Files: {plan.affected_files}")
    
    print("\nChangeset Summary:")
    for step in plan.steps:
        print(f"--- File: {step['file']} ---")
        print(f"Change: {step['description']}")
        # print(f"Code: {step['code'][:50]}...") # Truncated
        
    print(f"\nRollback Strategy: {plan.rollback_strategy}")
    print("---------------------------------------------")
    print("✅ Demo Complete!")

if __name__ == "__main__":
    asyncio.run(main())
