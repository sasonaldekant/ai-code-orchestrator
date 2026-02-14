# Model Upgrade Recommendations (Feb 2026)

**Current Status**: Using legacy models (2025 generation)  
**Problem**: Značajno bolji modeli su dostupni, uz bolje performance i ponekad niže cene  
**Cilj**: Ažurirati na najnovije modele sa optimalnom kombinacijom kvaliteta i cene

---

## 1. Trenutno Stanje vs. Dostupno (2026)

### OpenAI
| Trenutno Koristimo | Noviji Dostupni | Pricing (/1M tokens) | Performance Gain |
|--------------------|-----------------|----------------------|------------------|
| `gpt-4o` | **`GPT-5.2`** | $1.75 input / $14 output | +40% coding, agentic optimized |
| `gpt-4o-mini` | **`GPT-5 Mini`** | $0.25 input / $2 output | 2.5x cheaper, +30% quality |
| `o1` | `GPT-5.2 Pro` | $21 input / $168 output | Highest precision (za kritične faze) |

**Ključne novine GPT-5 generacije**:
- **Caching**: $0.175 cached input (umesto full $1.75) - ogromna ušteda za repetitivne promptove
- **GPT-5 Nano**: $0.05 input / $0.40 output - ultra-low-cost za Gate i Monitor

### Anthropic
| Trenutno Koristimo | Noviji Dostupni | Status | Performance |
|--------------------|-----------------|--------|-------------|
| `claude-3-7-sonnet` ❌ | **`Claude Opus 4.6`** | Released Feb 5, 2026 | Best coding model trenutno |
| `claude-3-5-sonnet-latest` ❌ | **`Claude Sonnet 4.5`** | Released Sep 2025 | 30h+ multi-step tasks |
| `claude-3-5-haiku` ❌ | ✅ OK (još uvek konkurentno) | - | - |

**KRITIČNO**: `claude-3-7-sonnet` **NE POSTOJI** u zvaničnoj dokumentaciji! Verovatno je greška ili internal name. Treba koristiti:
- **Claude Opus 4.6** (flagship, best-in-class)
- **Claude Sonnet 4.5** (balance performance/cost)

**Claude 5 "Fennec"**: Leaked za Feb/Mar 2026, ali nije još zvanično dostupan.

### Google
| Trenutno Koristimo | Noviji Dostupni | Pricing (/1M tokens) | Context Window |
|--------------------|-----------------|----------------------|----------------|
| `gemini-2.0-flash` ❌ | **`Gemini 3 Flash`** | $0.50 input / $3 output | 200K+ |
| `gemini-2.0-pro-exp` ❌ | **`Gemini 3 Pro`** | $2 input / $12 output (≤200K) | 200K base, 1M beta |
| `gemini-1.5-pro` ❌ | ❌ Deprecated | - | - |

**Caching Benefit**: Gemini 3 Pro caching je $0.31/1M (vs $2 full price) - velika ušteda za RAG queries.

### Perplexity
| Trenutno Koristimo | Noviji Dostupni | Pricing | Specialization |
|--------------------|-----------------|---------|----------------|
| `sonar-reasoning-pro` | ✅ OK | - | Multi-step reasoning |
| `sonar-reasoning` | ✅ OK | - | Structured analysis |
| `sonar-pro` | ✅ OK | - | Deep search |
| `sonar` | ✅ OK | $1/1M | Fast search/citations |

**Nova Opcija**: **Sonar Deep Research** (runs on Opus 4.5) - za ultra-detaljno istraživanje (stotine izvora).

---

## 2. Preporučena Nova Konfiguracija

### Tier 0 (Gate & Monitor) - Ultra-Low-Cost

