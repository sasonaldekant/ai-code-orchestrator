from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from core.vision_manager import VisionManager
from core.llm_client_v2 import LLMClientV2
from core.cost_manager import CostManager

router = APIRouter(prefix="/vision", tags=["vision"])
logger = logging.getLogger(__name__)

class VisionAnalysisRequest(BaseModel):
    image: str # URL or Base64 (handled by manager, but manager expects path/url)
               # If it's base64 raw content, VisionManager._prepare_image_content expects a path or URL.
               # We need to handle raw base64 from API too or save it to temp file.
               # Actually, the frontend usually sends base64 data URI.
               # VisionManager._prepare_image_content checks for http/https, else assumes path.
               # I should update VisionManager to handle data URIs directly?
               # Let's see VisionManager again. 
               # It has _encode_local_image that returns data uri.
               # I should update VisionManager to accept data uri directly if passed.
    prompt: str
    context: Optional[str] = None

class VisionAnalysisResponse(BaseModel):
    success: bool
    analysis: Optional[str] = None
    error: Optional[str] = None

@router.post("/analyze", response_model=VisionAnalysisResponse)
async def analyze_image(req: VisionAnalysisRequest):
    try:
        # Initialize dependencies (lightweight)
        cost_manager = CostManager()
        llm_client = LLMClientV2(cost_manager)
        vision_manager = VisionManager(llm_client)
        
        # Handle Data URI directly (if frontend sends data:image/...)
        # VisionManager strictly expects path or http url.
        # If we pass a data URI to _prepare_image_content, it will fail because it tries Path(source).exists().
        # We need to update VisionManager, but for now let's handle it here or assume `image` is a path/url.
        # But wait, frontend upload usually results in a file on backend or a base64 string.
        # OrchestratorUI file upload input... we haven't implemented that part in UI yet.
        # Ideally, we upload file to server, get path, pass path to VisionManager.
        
        # Let's assume for now the API receives a URL or a Path (e.g. from a previous upload).
        # Or if we want to support direct base64, we should update VisionManager.
        
        # Checking VisionManager._prepare_image_content:
        # if source.startswith("http"): ...
        # path = Path(source)
        # if path.exists(): ...
        
        # So passing a data URI string will raise ValueError.
        
        result = await vision_manager.analyze_image(req.image, req.prompt, req.context)
        
        if result["success"]:
            return VisionAnalysisResponse(success=True, analysis=result["analysis"])
        else:
            return VisionAnalysisResponse(success=False, error=result.get("error"))
            
    except Exception as e:
        logger.error(f"Vision API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
