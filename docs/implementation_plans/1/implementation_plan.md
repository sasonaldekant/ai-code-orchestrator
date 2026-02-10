# AI Code Orchestrator v3.0 - Complete Roadmap

**Goal:** Napraviti savršenu mašinu za proizvodnju kvalitetnog koda

---

## 1. Current State Analysis

### ✅ What We Have

| Category            | Components                                  | Status     |
| ------------------- | ------------------------------------------- | ---------- |
| **Orchestration**   | `lifecycle_orchestrator`, `orchestrator_v2` | ✅ Working |
| **Model Routing**   | `model_router_v2`, phase-based selection    | ✅ Working |
| **Quality Control** | `producer_reviewer`, `consensus_engine`     | ✅ Working |
| **Cost Management** | `cost_manager_v2`, budgets, alerts          | ✅ Working |
| **Validation**      | `OutputValidator` (JSON Schema)             | ✅ Basic   |
| **RAG**             | ChromaDB, domain retrieval                  | ✅ Working |
| **GUI**             | Nexus + Admin Panel                         | ✅ Working |
| **Agents**          | 18 agents (6 phase + 12 specialist)         | ✅ Working |

### ❌ Critical Gaps (vs Industry Standards)

| Gap                            | Risk        | Status   |
| ------------------------------ | ----------- | -------- |
| No automated code testing      | 🔴 Critical | ✅ Fixed |
| No evaluation framework        | 🔴 Critical | ✅ Fixed |
| No lessons learned system      | 🔴 High     | ✅ Fixed |
| No guardrails/circuit breakers | 🟡 Medium   | ✅ Fixed |
| No real-time quality metrics   | 🟡 Medium   | ✅ Fixed |
| No code similarity detection   | 🟢 Low      | ✅ Fixed |

---

## 2. Implementation Roadmap

### Phase 1: Quality Gates (P0) - 2 weeks

**Goal:** Ensure generated code actually works

#### 1.1 Automated Code Execution

```python
# core/code_executor.py (NEW)
class CodeExecutor:
    def execute_python(code: str) -> ExecutionResult
    def execute_typescript(code: str) -> ExecutionResult
    def execute_dotnet(code: str) -> ExecutionResult
```

#### 1.2 Test Generation Agent

```python
# agents/specialist_agents/test_generator.py (NEW)
class TestGeneratorAgent:
    def generate_unit_tests(code: str, context: dict) -> List[TestCase]
    def generate_integration_tests(plan: dict) -> List[TestCase]
```

#### 1.3 Verification Loop

```
Implementer → Code → Test Generator → Tests → Executor →
    ├── Pass → Continue
    └── Fail → Feedback to Implementer (max 3 retries)
```

**Deliverables:**

- [ ] `core/code_executor.py`
- [ ] `core/sandbox_runner.py` (Docker isolation)
- [ ] `agents/test_generator.py`
- [ ] Update `lifecycle_orchestrator` with verification step

---

### Phase 2: Evaluation Framework (P0) - 2 weeks

**Goal:** Measure code quality objectively

#### 2.1 Code Quality Metrics

```python
# core/code_evaluator.py (NEW)
class CodeEvaluator:
    metrics = {
        "functional_correctness": PassAtKEvaluator(),
        "code_quality": StaticAnalysisEvaluator(),  # pylint, eslint
        "complexity": ComplexityEvaluator(),        # cyclomatic
        "security": SecurityScanner(),              # bandit, semgrep
        "performance": PerformanceProfiler()
    }
```

#### 2.2 Benchmark Suite

```
evals/
├── benchmarks/
│   ├── humaneval_dotnet/    # Adapted for C#
│   ├── react_components/    # Component generation
│   └── database_queries/    # SQL/EF Core
├── test_cases/
└── runners/
```

**Deliverables:**

- [ ] `core/code_evaluator.py`
- [ ] `evals/benchmarks/` structure
- [ ] Integration with CI/CD
- [ ] Dashboard metrics in GUI

---

### Phase 3: Lessons Learned System (P1) - 2 weeks

**Goal:** Learn from mistakes, prevent repetition

#### 3.1 Error Tracker