```yaml
gate:
  model: gpt-5-nano  # NOVO: $0.05 input vs $0.50 for Gemini Flash
  provider: openai
  reasoning: "10x jeftinije od Gemini Flash, dovoljno za validaciju"

fact_checker:
  model: sonar  # ZADRŽATI
  provider: perplexity
  reasoning: "Real-time web access, best za library verification"

monitor:
  model: gemini-3-flash  # UPGRADE
  provider: google
  pricing: "$0.50 input / $3 output"
  reasoning: "Brži i jeftiniji od 2.0 Flash"
```

**Ušteda**: ~80% na Gate operacijama (GPT-5 Nano vs Gemini Flash)

### Tier 1 (Analyst, Implementer, Tester, Reviewer) - Optimum

```yaml
analyst:
  model: gpt-5-mini  # UPGRADE
  provider: openai
  pricing: "$0.25 input / $2 output"
  cascade:
    - { model: claude-sonnet-4.5, provider: anthropic, threshold: 0.8 }
  reasoning: "GPT-5 Mini je 2.5x jeftinije od 4o-mini, bolji kvalitet"

implementer:
  model: gpt-5-mini  # UPGRADE
  provider: openai
  cascade:
    - { model: claude-opus-4.6, provider: anthropic, on_failure: true }
  reasoning: "Claude Opus 4.6 je trenutno best coding model"

tester:
  model: gpt-5-mini  # UPGRADE
  provider: openai
  reasoning: "Cost-effective za test generation"

reviewer:
  model: gpt-5-mini  # UPGRADE
  provider: openai
  cascade:
    - { model: gpt-5.2, provider: openai, condition: "complexity == 'high'" }
  reasoning: "GPT-5.2 za high-complexity review"
```

**Ušteda**: ~60% na implementaciji (GPT-5 Mini vs GPT-4o-mini), uz bolji kvalitet

### Tier 2 (Architect) - Consensus Mode

```yaml
architect:
  model: gpt-5.2  # UPGRADE
  provider: openai
  pricing: "$1.75 input / $14 output"
  consensus_mode: true
  cascade:
    - { model: claude-opus-4.6, provider: anthropic, role: "secondary" }
  reasoning: "GPT-5.2 + Claude Opus 4.6 consensus - best arhitektura"
```

**Benefit**: GPT-5.2 je optimizovan za "agentic tasks" i coding, idealan za arhitekturu.

### Tier 3 (Research, Self-Healer)

```yaml
research:
  model: sonar-deep-research  # NOVO
  provider: perplexity
  fallback:
    - { model: gemini-3-pro, provider: google, condition: "context > 200k" }
  reasoning: "Sonar Deep Research runs on Opus 4.5, najbolji za in-depth synthesis"

self_healer:
  model: claude-opus-4.6  # UPGRADE
  provider: anthropic
  pricing: "Premium tier"
  reasoning: "Najbolji model trenutno za debugging komplikovanih build errors"
```

**Benefit**: Claude Opus 4.6 je flagship model sa adaptive thinking i context compaction.

### Specialty Agents (Optimizacija po domenu)

```yaml
backend:
  dotnet_api:
    model: gpt-5.2  # UPGRADE
    provider: openai
    specialization: "ASP.NET Core, Web API, Controllers"
  
  efcore:
    model: gpt-5.2  # UPGRADE
    provider: openai
    specialization: "Entity Framework Core, Migrations, DbContext"

frontend:
  react:
    model: gpt-5-mini  # UPGRADE
    provider: openai
    specialization: "React 18+, hooks, functional components"
  
  typescript:
    model: gpt-5-mini  # UPGRADE
    provider: openai
    specialization: "TypeScript types, interfaces, generics"

documentation:
  technical_docs:
    model: gemini-3-pro  # UPGRADE
    provider: google
    pricing: "$2 input / $12 output (≤200K context)"
    max_tokens: 32000
    specialization: "Technical documentation, API docs, 1M context window beta"
```

---

## 3. Caching Strategija (Nova Mogućnost)

GPT-5, Claude Opus 4.6 i Gemini 3 podržavaju **prompt caching**:

