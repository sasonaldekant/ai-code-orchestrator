# DynUI Agent Must-Follow Rules (Tier 1)

## 1. Component Discovery Protocol (The 4-Step Rule)
1.  **QUERY RAG Tier 3 FIRST**: "DynUI component [feature/requirement]"
2.  **IDENTIFY MATCH**: Find the component name and its `file_path` from metadata.
3.  **READ SOURCE**: Use `view_file` on the physical path returned (e.g., `packages/dyn-ui-react/src/components/...`).
4.  **USE EXACT TYPES**: Never guess props. Strictly follow the TypeScript interfaces found in the `.tsx` source code.

## 2. Token-First Implementation (No Hardcoding)
- ❌ **FORBIDDEN**: Using hex codes (`#FFFFFF`), pixels (`24px`), or direct colors.
- ✅ **REQUIRED**: Use DynUI Design Tokens (`var(--dyn-color-...)`).
- **Composition Rule**: If a specific style is needed but no high-level component exists, compose it using `DynBox`, `DynFlex`, or `DynStack` with appropriate tokens.

## 3. Hybrid Access Pattern Enforcement
- **RAG = Context & Discovery**: Use RAG to understand "what" exists and see Storybook examples.
- **FS = Truth & Implementation**: Use the File System to read the "actual" current state of the code.
- **Zero Hallucination Policy**: If RAG says a component exists but you cannot find the file, report it immediately. Do not invent a component.

## 4. Backend & Configuration Integration
- When dealing with dynamic UI, consult **Tier 4 RAG** for the API map.
- Read physical **Prisma models** (`prisma/schema.prisma`) to understand how component properties are persisted.
- Follow the **Controller patterns** found in `src/api/controllers` for all UI-to-Backend interactions.

## 5. Fallback Protocol
1.  If a specific `Dyn[Component]` is missing, use **Primitives**: `DynStack`, `DynFlex`, `DynBox`, `DynTypography`.
2.  If a complex UI is needed that isn't a single component, document it as a **Composition** in the Architect explanation.
3.  Always prefix native HTML tag usage with a "DYN-PROPOSAL" comment if it's absolutely unavoidable (rare).
