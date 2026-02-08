# AI Code Orchestrator v3.0 --- Technical Documentation

**Version:** 3.0.0  
**Last updated:** 2026-02-08  
**Evolution:** From domain-specific to domain-agnostic architecture

---

## 1. Executive Summary

The **AI Code Orchestrator v3.0** represents a fundamental architectural shift from domain-specific tooling to a **universal, domain-agnostic framework** capable of working with any software domain—provided the necessary prerequisites are met.

### What's New in v3.0

1. **Domain Knowledge Layer** — Pluggable system for ingesting knowledge from databases, component libraries, design systems, and existing codebases
2. **Incremental Development Workflows** — Support for extending, refactoring, and migrating existing projects (not just greenfield)
3. **Multi-Collection RAG Strategy** — Intelligent context retrieval across heterogeneous knowledge sources
4. **Domain Configuration DSL** — YAML-based domain definitions

### Key Principles

- **Generic by Design:** No hardcoded domain assumptions
- **Configurable:** All domain knowledge via YAML
- **Extensible:** Plugin architecture for parsers
- **Incremental-Friendly:** Greenfield + existing projects

---

## 2. Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                   API Gateway (FastAPI)                        │
└─────────────────────┬──────────────────────────────────────────┘
                      │
              ┌───────▼───────┐
              │ Orchestrator  │
              └───────┬───────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
    ┌────▼────┐  ┌───▼────┐  ┌───▼──────────────┐
    │  Cost   │  │  RAG   │  │ Domain Knowledge │ ◀── NEW
    │ Manager │  │ System │  │     Ingestion    │
    └─────────┘  └────────┘  └──────────────────┘
```

---

## 3. Domain Configuration

### 3.1 Configuration Structure

```yaml
domain:
  name: "project-name"
  description: "Project description"
  
knowledge_sources:
  - type: "database"
    source_format: "sql_ddl"  # or ef_core, prisma, django
    path: "./data/schema.sql"
    bounded_contexts:
      context1: ["Table1", "Table2"]
      context2: ["Table3", "Table4"]
  
  - type: "existing_codebase"
    source_format: "dotnet_solution"  # or nodejs, react, python
    path: "https://github.com/user/repo"
    analysis_depth: "deep"  # shallow, medium, deep
    focus_areas:
      - "api_endpoints"
      - "data_models"
      - "business_logic"
  
  - type: "component_library"
    source_format: "react_tsx"
    path: "https://github.com/user/components"
    component_groups:
      basic: ["Button", "Input", "Select"]
      layout: ["Grid", "Flex", "Container"]

rag_strategy:
  vector_store: "chromadb"  # or faiss, weaviate
  embedding_model: "text-embedding-3-small"
  collection_per_source: true
  max_context_tokens: 12000
```

### 3.2 Example: Insurance System (WIWA)

```yaml
domain:
  name: "wiwa-insurance-system"
  description: "Property and risk insurance management platform"
  
knowledge_sources:
  # 150+ table database
  - type: "database"
    source_format: "sql_ddl"
    path: "./data/WIWA_DB_NEW_09_01_2026.sql"
    bounded_contexts:
      policies:
        - "Concerns"
        - "ConcernRisks"
        - "ConcernRiskCovers"
      properties:
        - "ConcernProperties"
        - "PropertyBuildings"
      questionnaires:
        - "QuestionnaireByQuestionnaireIdentificator"
        - "QuestionnaireAnswers"
      tariffs:
        - "Tariffs"
        - "TariffRisks"
        - "PremiumRateMatrix"
  
  # C# .NET Backend
  - type: "existing_codebase"
    source_format: "dotnet_solution"
    path: "https://github.com/mgasic/WIWA_Questionnaires"
    analysis_depth: "deep"
    focus_areas:
      - "api_endpoints"
      - "data_models"
      - "business_logic"
  
  # React/TypeScript Frontend
  - type: "existing_codebase"
    source_format: "react_typescript"
    path: "https://github.com/mgasic/WIWA_Questionnaires"
    subpath: "src/Frontend/wiwa-questionnaire-fe"
    analysis_depth: "medium"
    focus_areas:
      - "ui_components"
      - "api_clients"
  
  # Component Library
  - type: "component_library"
    source_format: "react_tsx"
    path: "https://github.com/mgasic/dyn-ui-main-v01"
    component_groups:
      basic: ["DynButton", "DynInput", "DynSelect"]
      layout: ["DynGrid", "DynFlex", "DynContainer"]
      data: ["DynTable", "DynListView", "DynChart"]

rag_strategy:
  vector_store: "chromadb"
  embedding_model: "text-embedding-3-small"
  collection_per_source: true
  max_context_tokens: 12000
