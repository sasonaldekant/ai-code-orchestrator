# Functional & Technical Specification — Domain‑Specific AI Code Orchestrator (Extended)

## Overview

This document extends the original **Functional & Technical Specification** by providing additional details, examples and code references drawn from the domain‑specific strategy document, the enhanced technical documentation (v2.0.0), the v3.0 roadmap, and the Advanced RAG design.  It aims to fill the gaps left in the initial specification by illustrating how domain knowledge is ingested, indexed and retrieved; how the orchestrator coordinates multi‑model phases; and how incremental and domain‑agnostic workflows are supported in v3.0.  To avoid cluttering this specification with large code samples, implementation snippets are collected in a separate companion file (`domain_specific_code_examples.md`), which this document references where appropriate.

### Structure of this Extension

* **Section 1:** Domain knowledge ingestion — describes ingesters for EF Core schemas and React component libraries, and how they generate embedding documents for a vector store.
* **Section 2:** Domain‑aware retrieval — details the `DomainAwareRetriever` and context optimisation strategies, showing how structured domain context is constructed and formatted.
* **Section 3:** Prompt templates & lifecycle orchestration — explains the use of domain‑aware prompt templates and outlines the lifecycle orchestrator with examples of task breakdown and compliance checking.
* **Section 4:** YAML DSL & v3.0 features — introduces the domain configuration DSL, multi‑collection RAG and incremental workflows.
* **Section 5:** Advanced RAG system — summarises the smart chunking, hybrid search and context manager introduced in the **Advanced RAG** document.
* **Section 6:** Configuration & deployment — presents sample configuration files, CI/CD integration and performance guidelines.
* **Section 7:** ROI, benchmarks & next steps — synthesises metrics from the enhanced documentation and outlines next implementation steps.

Wherever code is referenced, the reader is directed to **`domain_specific_code_examples.md`** for the full implementation.

## 1. Domain Knowledge Ingestion

### 1.1 Database Schema Ingester

The **DatabaseSchemaIngester** parses EF Core DbContext and entity classes to extract entities, properties and relationships.  It uses regular expressions to find `DbSet<T>` declarations and navigation properties, and produces a structured schema dictionary.  A key function, `generate_embeddings_documents(schema)`, converts the structured schema into natural‑language descriptions (one per entity and relationship) suitable for embedding and vector indexing.  A sample implementation of this class is provided in the companion file (`domain_specific_code_examples.md`).

Usage:

1. Instantiate `DatabaseSchemaIngester` with the path to the DbContext file and the directory containing entity models.
2. Call `extract_schema()` to produce a nested dictionary of entities and relationships.
3. Call `generate_embeddings_documents()` to produce a list of documents (each with `id`, `type`, `content` and `metadata` fields).  These documents describe entity properties, max lengths, nullability and relationships.
4. Pass the documents to a vector store such as ChromaDB via its API (e.g. `vector_store.add_documents(documents)`).  See the example in the companion file.

### 1.2 Component Library Ingester

The **ComponentLibraryIngester** performs a similar role for React TypeScript components.  It iterates over `.tsx` files, extracts the component name, its props interface, design tokens and usage examples (via JSDoc), and packages these into documents for embedding.  The ingester’s methods `_extract_props_interface`, `_extract_design_tokens` and `_extract_jsdoc` use regular expressions to parse TypeScript interfaces and design token references (e.g. `theme.colors.primary`).

After collecting component metadata, the method `generate_embeddings_documents()` produces natural‑language descriptions summarising each component’s props, tokens and examples.  These documents are then indexed in a separate vector collection (e.g. `pos_component_library`).

Sample code is provided in the companion file.

### 1.3 Query Pattern & Design Token Catalogues

In addition to schema and components, the ingestion stage may add **query pattern** documents (common EF Core query structures) and **design token** definitions.  The schema ingester demonstrates adding a sample `pattern_user_orders` document describing a typical `Include`/`ThenInclude` query.  Similar pattern documents can be added manually or generated from code analysis.

### 1.4 Indexing & Setup Script

A shell script (`scripts/setup_domain_knowledge.sh`) orchestrates the indexing process.  It calls separate entry points to index the database schema and component library, verifies the resulting indices, and emits progress messages.  This script can be invoked locally or integrated into a CI/CD pipeline.  Example configuration values are shown in Section 6.

## 2. Domain‑Aware Retrieval & Context Optimisation

### 2.1 DomainAwareRetriever

The **DomainAwareRetriever** (see companion file) wraps multiple collections (database schema and component library) and uses a CPU‑friendly embedding model (e.g. `all‑MiniLM‑L6‑v2`).  It provides:

