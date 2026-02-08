"""
CPU-friendly retrieval (no GPU, no external deps).
BM25 over chunked .md/.txt docs. Stores a JSON index on disk.
"""
from __future__ import annotations

from pathlib import Path
import json, math, re
from dataclasses import dataclass
from typing import List, Dict, Tuple

_WORD_RE = re.compile(r"[\w]+", re.UNICODE)

def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in _WORD_RE.findall(text)]

@dataclass
class Hit:
    path: str
    text: str
    score: float

def _chunk_text(txt: str, chunk_chars: int = 800, overlap: int = 120) -> List[str]:
    if len(txt) <= chunk_chars:
        return [txt]
    chunks = []
    i = 0
    while i < len(txt):
        chunk = txt[i:i+chunk_chars]
        chunks.append(chunk)
        if i + chunk_chars >= len(txt):
            break
        i += max(1, chunk_chars - overlap)
    return chunks

def ingest(docs_dir: str, index_path: str, chunk_chars: int = 800, overlap: int = 120) -> None:
    docs = []
    df: Dict[str, int] = {}
    idx = 0
    for p in Path(docs_dir).rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".md", ".txt"}:
            continue
        raw = p.read_text(encoding="utf-8", errors="ignore")
        for chunk in _chunk_text(raw, chunk_chars, overlap):
            tokens = _tokenize(chunk)
            if not tokens:
                continue
            tf: Dict[str, int] = {}
            seen = set()
            for tok in tokens:
                tf[tok] = tf.get(tok, 0) + 1
                if tok not in seen:
                    df[tok] = df.get(tok, 0) + 1
                    seen.add(tok)
            docs.append({
                "id": idx,
                "path": str(p),
                "text": chunk,
                "dl": len(tokens),
                "tf": tf
            })
            idx += 1
    N = len(docs) or 1
    avgdl = sum(d["dl"] for d in docs) / N
    index = {"N": N, "avgdl": avgdl, "docs": docs, "df": df}
    Path(index_path).write_text(json.dumps(index), encoding="utf-8")

def _bm25_score(query_tokens: List[str], doc, df: Dict[str,int], N: int, avgdl: float, k1: float = 1.5, b: float = 0.75) -> float:
    score = 0.0
    dl = doc["dl"]
    tf = doc["tf"]
    for t in query_tokens:
        ni = df.get(t, 0)
        if ni == 0:
            continue
        idf = math.log((N - ni + 0.5) / (ni + 0.5) + 1.0)
        f = tf.get(t, 0)
        if f == 0:
            continue
        score += idf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * dl / avgdl))
    return score

def query(question: str, index_path: str, top_k: int = 4) -> List[Hit]:
    idx = json.loads(Path(index_path).read_text(encoding="utf-8"))
    q = _tokenize(question)
    scored: List[Tuple[float, dict]] = []
    for d in idx["docs"]:
        s = _bm25_score(q, d, idx["df"], idx["N"], idx["avgdl"])
        if s > 0:
            scored.append((s, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    hits: List[Hit] = []
    for s, d in scored[:top_k]:
        hits.append(Hit(path=d["path"], text=d["text"], score=float(s)))
    return hits
