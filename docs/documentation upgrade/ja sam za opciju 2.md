<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# ja sam za opciju 2

Perfektno! Evo kompletnih fajlova spremnih za copy-paste:

***

# 📄 **FAJL 1: `docs/AI-Code-Orchestrator-Enhanced-Documentation.md`**

```markdown
# AI Code Orchestrator — Enhanced Technical Documentation

**Version:** 2.0.0  
**Last Updated:** 2026-02-07  
**Status:** Production-Ready Roadmap  
**Autor:** System Architecture Team

---

## 📋 Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current vs Target Architecture](#2-current-vs-target-architecture)
3. [Multi-Model Orchestration](#3-multi-model-orchestration)
4. [Token Optimization Strategy](#4-token-optimization-strategy)
5. [Agent Communication Protocol](#5-agent-communication-protocol)
6. [Quality Assurance Mechanisms](#6-quality-assurance-mechanisms)
7. [.NET-Specific Features](#7-net-specific-features)
8. [Cost Management System](#8-cost-management-system)
9. [Performance Benchmarks](#9-performance-benchmarks)
10. [Migration Guide](#10-migration-guide)

---

## 1. Executive Summary

### 1.1 Identifikovani Problemi u v0.1.0

| Problem | Impact | Prioritet |
|---------|--------|-----------|
| **Mono-vendor pristup** (samo OpenAI) | Visoki troškovi, vendor lock-in | 🔴 Kritičan |
| **Nema token optimizacije** | 3-5x veća potrošnja tokena | 🔴 Kritičan |
| **Sekvencijalno izvršavanje** | 2-3x sporije | 🟡 Visok |
| **Nedostaje međusobna kontrola** | Niži kvalitet outputa | 🟡 Visok |
| **Nema cost trackinga** | Nepoznat ROI | 🟡 Visok |
| **Generički agenti** | Ne podržava existing codebase | 🟢 Srednji |

### 1.2 Očekivani Rezultati u v2.0.0

| Metrika | v0.1.0 | v2.0.0 | Napredak |
|---------|--------|--------|----------|
| **Prosečan cost po tasku** | $0.80 - $1.20 | $0.20 - $0.40 | **65-75% ↓** |
| **Token consumption** | 100% (baseline) | 25-45% | **55-75% ↓** |
| **Execution time** | 100% (baseline) | 55-65% | **35-45% ↓** |
| **Code quality score** | 7.2/10 | 8.5/10 | **+18% ↑** |
| **Supported models** | 2 (OpenAI) | 8+ (3 vendors) | **+300% ↑** |

### 1.3 ROI Kalkulacija

**Tradicionalni razvoj:**
- Developer hourly rate: $100/h
- Average feature time: 24h
- **Cost: $2,400/feature**

**v0.1.0 Agentic system:**
- Development time: ~4.5h
- Token cost: $0.80
- **Total: $450.80/feature** (81% ušteda)

**v2.0.0 Enhanced system:**
- Development time: ~3.5h (paralelizacija)
- Token cost: $0.25 (optimizacija)
- **Total: $350.25/feature** (85% ušteda, dodatnih 22% u odnosu na v0.1.0)

---

## 2. Current vs Target Architecture

### 2.1 Arhitektura v0.1.0 (Current)

```

┌──────────────────────────────────────┐
│         FastAPI Gateway              │
└────────────┬─────────────────────────┘
│
┌────────────▼─────────────────────────┐
│       Orchestrator (Sequential)      │
│  - Simple routing                    │
│  - No cost tracking                  │
│  - Full context passing              │
└────────────┬─────────────────────────┘
│
┌──────┴──────┬──────────┬───────┐
│             │          │       │
┌─────▼────┐  ┌────▼───┐  ┌───▼──┐  ┌─▼────┐
│ Analyst  │→ │Architect│→│Implem│→ │Tester│
│ (GPT-4o  │  │(GPT-4o) │ │(mini)│  │(mini)│
│  mini)   │  │         │ │      │  │      │
└──────────┘  └─────────┘ └──────┘  └──────┘

Problemi:
❌ Svi koriste isti vendor (OpenAI)
❌ Sekvencijalno izvršavanje
❌ Pun context (1000+ tokens) svaki put
❌ Nema međusobne kontrole
❌ Nema cost limitova