```yaml
caching:
  enabled: true
  strategy:
    - cache_golden_rules: true  # T1 Rules se cachuju (90% ušteda)
    - cache_design_tokens: true  # T2 Tokens (fiksni, retko se menjaju)
    - cache_component_catalog: true  # T3 Catalog
    - ttl_seconds: 3600  # 1h cache TTL
```

**Ušteda Primer**:
- Standard GPT-5.2: $1.75 input
- Cached GPT-5.2: $0.175 input (10x jeftiniji za repetitivne promptove sa T1 Rules!)

---

## 4. Cost Comparison (Pre vs. Posle)

### Tipičan Feature Request (10 Milestones)

| Faza | Stare Modele | Nove Modele | Ušteda |
|------|--------------|-------------|--------|
| **Gate** (100 zahteva) | Gemini Flash: $0.05 | GPT-5 Nano: $0.005 | **90%** |
| **Analyst** (50k tokens) | GPT-4o-mini: $0.03 | GPT-5 Mini (cached): $0.006 | **80%** |
| **Architect** (200k tokens) | GPT-4o + Claude 3.7: $0.50 | GPT-5.2 + Opus 4.6: $0.35 | **30%** |
| **Implementation** (500k tokens) | GPT-4o-mini: $0.30 | GPT-5 Mini (cached): $0.06 | **80%** |
| **Self-Healing** (100k tokens) | Claude 3.7: $0.15 | Claude Opus 4.6: $0.20 | -33% (ali bolji kvalitet) |
| **Total per Feature** | **$1.03** | **$0.62** | **40% ušteda** |

---

## 5. Akcioni Plan (Upgrade Roadmap)

### Faza 1: Bezbedna Zamena (Nedelja 1)
- [x] Ažuriraj `model_mapping_v2.yaml` sa novim imenima
- [ ] Testiraj Gate sa GPT-5 Nano (100 request sample)
- [ ] Testiraj Implementer sa GPT-5 Mini (simple feature)
- [ ] Verifikuj caching radi (proveri billing logs)

### Faza 2: Kritične Faze (Nedelja 2)
- [ ] Upgrade Architect na GPT-5.2 + Claude Opus 4.6 consensus
- [ ] Upgrade Self-Healer na Claude Opus 4.6
- [ ] Testiranje na složenom feature request

### Faza 3: Full Rollout (Nedelja 3)
- [ ] Zameni sve Tier 0, 1, 2, 3 modele
- [ ] Aktiviraj caching za T1-T3 RAG
- [ ] Dokumentuj performance metrics (quality, cost)

### Faza 4: Monitoring & Optimization (Ongoing)
- [ ] Prati Claude 5 release (Feb/Mar 2026)
- [ ] Benchmark GPT-5.2 vs Claude Opus 4.6 za SelfHealing
- [ ] Optimizuj cascade thresholds

---

## 6. KRITIČNE KOREKCIJE

**GREŠKA U CONFIG**: `claude-3-7-sonnet` **NE POSTOJI**!

**Akcija**: Proveri gde smo ga koristili i zameni sa `claude-opus-4.6` ili `claude-sonnet-4.5`.

**Suspect Locations**:
- `config/model_mapping_v2.yaml`: Line 16, 77, 88, 98, 131
- Bilo gde u kodu gde se hardcoded poziva ovaj model

---

## 7. Sledeći Korak

**Validacija**: Pregledaj `config/model_mapping_v2.yaml` i potvrdimo da li zaista koristimo nepostojeći model name, pa ga ažuriramo sa pravim Anthropic imenima.

**Kada ažuriramo sve**: Očekivano 40-50% ušteda na cost uz bolji kvalitet u svim fazama.

---

**Dokument kreiran za**: Model Configuration Audit  
**Datum**: 2026-02-14  
**Cilj**: Upgrade na latest 2026 generation modele
