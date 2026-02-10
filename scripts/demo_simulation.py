"""
Demo script for running AI Code Orchestrator in Simulation Mode.
This allows testing the full pipeline without API keys.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.lifecycle_orchestrator import LifecycleOrchestrator
from core.simulation.mock_retriever import MockRetriever
from api.event_bus import bus, Event, EventType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    print("🚀 Starting AI Code Orchestrator - Simulation Mode")
    print("--------------------------------------------------")
    
    # 1. Initialize Mock Components
    mock_retriever = MockRetriever()
    
    # 2. Initialize Orchestrator with Simulation Mode
    orchestrator = LifecycleOrchestrator(
        domain_retriever=mock_retriever,
        simulation_mode=True
    )
    
    # 3. Subscribe to events for visibility
    event_queue = bus.subscribe()
    
    async def process_events():
        while True:
            event = await event_queue.get()
            if event.type in [EventType.THOUGHT, EventType.TASK, EventType.TASK]:
                 if hasattr(EventType, 'CodeGenerated') and event.type == EventType.CodeGenerated:
                      print(f"\n[{event.agent}] {event.content}")
                 else:
                      print(f"\n[{event.agent}] {event.content}")
            elif event.type == EventType.ERROR:
                print(f"\n❌ [{event.agent}] {event.content}")
            elif event.type == EventType.WARNING:
                print(f"\n⚠️ [{event.agent}] {event.content}")
            elif event.type == EventType.LOG:
                 print(f"  > {event.content}")
            event_queue.task_done()

    # Start event processor in background
    event_task = asyncio.create_task(process_events())
    
    # 4. Define a user request
    # Scenario Selection
    print("\nSelect Simulation Scenario:")
    print("1. Happy Path (Standard CSV Analysis)")
    print("2. Force Hallucination (Import Error)")
    print("3. Force Syntax Error (Verification Loop)")
    print("4. Force Security Violation (Secret Leak)")
    
    choice = input("\nEnter choice (1-4) [1]: ").strip()
    
    user_request = "Create a Python script to analyze a CSV file using pandas."
    
    if choice == "2":
        user_request += " [FORCE_HALLUCINATION]"
        print("🔸 Selected: Force Hallucination")
    elif choice == "3":
        user_request += " [FORCE_SYNTAX_ERROR]"
        print("🔸 Selected: Force Syntax Error")
    elif choice == "4":
        user_request += " [FORCE_SECURITY_VIOLATION]"
        print("🔸 Selected: Force Security Violation")
    else:
        print("🔹 Selected: Happy Path")

    logger.info(f"Starting lifecycle execution for request: {user_request}")
    await bus.publish(Event(type=EventType.LOG, agent="Orchestrator", content=f"Initializing request: {user_request}"))
    
    try:
        result = await orchestrator.execute_request(user_request)
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        print(f"\n❌ Simulation failed: {e}")
        return

    try:
        # Print Summary
        print("\n--------------------------------------------------")
        print("✅ Simulation Complete!")
        print("--------------------------------------------------")
        print(f"Status: {result.get('status')}")
        
        if result.get('results'):
                print("\nGenerated Files:")
                # List files in current directory to verify
                for file in os.listdir("."):
                    if file.endswith(".py") and "analyzer" in file:
                        print(f"- {file}")
                    
    except Exception as e:
        print(f"\n❌ Simulation Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
