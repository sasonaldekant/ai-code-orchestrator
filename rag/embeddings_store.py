from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json, math, hashlib

def embed(text: str, dim: int = 128) -> list[float]:
    """Deterministic fake 'embedding': uses SHA256 rolling to fill dim."""
    seed = hashlib.sha256(text.encode("utf-8")).digest()
    vec = [(seed[i % len(seed)] / 255.0) for i in range(dim)]
    return vec

def cos(a: list[float], b: list[float]) -> float:
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    return dot / (na*nb + 1e-9)

@dataclass
class EmbeddingRecord:
    id: str
    text: str
    vector: list[float]

class EmbeddingStore:
    def __init__(self, path: Path):
        self.path = path
        self.records: list[EmbeddingRecord] = []
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            self.records = [EmbeddingRecord(**r) for r in data]

    def add(self, id: str, text: str):
        self.records.append(EmbeddingRecord(id=id, text=text, vector=embed(text)))

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps([r.__dict__ for r in self.records], indent=2), encoding="utf-8")

    def query(self, text: str, k: int = 3) -> list[tuple[str, float, str]]:
        q = embed(text)
        scored = [(r.id, cos(q, r.vector), r.text) for r in self.records]
        return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
