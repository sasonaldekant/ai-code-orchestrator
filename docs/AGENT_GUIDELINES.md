# AI Agent Implementation Guidelines & Rules

> **CRITICAL**: If this file is ingested with the tag `must-follow` (Tier 1), all AI Agents MUST adhere strictly to these guidelines. Violations will result in rejected code.

## 1. System Architecture & Tiers

The proprietary Knowledge Base is organized into 4 strict Tiers. You must respect this hierarchy when retrieving or implementing code.

### T1: Rules & Standards (High Priority)
*   **Content**: Architectural guidelines, coding standards, golden rules.
*   **Tags**: `must-follow`, `architecture`, `rules`.
*   **Usage**: ALWAYS load this first before starting any task.

### T2: Design Tokens & Assets
*   **Content**: Color palettes, typography, spacing variables, CSS utility classes.
*   **Tags**: `design-system`, `tokens`.
*   **Usage**: NEVER hardcode values (e.g., `#FFFFFF`, `16px`). ALWAYS use tokens (e.g., `--color-primary`, `--spacing-md`).

### T3: Core Components
*   **Content**: Reusable React components (`Button`, `Card`, `Modal`).
*   **Description**: These are the building blocks.
*   **Usage**: Do not reinvent the wheel. Check for existing components before creating new ones.

### T4: Backend Patterns
*   **Content**: API endpoints, database schemas, DTOs.
*   **Usage**: Follow established patterns for error handling and data validation.

---

## 2. The "Bridge Context" Protocol

The **"Bridge Context"** (or `bridge-context` tag) is a special mechanism for handling cross-domain dependencies.

*   **Definition**: Context that is critical for linking Frontend (T3) with Backend (T4) or Logic.
*   **When to Use**:
    *   When an API response structure dictates a Component's props.
    *   When a shared type definition is used across both stacks.
*   **Agent Behavior**: If you see the `bridge-context` tag, treat that information as **immutable ground truth** that bridges the gap between layers.

---

## 3. Strict Coding Standards

### Frontend (React/TypeScript)
1.  **Styling**:
    *   **Primary**: Vanilla CSS Modules or global `index.css` variables.
    *   **Tailwind**: ONLY if explicitly enabled in the project config.
    *   **Prohibited**: Inline styles (except for dynamic values).
2.  **Structure**:
    *   COMPONENTS must be small, focused, and composed.
    *   HOOKS should separate logic from view.
3.  **State Management**:
    *   Prefer local state -> Context -> Global Store (Zustand/Redux).
    *   Minimize prop drilling (max 2 levels).

### Backend (Python/FastAPI)
1.  **Typing**: Pydantic models for ALL request/response bodies.
2.  **Async**: All I/O bound operations must be `async`.
3.  **Error Handling**: Use `HTTPException` with clear error codes.

---

## 4. Documentation Requirements

Every new component or major module MUST have a corresponding `DOCS.md` or TSDoc block.

*   **Props**: Document strict types.
*   **Usage**: Provide at least one example usage.
*   **Edge Cases**: Document null states or error states.

---

## 5. Workflow for Agents

1.  **Retrieve Context**: Query T1 (Rules) and relevant T3 (Components).
2.  **Plan**: Outline the changes.
3.  **Check Bridge**: Verify if any T4 (Backend) changes affect T3.
4.  **Implement**: Write code.
5.  **Verify**: Ensure no "magic numbers" or hardcoded strings.

> **Final Rule**: If you are unsure, defaults to the **Existing Pattern** found in the codebase. Consistency > Novelty.
