from dataclasses import dataclass

@dataclass
class ModelChoice:
    name: str
    temperature: float = 0.0

# Basic heuristic: route by specialty/phase (placeholder)
def route(phase: str, specialty: str | None) -> ModelChoice:
    if specialty in {"css", "react", "typescript"}:
        return ModelChoice(name="gpt-4o-mini")
    if specialty in {"dotnet", "backend"}:
        return ModelChoice(name="gpt-4o")
    return ModelChoice(name="gpt-4o-mini")
