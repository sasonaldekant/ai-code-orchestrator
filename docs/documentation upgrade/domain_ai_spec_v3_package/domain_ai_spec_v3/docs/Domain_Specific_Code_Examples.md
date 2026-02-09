# Domain‑Specific Code Examples

This companion file collects the implementation snippets referenced in the extended functional specification.  The code is extracted from the internal domain strategy document and illustrates how domain knowledge ingestion, retrieval and lifecycle orchestration are implemented in Python.  You can copy these functions into your project as starting points.

## 1. Database Schema Ingester

The `DatabaseSchemaIngester` parses EF Core DbContext and entity classes to extract entities, properties and relationships.  It then produces natural‑language descriptions for embedding in a vector store.

```python
"""
Extract i indeksiranje EF Core modela.
"""
from pathlib import Path
from typing import List, Dict, Any
import re
import json


class DatabaseSchemaIngester:
    """
    Parsira C# DbContext i Entity klase i pravi strukturirane dokumentacije.
    """

    def __init__(self, dbcontext_path: str, models_dir: str):
        self.dbcontext_path = Path(dbcontext_path)
        self.models_dir = Path(models_dir)

    def extract_schema(self) -> Dict[str, Any]:
        """
        Parsira C# fajlove i izvlači:
        - Entity names
        - Properties (name, type, nullable, max length)
        - Relationships (one‑to‑many, many‑to‑many)
        - Indexes
        - Constraints
        """
        schema: Dict[str, Any] = {
            "entities": {},
            "relationships": [],
            "database_name": self._extract_db_name(),
        }

        # Parse DbContext za DbSet definitions
        dbsets = self._parse_dbcontext()

        # Parse svaki Entity model
        for entity_name in dbsets:
            entity_info = self._parse_entity_model(entity_name)
            schema["entities"][entity_name] = entity_info

        # Extract relationships iz navigation properties
        schema["relationships"] = self._extract_relationships(schema["entities"])
        return schema

    def _parse_dbcontext(self) -> List[str]:
        """Extract `DbSet<T>` declarations."""
        content = self.dbcontext_path.read_text()
        pattern = r'DbSet<(\w+)>\s+(\w+)'
        matches = re.findall(pattern, content)
        return [match[0] for match in matches]

    def _parse_entity_model(self, entity_name: str) -> Dict[str, Any]:
        """Parses an individual entity model file."""
        entity_path = self.models_dir / f"{entity_name}.cs"
        if not entity_path.exists():
            return {}
        content = entity_path.read_text()
        return {
            "name": entity_name,
            "properties": self._extract_properties(content),
            "navigation_properties": self._extract_navigation_properties(content),
            "attributes": self._extract_attributes(content),
        }

    def _extract_properties(self, content: str) -> List[Dict[str, Any]]:
        """Extract property definitions from a C# class."""
        properties = []
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
        # ICollection<T> ili List<T> → one‑to‑many
        collection_pattern = r'(?:ICollection|List)<(\w+)>\s+(\w+)'
        for match in re.findall(collection_pattern, content):
            nav_props.append({
                "type": "one‑to‑many",
                "related_entity": match[0],
                "property_name": match[1],
            })
        # Single reference pattern for many‑to‑one could be added here
        return nav_props

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

    def generate_embeddings_documents(self, schema: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate natural language descriptions for embedding.  Each entity and
        relationship is turned into a document with `id`, `type`, `content` and
        JSON‑encoded `metadata`.
        """
        documents: List[Dict[str, str]] = []
        # 1. Per‑entity descriptions
        for entity_name, entity_info in schema["entities"].items():
            doc = f"Entity: {entity_name}\n\n"
            doc += "Properties:\n"
            for prop in entity_info["properties"]:
                doc += f"- {prop['name']}: {prop['type']}"
                if prop['max_length']:
                    doc += f" (max length: {prop['max_length']})"
                if prop['nullable']:
                    doc += " (nullable)"
                doc += "\n"
            if entity_info.get("navigation_properties"):
                doc += "\nRelationships:\n"
                for nav_prop in entity_info["navigation_properties"]:
                    doc += f"- {nav_prop['property_name']}: {nav_prop['type']} to {nav_prop['related_entity']}\n"
            documents.append({
                "id": f"entity_{entity_name}",
                "type": "database_schema",
                "entity": entity_name,
                "content": doc,
                "metadata": json.dumps(entity_info),
            })
        # 2. Relationship patterns (not shown here) can be added similarly
        return documents
```

