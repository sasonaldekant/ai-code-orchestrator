def score_ts(doc: dict) -> dict:
    text = "\n".join(doc.get(k, []) if isinstance(doc.get(k), list) else [doc.get(k, "")] for k in ["types","enums","interfaces"])  # type: ignore
    strict = all(substr in text for substr in [":", "interface", "type "])
    return {"score": 1 if strict else 0, "notes": [] if strict else ["Missing basic TS constructs"]}
