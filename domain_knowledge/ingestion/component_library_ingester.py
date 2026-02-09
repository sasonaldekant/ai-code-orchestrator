"""Component library knowledge ingester for React TypeScript."""

import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from domain_knowledge.ingestion.base_ingester import Ingester
from rag.vector_store import Document

logger = logging.getLogger(__name__)

class ComponentLibraryIngester(Ingester):
    """
    Parses React .tsx files to extract component metadata, props, and docs.
    """

    def __init__(self, components_dir: str, docs_dir: Optional[str] = None):
        self.components_dir = Path(components_dir)
        self.docs_dir = Path(docs_dir) if docs_dir else None

    def ingest(self) -> List[Document]:
        """
        Extract components and generate vector-ready documents.
        """
        logger.info(f"Ingesting component library from {self.components_dir}")
        try:
            components = self.extract_components()
            return self.generate_embeddings_documents(components)
        except Exception as e:
            logger.error(f"Failed to ingest component library: {e}")
            return []

    def extract_components(self) -> List[Dict[str, Any]]:
        """
        Parses all `.tsx` files and extracts detailed component info.
        """
        components: List[Dict[str, Any]] = []
        if not self.components_dir.exists():
            return []
            
        for tsx_file in self.components_dir.rglob("*.tsx"):
            if tsx_file.name.startswith("index"):
                continue
            component_info = self._parse_component_file(tsx_file)
            if component_info:
                components.append(component_info)
        return components

    def _parse_component_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        content = file_path.read_text(encoding="utf-8")
        component_name = file_path.stem
        
        # Basic check if it's a component (has props interface or export function)
        if f"interface {component_name}Props" not in content and f"export const {component_name}" not in content:
             return None

        props_interface = self._extract_props_interface(content, component_name)
        design_tokens = self._extract_design_tokens(content)
        jsdoc = self._extract_jsdoc(content)
        
        return {
            "name": component_name,
            "file_path": str(file_path.relative_to(self.components_dir)),
            "props": props_interface,
            "design_tokens": design_tokens,
            "description": jsdoc.get("description", ""),
            "examples": jsdoc.get("examples", []),
        }

    def _extract_props_interface(self, content: str, component_name: str) -> List[Dict[str, Any]]:
        """Extract TypeScript interface for component props."""
        props: List[Dict[str, Any]] = []
        interface_pattern = rf'interface\s+{component_name}Props\s*\{{([^}}]+)\}}'
        match = re.search(interface_pattern, content, re.DOTALL)
        if not match:
            return props
            
        interface_body = match.group(1)
        # Matches: propName?: type;
        prop_pattern = r'(\w+)(\?)?:\s*([^;]+);'
        for match in re.finditer(prop_pattern, interface_body):
            prop_name, optional, prop_type = match.groups()
            props.append({
                "name": prop_name,
                "type": prop_type.strip(),
                "optional": optional == "?",
                "description": "", # Could extract from comment above prop
            })
        return props

    def _extract_design_tokens(self, content: str) -> List[str]:
        """
        Extract design tokens such as `theme.colors.primary` or `spacing.md`.
        """
        # Matches typical patterns: theme.X.Y or tokens.X
        pattern = r'(?:theme|design|tokens)\.(\w+\.\w+\.?\w*)'
        matches = re.findall(pattern, content)
        return list(set(matches))

    def _extract_jsdoc(self, content: str) -> Dict[str, Any]:
        jsdoc = {"description": "", "examples": []}
        # Matches block comments /** ... */
        jsdoc_pattern = r'/\*\*([^*]|\*(?!/))*\*/'
        match = re.search(jsdoc_pattern, content, re.DOTALL)
        if not match:
            return jsdoc
            
        jsdoc_content = match.group(0)
        
        # Extract description (text before tags)
        lines = []
        for line in jsdoc_content.split('\n'):
            line = line.strip().replace('/**', '').replace('*/', '').strip('* ')
            if line.startswith('@'):
                break
            if line:
                lines.append(line)
        jsdoc["description"] = " ".join(lines)

        # Extract @example
        example_pattern = r'@example\s+(.+?)(?=@|$)'
        for example_match in re.finditer(example_pattern, jsdoc_content, re.DOTALL):
            jsdoc["examples"].append(example_match.group(1).strip())
            
        return jsdoc

    def generate_embeddings_documents(self, components: List[Dict[str, Any]]) -> List[Document]:
        """
        Generate natural language descriptions summarising each component.
        """
        documents: List[Document] = []
        for component in components:
            doc_content = f"React Component: {component['name']}\n\n"
            if component['description']:
                doc_content += f"{component['description']}\n\n"
            
            doc_content += "Props:\n"
            for prop in component['props']:
                doc_content += f"- {prop['name']}"
                if prop['optional']:
                    doc_content += " (optional)"
                doc_content += f": {prop['type']}\n"
            
            if component['design_tokens']:
                doc_content += "\nDesign tokens used:\n"
                for token in component['design_tokens']:
                    doc_content += f"- {token}\n"
                    
            if component['examples']:
                doc_content += "\nUsage examples:\n"
                for example in component['examples']:
                    doc_content += f"```tsx\n{example}\n```\n\n"
            
            documents.append(Document(
                id=f"component_{component['name']}",
                text=doc_content,
                metadata={ 
                    "type": "react_component",
                    "component": component['name'],
                    "component_info": json.dumps(component)
                }
            ))
        return documents
