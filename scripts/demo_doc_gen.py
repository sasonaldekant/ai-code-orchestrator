"""
Demo: Documentation Generator Specialist
Verifies the DocGeneratorAgent in simulation mode.
"""

import sys
import asyncio
import logging

sys.path.insert(0, ".")

from agents.specialist_agents.doc_generator import DocGeneratorAgent
from core.simulation.mock_llm import MockLLMClient

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DocGenDemo")

async def run_demo():
    print("🚀 Starting Documentation Generator Demo...")
    
    # 1. Initialize Mock LLM
    mock_llm = MockLLMClient()
    
    # 2. Initialize Agent
    doc_agent = DocGeneratorAgent(llm_client=mock_llm)
    
    # 3. Generate API Docs (OpenAPI)
    print("\n[1] Generating OpenAPI Spec...")
    code_sample = """
from fastapi import FastAPI
app = FastAPI()

@app.post("/analyze")
def analyze(file: bytes):
    return {"rows": 10, "columns": 5}
"""
    api_docs = await doc_agent.generate_api_docs(code_sample)
    print(f"Type: {api_docs.type}")
    print(f"Format: {api_docs.format}")
    print("Content Preview:")
    print(api_docs.content[:200] + "...")
    
    # 4. Generate README
    print("\n[2] Generating README...")
    readme = await doc_agent.generate_readme(
        project_name="CsvAnalyzer",
        description="A tool to analyze CSV files.",
        features=["Parse CSV", "Summary Stats"]
    )
    print(f"Type: {readme.type}")
    print(f"Format: {readme.format}")
    print("Content Preview:")
    print(readme.content[:200] + "...")
    
    print("\n✅ Demo Complete!")

if __name__ == "__main__":
    asyncio.run(run_demo())
