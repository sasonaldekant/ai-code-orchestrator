"""
Code Executor Module for AI Code Orchestrator v3.0

This module provides safe execution of generated code in sandboxed environments.
Supports Python, TypeScript/JavaScript, and C#/.NET execution.
"""

from __future__ import annotations

import asyncio
import subprocess
import tempfile
import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class ExecutionResult:
    """Result of code execution."""
    status: ExecutionStatus
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    execution_time_ms: float = 0
    error: Optional[str] = None
    
    @property
    def passed(self) -> bool:
        return self.status == ExecutionStatus.SUCCESS and self.exit_code == 0


@dataclass
class TestResult:
    """Result of test execution."""
    test_name: str
    passed: bool
    message: str = ""
    execution_time_ms: float = 0
    
    
@dataclass
class TestSuiteResult:
    """Result of running a test suite."""
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    execution_time_ms: float = 0
    test_results: List[TestResult] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        return self.passed / self.total if self.total > 0 else 0.0


class CodeExecutor:
    """
    Safe code execution in sandboxed environments.
    
    Supports:
    - Python (direct execution)
    - TypeScript/JavaScript (via node/ts-node)
    - C#/.NET (via dotnet CLI)
    """
    
    def __init__(
        self,
        timeout_seconds: int = 30,
        max_output_size: int = 10000,
        use_docker: bool = False
    ):
        self.timeout_seconds = timeout_seconds
        self.max_output_size = max_output_size
        self.use_docker = use_docker
        
        # Initialize sandbox runner if docker is requested
        self.sandbox = None
        if use_docker:
            from .sandbox_runner import SandboxRunner
            self.sandbox = SandboxRunner(timeout_seconds=timeout_seconds)
            
    async def execute_python(
        self,
        code: str,
        test_code: Optional[str] = None
    ) -> ExecutionResult:
        """
        Execute Python code and optionally run tests.
        """
        # Check for Docker availability (lazy check)
        if self.use_docker and self.sandbox:
            if not await self.sandbox.is_docker_available():
                logger.warning("Docker requested but not available. Falling back to local execution.")
            else:
                # Use Sandbox
                with tempfile.TemporaryDirectory() as tmpdir:
                    # Write files to temp dir which will be mounted
                    code_path = Path(tmpdir) / "main.py"
                    code_path.write_text(code, encoding="utf-8")
                    
                    cmd = ["python", "main.py"]
                    
                    if test_code:
                        test_path = Path(tmpdir) / "test_main.py"
                        test_content = f"from main import *\n\n{test_code}"
                        test_path.write_text(test_content, encoding="utf-8")
                        cmd = ["python", "-m", "pytest", "test_main.py", "-v", "--tb=short"]
                    
                    return await self.sandbox.run_command(cmd, host_workdir=tmpdir)

        # Local Execution (Fallback)
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write main code
            code_path = Path(tmpdir) / "main.py"
            code_path.write_text(code, encoding="utf-8")
            
            if test_code:
                # Write test code
                test_path = Path(tmpdir) / "test_main.py"
                test_content = f"from main import *\n\n{test_code}"
                test_path.write_text(test_content, encoding="utf-8")
                
                # Run pytest
                return await self._run_command(
                    ["python", "-m", "pytest", str(test_path), "-v", "--tb=short"],
                    cwd=tmpdir
                )
            else:
                # Just execute the code
                return await self._run_command(
                    ["python", str(code_path)],
                    cwd=tmpdir
                )
    
    async def execute_typescript(
        self,
        code: str,
        test_code: Optional[str] = None
    ) -> ExecutionResult:
        """
        Execute TypeScript code using ts-node.
        """
        cmd_prefix = ["npx", "ts-node"]
        
        # Check Sandbox
        if self.use_docker and self.sandbox:
             if not await self.sandbox.is_docker_available():
                logger.warning("Docker requested but not available. Falling back to local execution.")
             else:
                with tempfile.TemporaryDirectory() as tmpdir:
                    code_path = Path(tmpdir) / "main.ts"
                    code_path.write_text(code, encoding="utf-8")
                    
                    cmd = cmd_prefix + ["main.ts"]
                    
                    if test_code:
                        test_path = Path(tmpdir) / "main.test.ts"
                        test_content = f"import {{ * as main }} from './main';\n\n{test_code}"
                        test_path.write_text(test_content, encoding="utf-8")
                        cmd = cmd_prefix + ["main.test.ts"]
                        
                    return await self.sandbox.run_command(cmd, host_workdir=tmpdir)

        # Local Execution
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write main code
            code_path = Path(tmpdir) / "main.ts"
            code_path.write_text(code, encoding="utf-8")
            
            if test_code:
                # Write test code
                test_path = Path(tmpdir) / "main.test.ts"
                test_content = f"import {{ * as main }} from './main';\n\n{test_code}"
                test_path.write_text(test_content, encoding="utf-8")
                
                # Run jest (simplified - in production would need proper setup)
                return await self._run_command(
                    ["npx", "ts-node", str(test_path)],
                    cwd=tmpdir
                )
            else:
                return await self._run_command(
                    ["npx", "ts-node", str(code_path)],
                    cwd=tmpdir
                )
    
    async def execute_dotnet(
        self,
        code: str,
        test_code: Optional[str] = None,
        project_type: str = "console"
    ) -> ExecutionResult:
        """
        Execute C#/.NET code using dotnet CLI.
        """
        # Docker Execution for Dotnet is trickier due to multi-step build/restore
        # For MVP, we will run the 'dotnet run' command, assuming the image has the SDK.
        # However, 'dotnet new' and 'restore' usually need to run first.
        # To keep it simple for the sandbox runner which runs ONE command:
        # We might need a shell script wrapper or chain commands.
        
        if self.use_docker and self.sandbox:
             if not await self.sandbox.is_docker_available():
                logger.warning("Docker requested but not available. Falling back to local execution.")
             else:
                # In Docker, we can just compile and run a single file if we use a specific tool
                # or we just map the whole project structure.
                # Simplest approach: Create project locally in temp, mount it, run 'dotnet run' in container.
                
                with tempfile.TemporaryDirectory() as tmpdir:
                    project_dir = Path(tmpdir) / "TestProject"
                    
                    # 1. Create Project Locally (to set up structure)
                    # This requires local dotnet SDK. If not present, we can't scaffold.
                    # Fallback: Create structure manually or run scaffolding IN docker.
                    # Let's run scaffolding IN docker.
                    
                    # We need to run multiple commands. SandboxRunner currently runs one.
                    # Let's chain them with bash -c
                    
                    setup_cmd = f"dotnet new {project_type} -o TestProject && cd TestProject"
                    
                    # We need to write the code AFTER creating the project. 
                    # This is hard to do in one shot without persistent container.
                    # Strategy: Create project locally (assuming dotnet exists? OR manual file creation)
                    
                    # Let's assumption: We write the file contents mapping to a standard csproj structure
                    # Manually creating a basic .csproj avoids local dotnet dependency.
                    
                    project_dir.mkdir()
                    (project_dir / "TestProject.csproj").write_text(self._get_basic_csproj(), encoding="utf-8")
                    (project_dir / "Program.cs").write_text(code, encoding="utf-8")
                    
                    cmd = ["dotnet", "run", "--project", "TestProject"]
                    
                    if test_code:
                         # Test setup is complex for single-command sandbox. 
                         # Skipping Dotnet Test in Sandbox for MVP.
                         return ExecutionResult(status=ExecutionStatus.ERROR, error="Dotnet testing in sandbox not yet supported")

                    return await self.sandbox.run_command(cmd, host_workdir=tmpdir)

        # Local Execution
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "TestProject"
            
            # Create new dotnet project
            create_result = await self._run_command(
                ["dotnet", "new", project_type, "-o", str(project_dir)],
                cwd=tmpdir
            )
            
            if not create_result.passed:
                return create_result
            
            # Write main code
            program_path = project_dir / "Program.cs"
            program_path.write_text(code, encoding="utf-8")
            
            if test_code:
                # Create test project
                test_dir = Path(tmpdir) / "TestProject.Tests"
                await self._run_command(
                    ["dotnet", "new", "xunit", "-o", str(test_dir)],
                    cwd=tmpdir
                )
                
                # Add reference
                await self._run_command(
                    ["dotnet", "add", str(test_dir), "reference", str(project_dir)],
                    cwd=tmpdir
                )
                
                # Write test code
                test_path = test_dir / "UnitTest1.cs"
                test_path.write_text(test_code, encoding="utf-8")
                
                # Run tests
                return await self._run_command(
                    ["dotnet", "test", str(test_dir), "--verbosity", "normal"],
                    cwd=tmpdir
                )
            else:
                # Just build and run
                build_result = await self._run_command(
                    ["dotnet", "build", str(project_dir)],
                    cwd=tmpdir
                )
                
                if not build_result.passed:
                    return build_result
                
                return await self._run_command(
                    ["dotnet", "run", "--project", str(project_dir)],
                    cwd=tmpdir
                )

    def _get_basic_csproj(self) -> str:
        return """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net7.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>"""
    
    async def execute_with_language(
        self,
        code: str,
        language: str,
        test_code: Optional[str] = None
    ) -> ExecutionResult:
        """
        Execute code based on detected or specified language.
        
        Args:
            code: The code to execute
            language: Programming language (python, typescript, csharp)
            test_code: Optional test code
            
        Returns:
            ExecutionResult
        """
        language = language.lower()
        
        if language in ("python", "py"):
            return await self.execute_python(code, test_code)
        elif language in ("typescript", "ts", "javascript", "js"):
            return await self.execute_typescript(code, test_code)
        elif language in ("csharp", "cs", "dotnet", "c#"):
            return await self.execute_dotnet(code, test_code)
        else:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error=f"Unsupported language: {language}"
            )
    
    async def _run_command(
        self,
        cmd: List[str],
        cwd: Optional[str] = None
    ) -> ExecutionResult:
        """
        Run a shell command with timeout and capture output.
        """
        start_time = time.time()
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout_seconds
                )
                
                execution_time = (time.time() - start_time) * 1000
                
                stdout_str = stdout.decode("utf-8", errors="replace")[:self.max_output_size]
                stderr_str = stderr.decode("utf-8", errors="replace")[:self.max_output_size]
                
                status = ExecutionStatus.SUCCESS if process.returncode == 0 else ExecutionStatus.FAILED
                
                return ExecutionResult(
                    status=status,
                    stdout=stdout_str,
                    stderr=stderr_str,
                    exit_code=process.returncode or 0,
                    execution_time_ms=execution_time
                )
                
            except asyncio.TimeoutError:
                process.kill()
                return ExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    error=f"Execution timed out after {self.timeout_seconds}s",
                    execution_time_ms=self.timeout_seconds * 1000
                )
                
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000
            )


