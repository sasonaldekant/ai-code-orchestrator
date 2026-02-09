# Architecture Strategy & Conceptual Model — Domain‑Specific AI Code Orchestrator

This document defines the strategic baseline for the domain‑specific version of the AI Code Orchestrator.  It answers **why** the system exists, outlines what it is and is not, and establishes the conceptual model, principles, layers, governance and lifecycle needed to guide functional and technical specifications.

## 1. Purpose & System Boundaries

### 1.1 Purpose

The domain‑specific orchestrator accelerates feature delivery for a particular product by combining **pre‑indexed domain knowledge**, **retrieval‑augmented generation (RAG)** and a **phase‑based orchestration pipeline**.  It aims to reduce cost and time while improving accuracy and adherence to existing schemas, components and patterns.

### 1.2 What the system is

- An **orchestration engine** that coordinates analysis, architecture, implementation, testing and review phases.
- A **decision‑support tool** that generates structured outputs (plans, tasks, code, tests) for human review.
- A **knowledge‑guided generator** that constrains outputs to existing domain assets (database schema, UI component library, design tokens, query patterns).

### 1.3 What the system is not

- Not a **CI/CD or deployment** system.  It can integrate with CI/CD but does not deploy code.
- Not a **production runtime** or execution environment for services.
- Not a **source‑of‑truth** for the final codebase: human developers remain responsible for merging and maintaining the code.
- Not an **autonomous deployer**; human approval is required before any generated artefact is used in production.

## 2. Architectural Goals

1. **Domain alignment:** ensure that generated artefacts reuse and respect existing domain assets.
2. **Token efficiency:** minimise prompt size via pre‑indexed knowledge and compact JSON context structures.
3. **Local‑first:** allow CPU‑friendly RAG for local development; avoid GPU dependencies by using efficient embedding models and vector stores.
4. **Deterministic contracts:** validate all phase outputs against formal JSON Schemas.
5. **Quality gates:** integrate producer–reviewer loops and compliance scoring to catch errors early.
6. **Traceability & audit:** record the relationship between requirements, tasks, code, tests and compliance checks.

## 3. Core Principles

- **Domain knowledge as a first‑class citizen:** the knowledge base is versioned and audited alongside the orchestrator.  Database schemas, UI component libraries, query patterns and design tokens are ingested and indexed up front.
- **Structured over prose:** agents exchange structured JSON objects rather than unstructured text.  Prompt templates embed structured domain context.
- **Pre‑computation beats prompt bloat:** indexing and caching domain knowledge reduces context size.  Only the minimal, relevant context is retrieved per task.
- **Separation of concerns:** ingestion, retrieval, orchestration and governance form distinct layers that can evolve independently.
- **Fail‑closed on contract violations:** if an agent’s output fails schema validation or exceeds a budget, the pipeline halts (unless explicitly allowed to degrade).  Safety over convenience.

## 4. Conceptual Model

```
┌──────────────────────────────┐
│   Domain Knowledge Sources   │
│  - DB schema (EF/DDL)        │
│  - UI components (TSX)       │
│  - Design tokens             │
│  - Query/code patterns       │
└───────────────┬──────────────┘
                │ ingest
                ▼
┌──────────────────────────────┐
│   Knowledge Base (Documents) │
│  VectorDocument{id,type,...} │
└───────────────┬──────────────┘
                │ embed/index
                ▼
┌──────────────────────────────┐
│   Vector Store (Collections) │
│  - db_schema                 │
│  - component_library         │
│  - patterns                  │
└───────────────┬──────────────┘
                │ retrieve
                ▼
┌──────────────────────────────┐
│  Domain‑Aware Retriever       │
│  DomainContext (structured)   │
└───────────────┬──────────────┘
                │ context
                ▼
┌──────────────────────────────┐
│   Orchestrator (Phases)       │
│  Analyst→Architect→Impl→Test  │
│   + Reviewer/Consensus         │
└───────────────┬──────────────┘
                │ artefacts
                ▼
┌──────────────────────────────┐
│ Governance & Observability    │
│ - JSON schema validation      │
│ - Budget & cost control       │
│ - Trace & audit logs          │
│ - Compliance gates            │
└──────────────────────────────┘
```

### 4.1 Layer Descriptions

1. **Domain Knowledge Layer:** ingesters parse source artefacts (database schema, components, tokens, patterns) into `VectorDocument` records.  The knowledge base is versioned; re‑ingestion policies are defined per source (e.g. when the DbContext changes).
2. **Vector Store Layer:** stores embedding vectors for each document.  Multiple collections allow separate retrieval strategies for schema, components and patterns.  CPU‑friendly embedding models (e.g. MiniLM) ensure local execution.
3. **Retrieval Layer:** the `DomainAwareRetriever` retrieves top‑K entities, relationships, components, design tokens and patterns relevant to a user requirement and packages them into a `DomainContext` structure.  Contexts are cached and compressed for token efficiency.
4. **Orchestration Layer:** the orchestrator coordinates phases.  For each milestone or task, it retrieves context, calls phase agents (analyst, architect, implementer, tester) and uses consensus or producer–reviewer loops when required.  It also manages execution order based on dependencies and workflows.
5. **Agent Layer:** specialized language model agents perform reasoning, planning, code generation, testing and review.  Models may be selected by cost, reasoning capability or context length.
6. **Governance & Observability Layer:** ensures adherence to JSON schemas, budgets and quality thresholds.  This layer captures trace events (who did what when), cost reports and compliance results.  It enforces redaction rules for sensitive data and implements error handling and retry policies.