## 2. Component Library Ingester

The `ComponentLibraryIngester` scans `.tsx` files, extracts component metadata and generates embedding documents.

```python
"""
Extract i indeksiranje React TypeScript komponenti.
"""
from pathlib import Path
from typing import List, Dict, Any
import re
import json


class ComponentLibraryIngester:
    """
    Parsira React TS komponente i njihovu dokumentaciju.
    """

    def __init__(self, components_dir: str, docs_dir: str = None):
        self.components_dir = Path(components_dir)
        self.docs_dir = Path(docs_dir) if docs_dir else None

    def extract_components(self) -> List[Dict[str, Any]]:
        """
        Parsira sve `.tsx` fajlove i izvlači:
        - component name
        - props interface
        - design tokens used
        - JSDoc description and examples
        """
        components: List[Dict[str, Any]] = []
        for tsx_file in self.components_dir.rglob("*.tsx"):
            if tsx_file.name.startswith("index"):
                continue
            component_info = self._parse_component_file(tsx_file)
            if component_info:
                components.append(component_info)
        return components

    def _parse_component_file(self, file_path: Path) -> Dict[str, Any]:
        content = file_path.read_text()
        component_name = file_path.stem
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
        prop_pattern = r'(\w+)(\?)?:\s*([^;]+);'
        for match in re.finditer(prop_pattern, interface_body):
            prop_name, optional, prop_type = match.groups()
            props.append({
                "name": prop_name,
                "type": prop_type.strip(),
                "optional": optional == "?",
                "description": "",
            })
        return props

    def _extract_design_tokens(self, content: str) -> List[str]:
        """
        Extract design tokens such as `theme.colors.primary` or `spacing.md`.
        """
        tokens = []
        pattern = r'(?:theme|design)\.(\w+\.\w+\.?\w*)'
        matches = re.findall(pattern, content)
        return list(set(matches))

    def _extract_jsdoc(self, content: str) -> Dict[str, Any]:
        jsdoc = {"description": "", "examples": []}
        jsdoc_pattern = r'/\*\*([^*]|\*(?!/))*\*/'
        match = re.search(jsdoc_pattern, content, re.DOTALL)
        if not match:
            return jsdoc
        jsdoc_content = match.group(0)
        desc_pattern = r'@description\s+(.+?)(?=@|$)'
        desc_match = re.search(desc_pattern, jsdoc_content, re.DOTALL)
        if desc_match:
            jsdoc["description"] = desc_match.group(1).strip()
        example_pattern = r'@example\s+(.+?)(?=@|$)'
        for example_match in re.finditer(example_pattern, jsdoc_content, re.DOTALL):
            jsdoc["examples"].append(example_match.group(1).strip())
        return jsdoc

    def generate_embeddings_documents(self, components: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Generate natural language descriptions summarising each component and
        preparing them for embedding.
        """
        documents: List[Dict[str, str]] = []
        for component in components:
            doc = f"React Component: {component['name']}\n\n"
            if component['description']:
                doc += f"{component['description']}\n\n"
            doc += "Props:\n"
            for prop in component['props']:
                doc += f"- {prop['name']}"
                if prop['optional']:
                    doc += " (optional)"
                doc += f": {prop['type']}\n"
            if component['design_tokens']:
                doc += "\nDesign tokens used:\n"
                for token in component['design_tokens']:
                    doc += f"- {token}\n"
            if component['examples']:
                doc += "\nUsage examples:\n"
                for example in component['examples']:
                    doc += f"```tsx\n{example}\n```\n\n"
            documents.append({
                "id": f"component_{component['name']}",
                "type": "react_component",
                "component": component['name'],
                "content": doc,
                "metadata": json.dumps(component),
            })
        return documents
```

## 3. Domain‑Aware Retriever & Context Optimisation

The `DomainAwareRetriever` uses multiple vector collections and an embedding model to retrieve entities, components and relationships.  It constructs a `DomainContext` object and formats it into compact JSON.

