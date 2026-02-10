"""Quick test for CodeExecutor"""
import asyncio
import sys
sys.path.insert(0, '.')

from core.code_executor import CodeExecutor

async def test():
    executor = CodeExecutor(timeout_seconds=10)
    
    # Test Python execution
    result = await executor.execute_python('print("Hello from CodeExecutor!")')
    print(f'Status: {result.status}')
    print(f'Output: {result.stdout.strip()}')
    print(f'Execution time: {result.execution_time_ms:.2f}ms')
    print(f'Passed: {result.passed}')

if __name__ == "__main__":
    asyncio.run(test())
