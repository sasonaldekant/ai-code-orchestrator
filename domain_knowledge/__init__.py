"""Domain Knowledge Ingestion Module.

This module provides tools for ingesting domain-specific knowledge from:
- Database schemas (SQL DDL, EF Core, Prisma, Django)
- Existing codebases (.NET, React, Node.js, Python)
- Component libraries (React, Vue, Angular, Blazor)
- Design systems (Style Dictionary, CSS-in-JS)

Usage:
    from domain_knowledge import DomainConfig, DomainKnowledgeIngester
    
    config = DomainConfig.from_yaml('path/to/domain_config.yaml')
    ingester = DomainKnowledgeIngester(config)
    documents = ingester.ingest_all()
"""

from .domain_config import DomainConfig, KnowledgeSource, RAGStrategy
from .base_ingester import BaseIngester

__all__ = [
    'DomainConfig',
    'KnowledgeSource',
    'RAGStrategy',
    'BaseIngester',
]

__version__ = '3.0.0'
