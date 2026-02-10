"""
Vision Manager for AI Code Orchestrator v3.0

Handles multi-modal interactions (image analysis) using LLMClientV2.
Supports:
- Error Screenshot Analysis
- UI Design Verification
- Implementation from Mockups
"""

import base64
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

from core.llm_client_v2 import LLMClientV2
from core.registry import register_tool

logger = logging.getLogger(__name__)

class VisionManager:
    def __init__(self, llm_client: LLMClientV2):
        self.llm_client = llm_client
        self.model = "gpt-4o" # Default model with strong vision capabilities

    @register_tool(
        name="analyze_image",
        description="Analyzes an image (screenshot, diagram) using a multimodal LLM.",
        category="vision"
    )

    async def analyze_image(
        self, 
        image_path_or_url: str, 
        prompt: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze an image with a specific prompt.
        """
        try:
            image_content = self._prepare_image_content(image_path_or_url)
            
            system_prompt = "You are an expert AI software engineer with computer vision capabilities. Analyze the provided image in the context of software development."
            
            user_content = [
                {"type": "text", "text": prompt},
                image_content
            ]
            
            if context:
                user_content.insert(0, {"type": "text", "text": f"Context: {context}"})
                
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
            
            logger.info(f"Sending vision request to {self.model}...")
            
            response = await self.llm_client.complete(
                messages=messages,
                model=self.model,
                temperature=0.2,
                json_mode=True # Expecting structured analysis if possible, but depends on prompt
            )
            
            return {
                "success": True,
                "analysis": response.content,
                "model": response.model,
                "tokens": response.tokens_used
            }
            
        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _prepare_image_content(self, source: str) -> Dict[str, Any]:
        """
        Prepare image content block for OpenAI API.
        Handles local paths (base64) and remote URLs.
        """
        # check if url
        if source.startswith("http://") or source.startswith("https://"):
            return {
                "type": "image_url",
                "image_url": {
                    "url": source
                }
            }
            
        # check if data uri
        if source.startswith("data:"):
            return {
                "type": "image_url",
                "image_url": {
                    "url": source
                }
            }
            
        # check if local file
        path = Path(source)
        if path.exists():
            return self._encode_local_image(path)
            
        raise ValueError(f"Image source not found: {source}")

    def _encode_local_image(self, path: Path) -> Dict[str, Any]:
        """Read and base64 encode a local image."""
        try:
            with open(path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                
            # Determine mime type roughly
            suffix = path.suffix.lower()
            mime_type = "image/jpeg" # default
            if suffix == ".png": mime_type = "image/png"
            elif suffix == ".webp": mime_type = "image/webp"
            elif suffix == ".gif": mime_type = "image/gif"
            
            return {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{base64_image}"
                }
            }
        except Exception as e:
            raise ValueError(f"Failed to encode image {path}: {e}")