```

---

## 4. Domain Knowledge Ingestion

### 4.1 Database Schema Ingestion

**Input:** SQL DDL script

**Process:**
1. Parse CREATE TABLE statements
2. Extract columns, types, constraints
3. Identify relationships (FOREIGN KEY)
4. Group by bounded context
5. Generate structured documents

**Output:**
```json
{
  "id": "table_concerns",
  "type": "database_table",
  "content": "Table: Concerns\nPK: ConcernID (int)\nColumns: InsuredSum (decimal), CurrencyID (smallint FK)...",
  "metadata": {
    "table_name": "Concerns",
    "bounded_context": "policies",
    "relationships": ["ConcernRisks", "ConcernMarks"]
  }
}
```

### 4.2 Codebase Ingestion (.NET)

**Input:** GitHub repo with .NET solution

**Process:**
1. Clone repository
2. Parse .sln → Find .csproj files
3. Parse .cs files using AST
4. Extract API endpoints ([ApiController], [HttpGet])
5. Extract data models (EF Core entities)
6. Generate structured documents

**Output:**
```json
{
  "id": "endpoint_questionnaires_get",
  "type": "api_endpoint",
  "content": "GET /api/questionnaires/{id}\nController: QuestionnairesController\nService: IQuestionnaireService",
  "metadata": {
    "file": "Controllers/QuestionnairesController.cs",
    "endpoint_route": "GET /api/questionnaires/{id}",
    "return_type": "ActionResult<QuestionnaireDto>"
  }
}
```

### 4.3 Component Library Ingestion (React)

**Input:** GitHub repo with React components

**Process:**
1. Clone monorepo
2. Parse package.json → Workspace structure
3. Parse .tsx files using TypeScript AST
4. Extract component name, props, exports
5. Generate component catalog

**Output:**
```json
{
  "id": "component_dyn_table",
  "type": "ui_component",
  "content": "Component: DynTable\nProps: columns (ColumnDef[]), data (T[]), pagination (boolean)",
  "metadata": {
    "component_name": "DynTable",
    "category": "data",
    "props": ["columns", "data", "pagination"]
  }
}
```

---

## 5. Multi-Collection RAG Strategy

### 5.1 Collection Structure

```
Vector Store (ChromaDB)
├── collection: "database_schema"
│   ├── document: table_concerns
│   └── document: table_concern_risks
├── collection: "existing_backend"
│   ├── document: endpoint_questionnaires_get
│   └── document: service_questionnaire_getbyid
├── collection: "existing_frontend"
│   ├── document: component_questionnaire_form
│   └── document: hook_use_questionnaires
└── collection: "component_library"
    ├── document: component_dyn_table
    └── document: component_dyn_button
```

### 5.2 Retrieval Strategy

```python
class DomainAwareRetriever:
    def retrieve(self, query: str, context_type: str):
        if context_type == "greenfield":
            # New feature → DB schema + components
            return {
                "database": self.query("database_schema", query, n=5),
                "components": self.query("component_library", query, n=3)
            }
        
        elif context_type == "incremental":
            # Extend existing → Existing code + DB + components
            return {
                "backend": self.query("existing_backend", query, n=3),
                "frontend": self.query("existing_frontend", query, n=3),
                "database": self.query("database_schema", query, n=5),
                "components": self.query("component_library", query, n=2)
            }
