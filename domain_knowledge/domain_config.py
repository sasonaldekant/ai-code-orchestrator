"""Domain Configuration Loader.

Loads and validates domain_config.yaml files.
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class SourceType(Enum):
    """Supported knowledge source types."""
    DATABASE = "database"
    EXISTING_CODEBASE = "existing_codebase"
    COMPONENT_LIBRARY = "component_library"
    DESIGN_SYSTEM = "design_system"
    API_SPEC = "api_spec"


class SourceFormat(Enum):
    """Supported source formats."""
    # Database formats
    SQL_DDL = "sql_ddl"
    EF_CORE = "ef_core"
    PRISMA = "prisma"
    DJANGO_MODELS = "django_models"
    
    # Codebase formats
    DOTNET_SOLUTION = "dotnet_solution"
    NODEJS = "nodejs"
    REACT_TYPESCRIPT = "react_typescript"
    REACT_TSX = "react_tsx"
    VUE = "vue"
    ANGULAR = "angular"
    PYTHON = "python"
    
    # Other
    OPENAPI = "openapi"
    GRAPHQL = "graphql"


class AnalysisDepth(Enum):
    """Analysis depth for codebase ingestion."""
    SHALLOW = "shallow"  # File structure + exports only
    MEDIUM = "medium"    # + Function signatures
    DEEP = "deep"        # + Implementation details


@dataclass
class KnowledgeSource:
    """Configuration for a single knowledge source."""
    type: SourceType
    source_format: SourceFormat
    path: str
    bounded_contexts: Optional[Dict[str, List[str]]] = None
    analysis_depth: Optional[AnalysisDepth] = None
    focus_areas: Optional[List[str]] = None
    component_groups: Optional[Dict[str, List[str]]] = None
    subpath: Optional[str] = None
    clone_to: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeSource':
        """Create KnowledgeSource from dict."""
        return cls(
            type=SourceType(data['type']),
            source_format=SourceFormat(data['source_format']),
            path=data['path'],
            bounded_contexts=data.get('bounded_contexts'),
            analysis_depth=AnalysisDepth(data['analysis_depth']) if 'analysis_depth' in data else None,
            focus_areas=data.get('focus_areas'),
            component_groups=data.get('component_groups'),
            subpath=data.get('subpath'),
            clone_to=data.get('clone_to')
        )


@dataclass
class RAGStrategy:
    """RAG configuration."""
    vector_store: str  # chromadb, faiss, weaviate
    embedding_model: str
    collection_per_source: bool = True
    multi_collection_retrieval: bool = True
    max_context_tokens: int = 8000
    collections: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RAGStrategy':
        """Create RAGStrategy from dict."""
        return cls(
            vector_store=data['vector_store'],
            embedding_model=data['embedding_model'],
            collection_per_source=data.get('collection_per_source', True),
            multi_collection_retrieval=data.get('multi_collection_retrieval', True),
            max_context_tokens=data.get('max_context_tokens', 8000),
            collections=data.get('collections', {})
        )


@dataclass
class DomainConfig:
    """Complete domain configuration."""
    name: str
    description: str
    knowledge_sources: List[KnowledgeSource]
    rag_strategy: RAGStrategy
    
    @classmethod
    def from_yaml(cls, path: str) -> 'DomainConfig':
        """Load configuration from YAML file."""
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        domain = data['domain']
        sources = [KnowledgeSource.from_dict(s) for s in data['knowledge_sources']]
        rag = RAGStrategy.from_dict(data['rag_strategy'])
        
        return cls(
            name=domain['name'],
            description=domain['description'],
            knowledge_sources=sources,
            rag_strategy=rag
        )
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        # Validate paths exist
        for source in self.knowledge_sources:
            if source.path.startswith('http'):
                continue  # Skip URL validation
            if not Path(source.path).exists():
                errors.append(f"Path not found: {source.path}")
        
        # Validate bounded contexts
        for source in self.knowledge_sources:
            if source.type == SourceType.DATABASE and not source.bounded_contexts:
                errors.append(f"Database source requires bounded_contexts: {source.path}")
        
        return errors