* **Multi‑collection retrieval:** It queries both the database and component collections using the user requirement as the query.  Each query returns the top‑`k` results filtered by document type (e.g. only `database_schema` documents when retrieving entities).  For each returned document, the retriever extracts metadata to build a structured context.
* **Relationship and pattern retrieval:** It queries the database collection for relationships involving the relevant entities and for predefined query patterns (e.g. “common patterns for User”).
* **Design token extraction:** It aggregates design tokens used in the retrieved components.
* **Caching:** Frequently requested contexts are cached to reduce retrieval latency and cost.

### 2.2 Context Formatting

Once raw results are retrieved, the retriever constructs a `DomainContext` object containing lists of entities, relationships, components, design tokens and query patterns.  To minimise token usage, the method `format_context_for_prompt()` serialises this object into a compact JSON string.  The representation uses shortened keys (`e` for entities, `r` for relationships, `c` for components, `t` for tokens) and lists only the most important properties (e.g. top 10 entity properties and top 5 relationships).  If the estimated token count exceeds `max_context_tokens`, the formatter trims the lists further.

A helper function `optimize_domain_context()` (see companion file) demonstrates more aggressive compression: encoding entities as `Name(Prop1,Prop2)` strings and relationships as `EntityA→EntityB` graph edges.  This can reduce context size by up to 70 % and is especially useful for long requirements.

### 2.3 Prompt Integration

Phase agents retrieve the domain context once per task and embed it into their prompts via templates.  For example, the **implementation** template (see `prompts/domain_prompts/implementation_with_context.txt` in the companion file) inserts the user requirement and the compact domain context and instructs the model to produce backend and frontend code, listing constraints such as “use only provided entities/components” and “no hard‑coded styles.”  By constraining the LLM with domain‑aware context, the system improves accuracy and reduces hallucinations.

## 3. Prompt Templates & Lifecycle Orchestration

### 3.1 Prompt Templates

Prompt templates live under `prompts/domain_prompts`.  The implementation template described above is just one example.  Other templates include:

* **Analysis template:** extracts features, requirements and constraints from user documentation.  It uses large‑context models (e.g. Gemini 2.5 Pro) and returns a JSON structure with fields such as `features`, `constraints` and `dependencies`.
* **Architecture template:** guides models to propose system architectures, considering best practices and security/performance guidelines.  When consensus mode is enabled, multiple models produce proposals and a synthesiser merges them.
* **Testing template:** instructs models to generate unit and integration tests for the code produced by the implementation phase.
* **Review template:** used in the producer–reviewer loop, instructing the reviewer model to check the output for errors, security flaws and style issues.

All templates embed structured domain context and specify the output format via JSON schemas to simplify validation.

### 3.2 Lifecycle Orchestrator

The **LifecycleOrchestrator** orchestrates complex workflows across multiple phases, including documentation analysis, best‑practice review, delivery planning, task breakdown, implementation, testing, bug fixing and compliance checking.  Its workflow is described in the domain strategy document and is summarised here:

1. **Analyze documentation:** Using high‑context models, extract features and technical constraints from documents.  Output is validated against a `requirements` schema.
2. **Review best practices:** Compare requirements with current best practices for .NET/React, security (OWASP Top 10), performance (Core Web Vitals) and accessibility (WCAG 2.1 AA).  Return compliance scores and improvement suggestions.
3. **Plan delivery:** Create a high‑level delivery plan with phases and milestones.  Milestones are defined as dataclasses with dependencies and estimated effort.
4. **Break down milestones into tasks:** For each milestone, retrieve domain context to assign relevant database entities and UI components to tasks (e.g. backend tasks get table names, frontend tasks get component names).  Each `Task` dataclass records the assigned workflow (implementation, testing, bug fixing) and dependencies.
5. **Execute tasks:** The orchestrator executes tasks by calling the appropriate phase agent.  Backend and frontend implementations can run concurrently via `asyncio.gather` when there are no dependencies.
6. **Compliance checking:** After implementation, the reviewer checks whether the output meets the requirements and standards and returns a compliance score and suggestions.

Code examples of the lifecycle orchestrator, task breakdown and workflow assignment are included in the companion file.

### 3.3 Producer–Reviewer Loop

To ensure high quality, the system employs a **producer–reviewer loop**: a producer agent generates code or design, and a reviewer agent (typically a higher‑capability model) analyses it.  If the reviewer identifies issues, feedback is provided and the producer regenerates the output.  This loop continues until the reviewer approves or a maximum number of iterations is reached.  The loop improves correctness and adherence to guidelines and is a key differentiator from earlier versions.

