# AI Code Orchestrator v4.0 - Bleeding Edge Roadmap

**Status:** Planning / Experimental
**Goal:** Push RAG performance to State-of-the-Art (SOTA) using Agentic & Graph-based techniques.

---

## 🏗️ Core Philosophy: Additive Enhancement

To preserve the stability of the v3.0 Enterprise release, all v4.0 features will be implemented as **additive modules** or wrapped in **Feature Flags**.

- **No breaking changes** to `Core/ChunkingEngine`.
- **No breaking changes** to `API/AdminRoutes`.
- New features default to `OFF` until explicitly enabled.

---

## 1. Advanced Retrieval (Re-ranking)

**Problem:** Cosine similarity retrieves "most similar looking" text, not necessarily "most relevant answer".
**Solution:** Implement a two-stage retrieval process.

### 1.1 `CrossEncoderReranker`

- **Component:** `rag/reranker.py`
- **Model:** `BAAI/bge-reranker-base` (or similar high-performance cross-encoder).
- **Logic:**
  1. Retrieve Top-50 via fast Cosine Similarity (`ChromaVectorStore`).
  2. Pass `(Query, Document)` pairs to Cross-Encoder.
  3. Re-sort based on relevance score.
  4. Return Top-10 to LLM.

### 1.2 Contextual Caching (Anthropic Pattern)

- **Component:** `core/cache_manager.py`
- **Logic:** Cache the "pre-filled" prompt context for massive codebases found in `VectorStore`.
- **Benefit:** Reduces Time-To-First-Token (TTFT) and cost for repetitive queries.

---

## 2. GraphRAG (Knowledge Graph)

**Problem:** Standard RAG misses implicit connections (e.g., `Class A` imports `Class B` but doesn't mention it by name in the chunk).
**Solution:** Build a dependency graph alongside the vector index.

### 2.1 `GraphIngester`

- **Component:** `core/graph/ingester.py`
- **Logic:**
  1. Parse code with `tree-sitter`.
  2. Extract nodes: `Function`, `Class`, `Module`.
  3. Extract edges: `Imports`, `Inherits`, `Calls`.
  4. Store in `NetworkX` (in-memory) or `Neo4j` (optional external).

### 2.2 `GraphRetriever`

- **Component:** `core/graph/retriever.py`
- **Logic:**
  - When retrieving `Chunk X`, check Graph for neighbors.
  - Automatically fetch "parents" (classes) and "children" (callees).
  - Inject this "Structural Context" into the LLM prompt.

---

## 3. Agentic Retrieval

**Problem:** "One-shot" retrieval often misses data if the user's query is vague.
**Solution:** Give the LLM tools to "investigate" the codebase.

### 3.1 `RetrievalAgent`

- **Component:** `agents/specialist_agents/retrieval_agent.py`
- **Tools:**
  - `search_code(query)`
  - `go_to_definition(symbol)`
  - `find_usage(symbol)`
- **Loop:**
  - "I need to find `PaymentService`. Searching..."
  - "Found `PaymentService`. Now looking for `ProcessPayment` method..."
  - "Found it. Returning context."

---

## 4. Implementation Plan (Phased)

### Phase 11: The Re-ranker (High Impact, Low Risk)

- [ ] Create `rag/reranker.py`
- [ ] Update `VectorStore.search` to accept `use_reranker=True`
- [ ] Add "Re-ranking" toggle in Admin Panel (Model Config)

### Phase 12: Knowledge Graph (High Effort, High Reward)

- [ ] Create `core/graph/` module
- [ ] Implement `GraphIngester` (Tree-sitter integration)
- [ ] Visualize Graph in Admin Panel (`react-force-graph`)

### Phase 13: The Investigator (Agentic)

- [ ] Create `RetrievalAgent`
- [ ] Expose as a "Deep Search" mode in Chat Interface

---

## 5. Success Metrics (v4.0)

| Metric                  | v3.0 (Current) | v4.0 (Target)   |
| :---------------------- | :------------- | :-------------- |
| **Recall@10**           | ~75%           | **>95%**        |
| **Context Precision**   | ~60%           | **>85%**        |
| **Multi-hop Reasoning** | ❌ Fail        | ✅ Pass         |
| **Answer Latency**      | ~2s            | ~3s (trade-off) |

---

## 6. Phase 16: Autonomous Evolution & Connectivity (New)

**Goal:** Move from "Assistant" to "Autonomous Partner" and expand access points.

### 16.1 Autonomous Self-Healing ("The Auto-Fixer")

- **Concept:** Agent that detects errors, investigates root causes, and applies fixes _without_ human intervention (until review).
- **Component:** `agents/specialist_agents/repair_agent.py`
- **Workflow:**
  1. **Monitor:** Listens to `Verification` phase or `TestRunner`.
  2. **Investigate:** Uses `RetrievalAgent` to find the bug.
  3. **Fix:** Uses `RefactoringAgent` to apply the patch.
  4. **Verify:** Re-runs the specific test case.

### 16.2 Multi-Modal Capabilities (Vision)

- **Concept:** Give the Orchestrator "eyes" to understand UI screenshots and diagrams.
- **Component:** `core/vision_manager.py`
- **Features:**
  - `POST /analyze-image`: Convert wireframe -> React Code.
  - `POST /audit-ui`: Check screenshot against design guidelines.

### 16.3 IDE Bridge (API)

- **Concept:** Expose a streamlined API specifically for VS Code / JetBrains extensions to hook into.
- **Features:**
  - WebSocket for real-time thought streaming.
  - `POST /ide/fix-selection`: Context-aware fix for highlighted code.
  - `POST /ide/explain`: Context-aware explanation.

## 7. Phase 17: Cognitive Memory & System Cortex (Current)

**Goal:** Transform the Orchestrator from a "Stateless Executor" to a "Learner" with a unified Tool Registry.

### 17.1 The API Registry ("The Cortex")

- **Concept:** A centralized registry of all capabilities (Vision, IDE actions, RAG options) with semantic descriptions.
- **Goal:** Allow the Orchestrator to dynamically select the right "Skill" or "API" based on intent, rather than hardcoded logic.
- **Component:** `core/registry.py`, `core/router.py`

### 17.2 Episodic Memory (User Preferences)

- **Concept:** Store and retrieve User Preferences across sessions.
- **Example:** "Always use TypeScript interfaces", "Prefer functional components".
- **Component:** `core/memory/user_preferences.py` (Vector-backed)

### 17.3 Experience Database (Self-Correction)

- **Concept:** Learn from past mistakes.
- **Logic:** When `RepairAgent` successfully fixes a bug, store the `(Error Pattern -> Fix Strategy)` tuple. Retrieve this when encountering similar errors.
- **Component:** `core/memory/experience_db.py`
