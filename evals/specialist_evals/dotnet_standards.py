def score_dotnet(doc: dict) -> dict:
    endpoints = doc.get("endpoints", [])
    openapi = doc.get("openapi", "")
    has_health = any("/health" in e.lower() for e in endpoints)
    has_openapi = "openapi:" in openapi.lower()
    score = (1 if has_health else 0) + (1 if has_openapi else 0)
    notes = []
    if not has_health: notes.append("No /health endpoint defined")
    if not has_openapi: notes.append("OpenAPI spec missing header")
    return {"score": score, "notes": notes}
