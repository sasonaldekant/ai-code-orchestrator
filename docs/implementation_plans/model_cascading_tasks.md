# Tasks: Model Cascading & Resource Optimization

**Plan:** [model_cascading_implementation_plan.md](./model_cascading_implementation_plan.md)  
**Created:** 2026-02-12  
**Status Legend:** `[ ]` Todo · `[/]` In Progress · `[x]` Done · `[!]` Blocked

---

## Sprint 1: Foundation & Config (Priority P0)

### Task 1.1 — Update model_mapping_v2.yaml with Tier System
- [ ] Add `tier` field to every phase config (0–4)
- [ ] Add `cascade_chain` list per phase (ordered fallback models)
- [ ] Add `gate` phase config using `gemini-2.0-flash`
- [ ] Add `fact_checker` phase config using `sonar`
- [ ] Add `research` phase config using `sonar-reasoning-pro` and `gemini-1.5-pro`
- [ ] Update provider model lists (add `o1-mini`, `claude-3-5-haiku`, `gemini-2.0-flash`, `sonar`)
- [ ] Verify all model names match actual API identifiers
- **Files:** `config/model_mapping_v2.yaml`
- **Effort:** Small
- **Dependencies:** None

### Task 1.2 — Create ModelCascadeRouter
- [ ] Create `core/model_cascade_router.py`
- [ ] Implement `get_cascade_chain(phase)` → returns ordered list of ModelConfig
- [ ] Implement `select_model(phase, complexity)` → pick tier based on task complexity
- [ ] Implement provider availability check (ping/health)
- [ ] Add fallback logic: if primary provider fails → try next in chain
- [ ] Add per-model call counter for metrics
- [ ] Write unit tests
- **Files:** `core/model_cascade_router.py`, `tests/test_model_cascade_router.py`
- **Effort:** Medium
- **Dependencies:** Task 1.1

### Task 1.3 — Integrate Cascade Router into OrchestratorV2
- [ ] Replace direct `model_router.get_model_for_phase()` calls with cascade router
- [ ] Add complexity classifier (simple/medium/complex based on token count + keywords)
- [ ] Ensure backward compatibility (if cascade config missing, fall back to current behavior)
- [ ] Test full pipeline with cascade routing enabled
- **Files:** `core/orchestrator_v2.py`
- **Effort:** Medium
- **Dependencies:** Task 1.2

---

## Sprint 2: Prompt Gate & Pre-Validation (Priority P1)

### Task 2.1 — Create PromptGate Module
- [ ] Create `core/prompt_gate.py`
- [ ] Implement `validate(prompt)` → uses `gemini-2.0-flash` to check clarity
- [ ] Implement `classify_complexity(prompt)` → returns `simple|medium|complex`
- [ ] Implement `extract_dependencies(prompt)` → list of libraries/APIs mentioned
- [ ] Add pass-through mode if gate model is unavailable
- [ ] Cache recent validations (same prompt within 5 min = skip)
- **Files:** `core/prompt_gate.py`
- **Effort:** Medium
- **Dependencies:** Task 1.1

### Task 2.2 — Integrate PromptGate into Pipeline
- [ ] Call `PromptGate.validate()` as Step 0 in `run_pipeline_adaptive()`
- [ ] Use complexity classification to choose cascade tier for subsequent phases
- [ ] Replace current `validate_prompt_with_small_model()` in SelfHealingManager
- [ ] Log gate decisions to audit trail
- [ ] Add SSE step event for gate validation
- **Files:** `core/orchestrator_v2.py`, `core/self_healing_manager.py`
- **Effort:** Small
- **Dependencies:** Task 2.1

### Task 2.3 — Add gemini-2.0-flash to LLMClientV2
- [ ] Verify GoogleProvider works with `gemini-2.0-flash` model name
- [ ] Test JSON mode compatibility with Gemini Flash
- [ ] Handle potential differences in response format
- [ ] Add Flash-specific token estimation (different tokenizer)
- **Files:** `core/llm_client_v2.py`
- **Effort:** Small
- **Dependencies:** None (can run in parallel with 2.1)

---

## Sprint 3: Self-Healing Enhancement (Priority P2)

### Task 3.1 — Upgrade SelfHealingManager Monitor to Tier 0
- [ ] Change monitor model from `gpt-4o-mini` to `gemini-2.0-flash`
- [ ] Update error parsing prompt for more structured output
- [ ] Add file content extraction (read the failing file for context)
- [ ] Add multi-error support (handle >1 error in single build)
- **Files:** `core/self_healing_manager.py`, `config/model_mapping_v2.yaml`
- **Effort:** Small
- **Dependencies:** Task 2.3

### Task 3.2 — Add File Patching to Self-Healer
- [ ] Parse large model fix output into structured patches
- [ ] Integrate with `core/file_writer.py` to apply changes
- [ ] Add diff preview logging before applying
- [ ] Add rollback capability (backup original before patching)
- [ ] Test with Python syntax errors
- [ ] Test with TypeScript compilation errors
- **Files:** `core/self_healing_manager.py`, `core/file_writer.py`
- **Effort:** Large
- **Dependencies:** Task 3.1

### Task 3.3 — Auto-Detect Build Commands from Project
- [ ] Scan project root for `package.json`, `pyproject.toml`, `*.csproj`
- [ ] Generate appropriate build/check commands per detected technology
- [ ] Store detected commands in session context (avoid re-scanning)
- [ ] Support: Python (`py_compile`), TypeScript (`tsc --noEmit`), .NET (`dotnet build`)
- **Files:** `core/self_healing_manager.py`
- **Effort:** Medium
- **Dependencies:** None