## 4. YAML DSL & v3.0 Architecture

### 4.1 Domain Configuration DSL

Version 3.0 introduces a YAML‑based **Domain Configuration DSL** that allows the orchestrator to operate on arbitrary domains.  A configuration file defines the project name and describes each knowledge source in a uniform way:

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
    source_format: "dotnet_solution"
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

Users supply this configuration via the CLI or API, and the v3 ingesters parse the specified sources using pluggable parsers.  The **DomainConfig** loader reads the YAML and generates ingestion tasks, while the **Multi‑Collection RAG** strategy orchestrates retrieval across collections.

### 4.2 Multi‑Collection RAG & Incremental Workflows

In v3.0, retrieval logic differentiates between **greenfield** (new features), **incremental** (adding features to existing code), **refactor**, **bug fix** and **migration** workflows.  Each workflow type determines which collections to query and how many results to return:

```python
def retrieve(self, query: str, context_type: str):
    if context_type == "greenfield":
        return {
            "database": self.query("database_schema", query, n=5),
            "components": self.query("component_library", query, n=3)
        }
    elif context_type == "incremental":
        return {
            "backend": self.query("existing_backend", query, n=3),
            "frontend": self.query("existing_frontend", query, n=3),
            "database": self.query("database_schema", query, n=5),
            "components": self.query("component_library", query, n=2)
        }
```

The incremental workflow uses existing code collections to provide references to current endpoints, services, frontend components or API clients so that changes are made in the correct files.  The refactor workflow focuses on code patterns and best practices, while the migration workflow emphasises schema migrations and framework upgrades.

## 5. Advanced RAG System

The **Advanced RAG** design extends the simple vector store by incorporating **smart chunking**, **hybrid semantic/keyword search** and a **context manager** that combines static schemas with dynamic retrieval.  Key innovations include:

* **Document chunker:** Splits documents according to strategy (code, markdown or plain text) preserving function boundaries, headings or sentences.  Configurable `chunk_size` and `chunk_overlap` parameters balance between context granularity and retrieval quality.
* **Enhanced retriever:** Provides semantic, keyword and hybrid search, metadata filtering and reciprocal rank fusion.  The hybrid approach mixes semantic similarity (70 % weight by default) and keyword overlap (30 %), improving results for general queries.
* **Context manager:** Builds enriched contexts by combining static configuration (schemas, rules) and retrieved documents.  It tracks which pieces of knowledge were used in a prompt and can add domain knowledge dynamically.
* **CLI indexer:** A script (`scripts/build_rag_index.py`) indexes files or directories, auto‑detects the chunking strategy and manages collections.  It supports `--reset` and `--stats` options and can ingest JSON records.

These features are optional upgrades for scenarios requiring rich contextual knowledge beyond the domain‑specific assets.  They are particularly useful when the project must search large codebases or documentation repositories.  See the **Advanced RAG** document for detailed usage patterns and performance benchmarks.

## 6. Configuration & Deployment

### 6.1 Domain Configuration (v2 Example)

The original specification describes basic configuration files stored under `config/`.  A typical domain configuration includes settings for the domain knowledge ingestion, RAG retrieval, vector store and embedding model:

```yaml
domain:
  name: "POS Insurance Sales"
  version: "1.0.0"
  database:
    collection_name: "pos_database_schema"
    dbcontext_path: "./MyProject.Data/ApplicationDbContext.cs"
    models_dir: "./MyProject.Data/Models"
    auto_update: true
  component_library:
    collection_name: "pos_component_library"
    components_dir: "./component-library/src/components"
    docs_dir: "./component-library/docs"
    auto_update: true
  retrieval:
    top_k_entities: 5
    top_k_components: 8
    cache_enabled: true
    cache_ttl_seconds: 3600
  optimization:
    max_context_tokens: 2000
    use_compact_format: true
    embedding_model: "all-MiniLM-L6-v2"
```

### 6.2 Vector Store Configuration

The vector store can be configured for development or production.  For small projects, ChromaDB with cosine distance and local persistence is sufficient.  For larger datasets, FAISS with an IVFFlat index and 100 clusters provides a good balance between speed and accuracy.  The configuration is typically stored in `config/vector_store_config.py` and loaded by the RAG subsystem.  See the companion file for sample code.

### 6.3 Setup & CI/CD

The `scripts/setup_domain_knowledge.sh` script automates the ingestion process.  In CI/CD, a workflow (e.g. `.github/workflows/update_domain_knowledge.yml`) triggers re‑indexing whenever the database or component library changes.  It installs dependencies, re‑indexes the knowledge, commits updated vector indices and pushes them to the repository.  This ensures that the RAG subsystem is always up to date and eliminates manual maintenance.