```python
"""
Domain‑aware RAG retriever sa optimizacijom za lokalni CPU.
"""
from typing import List, Dict, Any
from dataclasses import dataclass
from rag.vector_store import ChromaVectorStore
from rag.embeddings_provider import EmbeddingsProvider


@dataclass
class DomainContext:
    database_entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    components: List[Dict[str, Any]]
    design_tokens: List[str]
    query_patterns: List[str]


class DomainAwareRetriever:
    """
    Retriever optimizovan za domain‑specific knowledge.
    Ključne optimizacije:
    1. Multi‑collection retrieval (baza + komponente)
    2. Structured output (JSON umesto prose)
    3. Cachiranje često korišćenih konteksta
    4. CPU‑friendly embeddings
    """

    def __init__(
        self,
        database_collection: str = "pos_database_schema",
        components_collection: str = "pos_component_library",
        embedding_model: str = "all‑MiniLM‑L6‑v2",
    ):
        self.db_store = ChromaVectorStore(collection_name=database_collection)
        self.components_store = ChromaVectorStore(collection_name=components_collection)
        self.embeddings = EmbeddingsProvider(provider="sentence_transformers", model_name=embedding_model)
        self._context_cache: Dict[str, DomainContext] = {}

    async def retrieve_domain_context(self, user_requirement: str, top_k_entities: int = 5, top_k_components: int = 8) -> DomainContext:
        cache_key = f"{user_requirement[:50]}_{top_k_entities}_{top_k_components}"
        if cache_key in self._context_cache:
            return self._context_cache[cache_key]
        # 1. Retrieve database entities
        db_results = await self.db_store.query(query=user_requirement, top_k=top_k_entities, filter={"type": "database_schema"})
        # 2. Retrieve React components
        component_results = await self.components_store.query(query=user_requirement, top_k=top_k_components, filter={"type": "react_component"})
        # 3. Extract relationships
        relevant_entities = [r["metadata"]["entity"] for r in db_results]
        relationships = await self._get_relationships(relevant_entities)
        # 4. Extract design tokens
        design_tokens = self._extract_design_tokens(component_results)
        # 5. Get query patterns
        query_patterns = await self._get_query_patterns(relevant_entities)
        context = DomainContext(
            database_entities=[
                {
                    "name": r["metadata"]["entity"],
                    "properties": r["metadata"]["properties"],
                    "relationships": r["metadata"].get("navigation_properties", []),
                }
                for r in db_results
            ],
            relationships=relationships,
            components=[
                {
                    "name": r["metadata"]["component"],
                    "props": r["metadata"]["props"],
                    "examples": r["metadata"].get("examples", []),
                }
                for r in component_results
            ],
            design_tokens=design_tokens,
            query_patterns=query_patterns,
        )
        self._context_cache[cache_key] = context
        return context

    async def _get_relationships(self, entity_names: List[str]) -> List[Dict[str, Any]]:
        relationships: List[Dict[str, Any]] = []
        for entity in entity_names:
            results = await self.db_store.query(query=f"relationships involving {entity}", top_k=10, filter={"type": "database_relationship"})
            for r in results:
                rel = r["metadata"]
                if rel["from"] in entity_names or rel["to"] in entity_names:
                    relationships.append(rel)
        return relationships

    def _extract_design_tokens(self, component_results: List[Dict]) -> List[str]:
        tokens = set()
        for result in component_results:
            tokens.update(result["metadata"].get("design_tokens", []))
        return sorted(list(tokens))

    async def _get_query_patterns(self, entity_names: List[str]) -> List[str]:
        patterns: List[str] = []
        for entity in entity_names:
            results = await self.db_store.query(query=f"common patterns for {entity}", top_k=3, filter={"type": "query_pattern"})
            patterns.extend([r["content"] for r in results])
        return patterns

    def format_context_for_prompt(self, context: DomainContext) -> str:
        """
        Format the structured context into compact JSON for a prompt.  Keys are
        shortened to save tokens (e.g. `e` for entities, `c` for components).
        """
        context_json = {
            "db": {
                "e": [
                    {
                        "name": e["name"],
                        "props": [f"{p['name']}:{p['type']}" for p in e["properties"][:10]],
                        "rels": [f"{r['property_name']}→{r['related_entity']}" for r in e["relationships"][:5]],
                    }
                    for e in context.database_entities
                ],
                "r": [f"{r['from']}→{r['to']} ({r['type']})" for r in context.relationships[:10]],
            },
            "ui": {
                "c": [
                    {
                        "name": c["name"],
                        "props": [f"{p['name']}:{p['type']}" for p in c["props"][:8]],
                    }
                    for c in context.components
                ],
                "t": context.design_tokens[:15],
            },
        }
        import json
        return json.dumps(context_json, separators=(",", ":"))

```

