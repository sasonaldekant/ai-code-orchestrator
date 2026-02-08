<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# da li možeš da uradiš reviziju dokumentacije koju imamo u projektu i dopuniš je svime povime , a onda napraviš plan detaljan implementacije svega što nedostaje i projektu

Odličo! Sada ću kreirati sveobuhvatne dokumente. Pošto ne mogu direktno da kreiram fajlove na GitHub-u putem web interfejsa, pripremićiu kompletne dokumente koje možeš da kopirate i dodaš u projekat.

# 📄 DOKUMENT 1: Revidirani Tehnički Dokument

Kreiraću fajl: `docs/AI-Code-Orchestrator-Enhanced-Documentation.md`

```markdown
# AI Code Orchestrator — Enhanced Technical Documentation
**Version:** 2.0.0  
**Last Updated:** 2026-02-07  
**Status:** Production-Ready Roadmap

---

## 📋 Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Multi-Model Orchestration Strategy](#3-multi-model-orchestration-strategy)
4. [Token Optimization Techniques](#4-token-optimization-techniques)
5. [Agent Communication Protocols](#5-agent-communication-protocols)
6. [Quality Assurance Mechanisms](#6-quality-assurance-mechanisms)
7. [.NET-Specific Implementations](#7-net-specific-implementations)
8. [Cost Management & Monitoring](#8-cost-management--monitoring)
9. [Implementation Phases](#9-implementation-phases)
10. [API Reference](#10-api-reference)

---

## 1. Executive Summary

### 1.1 Current State (v0.1.0)
AI Code Orchestrator je scaffold sistem za mikrospecijalizovanu agentsku orkestraciju sa sledećim komponentama:
- Phase agents (analyst, architect, implementer, tester)
- Specialist agents (frontend: CSS/TS/React; backend: .NET; integration; DevOps)
- Schema-driven outputs (JSON Schema validacija)
- RAG layer (embeddings + ingest/query)
- REST API (FastAPI) sa auth/rate limiting/metrics
- Tracing/Audit (JSONL)

**Identifikovani problemi:**
- ❌ Mono-vendor pristup (samo OpenAI modeli)
- ❌ Nema token optimizacionih tehnika (visoka potrošnja)
- ❌ Nedostaje međusobna kontrola agenata
- ❌ Nema cost trackinga
- ❌ Sekvencijalno izvršavanje (nema paralelizacije)
- ❌ Nedostaju .NET-specifični agenti za existing codebase

### 1.2 Target State (v2.0.0)
**Ciljevi:**
- ✅ Multi-model routing (OpenAI + Claude + Gemini)
- ✅ 60-87% token reduction kroz optimizacione tehnike
- ✅ Producer-Reviewer loop za kvalitet
- ✅ Real-time cost tracking i budget management
- ✅ Parallel execution (MapReduce pattern)
- ✅ EF Core aware agents za incremental development
- ✅ ROI: $1,950 uštede po feature-u (81%)

---

## 2. Architecture Overview

### 2.1 Komponente Sistema

```

┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY (FastAPI)                     │
│  - Authentication (JWT + API Key)                            │
│  - Rate Limiting (Redis-based)                               │
│  - Request Routing                                           │
└──────────────────────────┬──────────────────────────────────┘
│
┌─────────────────┴─────────────────┐
│                                   │
┌────────▼────────┐              ┌───────────▼──────────┐
│  ORCHESTRATOR   │              │  COST MANAGER        │
│  - Multi-model  │              │  - Token tracking    │
│  - Parallel exec│              │  - Budget control    │
│  - Context mgmt │              │  - Real-time alerts  │
└────────┬────────┘              └──────────────────────┘
│
┌────┴─────┬──────────┬──────────┬──────────┐
│          │          │          │          │
┌───▼───┐  ┌──▼───┐  ┌───▼───┐  ┌───▼───┐  ┌──▼───┐
│Router │  │RAG   │  │Trace  │  │Valid. │  │Queue │
│       │  │      │  │       │  │       │  │      │
└───┬───┘  └──────┘  └───────┘  └───────┘  └──────┘
│
│ Phase/Specialty-based routing
│
┌───▼──────────────────────────────────────────────────────┐
│                    AGENT LAYER                            │
│                                                            │
│  Phase Agents:                                            │
│  ├─ Analyst       (Claude Sonnet 3.5)                    │
│  ├─ Architect     (Claude Sonnet 3.5 + Consensus)        │
│  ├─ Implementer   (GPT-4o / Specialized per tech)        │
│  └─ Tester        (GPT-4o mini)                          │
│                                                            │
│  Specialist Agents:                                       │
│  ├─ Backend                                               │
│  │   ├─ .NET API Dev        (GPT-4o)                     │
│  │   ├─ EF Core Manager     (GPT-4o + AST parsing)       │
│  │   ├─ Database Designer   (Claude Sonnet)              │
│  │   └─ Security Specialist (Claude Sonnet)              │
│  ├─ Frontend                                              │
│  │   ├─ React Builder       (GPT-4o mini)                │
│  │   ├─ TypeScript Dev      (GPT-4o mini)                │
│  │   └─ CSS/UX Designer     (GPT-4o mini)                │
│  ├─ Integration                                           │
│  │   ├─ API Integrator      (GPT-4o)                     │
│  │   └─ DevOps Engineer     (GPT-4o)                     │
│  └─ Quality Assurance                                     │
│      ├─ Code Reviewer       (Claude Sonnet 3.5)          │
│      ├─ Test Generator      (GPT-4o mini)                │
│      └─ Documentation       (Gemini 2.5 Pro)             │
└───────────────────────────────────────────────────────────┘

```

### 2.2 Data Flow

```

1. User Request → API Gateway
2. Auth \& Rate Limit Check
3. Cost Budget Check
4. Orchestrator: Select Execution Pattern
├─ Sequential (new feature, complex dependencies)
├─ Parallel (independent backend/frontend work)
└─ Producer-Reviewer Loop (critical code)
5. Agent Execution
├─ Context Retrieval (RAG)
├─ Model Selection (Router)
├─ Execution (LLM Call)
└─ Validation (Schema + Custom)
6. Inter-Agent Communication (Codified Protocol)
7. Output Aggregation
8. Cost Tracking \& Logging
9. Response to User
```

---

## 3. Multi-Model Orchestration Strategy

### 3.1 Model Selection Matrix

| **Task Type**          | **Primary Model**       | **Fallback**        | **Reason**                           | **Cost/1M Tokens** |
|------------------------|-------------------------|---------------------|--------------------------------------|--------------------|
| **Planning/Analysis**  | Claude Sonnet 3.5       | GPT-4o              | Best reasoning, context understanding| $3.00 in / $15 out |
| **Architecture Design**| Claude Sonnet 3.5       | GPT-4o              | Multi-step planning, consistency     | $3.00 in / $15 out |
| **Backend (.NET/C#)**  | GPT-4o                  | Claude Sonnet       | Strong C# performance (92% HumanEval)| $2.50 in / $10 out |
| **Frontend (React/TS)**| GPT-4o mini             | GPT-4o              | Cost-effective, good TypeScript      | $0.15 in / $0.60 out|
| **Code Review**        | Claude Sonnet 3.5       | GPT-4o              | Multi-perspective analysis           | $3.00 in / $15 out |
| **Testing**            | GPT-4o mini             | GPT-4o              | Simple task, cost-effective          | $0.15 in / $0.60 out|
| **Documentation**      | Gemini 2.5 Pro          | GPT-4o              | 1M context window, cheap             | $1.25 in / $5 out  |
| **Research**           | Gemini 2.5 Pro          | Claude Sonnet       | Large context for existing code      | $1.25 in / $5 out  |

### 3.2 Routing Configuration

**Fajl:** `config/model_mapping_enhanced.yaml`

```yaml
version: "2.0"
default:
  model: gpt-4o-mini
  temperature: 0.0
  max_tokens: 4000
  timeout: 30