```python
# core/error_tracker.py (NEW)
class ErrorTracker:
    def log_error(phase, error_type, context, details)
    def detect_patterns() -> List[ErrorPattern]
    def get_prevention_rules(phase) -> List[Rule]
```

#### 3.2 Error Pattern Detection (ML-based)

```
1. Collect errors with embeddings
2. Cluster similar errors (HDBSCAN)
3. After 3+ occurrences → create pattern
4. Generate prevention rule
5. Inject into future prompts
```

#### 3.3 Best Practices Injection

```yaml
# config/best_practices.yaml (NEW)
domains:
  dotnet:
    patterns:
      - name: "CQRS Controller"
        example: |
          [HttpPost]
          public async Task<ActionResult> Create(CreateCommand cmd)
          {
              var result = await _mediator.Send(cmd);
              return Ok(result);
          }
    anti_patterns:
      - name: "Business Logic in Controller"
        detection: "controller.*repository"
        fix: "Extract to service layer"
```

**Deliverables:**

- [ ] `core/error_tracker.py`
- [ ] `core/pattern_detector.py`
- [ ] `config/best_practices.yaml`
- [ ] Admin Panel → Lessons Learned tab

---

## Phase 8: Final Hardening & Advanced Automation [DONE]

### [Component] Refactoring Agent

Summary: New agent for handling structural changes across multiple files.

#### [NEW] [refactoring_agent.py](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/agents/specialist_agents/refactoring_agent.py)

- **Class:** `RefactoringAgent`
- **Methods:**
  - `analyze_dependencies(files)`: Uses RAG to find related modules.
  - `plan_refactoring(request, scope)`: Generates a `RefactoringPlan` (JSON).
  - `execute_refactoring(plan)`: Orchestrates `FileWriter` calls.
- **Verification:** `scripts/demo_refactoring.py`

### [Component] Resilience & Reliability

Summary: Infrastructure for production-grade API handling.

#### [NEW] [resilience.py](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/core/resilience.py)

- Implements decorators for `retry` and `circuit_breaker`.
- Integrates with `LLMClientV2`.

### [Component] Monitoring Dashboard

Summary: Visual analytics for the Admin Panel.

#### [NEW] [MonitoringDashboard.tsx](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/ui/src/components/admin/MonitoringDashboard.tsx)

- Charts for:
  - Task Success Rate (Area Chart)
  - Cost per Model (Donut Chart)
  - Latency Distribution (Bar Chart)

---

### Phase 4: Guardrails & Reliability (P1) - 1 week

**Goal:** Automatic intervention when things go wrong

#### 4.1 Circuit Breakers

```python
# core/guardrails.py (NEW)
class GuardrailMonitor:
    rules = {
        "max_phase_retries": 3,
        "max_total_errors": 5,
        "cost_limit_per_task": 0.50,
        "hallucination_threshold": 0.3
    }

    def check_and_intervene(context) -> Action
    # Returns: CONTINUE | RETRY | ESCALATE | ABORT
```

#### 4.2 Hallucination Detection

```python
# core/hallucination_detector.py (NEW)
class HallucinationDetector:
    def check_references(code, context) -> List[Issue]
    # Detects: non-existent imports, fake APIs, wrong types
```

**Deliverables:**

- [ ] `core/guardrails.py`
- [ ] `core/hallucination_detector.py`
- [ ] Integration with orchestrator
- [x] Admin Panel → Guardrails config

#### 4.3 Simulation & Tooling (New)

**Goal:** Enable development and testing without live API keys.

```python
# core/simulation/mock_llm.py (NEW)
class MockLLMClient:
    def complete(messages, model) -> MockResponse:
        # Returns predefined JSON for Analyst, Architect, Implementation phases
```

**Deliverables:**

- [x] `core/simulation/mock_llm.py`
- [x] `core/simulation/mock_retriever.py`
- [x] `scripts/demo_simulation.py`
- [x] Orchestrator support for `simulation_mode`

---

### Phase 5: Production Hardening (P2) - [DONE]

**Goal:** Enterprise-ready system

#### 5.1 Docker Sandbox [DONE]

- Implemented `Dockerfile` and `SandboxRunner`.
- Integrated with `CodeExecutor`.
- _Note:_ Requires Docker installation for activation.

#### 5.2 Admin Panel [DONE]

