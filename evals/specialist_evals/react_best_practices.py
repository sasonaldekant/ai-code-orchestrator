def score_react(doc: dict) -> dict:
    jsx = doc.get("jsx", "")
    hooks = "useState(" in jsx or "useEffect(" in jsx
    fncomp = "function" in jsx or "=>" in jsx
    return {"score": (1 if hooks else 0) + (1 if fncomp else 0), "notes": []}