### 3.1 Context Optimisation Helper

The following helper function further compresses a `DomainContext` into an ultra‑compact JSON representation.  It can be used to reduce token usage when prompts approach the context limit.

```python
def optimize_domain_context(domain_context: DomainContext, max_tokens: int = 2000) -> str:
    """
    Compress the domain context into a minimal representation.  Entities are
    encoded as `Name(Prop1,Prop2)`, relationships as `EntityA→EntityB`, and
    components as `Name(Prop1,Prop2)`.  If the resulting JSON exceeds
    `max_tokens`, lists are truncated.
    """
    entities_compact = [
        f"{e['name']}({','.join([p['name'] for p in e['properties'][:5]])})"
        for e in domain_context.database_entities
    ]
    rels_compact = [f"{r['from']}→{r['to']}" for r in domain_context.relationships]
    components_compact = [
        f"{c['name']}({','.join([p['name'] for p in c['props'][:5]])})"
        for c in domain_context.components
    ]
    context = {
        "db": {"e": entities_compact, "r": rels_compact},
        "ui": {"c": components_compact, "t": domain_context.design_tokens[:10]},
    }
    import json
    compact_json = json.dumps(context, separators=(",", ":"))
    # Rough token estimate: number of words × 1.3
    token_count = len(compact_json.split()) * 1.3
    if token_count > max_tokens:
        context["db"]["e"] = context["db"]["e"][:3]
        context["ui"]["c"] = context["ui"]["c"][:5]
        compact_json = json.dumps(context, separators=(",", ":"))
    return compact_json
```

## 4. Implementation Prompt Template

The following prompt template instructs the LLM to generate backend and frontend code using only the available database entities and UI components.  It also specifies the required output format.

```text
You are implementing a feature for a POS insurance sales application.

USER REQUIREMENT:
{user_requirement}

AVAILABLE DATABASE ENTITIES:
{domain_context.db}

AVAILABLE UI COMPONENTS:
{domain_context.ui}

IMPLEMENTATION CONSTRAINTS:
1. Use ONLY entities from the database schema provided above
2. Use ONLY components from the component library provided above
3. Follow EF Core best practices for data access
4. Follow React TypeScript best practices for UI
5. Use design tokens for all styling (no hard‑coded colors/spacing)
6. Implement proper error handling and validation

OUTPUT FORMAT:
Return a JSON object with this structure:
{
  "backend": {
    "controller": "C# code for API controller",
    "service": "C# code for business logic service",
    "queries": ["EF Core LINQ queries used"]
  },
  "frontend": {
    "component": "React TypeScript component code",
    "components_used": ["List of components from library"],
    "design_tokens_used": ["List of design tokens"]
  },
  "validation": {
    "backend_validation": "Validation rules in C#",
    "frontend_validation": "Validation rules in TypeScript"
  }
}

IMPORTANT: Keep implementation concise.  Use existing entities and components.  No placeholders.
```

## 5. Lifecycle Orchestrator (Key Methods)

The `LifecycleOrchestrator` coordinates long‑running workflows by delegating to the underlying v2 orchestrator and the domain retriever.  The following snippets highlight key methods; see the full class in the domain strategy document for complete implementation.