- Backend API implemented (`api/admin_routes.py`).
- Frontend implemented (`ui/src/components/admin/`).
- Includes RAG Ingestion, Model Config, Budgets.

#### 5.3 Stress Testing [DONE]

- Implemented `scripts/stress_test.py`.
- Verified 10 concurrent users with 100% success rate.
- Average latency: ~23s (Simulation Mode).

---

### Phase 6: Advanced Specialist Agents (P3) - [DONE]

**Goal:** Enhanced maintenance and documentation coverage.

#### 6.1 Documentation Generator [DONE]

- Implemented `DocGeneratorAgent`.
- Supports OpenAPI and README generation.
- Validated with `scripts/demo_doc_gen.py`.

#### 6.2 Code Reviewer V2 [DONE]

- Implemented `CodeReviewerV2`.
- Checks for Security, Performance, and Maintainability.
- Validated with `scripts/demo_review_v2.py`.

---

### Phase 7: GUI Integration (Specialist Agents) - [DONE]

**Goal:** Interactive access to specialist agents via Admin Panel.

#### 7.1 Backend API [DONE]

- Implemented `POST /admin/tools/doc-gen`.
- Implemented `POST /admin/tools/code-review`.

#### 7.2 Frontend UI [DONE]

- Created `DeveloperToolsPanel` component.
- Integrated into `AdminLayout`.
- Supports Documentation Generation and Code Review tabs.

---

## 3. Advanced Features (P3)

(Remaining items: Refactoring, Migration)

```python
# agents/specialist_agents/refactoring_agent.py
class RefactoringAgent:
    def analyze_dependencies(files: List[str])
    def plan_refactoring(change: str)
    def execute_with_rollback()
```

### 3.2 Code Review Agent (Enhanced)

```python
# agents/specialist_agents/code_reviewer_v2.py
class CodeReviewerV2:
    checklist = ["security", "performance", "maintainability", "style"]
    def review(code, context) -> ReviewReport
    def suggest_improvements() -> List[Suggestion]
```

### 3.3 Documentation Generator

```python
# agents/specialist_agents/doc_generator.py
class DocGenerator:
    def generate_api_docs(code) -> OpenAPISpec
    def generate_readme(project) -> Markdown
    def generate_inline_comments(code) -> AnnotatedCode
```

### 3.4 Migration Agent [IN PROGRESS]

Summary: Specialized agent for analyzing differences between versions and automating upgrades.

#### [NEW] [migration_agent.py](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/agents/specialist_agents/migration_agent.py)

- **Class:** `MigrationAgent`
- **Methods:**
  - `analyze_breaking_changes(old_code: str, new_code: str)`: Identifies signature changes, removals, and logic shifts.
  - `generate_migration_plan(scope_files: List[str])`: Creates a step-by-step upgrade guide.
  - `recommend_polyfills(missing_features: List[str])`: Suggests backward compatibility layer.
- **Verification:** `scripts/demo_migration.py`

### 3.5 Advanced Pattern Detection

#### [MODIFY] [pattern_detector.py](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/core/pattern_detector.py)

- **Enhancement:** Replace simple grouping with HDBSCAN clustering.
- **Goal:** Detect non-obvious relationship between errors across different phases.
- **Library:** `scikit-learn` or `hdbscan`.

---

## 4. Priority Matrix

| Feature                  | Impact      | Effort | Priority |
| ------------------------ | ----------- | ------ | -------- |
| Code Execution/Testing   | 🔴 Critical | Medium | **P0**   |
| Evaluation Framework     | 🔴 Critical | Medium | **P0**   |
| Error Tracker            | 🟡 High     | Low    | **P1**   |
| Guardrails               | 🟡 High     | Low    | **P1**   |
| Best Practices Injection | 🟡 High     | Medium | **P1**   |
| Monitoring Dashboard     | 🟡 Medium   | Medium | **P2**   |
| Resilience/Rate Limiting | 🟡 Medium   | Low    | **P2**   |
| Multi-File Refactoring   | 🟢 Medium   | High   | **P3**   |
| Doc Generator            | 🟢 Low      | Medium | **P3**   |
| Migration Agent          | 🟢 Low      | High   | **P3**   |

---

## 5. Success Metrics

