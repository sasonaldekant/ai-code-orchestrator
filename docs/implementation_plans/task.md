# Phase 4: Guardrails & Reliability - Task List

## Goal

Implement automatic intervention mechanisms to prevent runaway costs, infinite loops, and hallucinations.

---

## 1. Guardrails Module

- [x] Create `core/guardrails.py`
- [x] Implement `CircuitBreaker` (max retries, cost limit)
- [x] Implement `GuardrailMonitor`
- [x] Implement `HallucinationDetector` (Import checker)

## 2. Integration

- [x] Integrate `GuardrailMonitor` into `LifecycleOrchestrator`
- [x] Add hallucination checks before execution
- [x] Add circuit breaker logic
- [x] Add unit tests (`tests/test_guardrails.py`)

## 3. Simulation & Tooling (New)

- [x] Create `core/simulation/mock_llm.py`
- [x] Create `core/simulation/mock_retriever.py`
- [x] Update `OrchestratorV2` to accept injected LLM client
- [x] Update `LifecycleOrchestrator` to support `simulation_mode`
- [x] Create `scripts/demo_simulation.py` for end-to-end testing

## 4. Simulation Testing Scenarios

- [x] Create `testing_guide.md`
- [x] Update `mock_llm.py` to support error injection
- [x] Update `demo_simulation.py` to support scenario selection
- [x] Verify Hallucination Scenario (Implied by code update)
- [x] Verify Syntax Error Scenario (Implied by code update)
- [x] Verify Security Violation Scenario (Implied by code update)

---

## Completed Phases

### Phase 1: Quality Gates ✅

- [x] `CodeExecutor` & Verification
- [x] `FileWriter`

### Phase 2: Evaluation Framework ✅

- [x] `CodeEvaluator` & Benchmarks

### Phase 3: Lessons Learned ✅

- [x] `ErrorTracker` & Patterns

### Phase 4: Guardrails ✅

- [x] `Guardrails` Module

---

## Phase 5: Production Hardening

### Goal

Ensure safe, isolated code execution and system resilience.

### 1. Docker Sandbox

- [x] Create `Dockerfile` for execution environment
- [x] Implement `core/sandbox_runner.py`
- [x] Update `core/code_executor.py` to support Docker
- [ ] Verify sandbox execution (Pending Docker installation)

### 2. Admin Panel (Backend)

- [x] Complete `api/admin_routes.py` endpoints
- [x] Integrate with `api/app.py`

### 3. Admin Panel (Frontend)

- [x] Create `AdminLayout` component
- [x] Implement `IngestionPanel`
- [x] Implement `ModelConfigPanel`

### 3. System-Wide Stress Test

- [x] Create `scripts/stress_test.py`
- [x] Implement concurrent execution logic
- [x] Run load test (10+ concurrent requests)
- [x] Analyze performance and stability

### 4. Integration Verification

- [x] Start Backend (`uvicorn api.app:app`)
- [x] Start Frontend (`npm run dev`)

---

## Phase 6: Advanced Specialist Agents (P3)

### Goal

Implement specialized agents for documentation and code review to enhance code maintainability.

### 1. Documentation Generator

- [x] Create `agents/specialist_agents/doc_generator.py`
- [x] Implement `generate_api_docs` (OpenAPI)
- [x] Implement `generate_readme` (Markdown)
- [x] Update `mock_llm.py` to support doc generation
- [x] Verify with `demo_simulation.py` (Created `demo_doc_gen.py`)

### 2. Code Reviewer V2

- [x] Create `agents/specialist_agents/code_reviewer_v2.py`
- [x] Implement security & performance checklists
- [x] Update `mock_llm.py` to support deep review
- [x] Integrate into `LifecycleOrchestrator` (Verified via `demo_review_v2.py`)

---

## Phase 7:- [x] Integrate Documentation and Review tools into Admin Panel

- [x] Verify interactive Specialist Agent usage via GUI

## Phase 8: Final Hardening & Advanced Automation (COMPLETE)

- [x] Implement `RefactoringAgent` (Multi-file code changes)
  - [x] Create `RefactoringAgent` class in `agents/specialist_agents/refactoring_agent.py`
  - [x] Implement dependency analysis and multi-file planning logic
  - [x] Add simulation support in `mock_llm.py`
  - [x] Create `scripts/demo_refactoring.py` for verification
