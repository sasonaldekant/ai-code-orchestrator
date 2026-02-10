"""Database schema knowledge ingester for EF Core."""

import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from domain_knowledge.ingestion.base_ingester import Ingester
from rag.vector_store import Document

logger = logging.getLogger(__name__)

class DatabaseSchemaIngester(Ingester):
    """
    Parses C# DbContext and Entity classes to create structured documentation.
    """

    def __init__(self, dbcontext_path: str, models_dir: str):
        self.dbcontext_path = Path(dbcontext_path)
        self.models_dir = Path(models_dir)
        
        # If directory provided, try to find the DbContext file
        if self.dbcontext_path.is_dir():
            # Look for logical DbContext file
            candidates = list(self.dbcontext_path.rglob("*Context.cs"))
            if candidates:
                self.dbcontext_path = candidates[0]
                logger.info(f"Auto-detected DbContext file: {self.dbcontext_path}")
            else:
                logger.warning(f"No *Context.cs file found in {dbcontext_path}, ingestion might fail.")

    def ingest(self) -> List[Document]:
        """
        Extract schema and generate vector-ready documents.
        """
        logger.info(f"Ingesting database schema from {self.dbcontext_path}")
        try:
            schema = self.extract_schema()
            return self.generate_embeddings_documents(schema)
        except Exception as e:
            logger.error(f"Failed to ingest database schema: {e}")
            return []

    def extract_schema(self) -> Dict[str, Any]:
        """
        Parses C# files to extract:
        - Entity names
        - Properties (name, type, nullable, max length)
        - Relationships (one-to-many, many-to-many)
        """
        schema: Dict[str, Any] = {
            "entities": {},
            "relationships": [],
            "database_name": self._extract_db_name(),
        }

        # Parse DbContext for DbSet definitions
        dbsets = self._parse_dbcontext()

        # Parse each Entity model
        for entity_name in dbsets:
            entity_info = self._parse_entity_model(entity_name)
            if entity_info:
                schema["entities"][entity_name] = entity_info

        # Extract relationships from navigation properties
        schema["relationships"] = self._extract_relationships(schema["entities"])
        return schema

    def _extract_db_name(self) -> str:
        """Attempts to extract database name from DbContext or uses default."""
        # Simple heuristic or configuration lookup could go here
        return self.dbcontext_path.stem

    def _parse_dbcontext(self) -> List[str]:
        """Extract `DbSet<T>` declarations."""
        if not self.dbcontext_path.exists():
            logger.warning(f"DbContext file not found: {self.dbcontext_path}")
            return []
            
        content = self.dbcontext_path.read_text(encoding="utf-8")
        pattern = r'DbSet<(\w+)>\s+(\w+)'
        matches = re.findall(pattern, content)
        # Return the type name (T), assuming it matches the file name
        return [match[0] for match in matches]

    def _parse_entity_model(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """Parses an individual entity model file."""
        # Try both direct path and recursive search if needed, but keeping it simple for now
        entity_path = self.models_dir / f"{entity_name}.cs"
        if not entity_path.exists():
            # Try subdirectories if flattened structure assumption fails
            found_files = list(self.models_dir.rglob(f"{entity_name}.cs"))
            if found_files:
                entity_path = found_files[0]
            else:
                logger.warning(f"Entity file not found: {entity_name}.cs")
                return None
        
        content = entity_path.read_text(encoding="utf-8")
        return {
            "name": entity_name,
            "properties": self._extract_properties(content),
            "navigation_properties": self._extract_navigation_properties(content),
            "attributes": self._extract_attributes(content),
        }

    def _extract_properties(self, content: str) -> List[Dict[str, Any]]:
        """Extract property definitions from a C# class."""
        properties = []
        # Matches: [Attribute] public Type PropName { get; set; }
        # Simplified regex for demonstration
        pattern = r'(?:\[(\w+)(?:\((\d+)\))?\]\s+)?public\s+(\w+\??)\s+(\w+)\s*\{\s*get;\s*set;\s*\}'
        matches = re.findall(pattern, content)
        for match in matches:
            attribute, max_length, prop_type, prop_name = match
            properties.append({
                "name": prop_name,
                "type": prop_type,
                "nullable": "?" in prop_type,
                "max_length": int(max_length) if max_length else None,
                "attribute": attribute if attribute else None,
            })
        return properties

    def _extract_navigation_properties(self, content: str) -> List[Dict[str, str]]:
        """Extract navigation properties (collections and references)."""
        nav_props: List[Dict[str, str]] = []
        # ICollection<T> or List<T> -> one-to-many
        collection_pattern = r'(?:ICollection|List)<(\w+)>\s+(\w+)'
        for match in re.findall(collection_pattern, content):
            nav_props.append({
                "type": "one-to-many",
                "related_entity": match[0],
                "property_name": match[1],
            })
        
        # Simple reference properties (virtual T PropName)
        # This regex is a bit broad, might need refinement for production
        ref_pattern = r'public\s+virtual\s+(\w+)\s+(\w+)\s*\{\s*get;\s*set;\s*\}'
        for match in re.findall(ref_pattern, content):
            # Exclude scalar types if they accidentally match (though 'virtual' usually implies nav prop in EF)
            if match[0] not in ["string", "int", "bool", "decimal", "double", "float", "DateTime"]:
                 nav_props.append({
                    "type": "many-to-one", # Typical for reference
                    "related_entity": match[0],
                    "property_name": match[1],
                })

        return nav_props
        
    def _extract_attributes(self, content: str) -> List[str]:
        """Extract class level attributes."""
        # TODO: Implement extracting [Table("name")], [Index], etc.
        return []

    def _extract_relationships(self, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build relationship graph from navigation properties."""
        relationships: List[Dict[str, Any]] = []
        for entity_name, entity_info in entities.items():
            for nav_prop in entity_info.get("navigation_properties", []):
                relationships.append({
                    "from": entity_name,
                    "to": nav_prop["related_entity"],
                    "type": nav_prop["type"],
                    "property": nav_prop["property_name"],
                })
        return relationships

    def generate_embeddings_documents(self, schema: Dict[str, Any]) -> List[Document]:
        """
        Generate natural language descriptions for embedding.
        """
        documents: List[Document] = []
        
        # 1. Per-entity descriptions
        for entity_name, entity_info in schema["entities"].items():
            doc_content = f"Entity: {entity_name}\n\n"
            doc_content += "Properties:\n"
            for prop in entity_info["properties"]:
                doc_content += f"- {prop['name']}: {prop['type']}"
                if prop['max_length']:
                    doc_content += f" (max length: {prop['max_length']})"
                if prop['nullable']:
                    doc_content += " (nullable)"
                doc_content += "\n"
            
            if entity_info.get("navigation_properties"):
                doc_content += "\nRelationships:\n"
                for nav_prop in entity_info["navigation_properties"]:
                    doc_content += f"- {nav_prop['property_name']}: {nav_prop['type']} into {nav_prop['related_entity']}\n"
            
            documents.append(Document(
                id=f"entity_{entity_name}",
                text=doc_content,
                metadata={
                    "type": "database_schema",
                    "entity": entity_name,
                    "schema_info": json.dumps(entity_info) # Store full info as string if needed by vector store limits
                }
            ))
            
        # 2. Relationship descriptions (optional, for explicit relationship queries)
        for rel in schema["relationships"]:
             doc_content = f"Relationship: {rel['from']} has {rel['type']} relationship with {rel['to']} via {rel['property']}"
             documents.append(Document(
                id=f"rel_{rel['from']}_{rel['to']}_{rel['property']}",
                text=doc_content,
                metadata={
                    "type": "database_relationship",
                    "from": rel['from'],
                    "to": rel['to']
                }
            ))

        return documents
