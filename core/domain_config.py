"""
Domain Configuration Parser.
Parses the domain_config.yaml file to configure the orchestrator and ingestion.
"""

import yaml
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path

@dataclass
class KnowledgeSource:
    type: str # database, component_library
    source_format: str # ef_core, react_tsx
    path: str
    bounded_contexts: Optional[Dict[str, List[str]]] = None

@dataclass
class DomainConfig:
    name: str
    description: str
    knowledge_sources: List[KnowledgeSource] = field(default_factory=list)

class DomainConfigParser:
    def __init__(self, config_path: str = "config/domain_config.yaml"):
        self.config_path = Path(config_path)

    def parse(self) -> DomainConfig:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Domain config file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        domain_data = data.get("domain", {})
        
        sources = []
        for src in domain_data.get("knowledge_sources", []):
            sources.append(KnowledgeSource(
                type=src.get("type"),
                source_format=src.get("source_format"),
                path=src.get("path"),
                bounded_contexts=src.get("bounded_contexts")
            ))

        return DomainConfig(
            name=domain_data.get("name", "Unknown Domain"),
            description=domain_data.get("description", ""),
            knowledge_sources=sources
        )