```

### 5.3 Context Formatting (JSON)

**Token Optimization:** JSON format reduces tokens by 55-70% vs. prose.

```json
{
  "context_type": "incremental",
  "query": "Add export to Excel",
  "existing_backend": [
    {"route": "GET /api/questionnaires", "file": "QuestionnairesController.cs"}
  ],
  "existing_frontend": [
    {"name": "QuestionnaireList", "uses": "DynTable"}
  ],
  "database_tables": [
    {"table": "Questionnaires", "columns": ["ID", "Title", "CreatedAt"]}
  ],
  "reusable_components": [
    {"name": "DynExportButton", "props": ["data", "filename", "format"]}
  ]
}
```

---

## 6. Incremental Development Workflows

### 6.1 Workflow Types

| Workflow | Mode | Use Case |
|----------|------|----------|
| **Greenfield** | `greenfield` | Build new feature from scratch |
| **Incremental** | `incremental` | Add feature to existing code |
| **Refactor** | `refactor` | Improve code quality |
| **Bug Fix** | `bug_fix` | Fix specific issue |
| **Migration** | `migration` | DB schema or framework upgrade |

### 6.2 Example: Add 2FA to Existing Login

**Request:** "Add two-factor authentication to login flow"

**Step 1: Analysis**
```python
analyst_output = {
  "affected_backend_files": [
    "Controllers/AuthController.cs",
    "Services/AuthService.cs"
  ],
  "db_changes": {
    "alter_table": "Users",
    "add_column": "TwoFactorEnabled bit, TwoFactorSecret nvarchar(255)"
  },
  "new_dependencies": ["OtpNet (NuGet)"]
}
```

**Step 2: Incremental Developer Agent**
```python
incremental_dev_output = {
  "file_changes": [
    {"file": "Controllers/AuthController.cs", "change_type": "modify"},
    {"file": "Services/AuthService.cs", "change_type": "modify"}
  ],
  "new_files": [
    {"file": "Services/TwoFactorService.cs"}
  ]
}
```

**Step 3: Frontend Implementer**
```python
frontend_output = {
  "file_changes": [
    {"file": "src/pages/Login.tsx", "change_type": "modify"},
    {"file": "src/components/TwoFactorModal.tsx", "change_type": "create"}
  ]
}
```

---

## 7. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] `domain_knowledge/` module structure
- [ ] `DomainConfig` YAML parser
- [ ] `DatabaseIngester` (SQL DDL)
- [ ] Unit tests

### Phase 2: Codebase Ingesters (Weeks 3-4)
- [ ] `DotNetCodebaseIngester`
- [ ] `ReactCodebaseIngester`
- [ ] Integration tests with WIWA repo

### Phase 3: Multi-Collection RAG (Weeks 5-6)
- [ ] `DomainAwareRetriever`
- [ ] Collection routing logic
- [ ] JSON context formatter

### Phase 4: Incremental Agents (Weeks 7-8)
- [ ] `IncrementalDeveloperAgent`
- [ ] `RefactoringAgent`
- [ ] `MigrationAgent`

### Phase 5: Examples & Docs (Weeks 9-10)
- [ ] WIWA example configuration
- [ ] Accounting-online example
- [ ] Generic template
- [ ] Video demo

---

## 8. Usage Examples

### 8.1 Setup Domain

```bash
# Copy template
cp examples/generic-template/domain_config.yaml my-project/

# Edit configuration
vim my-project/domain_config.yaml

# Ingest knowledge
python -m domain_knowledge.cli ingest --config my-project/domain_config.yaml
```

### 8.2 Greenfield Development

```bash
python -m core.orchestrator \
  --mode greenfield \
  --domain-config my-project/domain_config.yaml \
  --request "Create REST API for products" \
  --bounded-context products
```

### 8.3 Incremental Development

```bash
python -m core.orchestrator \
  --mode incremental \
  --domain-config my-project/domain_config.yaml \
  --request "Add export to Excel for product list"
```

### 8.4 Refactoring

```bash
python -m core.orchestrator \
  --mode refactor \
  --domain-config my-project/domain_config.yaml \
  --request "Refactor ProductService to use repository pattern" \
  --target-file Services/ProductService.cs
```

---

## 9. File Structure

```
ai-code-orchestrator/
├── domain_knowledge/       # NEW in v3.0
│   ├── domain_config.py
│   ├── base_ingester.py
│   ├── database_ingester.py
│   ├── codebase_ingester.py
│   └── adapters/
│       ├── sql_parser.py
│       ├── dotnet_parser.py
│       └── react_parser.py
├── rag/
│   ├── domain_aware_retriever.py  # NEW
│   └── context_formatter.py       # NEW
├── agents/
│   └── specialist_agents/
│       ├── incremental_developer.py  # NEW
│       ├── refactoring_agent.py      # NEW
│       └── migration_agent.py        # NEW
└── examples/                     # NEW
    ├── insurance-system/
    ├── accounting-system/
    └── generic-template/
```

---

## 10. Comparison: v3.0 vs. Alternatives

| Feature | v3.0 | GitHub Copilot | Cursor AI |
|---------|------|----------------|----------|
| **Domain-Agnostic** | ✅ YAML config | ❌ Generic | ❌ Generic |
| **Existing Codebase** | ✅ Parses & understands | ⚠️ Context only | ⚠️ Context |
| **Multi-File Changes** | ✅ Orchestrated | ❌ One file | ⚠️ Some |
| **Database Awareness** | ✅ Schema + migrations | ❌ No | ❌ No |
| **Component Library** | ✅ Reuses | ❌ No | ❌ No |
| **Cost Control** | ✅ Per-task budgets | ❌ Flat | ❌ Flat |
| **Incremental Mode** | ✅ Designed for it | ❌ Greenfield | ⚠️ Some |

---

## 11. Next Steps

1. **Review this document** and provide feedback
2. **Set up WIWA example** configuration
3. **Begin Phase 1 implementation**
4. **Create PR #1**: Documentation + skeleton

---

**Questions?** Contact: mgasic (GitHub: https://github.com/mgasic)

**Repository:** https://github.com/mgasic/ai-code-orchestrator

**License:** MIT