| Metric                         | Current | Target     |
| ------------------------------ | ------- | ---------- |
| Code passes tests on first try | ~40%    | **>80%**   |
| Average retries per feature    | 3+      | **<1.5**   |
| Hallucination rate             | Unknown | **<5%**    |
| Cost per feature               | ~$0.40  | **<$0.25** |
| Time to complete feature       | ~5min   | **<3min**  |
| User satisfaction              | -       | **>4.5/5** |

---

## Phase 10: Auto-Chunking & Token Optimization

**Goal:** Automate the splitting of large content into optimal chunks for LLM processing and RAG ingestion.

### [Component] Chunking Engine

Summary: A modular system for splitting text/code using various strategies.

#### [NEW] [engine.py](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/core/chunking/engine.py)

- **Class:** `ChunkingEngine`
- **Method:** `chunk_content(content: str, file_type: str, max_tokens: int) -> List[Chunk]`
- **Logic:** Automatically selects `CodeChunker` for .cs, .py, .ts, etc., and `TextChunker` for others.

#### [NEW] [code_chunker.py](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/core/chunking/strategies/code_chunker.py)

- Uses regex/AST to identify logical boundaries (functions, classes).
- Ensures chunks are self-contained with minimal context loss.

#### [NEW] [text_chunker.py](file:///e:/PROGRAMING/AI_Projects/ai-code-orchestrator/core/chunking/strategies/text_chunker.py)

- Implements recursive character splitting.
- Optimizes for sentence/paragraph boundaries.

### Integration Plan

1.  **Ingestion:** `api/admin_routes.py` will replace its manual loop with `ChunkingEngine.chunk_content()`.
2.  **Specialist Agents:** Agents will use the engine when provided code exceeds `LLM_CONTEXT_WINDOW_LIMIT`.
3.  **Optimization UI:** The Admin Panel will display "Auto-Chunking Active" and metrics on saved tokens. [x]

## Phase 11: Bleeding Edge RAG (Advanced Retrieval)

**Goal:** Implement Re-ranking and GraphRAG to achieve SOTA performance.

### 11.1 Re-ranking Module [Complete]

- [x] Create `rag/reranker.py` with `CrossEncoderReranker`
- [x] Verify with `scripts/demo_reranking.py`
- [x] Integrate into `VectorStore` (optional toggle)

### 11.2 Knowledge Graph (GraphRAG) [Complete]

- [x] Implement `GraphIngester` (AST/Regex)
- [x] Implement `GraphRetriever` (Neighbor fetching)

### 11.3 Agentic Workflow (Retrieval Agent) [Complete]

- [x] Implement `RetrievalAgent` (Orchestrator)
- [x] Implement "Investigator" mode (Plan -> Search -> graph -> Answer)
- [x] Verify with complex queries

### Phase 12: Knowledge Graph Visualization [Complete]

- [x] Backend: API for Graph Build/Retrieve
- [x] Frontend: `GraphTab` with `react-force-graph-2d`
- [x] Frontend: Integrated into Admin

### Phase 13: Database Content Ingestion [Complete]

- [x] Core: `DatabaseContentIngester` class
  - Mode A: Direct SQL (using `pyodbc`)
  - Mode B: JSON Import (fallback)
- [x] API: New endpoints for content ingestion
- [x] UI: New "Data Content" section in Ingestion Panel

### Phase 14: External AI Delegation [Planned]

- [ ] Strategy Guide: When to use ChatGPT/Perplexity vs Orchestrator
- [x] Prompt Generator: Tool to package code context into a prompt for external models
- [x] Proactive Advisor: Logic to detect high-token/complex tasks and suggest delegation
- [x] Response Ingester: Tool to save external AI answers into the project memory

### Phase 15: Agentic Retrieval ("The Investigator") [Planned]

- [ ] Investigator Agent: A specialized LangChain/Custom agent with filesystem access
- [ ] Toolset:
  - `grep_search`: For finding string matches
  - `file_read`: For reading content
  - `definition_lookup`: Using part of the Graph system (if available) or regex
- [ ] Integration:
  - Orchestrator calls Investigator when standard RAG returns low confidence
  - "Analyst" phase uses Investigator to answer "How does X work?" questions deeply

## 4. Priority Matrix
