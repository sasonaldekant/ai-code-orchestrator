import os, json, hashlib, time, random, datetime, sys
from dataclasses import dataclass

@dataclass
class LLMResponse:
    text: str
    model: str
    usage: dict | None = None

def _trace(event: str, payload: dict):
    if os.getenv("TRACE_JSONL", "1") == "1":
        line = json.dumps({
            "ts": datetime.datetime.utcnow().isoformat() + "Z",
            "event": event,
            **payload
        }, ensure_ascii=False)
        with open(os.getenv("TRACE_FILE", "trace.jsonl"), "a", encoding="utf-8") as f:
            f.write(line + "\n")

def _offline_response(model: str, prompt: str) -> LLMResponse:
    h = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:8]
    text = json.dumps({"note": f"offline-{model}", "id": h})
    _trace("llm.offline", {"model": model, "prompt_hash": h, "bytes": len(text)})
    return LLMResponse(text=text, model=model, usage={"prompt_tokens": 0, "completion_tokens": 0})

def call(model: str, prompt: str, temperature: float = 0.0, max_retries: int = 3) -> LLMResponse:
    """LLM call with optional OpenAI SDK and exponential backoff.
    OFFLINE_LLM=1 forces deterministic stub.
    TRACE_JSONL=1 writes events to TRACE_FILE (default: trace.jsonl).
    """
    if os.getenv("OFFLINE_LLM", "1") == "1":
        return _offline_response(model, prompt)

    # Try OpenAI SDK if available
    try:
        from openai import OpenAI  # type: ignore
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        backoff = 0.5
        for attempt in range(max_retries + 1):
            try:
                _trace("llm.request", {"model": model, "temperature": temperature})
                # Using Responses API (unified); adjust if using older SDKs
                rsp = client.responses.create(
                    model=model,
                    input=prompt,
                    temperature=temperature
                )
                text = rsp.output_text or ""
                usage = getattr(rsp, "usage", None)
                _trace("llm.response", {"model": model, "bytes": len(text)})
                return LLMResponse(text=text, model=model, usage=usage if isinstance(usage, dict) else None)
            except Exception as e:
                _trace("llm.error", {"model": model, "attempt": attempt, "error": str(e)})
                if attempt >= max_retries:
                    raise
                time.sleep(backoff + random.random() * 0.25)
                backoff *= 2
    except Exception as e:
        # Fallback to offline stub when SDK missing or call failed
        _trace("llm.fallback", {"model": model, "reason": str(e.__class__.__name__)})
        return _offline_response(model, prompt)
