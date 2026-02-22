"""
Form Studio Chat API Routes.

Provides endpoints for AI-powered chat within Form Studio,
focused exclusively on JSON form schema context and DynUI components.
Includes SSE streaming endpoint for real-time token delivery.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
import json
import logging

from core.form_engine.form_chat_service import FormChatService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/forms", tags=["forms-chat"])

# Shared service instance
chat_service = FormChatService()


# ─── Pydantic Models ───────────────────────────────────────────────────────

class ChatMessageInput(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class FormChatRequest(BaseModel):
    message: str
    current_schema: Dict[str, Any]
    chat_history: List[ChatMessageInput] = []
    preview_state: Optional[Dict[str, Any]] = None


class FormChatSummarizeRequest(BaseModel):
    current_schema: Dict[str, Any]
    chat_history: List[ChatMessageInput]
    preview_state: Optional[Dict[str, Any]] = None


# ─── Chat Endpoint (Standard) ─────────────────────────────────────────────

@router.post("/chat")
async def form_chat(req: FormChatRequest):
    """
    AI chat focused on JSON form schema context.
    Sends user message + current schema + history → returns AI reply + optional schema update.
    Uses RAG Tier 2-3 for DynUI tokens and component patterns.
    """
    try:
        history_dicts = [{"role": m.role, "content": m.content} for m in req.chat_history]

        response = await chat_service.chat(
            message=req.message,
            current_schema=req.current_schema,
            chat_history=history_dicts,
            preview_state=req.preview_state,
        )

        return {
            "reply": response.reply,
            "updated_schema": response.updated_schema,
            "schema_diff": response.schema_diff,
            "rag_sources": response.rag_sources,
            "ui_hints": response.ui_hints,
        }
    except Exception as e:
        logger.error(f"Form chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Chat Endpoint (SSE Streaming) ────────────────────────────────────────

@router.post("/chat/stream")
async def form_chat_stream(req: FormChatRequest, request: Request):
    """
    SSE streaming version of /forms/chat.
    Streams the AI reply token-by-token, then sends the final metadata
    (schema update, diff, rag sources) as the last event.

    SSE Event types:
    - "token": partial reply text chunk
    - "metadata": final payload with updated_schema, schema_diff, rag_sources
    - "error": error message
    - "done": stream complete
    """
    async def event_generator():
        try:
            history_dicts = [{"role": m.role, "content": m.content} for m in req.chat_history]

            response = await chat_service.chat(
                message=req.message,
                current_schema=req.current_schema,
                chat_history=history_dicts,
                preview_state=req.preview_state,
            )

            # Simulate streaming by chunking the reply into words
            # (Real streaming would use LLM streaming API — this provides
            #  the SSE infrastructure for when we enable true token streaming)
            reply = response.reply
            words = reply.split(' ')
            buffer = ""

            for i, word in enumerate(words):
                if await request.is_disconnected():
                    return

                buffer += word + (' ' if i < len(words) - 1 else '')

                # Send chunks of ~3-5 words for natural reading speed
                if (i + 1) % 4 == 0 or i == len(words) - 1:
                    chunk_data = json.dumps({"type": "token", "content": buffer})
                    yield f"data: {chunk_data}\n\n"
                    buffer = ""
                    await asyncio.sleep(0.03)  # 30ms between chunks

            # Send metadata (schema update, diff, sources)
            metadata = {
                "type": "metadata",
                "updated_schema": response.updated_schema,
                "schema_diff": response.schema_diff,
                "rag_sources": response.rag_sources,
                "ui_hints": response.ui_hints,
            }
            yield f"data: {json.dumps(metadata)}\n\n"

            # Done event
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            logger.error(f"Form chat stream error: {e}")
            error_data = json.dumps({"type": "error", "content": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ─── Summarize Endpoint ───────────────────────────────────────────────────

@router.post("/chat/summarize")
async def form_chat_summarize(req: FormChatSummarizeRequest):
    """
    Summarize the chat session into enriched instructions for the orchestrator.
    Called before 'Approve & Generate' to assemble all user decisions.
    """
    try:
        history_dicts = [{"role": m.role, "content": m.content} for m in req.chat_history]

        result = chat_service.generate_enriched_prompt(
            current_schema=req.current_schema,
            chat_history=history_dicts,
            preview_state=req.preview_state,
        )

        return result
    except Exception as e:
        logger.error(f"Form chat summarize error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
