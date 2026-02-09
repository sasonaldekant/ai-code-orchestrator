# Architecture Strategy & Conceptual Model — Domain‑Specific AI Code Orchestrator

**Scope:** Domain‑specific extension of AI Code Orchestrator (v2 direction), with a clear path to v3 domain‑agnostic evolution.

## 1. Purpose

The system accelerates **feature delivery** for a specific product domain by combining:

- **Domain knowledge ingestion** (schema, components, patterns) → durable knowledge base
- **Retrieval‑augmented generation (RAG)** → relevant context per request
- **Phase‑based orchestration** (analyst → architect → implementer → tester → reviewer)
- **Governance controls** (validation, cost limits, tracing, compliance gates)

### 1.1 What the system is

- A **development orchestration framework** that produces *structured* outputs (plans, tasks, code, tests) for human review.
- A **knowledge‑guided generator**: it constrains outputs to existing domain assets.

### 1.2 What the system is not

- Not a CI/CD system (it can integrate with CI, but does not deploy).
- Not a production runtime.
- Not a single‑file “code assistant”; it is a **workflow engine**.

## 2. Architectural Goals

1. **Domain alignment**: generated outputs must reuse existing schema/components/patterns.
2. **Token efficiency**: keep prompts minimal via pre‑indexed knowledge and compact JSON context.
3. **Local‑first**: allow CPU‑friendly RAG for local development (Sentence Transformers + ChromaDB).
4. **Deterministic contracts**: phase outputs validated against JSON Schemas.
5. **Quality gates**: producer‑reviewer loop + compliance scoring.
6. **Traceability**: requirement → task → output artefacts → validation/compliance.

## 3. Key Principles

- **Domain Knowledge as First‑Class Citizen**: the knowledge base is a product artefact, versioned and auditable.
- **Structured over Prose**: agents exchange JSON objects; prose is allowed only inside bounded fields.
- **Pre‑computation beats prompt bloat**: ingest & index once; retrieve small slices per request.
- **Separation of concerns**: ingestion, retrieval, orchestration, governance are distinct layers.
- **Fail‑closed on contract violations**: schema validation failures block the pipeline (unless explicitly configured).

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
│ - Cost budgets                │
│ - Traces & reports            │
│ - Compliance gates            │
└──────────────────────────────┘
```

## 5. Logical Architecture Layers

1. **Domain Knowledge Layer**
   - Ingesters parse domain assets into `VectorDocument` records.
   - Owns **knowledge lifecycle**: versioning, invalidation, re‑index.

2. **Retrieval Layer (RAG)**
   - Multi‑collection retrieval (db + components + patterns).
   - Outputs a structured `DomainContext` (compact JSON for prompts).

3. **Orchestration Layer**
   - Executes phases (and optionally parallel sub‑phases).
   - Routes tasks to workflows (greenfield/incremental/refactor/migration).

4. **Agent Execution Layer**
   - Phase agents: Analyst, Architect, Implementer, Tester.
   - Specialist agents: domain‑specific (.NET EF, React TS) and governance (Reviewer).

5. **Governance Layer**
   - Schema validation, retry policy, budget enforcement, redaction rules.
   - Produces trace & cost artefacts.

## 6. Decision Governance

### 6.1 Ownership

- **Contracts** (schemas, output formats): owned by Architecture/Platform team.
- **Domain knowledge content** (schema/components/patterns): owned by product engineering.
- **Run approvals**: human‑in‑the‑loop for merge/deploy (outside orchestrator).

### 6.2 When to use consensus

Use multi‑model consensus when:
- architecture decisions impact multiple bounded contexts
- migration/refactor tasks can introduce systemic risk

Otherwise use a single best‑fit model selected via routing rules.

### 6.3 Producer–Reviewer loop

- Producer generates artefact → Reviewer checks against criteria.
- If violations exist: feedback → regenerate.
- Stop conditions: approved OR max iterations OR budget exhausted.

## 7. Knowledge Lifecycle

### 7.1 Versioning

- Knowledge base is versioned by:
  - source commit hash (code/components)
  - schema migration id / timestamp (database)
  - ingestion config version

### 7.2 Invalidation & Re‑index policy

- Re‑index triggered by:
  - schema migrations
  - changes under component library paths
  - prompt/schema contract changes that alter retrieval semantics

### 7.3 Reproducibility

Each run records:
- knowledge version(s) used
- retrieved document ids
- prompt template version
- model/provider versions (when available)

## 8. Quality Model

### 8.1 Dimensions

- Correctness (functional)
- Domain alignment (only allowed entities/components)
- Maintainability (patterns, conventions)
- Security (OWASP‑aligned checks)
- Performance (N+1, caching, frontend perf)
- Test coverage (unit/integration targets)

### 8.2 Gates

- **Schema validation gate**: hard fail.
- **Compliance score gate**: configurable threshold (e.g. ≥ 0.8).
- **Budget gate**: stop when cost/token caps exceeded.

## 9. Human‑in‑the‑Loop

Recommended control points:

1. After **Architecture** output (approve design direction)
2. After **Task Breakdown** (approve scope/estimates)
3. After **Implementation+Tests** (approve code before PR)

## 10. References into Specification

- Normative technical contracts (schemas, API, lifecycle): see **Functional & Technical Specification**.
- Code snippets and examples: see **Domain‑Specific Code Examples**.
