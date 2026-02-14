# Implementation Plan: Model Cascading & Resource Optimization

**Version:** 1.0  
**Date:** 2026-02-12  
**Status:** Draft – Pending Review

---

## 1. Objective

Implement a **multi-tier model cascading system** across the AI Code Orchestrator to minimize API costs and latency while maintaining output quality. The system routes every action through the cheapest capable model first, escalating to stronger models only when needed.

**Target savings:** 60–90% cost reduction on average tasks.

---

## 2. Architecture: 5-Tier Model Hierarchy

Every action in the orchestrator follows this cascade:

```
Tier 0 (Gate)      → gemini-2.0-flash        $0.075/1M input   — Filter, validate, classify
Tier 1 (Worker)    → gpt-4o-mini             $0.15/1M input    — Standard generation & monitoring
Tier 1B (Worker)   → claude-3-5-haiku        $1.00/1M input    — Alt worker (strong at code)
Tier 2 (Standard)  → gpt-4o                  $2.50/1M input    — Architecture, review
Tier 3 (Heavy)     → claude-3-7-sonnet       $3.00/1M input    — Complex fixes, self-healing
Tier 3B (Research) → sonar-reasoning-pro     $2.00/1M input    — Live web research
Tier 4 (Mega)      → gemini-1.5-pro          $1.25/1M input    — 1M context window analysis
```

### Provider Coverage (all 4 APIs utilized)

| Provider    | Models Used                          | Primary Role              |
|-------------|--------------------------------------|---------------------------|
| **Google**  | gemini-2.0-flash, gemini-1.5-pro     | Gate, Mega Context        |
| **OpenAI**  | gpt-4o-mini, gpt-4o, o1-mini        | Workers, Architecture     |
| **Anthropic** | claude-3-5-haiku, claude-3-7-sonnet | Alt Worker, Self-Healing  |
| **Perplexity** | sonar, sonar-reasoning-pro        | Fact-check, Deep Research |

---

## 3. Cascade Flow Per Orchestrator Phase

### Phase 0: Prompt Gate (NEW)
- **Model:** `gemini-2.0-flash` (Tier 0)
- **Action:** Validate prompt clarity, completeness, format
- **Output:** `VALID` or refined prompt
- **Fallback:** Pass-through if gate model unavailable
- **Cost:** ~$0.0001 per call

### Phase 0.5: Fact Check (NEW)
- **Model:** `sonar` (Perplexity base, $1/1M)
- **Action:** Verify library names, API versions, dependency existence
- **When:** Only if prompt mentions external libraries/APIs
- **Output:** Verified facts or corrections appended to context

### Phase 1: Analyst
- **Primary:** `gpt-4o-mini` (Tier 1) — attempt first
- **Escalation:** If confidence < 0.8 → `claude-3-7-sonnet` (Tier 3)
- **Savings:** ~70% of analyses resolved by mini

### Phase 2: Architect  
- **Primary:** `gpt-4o` (Tier 2) — standard
- **For consensus:** Add `claude-3-7-sonnet` as second opinion
- **No change** from current behavior (architecture needs strong reasoning)

### Phase 2.5: Research (NEW, optional)
- **Quick lookup:** `sonar` ($1/1M) — "Does library X support feature Y?"
- **Deep research:** `sonar-reasoning-pro` ($2/1M) — multi-step investigation
- **Codebase analysis:** `gemini-1.5-pro` (Tier 4) — when context > 100K tokens
- **When:** Triggered by deep_search flag or unknown dependencies

### Phase 3: Implementation
- **Primary:** `gpt-4o-mini` (Tier 1) — generate code
- **Review:** `gemini-2.0-flash` (Tier 0) — quick syntax check on output
- **Escalation:** If build fails → `claude-3-7-sonnet` (Tier 3) for fix

### Phase 3.5: Self-Healing Build Check
- **Step 1:** Run build commands (free — local execution)
- **Step 2:** `gemini-2.0-flash` (Tier 0) reads terminal logs
- **Step 3:** If errors found → `claude-3-7-sonnet` (Tier 3) generates fix
- **Step 4:** Re-run build to verify fix

### Phase 4: Review
- **Pre-check:** `gpt-4o-mini` (Tier 1) — checklist validation
- **Deep review:** `gpt-4o` (Tier 2) — only if pre-check finds issues
- **Savings:** ~50% of reviews completed by mini alone

### Phase 5: Testing
- **Generation:** `gpt-4o-mini` (Tier 1) — write test cases
- **Monitoring:** `gemini-2.0-flash` (Tier 0) — parse test output
- **Fix failing tests:** `gpt-4o` (Tier 2) — only if tests fail

---

## 4. New Components to Build

### 4.1 ModelCascadeRouter (core/model_cascade_router.py)
Central decision engine that:
- Accepts a task classification (gate, monitor, worker, heavy, research)
- Returns the appropriate model from the tier hierarchy
- Tracks per-model usage for cost analytics
- Supports fallback chains (if provider is down)

### 4.2 PromptGate (core/prompt_gate.py)
Pre-processing layer:
- Validates prompt quality using Tier 0 model
- Extracts keywords for fact-checking
- Classifies task complexity (simple/medium/complex)
- Routes to appropriate tier based on classification

### 4.3 FactChecker (core/fact_checker.py)
Perplexity-powered verification:
- Checks external library versions and API compatibility
- Validates technology assumptions before code generation
- Caches verified facts to avoid repeat lookups

### 4.4 Enhanced SelfHealingManager (core/self_healing_manager.py)
Upgrade existing implementation:
- Replace monitor model with `gemini-2.0-flash` (10x cheaper)
- Add file patching capability (parse model output → apply changes)
- Add build command auto-detection from project structure
- Support multi-language builds (Python, TypeScript, C#)

### 4.5 CascadeMetrics (core/cascade_metrics.py)
Observability layer:
- Track cascade hit rates (% resolved at each tier)
- Per-model cost accumulation
- Latency per tier
- Dashboard data for Admin UI

### 4.6 Config Updates (config/model_mapping_v2.yaml)
- Add tier classification to all phase configs
- Add cascade_chain per phase
- Add fact_check and gate settings
- Update provider model lists with latest offerings

---

## 5. Cost Projections

| Task Type     | Current Cost | With Cascading | Savings |
|---------------|-------------|----------------|---------|
| Simple task   | $0.50       | $0.05          | **90%** |
| Medium task   | $1.20       | $0.35          | **71%** |
| Complex task  | $3.00       | $1.80          | **40%** |
| Research task | $2.00       | $1.20          | **40%** |

**Monthly projection (200 tasks/month):**
- Current: ~$240/month
- With cascading: ~$70/month
- **Savings: ~$170/month (71%)**

---

## 6. Implementation Order

Priority is based on **impact × effort**:

1. **P0 — Config & Routing** (Foundation)
2. **P1 — Prompt Gate** (Biggest single cost saver)
3. **P2 — Enhanced Self-Healing** (Quality safety net)
4. **P3 — Fact Checker** (Prevents hallucination waste)
5. **P4 — Cascade Metrics** (Observability)
6. **P5 — Admin UI Dashboard** (Visibility for user)

---

## 7. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Small model gives wrong answer | Medium | Confidence scoring + escalation threshold |
| Provider API outage | High | Fallback chains across providers |
| Cascade adds latency | Low | Gate call is <500ms; net savings from avoiding heavy models |
| Over-escalation wastes savings | Medium | Track cascade metrics, tune thresholds monthly |
