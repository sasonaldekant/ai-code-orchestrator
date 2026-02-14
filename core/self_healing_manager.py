import logging
import asyncio
import json
from typing import Dict, Any, List, Optional
from core.llm_client_v2 import LLMClientV2
from core.model_router_v2 import ModelRouterV2
from core.code_executor import CodeExecutor # Assuming this exists or I'll use run_command logic

logger = logging.getLogger(__name__)

class SelfHealingManager:
    """
    Implements a resource-efficient self-healing loop.
    1. Runs build/validation commands.
    2. Small model monitors output and identifies errors.
    3. Large model fixes errors based on small model's report.
    """

    def __init__(self, llm_client: LLMClientV2, model_router: ModelRouterV2):
        self.llm_client = llm_client
        self.model_router = model_router
        # CodeExecutor likely handles shell execution
        self.executor = CodeExecutor()

    async def run_self_healing_cycle(
        self,
        build_commands: List[str] = None,
        context: Dict[str, Any] = None,
        max_attempts: int = 2
    ) -> Dict[str, Any]:
        """
        Main entry point for self-healing.
        If build_commands are not provided, auto-detects them.
        """
        if not build_commands:
            build_commands = await self._detect_build_commands()
            logger.info(f"Auto-detected build commands: {build_commands}")

        if not build_commands:
            logger.warning("No build commands detected or provided. Skipping self-healing.")
            return {"status": "skipped", "reason": "no_commands"}

        for attempt in range(max_attempts):
            logger.info(f"Self-healing cycle attempt {attempt + 1}")
            
            # 1. Run build commands and capture logs
            logs = []
            all_passed = True
            for cmd in build_commands:
                result = await self.executor.execute_command(cmd)
                logs.append({
                    "command": cmd,
                    "stdout": result.get("stdout", ""),
                    "stderr": result.get("stderr", ""),
                    "exit_code": result.get("exit_code", 0)
                })
                if result.get("exit_code", 0) != 0:
                    all_passed = False
                    break
            
            if all_passed:
                logger.info("Integrity check passed. No self-healing needed.")
                return {"status": "success", "attempts": attempt + 1}

            # 2. Use small model to interpret logs
            msg = "Small model interpreting build errors..."
            print(f":::STEP:{{\"type\": \"analyzing\", \"text\": \"{msg}\"}}:::", flush=True)
            
            error_report = await self._interpret_with_small_model(logs, context)
            
            if not error_report.get("errors_found"):
                logger.warning("Integrity failed but small model found no actionable errors.")
                return {"status": "unresolved", "error": "Integrity failed, but no actionable errors identified."}

            # 3. Use large model to fix based on report
            msg = "Strong model generating fixes based on error report..."
            print(f":::STEP:{{\"type\": \"editing\", \"text\": \"{msg}\"}}:::", flush=True)
            
            fix_result = await self._apply_fix_with_large_model(error_report, context)
            
            # Logic to actually apply changes (likely via FileWriter/apply_patch)
            # For now, we assume _apply_fix_with_large_model returns status
            
        return {"status": "failed", "attempts": max_attempts}

    async def _interpret_with_small_model(self, logs: List[Dict], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use a cheap model (Gemini Flash) to find the 'needle' in the 'haystack' of logs.
        """
        # Get cheap model (Tier 0)
        config = self.model_router.base_router.get_model_for_phase("monitor")
        
        log_text = "\n".join([f"CMD: {l['command']}\nSTDOUT: {l['stdout']}\nSTDERR: {l['stderr']}" for l in logs])
        
        prompt = (
            "You are a Build Log Analyzer. Your goal is to extract technical errors from build logs.\n"
            "Analyze the following logs to find compilation errors, syntax errors, or test failures.\n"
            "Ignore warnings unless they cause failure.\n\n"
            "Return JSON format:\n"
            "{\n"
            "  \"errors_found\": true/false,\n"
            "  \"files\": [\n"
            "    {\"path\": \"path/to/file.py\", \"line\": 10, \"error\": \"syntax error...\", \"context\": \"code snippet if available\"}\n"
            "  ],\n"
            "  \"summary\": \"Brief description of the failure\"\n"
            "}"
        )

        user_content = f"LOGS:\n{log_text[:10000]}" # Increase context limit for logs

        response = await self.llm_client.complete(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_content}
            ],
            model=config.model,
            json_mode=True
        )
        
        return json.loads(response.content)

    async def _apply_fix_with_large_model(self, error_report: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use a strong model (Claude Sonnet or GPT-4o) to generate a precise code fix.
        """
        # Get healer model (Tier 3)
        config = self.model_router.base_router.get_model_for_phase("self_healer")
        
        # Read content of failing files to provide context
        file_contexts = []
        for f in error_report.get("files", []):
            path = f.get("path")
            if path:
                try:
                    # Provide snippet or full file depending on size
                    # prioritizing full file for accurate patching
                    content = await self._read_file_safe(path)
                    file_contexts.append(f"FILE: {path}\nCONTENT:\n{content}\n")
                except Exception as e:
                    logger.warning(f"Could not read failing file {path}: {e}")

        files_str = "\n".join(file_contexts)
        
        system_prompt = (
            "You are a Senior Software Engineer specializing in debugging.\n"
            "You will receive an error report and the content of the failing files.\n"
            "Your task is to provide a corrected version of the code that fixes the errors.\n\n"
            "IMPORTANT: Return the response in strict JSON format:\n"
            "{\n"
            "  \"patches\": [\n"
            "    {\"path\": \"path/to/file.py\", \"new_content\": \"...full corrected file content...\"}\n"
            "  ],\n"
            "  \"explanation\": \"Brief explanation of the fix\"\n"
            "}"
        )

        user_prompt = (
            f"ERROR REPORT:\n{json.dumps(error_report, indent=2)}\n\n"
            f"FAILING FILES:\n{files_str}\n\n"
            "Generate the fixes."
        )

        try:
            response = await self.llm_client.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=config.model,
                temperature=0.0,
                json_mode=True
            )
            
            fix_data = json.loads(response.content)
            await self._apply_patches(fix_data.get("patches", []))
            
            return {
                "status": "applied", 
                "patches": len(fix_data.get("patches", [])),
                "explanation": fix_data.get("explanation")
            }
            
        except Exception as e:
            logger.error(f"Self-healing fix failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def _apply_patches(self, patches: List[Dict[str, str]]):
        """
        Write the new content to files. 
        Note: In production, consider using diff/patch instead of full overwrite for safety.
        """
        import aiofiles
        import os
        
        for patch in patches:
            path = patch.get("path")
            content = patch.get("new_content")
            
            if path and content:
                # Ensure directory exists (rarely needed for healing but good practice)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                    await f.write(content)
                logger.info(f"Self-healer patched file: {path}")

    async def _read_file_safe(self, path: str) -> str:
        """Helper to read file async"""
        import aiofiles
        import os
        if os.path.exists(path):
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                return await f.read()
        return ""

    async def validate_prompt_with_small_model(self, prompt: str) -> str:
        """
        Refine/Verify a prompt using a small model before sending to expensive workflow.
        """
        config = self.model_router.get_model_for_phase("monitor")
        
        verify_prompt = (
            "Review the following LLM prompt. Check if it is:\n"
            "1. Clear and unambiguous.\n"
            "2. Provides enough context.\n"
            "3. Specifies desired output format.\n\n"
            f"PROMPT TO REVIEW:\n{prompt}\n\n"
            "If it's perfect, return 'VALID'. Otherwise, return a refined version of the prompt that is more effective."
        )

        response = await self.llm_client.complete(
            messages=[{"role": "user", "content": verify_prompt}],
            model=config.model
        )
        
        result = response.content.strip()
        if "VALID" in result[:10]:
            return prompt
        return result

    async def _detect_build_commands(self) -> List[str]:
        """
        Scan for project markers to determine appropriate build/check commands.
        """
        import os
        commands = []
        
        # Check for Python (FastAPI/General)
        if os.path.exists("api/app.py"):
            commands.append("python -m py_compile api/app.py")
        elif os.path.exists("app.py"):
            commands.append("python -m py_compile app.py")
            
        # Check for Node/TypeScript (Frontend)
        if os.path.exists("ui/package.json"):
            # Ensure npm install was run at some point? No, just try tsc
            commands.append("cd ui && call npx tsc --noEmit")
        elif os.path.exists("package.json"):
             commands.append("call npx tsc --noEmit")

        # Check for .NET
        # Find any csproj
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".csproj"):
                    commands.append(f"dotnet build {os.path.join(root, file)}")
                    if commands: break # Just build one for now
            if commands: break

        return commands
