"""
System-Wide Stress Test for AI Code Orchestrator v3.0

Simulates concurrent user sessions to validate:
- Concurrency handling (asyncio event loop)
- Resource locking (simulated)
- Error rate under load
- Throughput (requests/minute)

Usage:
    python scripts/stress_test.py --users 10 --iterations 1
"""

import sys
import asyncio
import logging
import time
import argparse
import random
from typing import List, Dict, Any

# Ensure project root is in path
sys.path.insert(0, ".")

from core.lifecycle_orchestrator import LifecycleOrchestrator
from api.event_bus import bus, Event, EventType

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("stress_test.log", mode="w", encoding="utf-8")
    ]
)
logger = logging.getLogger("StressTest")

# Metrics
metrics = {
    "total": 0,
    "success": 0,
    "failed": 0,
    "latencies": []
}

async def simulate_user_session(user_id: int, mock_retriever):
    """Simulate a single user request."""
    # Instantiate Orchestrator per request to avoid shared state (milestones)
    orchestrator = LifecycleOrchestrator(
        simulation_mode=True, 
        domain_retriever=mock_retriever
    )
    
    scenarios = [
        "Create a Python script to analyze CSV files.",
        "Generate a React component for a login form.",
        "Write a SQL query to find top customers.",
        # Triggers for failures (if implemented in mock)
        "Create a script using pndas [FORCE_HALLUCINATION]", # Typo
        "Write a broken script [FORCE_SYNTAX_ERROR]",
    ]
    
    request = random.choice(scenarios)
    complexity = "High" if "React" in request else "Medium"
    
    logger.info(f"User {user_id}: Starting request: {request}")
    start_time = time.time()
    
    try:
        # Simulate thinking time / network latency
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        result = await orchestrator.execute_request(request)
        
        latency = time.time() - start_time
        metrics["latencies"].append(latency)
        
        if result["status"] == "completed":
            metrics["success"] += 1
            logger.info(f"User {user_id}: Success ({latency:.2f}s)")
        else:
            metrics["failed"] += 1
            logger.warning(f"User {user_id}: Failed ({latency:.2f}s) - {result.get('error')}")
            
    except Exception as e:
        latency = time.time() - start_time
        metrics["failed"] += 1
        metrics["latencies"].append(latency)
        logger.error(f"User {user_id}: Error: {e}")
    finally:
        metrics["total"] += 1

async def run_stress_test(num_users: int, iterations: int):
    """Run concurrent user sessions."""
    logger.info(f"Starting Stress Test: {num_users} concurrent users, {iterations} iterations each.")
    
    # In simulation mode, we can pass None or a mock retriever if the Orchestrator handles it
    # Checking Orchestrator init... it likely defaults to None or creates it.
    # The error says 'domain_retriever' is required.
    
    from rag.domain_aware_retriever import DomainAwareRetriever
    # For simulation, we might want a mock retriever to avoid ChromaDB locking issues under stress
    # But let's try with the real one first, or None if configured.
    
    # Actually, LifecycleOrchestrator signature is: 
    # def __init__(self, domain_retriever: DomainAwareRetriever = None, ...)? 
    # The error says it's missing 1 required arg.
    # Let's check lifecycle_orchestrator.py briefly to be sure, but for now assuming we need to pass one.
    
    from core.simulation.mock_retriever import MockRetriever
    mock_retriever = MockRetriever()
    
    # orchestrator = LifecycleOrchestrator(...) # Removed shared instance
    
    start_time = time.time()
    
    tasks = []
    for i in range(iterations):
        for u in range(num_users):
            user_id = u + (i * num_users) + 1
            tasks.append(simulate_user_session(user_id, mock_retriever))
            
    # Run all tasks concurrently
    await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    
    # Report
    print("\n" + "="*50)
    print("STRESS TEST RESULTS")
    print("="*50)
    print(f"Total Requests: {metrics['total']}")
    print(f"Successful:     {metrics['success']} ({metrics['success']/metrics['total']*100:.1f}%)")
    print(f"Failed:         {metrics['failed']} ({metrics['failed']/metrics['total']*100:.1f}%)")
    print(f"Total Time:     {total_time:.2f}s")
    if metrics["latencies"]:
        print(f"Avg Latency:    {sum(metrics['latencies'])/len(metrics['latencies']):.2f}s")
        print(f"Max Latency:    {max(metrics['latencies']):.2f}s")
    print(f"Throughput:     {metrics['total']/total_time*60:.2f} req/min")
    print("="*50 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run system stress test")
    parser.add_argument("--users", type=int, default=10, help="Number of concurrent users")
    parser.add_argument("--iterations", type=int, default=1, help="Iterations per user")
    
    args = parser.parse_args()
    
    asyncio.run(run_stress_test(args.users, args.iterations))