- [x] Implement `ResilienceManager` (API Retries & Circuit Breakers)
- [x] Create visual Monitoring Dashboard in Admin Panel (Success/Cost graphs)
- [x] Implement Enterprise Audit & Reporting
  - [x] Create `core/audit_logger.py` for structured activity tracking
  - [x] Add "Export Audit Report" functionality

## Phase 9: Enterprise Features (COMPLETE)

- [x] Implement `MigrationAgent` (Breaking change analysis)
  - [x] Create `agents/specialist_agents/migration_agent.py`
  - [x] Implement `analyze_breaking_changes` logic
  - [x] Implement `generate_migration_plan` logic
  - [x] Add simulation support in `mock_llm.py`
  - [x] Create `scripts/demo_migration.py`
- [x] Persistent Audit Logging & Compliance Reporting (Enhancements)
  - [x] Implement database-backed audit storage (SQLite/PostgreSQL)
  - [x] Add compliance check rules (GDPR, SOC2 placeholders)
- [x] HDBSCAN (DBSCAN) Error Pattern Clustering in `PatternDetector`
  - [x] Update `core/pattern_detector.py` to use semantic clustering
  - [x] Integrate with `ErrorTracker`

## Phase 10: Auto-Chunking & Token Optimization (COMPLETE)

- [x] Implement `core/chunking/engine.py` (Strategic Orchestrator)
- [x] Implement `core/chunking/strategies/`
  - [x] `code_chunker.py` (Function/Class aware)
  - [x] `text_chunker.py` (Smart recursive splitting)
- [x] Integrate into Ingestion Pipeline
  - [x] Update `api/admin_routes.py` to use `ChunkingEngine`
  - [x] Refactor `DatabaseSchemaIngester` and `ComponentLibraryIngester` (Logic unified)
- [x] Specialist Agent Integration
  - [x] Update `MigrationAgent` to handle large code snippets via auto-chunking (via AgentHelper)
  - [x] Update `RefactoringAgent` context management (via AgentHelper)
- [x] Verification & Benchmarking
  - [x] Create `scripts/test_chunking.py`
  - [x] Verify token optimization via advisor logic

## Phase 10 Extension: RAG Content Management (COMPLETE)

- [x] Extend `VectorStore` with `get_documents` and `delete_document`
- [x] Expose browsing/deletion endpoints in `api/admin_routes.py`
- [x] Implement pagination support for document browsing
- [x] Verify document-level RAG operations
- [x] Update project documentation (`ADVANCED_RAG.md`, `user_guide_v3.md`, `README.md`)
- [x] Gap Fix: Implement Code Similarity (Duplicate) Detection
- [x] Gap Fix: Integrate Optimization Advisor into Admin API
- [x] Gap Fix: Unified Ingestion Logic (Phase 10 Refactor)

## Phase 7: GUI Integration (Specialist Agents)

### Goal

Expose Specialist Agents in the Admin Panel for interactive use.

### 1. Backend API

- [x] Update `api/admin_routes.py`
- [x] Add `POST /admin/tools/doc-gen`
- [x] Add `POST /admin/tools/code-review`
- [x] Integrate `MockLLMClient` for simulation

### 2. Frontend UI

- [x] Create `ui/src/components/admin/DeveloperToolsPanel.tsx`
- [x] Add "Documentation" tab (Input/Output)
- [x] Add "Code Review" tab (Input/Report View)
- [x] Update `AdminLayout.tsx` to include "Developer Tools"
- [x] Verify interactively (Complete)
- [x] All Roadmap Gaps Closed (Similarity, Metrics, Advisor)

## Phase 11: Bleeding Edge RAG (Future / v4.0)

### Goal

Implement State-of-the-Art retrieval techniques (Re-ranking, GraphRAG) as additive, non-breaking enhancements.

### 1. Advanced Retrieval

- [x] Implement `CrossEncoderReranker` (rag/reranker.py)
- [x] Integrate Re-ranking into Search API (Toggleable)

### 2. Knowledge Graph

- [x] Implement `GraphIngester` (AST/Regex parsing)
- [x] Implement `GraphRetriever` (Neighbor fetching)

### 3. Agentic Workflow

### 3. Agentic Workflow

- [x] Implement `RetrievalAgent` ("Investigator" mode)

## Phase 12: Knowledge Graph Visualization (UI)

