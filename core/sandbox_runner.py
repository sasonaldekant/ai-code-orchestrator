"""
Docker Sandbox Runner for AI Code Orchestrator.
Manages isolated execution environments.
"""

import asyncio
import logging
import uuid
import os
from typing import List, Optional, Tuple
from .code_executor import ExecutionResult, ExecutionStatus

logger = logging.getLogger(__name__)

class SandboxRunner:
    """
    Handles execution of code within Docker containers.
    """
    
    IMAGE_NAME = "ai-orchestrator-sandbox:latest"
    
    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds
        
    async def is_docker_available(self) -> bool:
        """Check if Docker daemon is running."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "docker", "info",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await proc.wait()
            return proc.returncode == 0
        except FileNotFoundError:
            return False

    async def build_image(self) -> bool:
        """Build the sandbox image if it doesn't exist."""
        logger.info(f"Building Docker image: {self.IMAGE_NAME}")
        proc = await asyncio.create_subprocess_exec(
            "docker", "build", "-t", self.IMAGE_NAME, ".",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            logger.error(f"Failed to build image: {stderr.decode()}")
            return False
        
        logger.info("Docker image built successfully.")
        return True

    async def run_command(
        self, 
        cmd: List[str], 
        host_workdir: str, 
        timeout: int = 30
    ) -> ExecutionResult:
        """
        Run a command inside a fresh container instance.
        
        Args:
            cmd: Command to run (e.g. ["python", "main.py"])
            host_workdir: Local directory to mount to /sandbox
            timeout: Execution timeout in seconds
        """
        container_name = f"sandbox_{uuid.uuid4().hex[:8]}"
        
        # Construct docker run command
        # -rm: Remove container after exit
        # -v: Mount host dir to container workdir
        # --network none: Disable network for security
        # --cpus 1.0: Limit CPU
        # --memory 512m: Limit memory
        docker_cmd = [
            "docker", "run", "--rm",
            "--name", container_name,
            "--network", "none",
            "--cpus", "1.0",
            "--memory", "512m",
            "-v", f"{os.path.abspath(host_workdir)}:/sandbox",
            "-w", "/sandbox",
            self.IMAGE_NAME
        ] + cmd
        
        logger.info(f"Executing in sandbox: {' '.join(cmd)}")
        
        start_time = asyncio.get_running_loop().time()
        
        try:
            process = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                execution_time = (asyncio.get_running_loop().time() - start_time) * 1000
                
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS if process.returncode == 0 else ExecutionStatus.FAILED,
                    stdout=stdout.decode("utf-8", errors="replace"),
                    stderr=stderr.decode("utf-8", errors="replace"),
                    exit_code=process.returncode or 0,
                    execution_time_ms=execution_time
                )
                
            except asyncio.TimeoutError:
                # Kill container if timeout
                subprocess_kill = await asyncio.create_subprocess_exec(
                    "docker", "kill", container_name,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await subprocess_kill.wait()
                
                return ExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    error=f"Execution timed out after {timeout}s",
                    execution_time_ms=timeout * 1000
                )
                
        except Exception as e:
            logger.error(f"Sandbox execution error: {e}")
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error=str(e),
                execution_time_ms=(asyncio.get_running_loop().time() - start_time) * 1000
            )