### 6.4 Performance & Tuning

* **Embedding models:** Use CPU‑friendly models like `all‑MiniLM‑L6‑v2` for local development.  `all‑mpnet‑base‑v2` offers higher accuracy at the cost of slower inference; use `instructor‑large` only for offline indexing due to its 2 × memory and compute requirements.
* **Chunk sizes:** For general documentation, 512‑token chunks with 10 % overlap achieve a good balance.  For code, 512–1024 tokens preserve function boundaries.  Use smaller chunks for precise code retrieval and larger chunks for high‑level documentation searches.
* **top_k:** Set `top_k` to 3–5 for focused prompts and 10–15 for broad research.  Adjust the `semantic_weight` in hybrid search to favour semantic similarity when queries are conceptual and keyword matching when looking up exact API names.

## 7. ROI, Benchmarks & Roadmap

### 7.1 Cost & Time Savings

The enhanced system (v2.0.0) reduces cost per task from \$0.80–\$1.20 in v0.1.0 to \$0.20–\$0.40 by optimising token usage and leveraging lower‑cost models【663633728689534†L118-L137】.  Execution time is reduced by 35–45 % through parallel processing, and quality scores improve by ~18 % thanks to the producer–reviewer loop and consensus mechanism.

### 7.2 Next Steps & Implementation Plan

The domain strategy document provides an eight‑week roadmap for implementing the domain‑specific extensions.  It begins with building the ingesters and vector store, then integrates the domain‑aware retriever into the orchestrator, adds the lifecycle orchestrator, and finally optimises and tests the system.  Meanwhile, the v3.0 roadmap outlines five phases: foundation (DomainConfig parser), codebase ingesters, multi‑collection RAG, incremental agents and examples.  See the strategy and v3.0 documents for detailed task lists and recommended timelines.

### 7.3 Future Research

* **Streaming & distributed ingestion:** For very large projects, ingestion could be distributed across multiple workers and incremental updates streamed into the vector store.
* **Learning domain patterns:** By analysing previous successful implementations, the system could learn common patterns and propose them proactively during planning.
* **Cross‑domain reasoning:** With multi‑domain projects, the orchestrator could reason about interactions between subsystems (e.g. a React frontend and a Django backend).

---

### Reference Companion

The companion file **`domain_specific_code_examples.md`** contains the full code listings for the DatabaseSchemaIngester, ComponentLibraryIngester, DomainAwareRetriever, context optimisation functions, prompt templates and lifecycle orchestrator described above.  Refer to that file for implementation details and copy‑paste examples when integrating these components into your project.

## 8. Schema Contracts

This specification defines functional and technical requirements but delegates the precise structure of phase outputs to separate JSON Schema files.  These schemas live under the `schemas/` directory and are versioned alongside the orchestrator.  They enable automatic validation of agent outputs and provide machine‑readable contracts for integration.

### 8.1 Phase Output Schemas

| Phase | Schema file |
|---|---|
| Analysis (requirements) | `schemas/requirements.schema.json` |
| Architecture | `schemas/architecture.schema.json` |
| Planning (delivery plan) | `schemas/delivery_plan.schema.json` |
| Task breakdown | `schemas/task_breakdown.schema.json` |
| Implementation | `schemas/implementation.schema.json` |
| Testing | `schemas/testing.schema.json` |
| Compliance check | `schemas/compliance_check.schema.json` |

### 8.2 Domain Context Schema

The `DomainContext` structure returned by the domain‑aware retriever is defined in `schemas/DomainContext.schema.json`.  It describes the compact representation of database entities, relationships, UI components, design tokens and query patterns used in prompts.

### 8.3 Task & Milestone Schemas

Tasks and milestones are defined formally in `schemas/task.schema.json` and `schemas/milestone.schema.json`.  These schemas mirror the dataclasses used in the lifecycle orchestrator.

### 8.4 Vector Document Schema

Documents ingested into the vector store conform to `schemas/VectorDocument.schema.json`.

### 8.5 Workflow Assignment & Bounded Context Schemas

Workflows and bounded contexts are defined in `schemas/WorkflowAssignment.schema.json` and `schemas/BoundedContext.schema.json`.  These help validate YAML configurations for v3.

### 8.6 Observability Schemas

Trace and cost reporting events conform to `schemas/TraceEvent.schema.json` and `schemas/CostReport.schema.json`.

### 8.7 API & CLI Contracts

The REST API is formally described in `api/openapi.yaml`.  CLI command definitions are provided in `api/cli_commands.md`.