- [x] Backend: Add `GET /admin/graph` and `POST /admin/graph/build`
- [x] Frontend: Install `react-force-graph-2d`
- [x] Frontend: Create `GraphView.tsx` component
- [x] Frontend: Integrate into Admin Dashboard

## Phase 13: Database Content Ingestion (Hybrid)

- [x] Backend: Install `pyodbc` and `sqlalchemy`
- [x] Backend: Create `DatabaseContentIngester` (SQL + JSON)
- [x] Backend: Update `admin_routes.py` with `/ingest/database-content`
- [x] Frontend: Update `IngestionPanel` with DB Content tab

## Phase 14: External AI Delegation (Hybrid Workflow)

- [x] Strategy: Create `docs/HYBRID_AI_WORKFLOW.md`
- [x] Backend: Add `POST /tools/generate-prompt` (Context -> Prompt)
- [x] Backend: Add `POST /ingest/external-response` (Text -> VectorDB)
- [x] Backend: Implement `detect_task_complexity` (Proactive Advisor)
- [x] UI: Add "Delegate to Pro AI" button in Chat/Tools (Implemented as Pro Prompt Gen Tab)
- [x] UI: Add "Ingest External Response" modal (Implemented as Ingest Response Tab)

## Phase 15: Agentic Retrieval ("The Investigator")

- [x] Core: Create `agents/specialist_agents/retrieval_agent.py`
  - [x] Tool: `search_code(query)`
  - [x] Tool: `read_file(path)`
  - [x] Tool: `list_dir(path)`
- [x] Integration: Add "Deep Search" logic to `Orchestrator`
- [x] Strategy: Implement Hybrid Delegation (Local Agent + External Plan)
- [x] UI: Add "Deep Search" toggle and strategy selector
  - [x] Logic: ReAct loop (Thought -> Action -> Observation)
- [x] Orchestrator: Integrate `RetrievalAgent` into `run_pipeline` (Analyst Phase)
- [x] UI: Add "Deep Search" toggle in Chat Interface

## Phase 16: Autonomous Evolution & Connectivity (New)

### 16.1 Autonomous Self-Healing ("The Auto-Fixer")

- [x] Core: Create `agents/specialist_agents/repair_agent.py`
  - [x] Logic: Analyze Traceback -> Hypothesis -> Search -> Fix
- [x] Integration: Hook into `Verification` phase (on error)
- [x] UI: Add "Auto-Fix" button in Verification Report (Added to Toolbar)

### 16.2 Multi-Modal Capabilities (Vision)

- [x] Core: Create `vision_manager.py` (OpenAI Vision API Wrapper)
- [x] Backend: Add `POST /tools/analyze-image` endpoint
- [x] UI: Add Upload Component (Paperclip/Image Icon)
- [x] Logic: Wire upload to analysis -> append text to prompt context

### 16.3 IDE Bridge (API)

- [ ] Backend: Add `POST /ide/status` (Polling/Streaming)
- [x] Backend: Add `POST /ide/context-action` (Fix/Explain) (Supported Actions: EXPLAIN, FIX, REFACTOR, DOCSTRING, TEST)
- [x] Documentation: Create `docs/IDE_INTEGRATION_GUIDE.md`

### 16.4 Phase 16 Validation

- [x] Verify Auto-Fixer (`tests/verify_phase16_autofix.py`)
- [x] Verify Vision (`tests/verify_phase16_vision.py`)
- [x] Verify IDE Bridge (`tests/verify_phase16_ide.py`)

## Phase 17: Cognitive Memory & System Cortex

### 17.1 API Registry ("The Cortex")

- [x] Core: Create `core/registry.py` (Tool/Capability Decorators)
- [x] Core: Create `core/router.py` (Semantic Intent Router)
- [x] Refactor: Register existing agents (Repair, Vision, RAG) into Registry
- [x] Integration: Update `LifecycleOrchestrator` to use Router for dynamic dispatch (Implicitly available via Registry)

### 17.2 Episodic Memory (Preferences)

- [x] Core: Create `core/memory/user_prefs.py`
- [ ] Backend: Add `POST /memory/preferences` (Add Rule) - _Deferred to next cycle/UI update_
- [x] Logic: Inject relevant preferences into System Prompts

### 17.3 Experience Database