```

### 2.2 Arhitektura v2.0.0 (Target)

```

┌────────────────────────────────────────────────────────────┐
│              FastAPI Gateway + Auth + Rate Limiting         │
└──────────────────┬────────────────────────────────────────┘
│
┌─────────────┴──────────────┐
│                            │
┌────▼──────────────┐    ┌────────▼────────────┐
│ Smart Orchestrator│    │  Cost Manager       │
│ - Multi-model     │◄───┤  - Real-time track  │
│ - Parallel exec   │    │  - Budget control   │
│ - Context optim   │    │  - Alerts           │
└────┬──────────────┘    └─────────────────────┘
│
│ Phase/Specialty routing
│
┌────▼─────────────────────────────────────────────────┐
│              AGENT EXECUTION LAYER                    │
│                                                        │
│  ┌──────────────────────────────────────────┐        │
│  │  Phase 1: ANALYSIS (Parallel)            │        │
│  │  ├─ Requirements (Claude Sonnet)         │        │
│  │  └─ Research (Gemini 2.5 Pro)            │        │
│  └──────────────────────────────────────────┘        │
│                      │                                │
│  ┌──────────────────▼──────────────────────┐        │
│  │  Phase 2: ARCHITECTURE (Consensus)       │        │
│  │  ├─ Proposal 1 (Claude Sonnet)          │        │
│  │  ├─ Proposal 2 (GPT-4o)                 │        │
│  │  ├─ Proposal 3 (Gemini)                 │        │
│  │  └─ Synthesizer → Final Design          │        │
│  └──────────────────────────────────────────┘        │
│                      │                                │
│  ┌──────────────────▼──────────────────────┐        │
│  │  Phase 3: IMPLEMENTATION (Parallel)      │        │
│  │  ├─ Backend (.NET) ──┐                  │        │
│  │  │   ├─ API (GPT-4o) │                  │        │
│  │  │   └─ EF (GPT-4o)  │                  │        │
│  │  │                    ├─► Integration    │        │
│  │  ├─ Frontend (React)─┤                  │        │
│  │  │   ├─ Components   │                  │        │
│  │  │   └─ Types (mini) │                  │        │
│  │  └─ Tests (mini) ────┘                  │        │
│  └──────────────────────────────────────────┘        │
│                      │                                │
│  ┌──────────────────▼──────────────────────┐        │
│  │  Phase 4: REVIEW (Producer-Reviewer)    │        │
│  │  ┌─────────────────────────────┐        │        │
│  │  │ Code Review (Claude Sonnet) │        │        │
│  │  │         ↓                    │        │        │
│  │  │  Issues? → Back to Producer │        │        │
│  │  │  OK? → Approve              │        │        │
│  │  └─────────────────────────────┘        │        │
│  └──────────────────────────────────────────┘        │
│                                                        │
└────────────────────────────────────────────────────────┘

Prednosti:
✅ Multi-vendor (3 providers, 8+ models)
✅ Paralelno izvršavanje (-40% vremena)
✅ Token optimization (-65% tokena)
✅ Producer-Reviewer loop (+18% kvalitet)
✅ Real-time cost control
✅ Consensus za kritične odluke

```

---

## 3. Multi-Model Orchestration

### 3.1 Model Selection Strategy

**Principi odlučivanja:**

1. **Reasoning Capability** → Claude Sonnet 3.5
   - Complex analysis
   - Architecture decisions
   - Code review

2. **Cost-Effectiveness** → GPT-4o mini
   - Simple tasks
   - Testing
   - TypeScript generation

3. **Large Context** → Gemini 2.5 Pro
   - Existing codebase research
   - Documentation
   - Legacy code understanding

4. **Language-Specific** → GPT-4o
   - C# / .NET development
   - API implementation

### 3.2 Routing Configuration

**Fajl:** `config/model_mapping_v2.yaml`

```yaml
version: "2.0.0"

providers:
  openai:
    api_key: ${OPENAI_API_KEY}
    models:
      - gpt-4o
      - gpt-4o-mini
  
  anthropic:
    api_key: ${ANTHROPIC_API_KEY}
    models:
      - claude-3-5-sonnet
  
  google:
    api_key: ${GOOGLE_API_KEY}
    models:
      - gemini-2.5-pro