routing:
  phase:
    analyst:
      model: claude-3-5-sonnet
      temperature: 0.1
      max_tokens: 8000
      provider: anthropic
    
    architect:
      model: claude-3-5-sonnet
      temperature: 0.1
      max_tokens: 16000
      provider: anthropic
      consensus_mode: true  # Use 3 models for consensus
      consensus_models:
        - claude-3-5-sonnet
        - gpt-4o
        - gemini-2.5-pro
    
    implementer:
      model: gpt-4o
      temperature: 0.0
      max_tokens: 8000
      provider: openai
    
    tester:
      model: gpt-4o-mini
      temperature: 0.0
      max_tokens: 4000
      provider: openai

  specialty:
    backend:
      dotnet:
        model: gpt-4o
        temperature: 0.0
        provider: openai
      database:
        model: claude-3-5-sonnet
        temperature: 0.0
        provider: anthropic
      efcore:
        model: gpt-4o
        temperature: 0.0
        provider: openai
        context_aware: true  # Load existing DbContext
    
    frontend:
      react:
        model: gpt-4o-mini
        temperature: 0.0
        provider: openai
      typescript:
        model: gpt-4o-mini
        temperature: 0.0
        provider: openai
      css:
        model: gpt-4o-mini
        temperature: 0.0
        provider: openai
    
    review:
      code:
        model: claude-3-5-sonnet
        temperature: 0.0
        provider: anthropic
      security:
        model: claude-3-5-sonnet
        temperature: 0.0
        provider: anthropic
    
    documentation:
      technical:
        model: gemini-2.5-pro
        temperature: 0.2
        provider: google
        max_tokens: 32000
      research:
        model: gemini-2.5-pro
        temperature: 0.3
        provider: google

cost_limits:
  per_task: 0.50  # USD
  per_hour: 5.00
  per_day: 40.00
  alert_threshold: 0.80  # Alert at 80% of budget

optimization:
  enable_agentic_retrieval: true
  enable_codified_communication: true
  enable_context_truncation: true
  enable_minimal_context_passing: true
  parallel_execution: true
```


### 3.3 Provider Integration

**Fajl:** `core/llm_client_enhanced.py`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
import openai
import anthropic
import google.generativeai as genai

@dataclass
class LLMResponse:
    content: str
    model: str
    tokens_used: Dict[str, int]  # {input: X, output: Y}
    cost: float
    latency_ms: int
    provider: str

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, config: Dict[str, Any]) -> LLMResponse:
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
    
    async def generate(self, prompt: str, config: Dict[str, Any]) -> LLMResponse:
        start_time = time.time()
        
        response = await self.client.chat.completions.create(
            model=config["model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=config.get("temperature", 0.0),
            max_tokens=config.get("max_tokens", 4000)
        )
        
        latency = int((time.time() - start_time) * 1000)
        tokens = {
            "input": response.usage.prompt_tokens,
            "output": response.usage.completion_tokens
        }
        cost = self._calculate_cost(config["model"], tokens)
        
        return LLMResponse(
            content=response.choices.message.content,
            model=config["model"],
            tokens_used=tokens,
            cost=cost,
            latency_ms=latency,
            provider="openai"
        )
    
    def _calculate_cost(self, model: str, tokens: Dict[str, int]) -> float:
        # Pricing per 1M tokens
        prices = {
            "gpt-4o": {"input": 2.50, "output": 10.0},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60}
        }
        price = prices.get(model, prices["gpt-4o"])
        return (tokens["input"] / 1_000_000 * price["input"] + 
                tokens["output"] / 1_000_000 * price["output"])

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
    
    async def generate(self, prompt: str, config: Dict[str, Any]) -> LLMResponse:
        start_time = time.time()
        
        response = await self.client.messages.create(
            model=config["model"],
            max_tokens=config.get("max_tokens", 4000),
            temperature=config.get("temperature", 0.0),
            messages=[{"role": "user", "content": prompt}]
        )
        
        latency = int((time.time() - start_time) * 1000)
        tokens = {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
        cost = self._calculate_cost(config["model"], tokens)
        
        return LLMResponse(
            content=response.content.text,
            model=config```