class VerificationLoop:
    """
    Implements the verification loop pattern:
    1. Generate code
    2. Generate tests
    3. Execute tests
    4. If fail → feedback to generator
    5. Repeat until pass or max retries
    """
    
    def __init__(
        self,
        executor: CodeExecutor,
        max_retries: int = 3
    ):
        self.executor = executor
        self.max_retries = max_retries
        self.retry_count = 0
        
    async def verify(
        self,
        code: str,
        test_code: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Run verification loop on generated code.
        
        Returns:
            Dict with verification result and feedback
        """
        self.retry_count = 0
        
        while self.retry_count < self.max_retries:
            result = await self.executor.execute_with_language(
                code=code,
                language=language,
                test_code=test_code
            )
            
            if result.passed:
                return {
                    "verified": True,
                    "retries": self.retry_count,
                    "result": result
                }
            
            self.retry_count += 1
            
            # Generate feedback for next iteration
            feedback = self._generate_feedback(result)
            
            logger.info(f"Verification attempt {self.retry_count} failed: {feedback}")
            
            # In real implementation, this would call back to the LLM
            # For now, just return the failure
            if self.retry_count >= self.max_retries:
                return {
                    "verified": False,
                    "retries": self.retry_count,
                    "result": result,
                    "feedback": feedback
                }
        
        return {"verified": False, "retries": self.retry_count}
    
    def _generate_feedback(self, result: ExecutionResult) -> str:
        """Generate actionable feedback from execution result."""
        feedback_parts = []
        
        if result.status == ExecutionStatus.TIMEOUT:
            feedback_parts.append("Code execution timed out. Optimize for performance or check for infinite loops.")
        
        if result.stderr:
            feedback_parts.append(f"Errors:\n{result.stderr}")
        
        if result.exit_code != 0:
            feedback_parts.append(f"Exit code: {result.exit_code}")
        
        return "\n".join(feedback_parts) or "Unknown error"
