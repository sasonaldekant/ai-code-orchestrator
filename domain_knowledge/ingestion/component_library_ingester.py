"""Enhanced Component library knowledge ingester for React TypeScript.

This ingester extracts comprehensive information from component folders including:
- Main component (.tsx)
- TypeScript types (.types.ts)
- CSS modules (.module.css)
- Storybook stories (.stories.tsx)
- Documentation (DOCS.md)
"""

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
    Enhanced parser for React component folders with comprehensive file extraction.
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
            logger.info(f"Extracted {len(components)} components")
            return self.generate_embeddings_documents(components)
        except Exception as e:
            logger.error(f"Failed to ingest component library: {e}")
            return []

    def extract_components(self) -> List[Dict[str, Any]]:
        """
        Scans all files recursively and groups them correctly by component name.
        """
        if not self.components_dir.exists():
            logger.warning(f"Components directory does not exist: {self.components_dir}")
            return []
        
        # Group all files by base component name
        # key: component_name, value: dict of file_type -> Path
        component_files: Dict[str, Dict[str, Path]] = {}
        
        # 1. First, find all primary .tsx files (excluding tests and stories)
        for tsx_file in self.components_dir.rglob("*.tsx"):
            filename = tsx_file.name
            if filename.startswith("index") or ".test." in filename or ".spec." in filename or ".stories." in filename:
                continue
            
            component_name = tsx_file.stem
            if component_name not in component_files:
                component_files[component_name] = {}
            component_files[component_name]['tsx'] = tsx_file

        # 2. Now, find all other related files and associate them with existing components
        # Or create new ones if they only have types/docs
        
        # Types
        for types_file in self.components_dir.rglob("*.types.ts"):
            name = types_file.name.split('.')[0]
            if name not in component_files: component_files[name] = {}
            component_files[name]['types'] = types_file
            
        # CSS Modules
        for css_file in self.components_dir.rglob("*.module.css"):
            name = css_file.name.split('.')[0]
            if name not in component_files: component_files[name] = {}
            component_files[name]['css'] = css_file
            
        # Stories
        for stories_file in self.components_dir.rglob("*.stories.tsx"):
            name = stories_file.name.split('.')[0]
            if name not in component_files: component_files[name] = {}
            component_files[name]['stories'] = stories_file
            
        # Docs (Support DOCS.md, README.md, and other .md files in the folder)
        for docs_file in self.components_dir.rglob("*.md"):
            # Skip if in node_modules
            if "node_modules" in str(docs_file): continue
            
            # Use parent folder name as component name
            name = docs_file.parent.name
            if name not in component_files: 
                component_files[name] = {}
            
            # Priority: DOCS.md > README.md > others
            existing_docs = component_files[name].get('docs')
            if not existing_docs or docs_file.name == "DOCS.md" or (docs_file.name == "README.md" and existing_docs.name != "DOCS.md"):
                component_files[name]['docs'] = docs_file

        logger.info(f"Grouped {len(component_files)} unique components")
        
        # Parse each component
        components: List[Dict[str, Any]] = []
        for component_name, files in component_files.items():
            # Skip if we only found a random .types file without a main component if it's too small
            if not files.get('tsx') and not files.get('docs'):
                continue
                
            component_info = self._parse_component_files(component_name, files)
            if component_info:
                components.append(component_info)
        
        return components

    def _parse_component_files(self, component_name: str, files: Dict[str, Path]) -> Optional[Dict[str, Any]]:
        """
        Parse all files associated with a component with strict priority.
        """
        # Determine the primary path for relative_to
        primary_path = files.get('tsx') or files.get('types') or files.get('docs') or next(iter(files.values()))
        
        component_data = {
            "name": component_name,
            "folder_path": str(primary_path.parent.resolve()),
            "description": "",
            "props": [],
            "types": "",
            "css_classes": [],
            "design_tokens": [],
            "stories": [],
            "examples": [],
            "docs": ""
        }
        
        # Parse each file type if it exists
        if 'tsx' in files:
            self._parse_tsx_file(files['tsx'], component_data)
        
        if 'types' in files:
            self._parse_types_file(files['types'], component_data)
        
        if 'css' in files:
            self._parse_css_file(files['css'], component_data)
        
        if 'stories' in files:
            self._parse_stories_file(files['stories'], component_data)
        
        if 'docs' in files:
            self._parse_docs_file(files['docs'], component_data)
        
        # Only return if we found at least one file
        if files:
            return component_data
        
        return None

    def _parse_tsx_file(self, file_path: Path, component_data: Dict[str, Any]):
        """Extract information from main component .tsx file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # Extract JSDoc description
            jsdoc = self._extract_jsdoc(content)
            if jsdoc.get("description"):
                component_data["description"] = jsdoc["description"]
            if jsdoc.get("examples"):
                component_data["examples"].extend(jsdoc["examples"])
            
            # Extract props interface
            props = self._extract_props_interface(content, component_data["name"])
            if props:
                component_data["props"] = props
            
            # Extract design tokens
            tokens = self._extract_design_tokens(content)
            if tokens:
                component_data["design_tokens"].extend(tokens)
                
        except Exception as e:
            logger.warning(f"Error parsing TSX file {file_path}: {e}")

    def _parse_types_file(self, file_path: Path, component_data: Dict[str, Any]):
        """Extract TypeScript type definitions."""
        try:
            content = file_path.read_text(encoding="utf-8")
            component_data["types"] = content
            
            # Also extract props from types file if not found in main file
            if not component_data["props"]:
                props = self._extract_props_interface(content, component_data["name"])
                if props:
                    component_data["props"] = props
                    
        except Exception as e:
            logger.warning(f"Error parsing types file {file_path}: {e}")

    def _parse_css_file(self, file_path: Path, component_data: Dict[str, Any]):
        """Extract CSS classes and design tokens from CSS module."""
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # Extract class names
            class_pattern = r'\.(\w+)\s*\{'
            classes = re.findall(class_pattern, content)
            component_data["css_classes"] = list(set(classes))
            
            # Extract CSS variables (design tokens)
            var_pattern = r'var\((--[\w-]+)\)'
            css_vars = re.findall(var_pattern, content)
            component_data["design_tokens"].extend(css_vars)
            
        except Exception as e:
            logger.warning(f"Error parsing CSS file {file_path}: {e}")

    def _parse_stories_file(self, file_path: Path, component_data: Dict[str, Any]):
        """Extract Storybook stories as usage examples."""
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # Extract story exports
            story_pattern = r'export\s+const\s+(\w+)\s*[=:]'
            stories = re.findall(story_pattern, content)
            component_data["stories"] = stories
            
            # Extract story code as examples
            # Look for story definitions with args/render
            example_pattern = r'export\s+const\s+\w+\s*=\s*\{([^}]+)\}'
            examples = re.findall(example_pattern, content, re.DOTALL)
            for example in examples[:3]:  # Limit to first 3 examples
                component_data["examples"].append(example.strip())
                
        except Exception as e:
            logger.warning(f"Error parsing stories file {file_path}: {e}")

    def _parse_docs_file(self, file_path: Path, component_data: Dict[str, Any]):
        """Extract documentation from DOCS.md."""
        try:
            content = file_path.read_text(encoding="utf-8")
            component_data["docs"] = content
            
            # If no description yet, try to extract from docs
            if not component_data["description"]:
                # Get first paragraph as description
                lines = content.split('\n')
                desc_lines = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        desc_lines.append(line)
                        if len(desc_lines) >= 3:  # First 3 lines
                            break
                if desc_lines:
                    component_data["description"] = " ".join(desc_lines)
                    
        except Exception as e:
            logger.warning(f"Error parsing docs file {file_path}: {e}")

    def _extract_props_interface(self, content: str, component_name: str) -> List[Dict[str, Any]]:
        """Extract TypeScript interface for component props."""
        props: List[Dict[str, Any]] = []
        
        # Try multiple patterns
        patterns = [
            rf'interface\s+{component_name}Props\s*\{{([^}}]+)\}}',
            rf'type\s+{component_name}Props\s*=\s*\{{([^}}]+)\}}',
            rf'export\s+interface\s+{component_name}Props\s*\{{([^}}]+)\}}',
        ]
        
        interface_body = None
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                interface_body = match.group(1)
                break
        
        if not interface_body:
            return props
        
        # Extract props with comments
        prop_pattern = r'(?://\s*(.+?)\n)?\s*(\w+)(\?)?:\s*([^;]+);'
        for match in re.finditer(prop_pattern, interface_body):
            comment, prop_name, optional, prop_type = match.groups()
            props.append({
                "name": prop_name,
                "type": prop_type.strip(),
                "optional": optional == "?",
                "description": comment.strip() if comment else "",
            })
        
        return props

    def _extract_design_tokens(self, content: str) -> List[str]:
        """
        Extract design tokens from various patterns.
        """
        tokens = []
        
        # CSS variables
        var_pattern = r'var\((--[\w-]+)\)'
        tokens.extend(re.findall(var_pattern, content))
        
        # Theme object access
        theme_pattern = r'(?:theme|design|tokens)\.(\w+(?:\.\w+)*)'
        tokens.extend(re.findall(theme_pattern, content))
        
        return list(set(tokens))

    def _extract_jsdoc(self, content: str) -> Dict[str, Any]:
        """Extract JSDoc comments."""
        jsdoc = {"description": "", "examples": []}
        
        # Find JSDoc blocks
        jsdoc_pattern = r'/\*\*([^*]|\*(?!/))*\*/'
        match = re.search(jsdoc_pattern, content, re.DOTALL)
        if not match:
            return jsdoc
        
        jsdoc_content = match.group(0)
        
        # Extract description
        lines = []
        for line in jsdoc_content.split('\n'):
            line = line.strip().replace('/**', '').replace('*/', '').strip('* ')
            if line.startswith('@'):
                break
            if line:
                lines.append(line)
        jsdoc["description"] = " ".join(lines)
        
        # Extract @example tags
        example_pattern = r'@example\s+(.+?)(?=@|$)'
        for example_match in re.finditer(example_pattern, jsdoc_content, re.DOTALL):
            jsdoc["examples"].append(example_match.group(1).strip())
        
        return jsdoc

    def generate_embeddings_documents(self, components: List[Dict[str, Any]]) -> List[Document]:
        """
        Generate comprehensive natural language descriptions for each component.
        """
        documents: List[Document] = []
        
        for component in components:
            # Build comprehensive document
            doc_parts = []
            
            # Header
            doc_parts.append(f"# React Component: {component['name']}\n")
            
            # Description
            if component.get('description'):
                doc_parts.append(f"\n## Description\n{component['description']}\n")
            
            # Documentation
            if component.get('docs'):
                doc_parts.append(f"\n## Documentation\n{component['docs']}\n")
            
            # Props
            if component.get('props'):
                doc_parts.append("\n## Props\n")
                for prop in component['props']:
                    optional_str = " (optional)" if prop['optional'] else ""
                    desc_str = f" - {prop['description']}" if prop['description'] else ""
                    doc_parts.append(f"- **{prop['name']}**{optional_str}: `{prop['type']}`{desc_str}\n")
            
            # TypeScript Types
            if component.get('types'):
                doc_parts.append(f"\n## TypeScript Definitions\n```typescript\n{component['types']}\n```\n")
            
            # CSS Classes
            if component.get('css_classes'):
                doc_parts.append("\n## CSS Classes\n")
                for css_class in component['css_classes']:
                    doc_parts.append(f"- `.{css_class}`\n")
            
            # Design Tokens
            if component.get('design_tokens'):
                doc_parts.append("\n## Design Tokens Used\n")
                for token in set(component['design_tokens']):
                    doc_parts.append(f"- `{token}`\n")
            
            # Storybook Stories
            if component.get('stories'):
                doc_parts.append("\n## Available Stories\n")
                for story in component['stories']:
                    doc_parts.append(f"- {story}\n")
            
            # Examples
            if component.get('examples'):
                doc_parts.append("\n## Usage Examples\n")
                for i, example in enumerate(component['examples'], 1):
                    doc_parts.append(f"\n### Example {i}\n```tsx\n{example}\n```\n")
            
            doc_content = "".join(doc_parts)
            
            documents.append(Document(
                id=f"component_{component['name']}",
                text=doc_content,
                metadata={
                    "type": "react_component",
                    "component": component['name'],
                    "has_types": bool(component.get('types')),
                    "has_css": bool(component.get('css_classes')),
                    "has_stories": bool(component.get('stories')),
                    "has_docs": bool(component.get('docs')),
                    "props_count": len(component.get('props', [])),
                    "component_info": json.dumps(component)
                }
            ))
        
        logger.info(f"Generated {len(documents)} component documents")
        return documents
