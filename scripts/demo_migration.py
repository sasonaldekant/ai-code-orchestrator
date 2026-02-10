"""
Demo script for MigrationAgent in Simulation Mode.
"""

import asyncio
import json
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.specialist_agents.migration_agent import MigrationAgent
from core.simulation.mock_llm import MockLLMClient

async def main():
    print("=== MigrationAgent Simulation Demo ===\n")
    
    # Initialize agent with mock client
    mock_llm = MockLLMClient()
    agent = MigrationAgent(llm_client=mock_llm)
    
    # 1. Analyze Breaking Changes
    old_code = """
def process_data(data, strict_mode=False):
    return {"status": "ok", "result": data}
    """
    new_code = """
def execute_pipeline(data, version='1.0'):
    return [data]
    """
    
    print("Step 1: Analyzing Breaking Changes...")
    changes = await agent.analyze_breaking_changes(old_code, new_code)
    for change in changes:
        print(f" - {change}")
    
    print("\n" + "="*40 + "\n")
    
    # 2. Generate Migration Plan
    print("Step 2: Generating Migration Plan...")
    plan = await agent.generate_migration_plan(
        request="Migrate the data processing logic to the new execute_pipeline API.",
        affected_files=["main.py", "config.json"]
    )
    
    print(f"Plan Description: {plan.description}")
    print(f"Risk Level: {plan.risk_level}")
    print("\nBreaking Changes Summary:")
    for bc in plan.breaking_changes:
        print(f" - {bc}")
        
    print("\nMigration Steps:")
    for i, step in enumerate(plan.steps, 1):
        print(f"\n[{i}] File: {step.file}")
        print(f"    Description: {step.description}")
        print(f"    Rationale: {step.rationale}")
        print(f"    --- code change ---")
        print(f"    -  {step.original_code_snippet}")
        print(f"    +  {step.new_code_snippet}")

if __name__ == "__main__":
    asyncio.run(main())
