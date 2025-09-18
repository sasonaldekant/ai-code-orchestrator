import os, json, datetime
from dataclasses import asdict, is_dataclass

TRACE_FILE = os.getenv("TRACE_FILE", "trace.jsonl")

def log(event: str, payload):
    if is_dataclass(payload):
        payload = asdict(payload)
    rec = {"ts": datetime.datetime.utcnow().isoformat() + "Z", "event": event, **payload}
    with open(TRACE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
