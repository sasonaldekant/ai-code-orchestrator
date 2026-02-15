# Implementation Plan: AI Code Orchestrator v3.0 Upgrade

## Goal

Upgrade the existing `AI Code Orchestrator` from its skeletal v0.1.0 state to the fully realized **v3.0 Domain-Agnostic** architecture. This involves implementing the Advanced RAG system, Domain Configuration DSL, and Multi-Model Orchestration as defined in the `domain_ai_spec_v3_package-1`.

## Documentation Coverage Verification

**Confirmed.** The documentation in `docs/documentation upgrade/domain_ai_spec_v3_package-1` is comprehensive and acts as the superset of the legacy documentation in `docs/`.

- **Advanced RAG**: Fully covered in `Functional_Technical_Specification.md` and `notes/ADVANCED_RAG_Source.md`.
- **v3.0 Architecture**: Fully defined in `Architecture_Strategy...md` and `AI-Code-Orchestrator-v03.md`.
- **Implementation**: Specifics provided in `Domain_Specific_Code_Examples.md`.

## User Review Required

#### ✅ Šta JESTE Implementirano i RADI Dobro:
1. **Agent Prompts** (8/10) - Izuzetno napredni, koriste najnovije instrukcije za modele iz 2026. godine.
2. **Hybrid Protocol Concept** - Dobro definisan u promptovima.
3. **Model Routing** - `ModelCascadeRouter` koristi `model_mapping_v2.yaml` koji je **potpuno ažuran** sa najnovijim modelima (GPT-5, Claude 4.6, Gemini 3).
4. **RAG Infrastructure** - ChromaDB funkcionalan.
5. **Basic Caching** - `CacheManager` postoji (mada zahteva nadogradnju za Tier-based caching).

#### ❌ Šta NIJE Implementirano ili ZAHTEVA DORADU:
1. **RAG Tier Config Integration** - `rag_hybrid_config.yaml` postoji, ali logiku pristupa treba čvršće uvezati u `orchestrator_v2.py`.
2. **Tier-Based Prompt Caching** - Potrebna implementacija za 90% uštede koristeći native provider caching (npr. Anthropic Prompt Caching).
3. **Architect Consensus Logic** - Definisan u YAML-u ali zahteva finalnu implementaciju u `orchestrator_v2.py` i `architect.py`.
4. **RAG Metadata Enrichment** - ChromaDB dokumentima nedostaje sistematsko tagovanje po Tier-ovima (T1-T4).

---

## 🔍 Detaljne Analize

### 1. Model Configuration Status

**Fajl:** `config/model_mapping_v2.yaml`

**Status:** ✅ **IZUZETNO AŽURAN** (Usklađen sa stanjem iz februara 2026.)

**Nalaz:** Konfiguracija ispravno mapira najmoćnije modele današnjice:
- **Analyst**: `gpt-5-mini` sa cascade-om na `claude-sonnet-4.5`.
- **Architect**: `gpt-5.2` sa consensus-om sa `claude-opus-4.6`.
- **Research**: `sonar-deep-research` sa fallback-om na `gemini-3-pro`.

**Zaključak:** Nema potrebe za ispravkama naziva modela. Fokus prebacujemo na optimizaciju njihove upotrebe kroz caching.

---

### 2. RAG Hybrid Config Status

**Fajl:** `config/rag_hybrid_config.yaml`

**Status:** ✅ Postoji + ⚠️ Potrebna bolja integracija

**Sadržaj:** IZVRSAN - precizno definiše T1-T4 strukturu i access protocol.

**Nalaz:** Iako je fajl prisutan, `orchestrator_v2.py` trenutno koristi generički `RAGRetriever`. Potrebno je osigurati da se `rag_hybrid_config.yaml` koristi kao primarni izvor istine za tier-based pretragu.

---

### 3. Caching Infrastructure

**Fajl:** `core/cache_manager.py`

**Status:** ✅ Funkcionalan + ⚠️ Zahteva Upgrade

**Preporuka:** Implementirati preporuke iz `AGENT_PROMPTS_CONFIG_v4.1.md` za Tier-based caching kako bi se smanjili troškovi za 40-60%.

---

## 🎯 Prioritizovani Akcioni Plan (Ažurirano)

### FAZA 1: Tier-Based Prompt Caching (URGENT/HIGH ROI - 2 dana)
**Cilj:** Instantna ušteda od 40-60% troškova.
1. Nadogradnja `CacheManager`-a za podršku tier-based ključevima.
2. Integracija sa native API caching funkcionalnostima (OpenAI, Anthropic).

### FAZA 2: RAG Tier System Integration (2-3 dana)
1. Aktiviranje `rag_hybrid_config.yaml` unutar orchestratora.
2. Implementacija `query_tier(tier_id)` metode u retrieveru.
3. Migracija postojećih ChromaDB dokumenata na Tier metadata strukturu.

### FAZA 3: Architect Consensus Implementation (2 dana)
1. Implementacija `run_dual_model` logike u `orchestrator_v2.py`.
2. Ažuriranje `architect.py` agenta da obrađuje i poredi rezultate dva modela.

---

## 📊 Očekivani Rezultati

| Metrika | Trenutno | Posle Implementacije |
|---------|----------|----------------------|
| **Cost Efficiency** | Standardna | **40-60% veća** (zahvaljujući T1/T2 cashiranju) |
| **Accuracy (Types)** | Visoka | **Maksimalna** (kroz mandatory FS read) |
| **Arh. Robusnost** | Single-model | **Dual-model Consensus** |

---

**NAPOMENA:** Prethodni zaključak o "fiktivnosti" modela je bio pogrešan usled neusaglašenosti sa sistemskim vremenom projekta. Potvrđeno je da su svi navedeni modeli (GPT-5, Claude 4.6, Gemini 3) aktuelni i dostupni u simuliranom okruženju februara 2026. godine.

**Sledeći korak:** Da li želiš da krenemo odmah sa **Fazom 1** (Tier-Based Prompt Caching) za maksimalnu uštedu?

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