```python
from enum import Enum
from typing import List, Dict, Any
from dataclasses import dataclass
import asyncio


class LifecyclePhase(Enum):
    DOCUMENTATION_ANALYSIS = "doc_analysis"
    BEST_PRACTICES_REVIEW = "best_practices"
    DELIVERY_PLANNING = "planning"
    TASK_BREAKDOWN = "tasks"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    BUG_FIXING = "bug_fixing"
    COMPLIANCE_CHECK = "compliance"


@dataclass
class Milestone:
    id: str
    name: str
    description: str
    tasks: List['Task']
    dependencies: List[str]
    estimated_effort: int


@dataclass
class Task:
    id: str
    title: str
    description: str
    type: str
    assigned_workflow: str
    estimated_effort: int
    database_entities: List[str]
    ui_components: List[str]
    dependencies: List[str]


class LifecycleOrchestrator:
    def __init__(self, orchestrator_v2):
        self.orchestrator = orchestrator_v2
        self.domain_retriever = DomainAwareRetriever()

    async def break_down_to_tasks(self, milestone: Milestone) -> List[Task]:
        # Retrieve domain context for the milestone description
        domain_context = await self.domain_retriever.retrieve_domain_context(
            user_requirement=milestone.description,
            top_k_entities=10,
            top_k_components=15,
        )
        # Ask the analyst agent to break down the milestone
        result = await self.orchestrator.run_phase_with_retry(
            phase="analyst",
            schema_name="task_breakdown",
            context={
                "milestone": milestone,
                "domain_context": domain_context,
                "task": "Break down milestone into atomic tasks with DB entities and UI components",
            },
        )
        tasks = []
        for task_data in result.output["tasks"]:
            tasks.append(
                Task(
                    id=task_data["id"],
                    title=task_data["title"],
                    description=task_data["description"],
                    type=task_data["type"],
                    assigned_workflow=self._assign_workflow(task_data["type"]),
                    estimated_effort=task_data["estimated_effort"],
                    database_entities=task_data["database_entities"],
                    ui_components=task_data["ui_components"],
                    dependencies=task_data.get("dependencies", []),
                )
            )
        return tasks

    def _assign_workflow(self, task_type: str) -> str:
        workflow_mapping = {
            "backend": "implementation",
            "frontend": "implementation",
            "database": "implementation",
            "testing": "testing",
            "bug_fixing": "bug_fixing",
            "documentation": "documentation",
        }
        return workflow_mapping.get(task_type, "implementation")

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        # Prebuild minimal domain context from assigned entities/components
        db_entities = [await self._get_entity_details(e) for e in task.database_entities]
        ui_components = [await self._get_component_details(c) for c in task.ui_components]
        context = {"task": task, "db_entities": db_entities, "ui_components": ui_components}
        # Route to appropriate workflow
        if task.assigned_workflow == "implementation":
            return await self._execute_implementation(context)
        elif task.assigned_workflow == "testing":
            return await self._execute_testing(context)
        elif task.assigned_workflow == "bug_fixing":
            return await self._execute_bug_fixing(context)
        else:
            raise ValueError(f"Unknown workflow: {task.assigned_workflow}")
```

## 6. Main Workflow Example

The following asynchronous function demonstrates how to initialise the orchestrator, analyse documentation, create a delivery plan, break it down into tasks, execute them in parallel and check compliance.  Use this as a template for your own projects.

```python
import asyncio
from core.orchestrator_v2 import OrchestratorV2
from core.lifecycle_orchestrator import LifecycleOrchestrator, Milestone


async def main():
    # 1. Initialise orchestrator and lifecycle orchestrator
    orchestrator = OrchestratorV2(config_path="config/model_mapping_v2.yaml")
    lifecycle = LifecycleOrchestrator(orchestrator)
    # 2. Analyse documentation
    requirements = await lifecycle.analyze_documentation("./docs/POS_Requirements.md")
    # 3. Review best practices
    review = await lifecycle.review_best_practices(requirements)
    # 4. Create delivery plan
    plan = await lifecycle.create_delivery_plan(requirements, review)
    # 5. Break down to tasks
    all_tasks: List[Task] = []
    for milestone_data in plan["milestones"]:
        milestone = Milestone(**milestone_data)
        tasks = await lifecycle.break_down_to_tasks(milestone)
        all_tasks.extend(tasks)
    # 6. Execute tasks (parallel where possible)
    independent_tasks = [t for t in all_tasks if not t.dependencies]
    results = await asyncio.gather(*[
        lifecycle.execute_task(task)
        for task in independent_tasks[:5]  # Execute first 5 tasks as example
    ])
    # 7. Check compliance
    for result in results:
        compliance = await lifecycle.check_compliance(result, requirements)
        if compliance.get("score", 1.0) < 0.8:
            print("Compliance issues found:", compliance.get("violations"))
    # 8. Summarise cost and tokens
    print("Total cost:", orchestrator.cost_manager.total_cost)
    print("Total tokens:", orchestrator.cost_manager.total_tokens)


if __name__ == "__main__":
    asyncio.run(main())
```

---

These code snippets provide a foundation for implementing the domain‑specific features of the AI Code Orchestrator.  Adapt and extend them according to your domain and project requirements.