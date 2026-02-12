# AI Context & Golden Rules for DynUI

This document defines the STRICT rules for all AI agents working on the DynUI project. Failure to follow these rules will result in rejected code.

## 1. "Assembler" Mindset
- **Role**: You are an Assembler, not a Builder.
- **Rule**: Do NOT create basic UI components from scratch (e.g., `<button>`, `<input>`).
- **Action**: Always retrieval and use existing components from `@dyn-ui/react`.
- **Imports**: `import { DynButton, DynInput } from '@dyn-ui/react';` (or specific paths if within the monorepo).

## 2. Design Tokens (The 3-Layer Law)
**NEVER use hardcoded values (hex, px, rem) for styles.**

1.  **Layer 1: Foundations** (Global)
    - `var(--dyn-color-primary)`, `var(--dyn-spacing-md)`
2.  **Layer 2: Components** (Scoped)
    - `var(--dyn-button-bg)`
3.  **Layer 3: Themes** (Overrides)
    - Handled via CSS variables.

**Syntax**: `var(--token-name, fallback)`
**Example**: `padding: var(--dyn-spacing-md, 0.75rem);`

## 3. Component Composition Rules
- **Contract of Space**:
    - Action components (Buttons, Badges) -> `width: auto`.
    - Input components -> `width: 100%` (fill container).
- **Layout Locking**:
    - Fixed elements (Icons) -> `flex: none`.
    - Fluid text -> `flex: 1; min-width: 0;`.
- **Polymorphism**:
    - Use `as` prop for semantic HTML.
    - `<DynBox as="section">`, `<DynBox as="h2">`.
- **DynBox Grid System**:
    - Use `display="grid"` with `gridTemplateColumns="repeat(12, 1fr)"`.
    - Use `colSpan` with semantic values: `full` (12), `half` (6), `third` (4), `quarter` (3).
    - Example: `<DynBox colSpan="half">...</DynBox>`

## 4. Tech Stack Standards
- **Forms**: `react-hook-form` + `zod` schema validation.
- **State**: Prefer `react-hook-form` for form state over `useState`.
- **API**: Use generated API clients, do not `fetch` manually.

## 5. File Structure (If creating new components)
- `DynName.tsx`
- `DynName.types.ts`
- `DynName.module.css`
- `DynName.stories.tsx`
- `DynName.test.tsx`
- `index.ts`
