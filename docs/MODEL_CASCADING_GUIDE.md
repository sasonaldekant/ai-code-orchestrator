# AI Code Orchestrator: Model Cascading & Optimization Guide

This document details the new Model Cascading System introduced to optimize resource utilization and reduce API costs while maintaining high-quality code generation.

## 1. The 5-Tier Model Hierarchy

The orchestrator now routes tasks through a strict 5-tier hierarchy, always attempting to use the most cost-effective model capable of handling the current complexity.

| Tier | Name | Role | Models (Example) | Cost (approx.) |
| :--- | :--- | :--- | :--- | :--- |
| **0** | **Gate / Monitor** | Pre-validation, routing, error log analysis | `gemini-2.0-flash` | ~$0.10 / 1M |
| **1** | **Worker** | Simple code gen, unit tests, routine tasks | `gpt-4o-mini`, `claude-3-5-haiku` | ~$0.15 / 1M |
| **2** | **Standard** | Core logic, architectural decisions | `gpt-4o`, `sonar` | ~$2.50 / 1M |
| **3** | **Heavy Lifter** | Complex debugging, self-healing fixes | `claude-3-5-sonnet` | ~$3.00 / 1M |
| **4** | **Mega / Reasoning** | Massive context analysis (100k+ tokens) | `gemini-1.5-pro` | ~$1.25 / 1M |

### Escalation Logic
- **Complexity Check**: If a task is classified as "complex" by the Gate, it bumps to Tier 2/3.
- **Context Size**: If context > 100,000 tokens, it forces escalation to Tier 4 (Gemini 1.5 Pro).
- **Failure**: If a model fails or hallucinates (caught by Fact Checker), the system retries with a higher-tier or alternative provider.

## 2. New Components

### Prompt Gate (Tier 0)
Located at the very start of the pipeline.
- **Validates** user prompts for clarity.
- **Refines** vague requirements.
- **Classifies** complexity (`simple`, `medium`, `complex`).
- **Extracts** key technical dependencies.

### Fact Checker (Tier 0/1)
Runs before the main planning phase.
- Uses **Perplexity Sonar** (Tier 2-ish capability at lower cost or specific search ability) to verify libraries and APIs.
- Prevents "hallucinations" about non-existent packages.
- Caches verification results for 24 hours.

### Self-Healing Manager (Optimized)
Runs after Implementation phase.
- **Detection (Tier 0)**: Uses `gemini-2.0-flash` to parse build logs and find errors.
- **Fixing (Tier 3)**: Uses `claude-3-5-sonnet` only when an error is confirmed, generating precise patches.
- **Auto-Detection**: Automatically identifies project type (Python, Node/TS, .NET) and runs appropriate build commands.

### Caching Layer
Integrated into `LLMClientV2`.
- Caches deterministic responses (temperature=0) to disk.
- Reduces cost for repeated queries (e.g., "how to center a div", "check library availability").
- Default TTL: 24 hours.

## 3. Monitoring & Metrics

### Dashboard
A new "Cascade Optimization Stats" section is available in the **Admin Dashboard**.
- **Tier Usage**: Pie chart showing distribution of requests across Tiers.
- **Savings Estimate**: Real-time calculation of cost avoidance.

### API Endpoint
GET `/admin/cascade-metrics` returns raw usage data:
```json
{
  "tier_usage": {"0": 150, "1": 45, "2": 10, "3": 5, "4": 1},
  "total_requests": 211,
  "saved_cost_estimated": 12.50
}
```

## 4. Configuration

Edit `config/model_mapping_v2.yaml` to adjust the tiers and models.

```yaml
routing:
  phase:
    analyst:
      model: "gpt-4o-mini"  # Primary
      tier: 1
      cascade:
        - { model: "claude-3-5-sonnet", provider: "anthropic" } # Fallback
    architect:
      model: "claude-3-5-sonnet"
      tier: 3
```

## 5. Usage

The cascading system is **enabled by default** in `OrchestratorV2`.
To run a pipeline:
```python
orchestrator = OrchestratorV2()
result = await orchestrator.run_pipeline_adaptive(
    initial_requirements="Create a snake game in Python",
    strategy=ExecutionStrategy.ADAPTIVE
)
```
The system will automatically:
1. Validate prompt with Gemini Flash.
2. Fact-check "Python" and "pygame" (if inferred).
3. Plan and implement using Tier 1/2 models.
4. Auto-heal any syntax errors using Flash -> Sonnet loop.
