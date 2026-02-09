# Implementation Plan: AI Code Orchestrator v3.0 Upgrade

## Goal

Upgrade the existing `AI Code Orchestrator` from its skeletal v0.1.0 state to the fully realized **v3.0 Domain-Agnostic** architecture. This involves implementing the Advanced RAG system, Domain Configuration DSL, and Multi-Model Orchestration as defined in the `domain_ai_spec_v3_package-1`.

## Documentation Coverage Verification

**Confirmed.** The documentation in `docs/documentation upgrade/domain_ai_spec_v3_package-1` is comprehensive and acts as the superset of the legacy documentation in `docs/`.

- **Advanced RAG**: Fully covered in `Functional_Technical_Specification.md` and `notes/ADVANCED_RAG_Source.md`.
- **v3.0 Architecture**: Fully defined in `Architecture_Strategy...md` and `AI-Code-Orchestrator-v03.md`.
- **Implementation**: Specifics provided in `Domain_Specific_Code_Examples.md`.

## User Review Required

> [!IMPORTANT]
> **API Keys & Model Access**: The v3.0 architecture relies on multi-provider access (OpenAI, Anthropic, Gemini). Ensure valid API keys are available in `.env` for the `ModelRouter` to function as designed.

> [!NOTE]
> **Vector Database**: This plan assumes **ChromaDB** running locally (or in-memory for tests) as the vector store, consistent with the "Local-First" principle.

## Proposed Milestones

### Milestone 1: RAG Foundation & Ingestion Framework

**Focus**: Enabling the system to ingest and understand domain knowledge.

- [ ] **Dependency Update**: Add `chromadb`, `sentence-transformers`, `tiktoken` to `pyproject.toml`.
- [x] Create `Ingestion Framework` (Base + Database Schema + Component Library)
  - [x] Create `rag/ingestion/` directory
  - [x] Implement `Ingester` interface
  - [x] Implement `DatabaseSchemaIngester` (C# Parser)
  - [x] Implement `ComponentLibraryIngester` (React Parser)
- [x] Set up `Vector Store` wrapper
  - [x] Implement `ChromaVectorStore` class
  - [x] Add methods for adding/retrieving documents in a schema-aware way

### Milestone 2: Domain Configuration & Retrieval

**Focus**: Making the system domain-agnostic via YAML configuration.

- [ ] **Domain Config DSL**: Implement parser for `domain_config.yaml`.
- [ ] **Domain-Aware Retriever**: Implement `rag/domain_aware_retriever.py` to handle multi-collection retrieval (DB vs Components).
- [ ] **Context Manager**: Implement `core/context_manager.py` to prompt-optimize retrieval results (compressing context).

### Milestone 3: Orchestrator Core & Model Routing

**Focus**: Upgrading the execution engine.

- [x] Enhance `Model Router`
  - [x] Support multi-model configuration (Claude + GPT mixed)
  - [x] Implement prompt routing logic based on task complexity
- [x] Implement `Lifecycle Orchestrator`
  - [x] Task breakdown logic
  - [x] Milestone management
- [x] Implement `Cost Manager`
  - [x] Budget tracking per task/session.

### Milestone 4: Producer-Reviewer Loops & Agents

**Focus**: Quality assurance and autonomous iteration.

- [ ] Upgrade existing agents (`Analyst`, `Architect`, `Implementation`)
  - [x] `Analyst`: Structured JSON output, v2 integration
  - [ ] `Architect`: Review capabilities
  - [ ] `Implementation`: Code generation with context
- [ ] Implement `Producer-Reviewer` pattern in Orchestrator
  - [ ] Feedback loop logic
  - [ ] Consensus mechanism (Optional for v3.0, verified via `ConsensusConfig`)

### Milestone 5: Interfaces & Documentation

**Focus**: User interaction and guidance.

- [ ] **CLI**: Implement `api/cli_commands.py` for `run` and `query` commands.
- [ ] **API Gateway**: Set up FastAPI endpoints for external integration.
- [x] Create `User Guide` (v3.0)
  - [x] Documentation for Installation, Configuration, Usage
  - [x] Examples for Ingestion and Orchestration

## Verification Plan

### Automated Tests

- **Unit Tests**: `pytest` for all new core components (Chunker, Router, Config Parser).
- **Integration Tests**: End-to-end flow using the "POS Insurance" example data provided in the specs.

### Manual Verification

- **Ingestion Test**: Run ingestion on the provided example schema and verify ChromaDB collection stats.
- **Retrieval Test**: Run a CLI query (e.g., "Add login form") and verify the returned context contains relevant React components and DB tables.
- **Generation Test**: Run a full task (e.g., "Create API endpoint") and verify the output follows the schema constraints.