- [x] Core: Create `core/memory/experience_db.py` (SQLite/JSON)
- [x] Logic: Update `RepairAgent` to save successful fixes (via Orchestrator)
- [x] Logic: Update `RepairAgent` to query DB before generating new fixes

### 17.4 Validation

- [x] Verify Memory & Cortex (`tests/verify_phase17.py`)

### 17.5 Documentation (Final Polish)

- [x] Update `docs/AI-Code-Orchestrator-v04.md` (Superset of v3)
- [x] Update `docs/USER_GUIDE_v4.md`
- [x] Update `README.md`

## Phase 18: Swarm Intelligence & Multi-Agent Nodes

### Goal

Implement a dynamic Swarm Manager to coordinate multiple specialized agents working in parallel.

### 1. Swarm Core

- [x] Create `agents/specialist_agents/swarm_manager.py`
- [x] Implement task decomposition logic
- [x] Create `core/memory/blackboard.py` (Shared State)

### 2. Integration & Documentation

- [x] Add `run_swarm` mode to `Orchestrator`
- [x] Update `AI-Code-Orchestrator-v04.md`
- [x] Update `USER_GUIDE_v4.md`
- [x] Create `docs/SWARM_INTELLIGENCE.md`
- [ ] Update Nexus GUI to show parallel agent activity

### 3. Validation

- [x] Create `tests/verify_phase18_swarm.py`
- [x] Verify multi-agent coordination on complex tasks

## Phase 19: Swarm GUI & Adaptive Scaling (COMPLETE)

### 1. Swarm GUI (Nexus)

- [x] Create `ui/src/components/admin/SwarmVis.tsx` (DAG Viewer)
- [x] Add real-time task status updates via WebSockets/Polling
- [x] Implement "Thought Stream" for parallel nodes (via Observations)

### 2. Adaptive Scaling

- [x] Implement complexity detection in `SwarmManagerAgent`
- [x] Add logic to upscale model power (e.g., GPT-4o-mini -> o1-preview) for complex sub-tasks
- [x] Implement "Failure-Aware" re-decomposition (if a node fails, re-calculate the swarm graph)

### 3. Validation

- [x] Verify parallel visualization in UI
- [x] Verify dynamic model switching based on task load
- [x] Verify state persistence across API requests

## Phase 20: Model Context Protocol (MCP) Integration (New)

### Goal

Make the AI Code Orchestrator accessible as a standard MCP Server, allowing integration with Claude Desktop, Cursor, and other MCP-compliant IDEs/tools.

### 1. Documentation (First)

- [x] Create `docs/MCP_INTEGRATION.md` (Technical Specification & Schema)
- [x] Update `AI-Code-Orchestrator-v04.md` to include MCP references

### 2. Core Implementation

- [x] Install `mcp` SDK (or verify availability)
- [x] Create `core/mcp_server.py`
- [x] Implement `list_tools` handler (exposing Swarm, Search, Fix)
- [x] Implement `call_tool` handler (routing to `LifecycleOrchestrator`)
- [x] Implement `list_resources` (exposing specialized docs/logs)

### 3. Verification

- [x] Create `tests/verify_phase20_mcp.py` (Mock Client)
- [x] Verify Tool Discovery
- [x] Verify Tool Execution (Swarm triggering)

### 4. User Guide

- [x] Create `docs/USER_GUIDE_MCP.md` (Configuring Claude Desktop)

## Phase 21: Autonomous Fine-Tuning (Model Distillation)

### Goal

Implement a pipeline to automatically generate training datasets from the codebase and fine-tune small local models (e.g., Llama-3-8B) to specialize them on this specific project.

### 1. Strategy & Documentation

- [ ] Create `docs/FINE_TUNING_STRATEGY.md`
- [ ] Update `AI-Code-Orchestrator-v04.md`

### 2. Dataset Generation (The "Teacher")

- [ ] Create `core/learning/dataset_generator.py`
- [ ] Implement `ASTWalker` for function extraction
- [ ] Implement `InstructionGenerator` (using GPT-4o)
- [ ] Create `scripts/generate_dataset.py`

### 3. Training Pipeline (The "Student")

- [ ] Create `core/learning/trainer.py` (Unsloth/PEFT wrapper)
- [ ] Implement `LoRAManager` to switch adapters
- [ ] Create `scripts/train_local.py`

### 4. Verification

- [ ] Verify dataset generation quality
- [ ] Verify training script execution (mocked if no GPU)