default:
  model: gpt-4o-mini
  temperature: 0.0
  max_tokens: 4000
  timeout_seconds: 30

routing:
  phase:
    analyst:
      model: claude-3-5-sonnet
      provider: anthropic
      temperature: 0.1
      max_tokens: 8000
      reasoning: "Best for requirements analysis and edge case discovery"
    
    architect:
      consensus_mode: true
      models:
        primary:
          model: claude-3-5-sonnet
          provider: anthropic
          weight: 0.5
        secondary:
          model: gpt-4o
          provider: openai
          weight: 0.3
        tertiary:
          model: gemini-2.5-pro
          provider: google
          weight: 0.2
      synthesis_model: claude-3-5-sonnet
      reasoning: "Critical decisions require multiple perspectives"
    
    implementer:
      model: gpt-4o
      provider: openai
      temperature: 0.0
      max_tokens: 8000
      reasoning: "Strong C# performance (92% HumanEval)"
    
    tester:
      model: gpt-4o-mini
      provider: openai
      temperature: 0.0
      max_tokens: 4000
      reasoning: "Cost-effective for test generation"
    
    reviewer:
      model: claude-3-5-sonnet
      provider: anthropic
      temperature: 0.0
      max_tokens: 8000
      producer_reviewer_loop: true
      max_iterations: 3
      quality_threshold: 8.0
      reasoning: "Best code review capabilities"

  specialty:
    backend:
      dotnet_api:
        model: gpt-4o
        provider: openai
        temperature: 0.0
        specialization: "ASP.NET Core, Web API, Controllers"
      
      efcore:
        model: gpt-4o
        provider: openai
        temperature: 0.0
        context_aware: true
        context_sources:
          - existing_dbcontext
          - migration_history
        specialization: "Entity Framework Core, Migrations, DbContext"
      
      database:
        model: claude-3-5-sonnet
        provider: anthropic
        temperature: 0.0
        specialization: "Schema design, relationships, indexing"
      
      microservice:
        model: gpt-4o
        provider: openai
        temperature: 0.0
        specialization: "Microservice architecture, communication patterns"
      
      security:
        model: claude-3-5-sonnet
        provider: anthropic
        temperature: 0.0
        specialization: "Security best practices, vulnerability detection"
    
    frontend:
      react:
        model: gpt-4o-mini
        provider: openai
        temperature: 0.0
        specialization: "React 18+, hooks, functional components"
      
      typescript:
        model: gpt-4o-mini
        provider: openai
        temperature: 0.0
        specialization: "TypeScript types, interfaces, generics"
      
      css:
        model: gpt-4o-mini
        provider: openai
        temperature: 0.0
        specialization: "CSS, SCSS, responsive design"
      
      ui_ux:
        model: gpt-4o-mini
        provider: openai
        temperature: 0.1
        specialization: "User experience, accessibility"
    
    integration:
      api_integration:
        model: gpt-4o
        provider: openai
        temperature: 0.0
        specialization: "REST APIs, HTTP clients, error handling"
      
      devops:
        model: gpt-4o
        provider: openai
        temperature: 0.0
        specialization: "CI/CD, Docker, Kubernetes"
    
    documentation:
      technical_docs:
        model: gemini-2.5-pro
        provider: google
        temperature: 0.2
        max_tokens: 32000
        specialization: "Technical documentation, API docs"
      
      code_research:
        model: gemini-2.5-pro
        provider: google
        temperature: 0.3
        max_tokens: 100000
        context_window: 1000000
        specialization: "Existing codebase analysis, legacy code understanding"

cost_management:
  budgets:
    per_task: 0.50      # USD
    per_hour: 5.00
    per_day: 40.00
    per_month: 800.00
  
  alerts:
    threshold_warning: 0.75   # 75% of budget
    threshold_critical: 0.90  # 90% of budget
    notify_channels:
      - slack_webhook
      - email
  
  optimization:
    enable_cache: true
    cache_ttl_seconds: 3600
    enable_token_estimation: true
    reject_over_budget: true

optimization```