## 5. Decision Governance

### 5.1 Ownership & Roles

- **Schema & contract ownership:** the architecture/platform team owns the JSON schemas and OpenAPI/CLI contracts.
- **Domain knowledge ownership:** product engineering owns the content of the knowledge base (schemas, components, patterns) and approves updates.
- **Run approval:** humans remain in control.  A human reviewer must approve outputs before they are merged or deployed.  The orchestrator provides structured evidence (scores, violations) to aid decisions.

### 5.2 Consensus & Reviewer Use

- Use **multi‑model consensus** when architectural decisions affect multiple bounded contexts or when a high‑risk migration is underway.  Each model proposes a design; a synthesiser merges and selects the best.
- Use **producer–reviewer loops** for code generation and testing.  The reviewer (often a higher‑capability model) checks correctness, style, security and domain alignment.  Feedback prompts the producer to regenerate.  The loop halts when either the reviewer approves or a maximum number of iterations is reached.

### 5.3 Error & Retry Policy

- **Validation error:** if an output does not conform to its JSON schema, the orchestrator retries with modified prompts or escalates to a higher‑capability model.  After `n` retries, it aborts the task.
- **Model failure:** if a model returns an error (e.g. network), the orchestrator retries on another provider or uses cached results if available.
- **Budget exhaustion:** if the cost or token budget is exceeded, the orchestrator halts the pipeline and reports partial results.

## 6. Knowledge Lifecycle & Traceability

### 6.1 Ingestion & Versioning

Each source has a version identifier (e.g. database migration ID, commit hash of the component library).  When the source changes, the ingestion pipeline regenerates documents and updates the vector store.  Old versions are archived for reproducibility.

### 6.2 Invalidation & Re‑indexing Policy

- **Database schema changes:** re‑ingest and update the `db_schema` collection; remove obsolete entity documents.
- **Component library updates:** re‑ingest modified components; version design tokens; maintain backward compatibility through aliasing.
- **Pattern updates:** add new query patterns when discovered; deprecate unused patterns.

### 6.3 Traceability

The orchestrator records for each run:
- The knowledge version(s) used (schema version, component commit hash).
- The retrieved document IDs for each context.
- The prompt template version and model versions.
- The chain from requirement → plan → tasks → outputs (code/tests) → compliance results.  This mapping is exported as a **traceability matrix** for audit and debugging.

## 7. Quality & Compliance Model

### 7.1 Quality Dimensions

1. **Correctness:** the code or output meets functional requirements and passes tests.
2. **Domain alignment:** only approved entities, components and patterns are used; naming and conventions match the domain style guide.
3. **Maintainability:** the output follows best practices (SOLID, DRY), uses modular structure and avoids anti‑patterns.
4. **Security:** the output adheres to OWASP Top 10 guidelines; inputs are validated and sanitised; sensitive data is not leaked.
5. **Performance:** backend code avoids N+1 queries and excessive network calls; frontend code respects Core Web Vitals.
6. **Test coverage:** adequate unit and integration tests are generated; error paths are exercised.

### 7.2 Scoring & Gates

The reviewer assigns a score (0–1) for each dimension.  A weighted average yields an overall compliance score.  Configurable thresholds determine gating:
- **Schema validation gate:** if failed → stop and fix.
- **Compliance gate:** if overall score < threshold (e.g. 0.8) → iterate with producer/regeneration.
- **Budget gate:** if total cost or tokens exceed budget → halt and request human intervention.

## 8. Human‑in‑the‑Loop Controls

Human intervention is recommended at critical points:

1. **Post‑architecture:** review architecture proposals before implementation tasks are generated.
2. **Post‑task breakdown:** review tasks, dependencies and effort estimates.
3. **Post‑implementation:** review generated code and tests before merging.  Human reviewers can override model decisions or request changes.
4. **Exception handling:** when error thresholds are exceeded or unexpected behaviour occurs, humans decide whether to retry, downgrade or cancel.

## 9. Risk & Evolution Strategy

### 9.1 Model & Prompt Drift

Model behaviour changes over time; prompts may degrade.  Mitigation strategies:
- **Version prompts** and store them alongside code so they can be rolled back.
- **Monitor outputs**: periodically re‑run benchmark requirements and compare results.  If the compliance score drops, trigger prompt tuning or model updates.
- **Fallback models**: maintain a pool of supported models; route based on observed quality and cost.

### 9.2 Evolution to Domain‑Agnostic v3

The strategy presented here is domain‑specific but forms the foundation for a domain‑agnostic orchestrator.  The v3 roadmap introduces a YAML DSL for domain configuration, multi‑collection RAG and incremental workflows.  This strategy emphasises clean layering, versioned knowledge and governance to ease the transition.

## 10. References

- **Functional & Technical Specification** — defines functional requirements, workflows, schemas and contracts; refers back to this strategy for conceptual grounding.
- **Domain‑specific code examples** — companion file containing implementation samples for ingesters, retrievers and orchestrator logic.
- **Master strategy document** — the source document from which this strategy was synthesised, included under `notes/Domain_Strategy_Source.md`.