### Task 3.4 — Wire Self-Healing into Post-Implementation Phase
- [ ] Auto-trigger after every implementation phase
- [ ] Use detected build commands from Task 3.3
- [ ] Report healing attempts in pipeline output
- [ ] Add max heal attempts config to `limits.yaml`
- [ ] Emit SSE events for each heal step
- **Files:** `core/orchestrator_v2.py`, `config/limits.yaml`
- **Effort:** Medium
- **Dependencies:** Task 3.2, Task 3.3

---

## Sprint 4: Fact Checker & Research Optimization (Priority P3)

### Task 4.1 — Create FactChecker Module
- [ ] Create `core/fact_checker.py`
- [ ] Implement `verify_dependencies(deps_list)` → uses `sonar` ($1/1M)
- [ ] Implement `check_api_version(library, version)` → live verification
- [ ] Add result caching (same query within 24h = cached)
- [ ] Handle Perplexity API rate limits gracefully
- **Files:** `core/fact_checker.py`
- **Effort:** Medium
- **Dependencies:** Task 1.1

### Task 4.2 — Integrate sonar for Quick Web Lookups
- [ ] Wire FactChecker into Phase 2.5 (after Architect, before Implementation)
- [ ] Auto-extract technology names from architect output
- [ ] Append verified facts to implementation context
- [ ] Skip fact-checking if no external dependencies detected
- **Files:** `core/orchestrator_v2.py`, `core/fact_checker.py`
- **Effort:** Small
- **Dependencies:** Task 4.1

### Task 4.3 — Optimize Deep Research with gemini-1.5-pro
- [ ] Use `gemini-1.5-pro` (1M context) for large codebase analysis
- [ ] Only activate when RAG context exceeds 100K tokens
- [ ] Replace current deep_search path with tiered approach:
  - `sonar` for simple lookups
  - `sonar-reasoning-pro` for multi-step investigation
  - `gemini-1.5-pro` for full codebase sweep
- **Files:** `core/orchestrator_v2.py`, `core/retriever_v2.py`
- **Effort:** Medium
- **Dependencies:** Task 4.1

---

## Sprint 5: Metrics & Observability (Priority P4)

### Task 5.1 — Create CascadeMetrics Module
- [x] Create `core/cascade_metrics.py`
- [x] Track per-tier hit rate (% of tasks resolved at each tier)
- [x] Track per-model cost accumulation
- [x] Track per-model latency averages
- [x] Track escalation frequency per phase
- [x] Persist metrics to `outputs/cascade_metrics.json`
- **Files:** `core/cascade_metrics.py`
- **Effort:** Medium
- **Dependencies:** Task 1.2

### Task 5.2 — Add Cascade Metrics API Endpoint
- [x] Create GET `/admin/cascade-metrics` endpoint
- [x] Return tier hit rates, costs, and latency data
- [x] Add time-range filtering (today, week, month)
- **Files:** `api/admin_routes.py`
- **Effort:** Small
- **Dependencies:** Task 5.1

### Task 5.3 — Cost Savings Dashboard Widget (Admin UI)
- [x] Add "Resource Savings" card to Admin dashboard
- [x] Show: current cost vs projected cost without cascading
- [x] Show: cascade hit rate pie chart (% per tier)
- [x] Show: top 5 most expensive operations
- **Files:** `ui/src/pages/AdminDashboard.tsx` (or equivalent)
- **Effort:** Medium
- **Dependencies:** Task 5.2

### Task 5.4 — Cost Management & Budgeting
- [x] Implement global budgets (task/hour/day) in `CostManager`
- [x] Implement local session budget limits in VS Code Extension
- [x] Create budget alert system (trigger at 80%)
- [x] Add VS Code notifications for cost alerts
- **Files:** `core/cost_manager.py`, `vscode-extension/src/SidebarProvider.ts`
- **Effort:** Medium
- **Dependencies:** Task 5.1

---

## Sprint 6: Advanced Optimizations (Priority P5)

### Task 6.1 — Response Caching Layer
- [x] Cache identical prompts + model responses (TTL-based)
- [x] Use hash of (prompt + model + temperature) as cache key
- [x] Store in SQLite or file-based cache
- [x] Add cache hit rate to metrics
- **Files:** `core/response_cache.py`
- **Effort:** Medium
- **Dependencies:** Task 1.2

### Task 6.2 — Adaptive Threshold Tuning
- [x] Analyze cascade metrics weekly
- [x] Auto-adjust escalation thresholds based on success rates
- [x] If Tier 1 resolves >90%, raise threshold to reduce unnecessary escalation
- [x] If Tier 1 quality drops, lower threshold to escalate sooner
- **Files:** `core/model_cascade_router.py`
- **Effort:** Large
- **Dependencies:** Task 5.1

### Task 6.3 — Batch Processing with Haiku
- [x] For bulk operations (multiple files, test generation), batch with `claude-3-5-haiku`
- [x] Anthropic offers 50% output discount for batch API
- [x] Implement async batch queue with result collection
- **Files:** `core/llm_client_v2.py`, `core/parallel_executor.py`
- **Effort:** Large
- **Dependencies:** None

---

## Summary

| Sprint | Tasks | Effort | Expected Impact |
|--------|-------|--------|-----------------|
| 1. Foundation | 3 tasks | ~3 days | Enable cascade routing |
| 2. Prompt Gate | 3 tasks | ~2 days | 30-50% cost reduction on simple tasks |
| 3. Self-Healing | 4 tasks | ~4 days | Eliminate manual build debugging |
| 4. Fact Checker | 3 tasks | ~3 days | Reduce hallucination-related rework |
| 5. Metrics | 3 tasks | ~3 days | Full visibility into savings |
| 6. Advanced | 3 tasks | ~5 days | Additional 10-20% optimization |

**Total estimated effort:** ~20 working days  
**Total expected cost reduction:** 60–90%
