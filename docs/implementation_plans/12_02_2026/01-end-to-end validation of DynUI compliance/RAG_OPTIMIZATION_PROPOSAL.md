# 🧠 RAG Optimization & Knowledge Integration Strategy

## 1. Executive Summary

To achieve "Antigravity-level" performance with the AI Code Orchestrator, we must shift the models from **guessing** component structures to **retrieving** authoritative definitions. 

The strategy focuses on two key pillars:
1.  **Deep Indexing of External Monorepo**: Directly ingesting the `dyn-ui-main-v01` source code into the vector database.
2.  **"Assembler" Mindset Enforcement**: Providing strict "Golden Rules" that force models to glue existing components rather than inventing new ones.

## 2. The Problem

Currently, the agents:
- **Hallucinate Imports**: `import { DynInput } from 'your-component-library'` (Generic placeholder).
- **Guess Props**: Inventing `variant="outlined"` when it might not exist.
- **Ignore Architecture**: Mixing `useState` with `react-hook-form` inappropriately.

This happens because they **do not see** the actual source code of `DynUI` during the reasoning phase.

## 3. The Solution: "Domain-Aware RAG"

### A. External Knowledge Ingestion
We will create a new pipeline to index the `dyn-ui-main-v01` repository, specifically:
- **Target**: `../dyn-ui-main-v01/packages/dyn-ui-react/src`
- **Extraction**:
  - **Component Names**: `DynInput`, `DynSelect`, `DynLayout`.
  - **Props Interfaces**: TypeScript definitions defining exactly what is allowed.
  - **JSDocs**: Descriptions of behavior.

### B. "Golden Rules" Context (`AI_CONTEXT.md`)
We will establish a strict "constitution" based on `COMPLETE_KNOWLEDGE_BASE.md`.

**1. Design Tokens (STRICT COMPLIANCE)**
- **Rule**: NEVER use hardcoded properties (e.g., `padding: 10px`).
- **Standard**: MUST use `var(--dyn-spacing-md, 0.75rem)`.
- **Pattern**: `--dyn-[component]-[property]-[state]`.
- **Layers**: Foundation -> Component -> Theme.

**2. Component Composition**
- **Contract of Space**: Components must not assume their width. Default to `width: auto` for actions, `width: 100%` for inputs.
- **Polymorphism**: `DynBox` supports `as` prop for semantic HTML.
  - Examples: `as="h2"`, `as="a"`, `as="section"`, `as="button"`.
  - **Rule**: Always use semantic tags instead of generic `div`s where possible.
- **DynBox Grid**:
  - Use `display="grid"` with `gridTemplateColumns="repeat(12, 1fr)"` for layouts.
  - Use `colSpan` with semantic values: `full` (12), `half` (6), `third` (4), `quarter` (3).
  - Example: `<DynBox colSpan="half" />`.

**3. "Assembler" Mindset**
- **Rule**: "Do not create basic UI components from scratch."
- **Stack**: `react-hook-form` + `zod` for forms.
- **Imports**: All UI imports must come from `@dyn-ui/react`.

## 4. Implementation Plan

### Phase 1: Knowledge Ingestion Scripts
- Create `scripts/ingest_dyn_ui.py`.
- Features:
  - Scans `../dyn-ui-main-v01`.
  - Parses TypeScript AST to extract component signatures.
  - **NEW**: Extracts Design Tokens from `packages/design-tokens`.
  - Generates specialized vector embeddings for "UI Components" and "Design Tokens".

### Phase 2: Context Manager Upgrade
- Update `core/context_manager_v3.py`.
- Logic:
  - If task involves "Frontend/UI":
    - Retrieve relevant DynUI components AND relevant Design Tokens.
    - Inject the "Golden Rules" section into the System Prompt.

### Phase 3: System Prompt Refinement
- Update prompts for `Analyst`, `Architect`, and `Implementation` agents.
- Add sections: `[EXTERNAL LIBRARY SPECS]`, `[PROJECT STANDARDS]`, and `[TOKEN SYSTEM]`.

## 5. Expected Outcome

| Feature | Before | After |
| :--- | :--- | :--- |
| **Imports** | `import ... from 'lib'` | `import { DynInput } from '@dyn-ui/react'` |
| **Props** | Hallucinated (`color="red"`) | Type-Safe (`variant="destructive"`) |
| **Style** | Custom CSS classes | Standardized Design Tokens (`token.color.primary`) |
| **Success Rate** | ~60% (Requires manual fix) | >90% (Run & Deploy) |

## 6. Next Steps

1.  **Approve this plan**.
2.  I will generate the `AI_CONTEXT.md` file immediately.
3.  I will write the ingestion script to index your local `dyn-ui-main-v01` folder.
