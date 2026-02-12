# Component Base Layer - Design Tokens

**Component-level reusable token patterns for the DynUI design system.**

---

## Overview

This directory contains **component base CSS files** that define reusable token patterns for groups of similar components. These files sit between the foundation layer and component-specific styles, providing a consistent token vocabulary.

### Token Hierarchy

```
Foundation Layer     →  Component Base Layer  →  Component Specific Layer
(colors.css, etc.)      (button-like.css, etc.)   (DynButton.module.css)
--dyn-color-primary     --dyn-button-bg           background-color: var(--dyn-button-bg)
```

---

## Files

### 1. `button-like.css`
**Used by:** DynButton, DynIconButton, and similar button-style components

**Tokens defined:**
- Background: `--dyn-button-bg`, `--dyn-button-bg-hover`, `--dyn-button-bg-active`
- Border: `--dyn-button-border`, `--dyn-button-border-hover`
- Text: `--dyn-button-color`, `--dyn-button-color-hover`
- Sizing: `--dyn-button-min-height`, `--dyn-button-padding-y`, `--dyn-button-padding-x`
- Typography: `--dyn-button-font-size`, `--dyn-button-font-weight`
- Effects: `--dyn-button-border-radius`, `--dyn-button-shadow-focus`

**Example usage in component:**
```css
/* DynButton.module.css */
.root {
  background-color: var(--dyn-button-bg);
  border: 1px solid var(--dyn-button-border);
  color: var(--dyn-button-color);
  padding: var(--dyn-button-padding-y) var(--dyn-button-padding-x);
  min-height: var(--dyn-button-min-height);
}

.root:hover {
  background-color: var(--dyn-button-bg-hover);
}
```

---

### 2. `input-like.css`
**Used by:** DynInput, DynTextArea, DynSelect, DynDatePicker, DynCheckbox

**Tokens defined:**
- Background: `--dyn-input-bg`, `--dyn-input-bg-hover`, `--dyn-input-bg-focus`, `--dyn-input-bg-disabled`
- Border: `--dyn-input-border`, `--dyn-input-border-hover`, `--dyn-input-border-focus`, `--dyn-input-border-error`
- Text: `--dyn-input-color`, `--dyn-input-placeholder`, `--dyn-input-color-disabled`
- Focus: `--dyn-input-focus-ring`, `--dyn-input-focus-ring-error`
- Sizing: `--dyn-input-height`, `--dyn-input-padding-y`, `--dyn-input-padding-x`
- Typography: `--dyn-input-font-size`, `--dyn-input-font-family`

**Example usage in component:**
```css
/* DynInput.module.css */
.input {
  background-color: var(--dyn-input-bg);
  border: 1px solid var(--dyn-input-border);
  color: var(--dyn-input-color);
  padding: var(--dyn-input-padding-y) var(--dyn-input-padding-x);
  height: var(--dyn-input-height);
}

.input:focus {
  border-color: var(--dyn-input-border-focus);
  box-shadow: var(--dyn-input-focus-ring);
}

.input::placeholder {
  color: var(--dyn-input-placeholder);
}
```

---

### 3. `layout.css`
**Used by:** DynFlex, DynGrid, DynStack, DynBox, DynContainer

**Tokens defined:**
- Spacing: `--dyn-layout-gap`, `--dyn-layout-padding` (with size variants: xs, sm, md, lg, xl)
- Container: `--dyn-container-max-width` (with breakpoint variants: sm, md, lg, xl, 2xl)
- Grid: `--dyn-grid-columns`, `--dyn-grid-gutter`
- Background: `--dyn-layout-bg`, `--dyn-layout-bg-surface`
- Border: `--dyn-layout-border-radius`

**Example usage in component:**
```css
/* DynFlex.module.css */
.root {
  display: flex;
  gap: var(--dyn-layout-gap);
}

.gapSmall {
  gap: var(--dyn-layout-gap-sm);
}

/* DynContainer.module.css */
.root {
  max-width: var(--dyn-container-max-width);
  padding: var(--dyn-layout-padding);
}
```

---

### 4. `table-like.css`
**Used by:** DynTable, DynListView, DynTreeView

**Tokens defined:**
- Header: `--dyn-table-header-bg-color`, `--dyn-table-header-text-color`, `--dyn-table-header-border-color`
- Row: `--dyn-table-row-bg-color`, `--dyn-table-row-hover-bg-color`, `--dyn-table-row-selected-bg-color`
- Border: `--dyn-table-border-color`, `--dyn-table-border-width`
- Spacing: `--dyn-table-padding` (with size variants: sm, lg)
- Typography: `--dyn-table-font-size`, `--dyn-table-header-font-weight`
- Checkbox: `--dyn-table-checkbox-size`

**Example usage in component:**
```css
/* DynTable.module.css */
.header {
  background-color: var(--dyn-table-header-bg-color);
  color: var(--dyn-table-header-text-color);
  font-weight: var(--dyn-table-header-font-weight);
  padding: var(--dyn-table-padding);
}

.row {
  background-color: var(--dyn-table-row-bg-color);
}

.row:hover {
  background-color: var(--dyn-table-row-hover-bg-color);
}

.rowSelected {
  background-color: var(--dyn-table-row-selected-bg-color);
}
```

---

### 5. `interactive-states.css`
**Used by:** All interactive components

**Tokens defined:**
- Hover: `--dyn-state-hover-opacity`, `--dyn-state-hover-bg`
- Focus: `--dyn-state-focus-ring-width`, `--dyn-state-focus-ring-color`, `--dyn-state-focus-outline`
- Active: `--dyn-state-active-opacity`, `--dyn-state-active-bg`
- Disabled: `--dyn-state-disabled-opacity`, `--dyn-state-disabled-cursor`
- Selected: `--dyn-state-selected-bg`, `--dyn-state-selected-color`
- Loading: `--dyn-state-loading-opacity`
- Error/Success/Warning: Status state colors and backgrounds

**Example usage in component:**
```css
/* Any component with interactive states */
.item:hover {
  background-color: var(--dyn-state-hover-bg);
}

.item:focus-visible {
  outline: var(--dyn-state-focus-outline);
  outline-offset: var(--dyn-state-focus-ring-offset);
}

.itemSelected {
  background-color: var(--dyn-state-selected-bg);
  color: var(--dyn-state-selected-color);
}

.itemDisabled {
  opacity: var(--dyn-state-disabled-opacity);
  cursor: var(--dyn-state-disabled-cursor);
}
```

---

## Usage Guidelines

### 1. Import Order

Always import component base layer **after** foundation layer:

```css
/* Application root CSS */
@import '@dyn/design-tokens/styles/foundations/index.css';  /* 1. Foundation */
@import '@dyn/design-tokens/styles/components/index.css';   /* 2. Component Base */
@import '@dyn/design-tokens/styles/themes/dark.css';        /* 3. Theme (optional) */
```

### 2. Token Reference Pattern

Component CSS modules should **reference component base tokens**, not foundation tokens directly:

**✅ Correct:**
```css
.root {
  background-color: var(--dyn-button-bg);  /* References component token */
}
```

**❌ Incorrect:**
```css
.root {
  background-color: var(--dyn-color-primary);  /* Skips component layer */
}
```

### 3. Token Customization

If a component needs a unique value, define it in the component CSS:

```css
/* DynSpecialButton.module.css */
.root {
  /* Override component token for this specific component */
  --dyn-button-bg: var(--dyn-color-success);
  
  /* Use the token */
  background-color: var(--dyn-button-bg);
}
```

### 4. State Overrides

Update token values for states without repeating properties:

**✅ Correct:**
```css
.root {
  --dyn-button-bg: var(--dyn-color-primary);
  background-color: var(--dyn-button-bg);
}

.root:hover {
  --dyn-button-bg: var(--dyn-color-primary-hover);  /* Update token only */
}
```

**❌ Incorrect:**
```css
.root {
  background-color: var(--dyn-color-primary);
}

.root:hover {
  background-color: var(--dyn-color-primary-hover);  /* Repeats property */
}
```

---

## Benefits

### 1. Consistency
All button-like components share the same token vocabulary, ensuring visual consistency.

### 2. Maintainability
Changing `--dyn-button-bg` updates all button-style components automatically.

### 3. Scalability
New components can adopt existing patterns without redefining tokens.

### 4. Theme Support
Dark mode and other themes can override component tokens centrally.

### 5. DRY Principle
No token duplication across components - single source of truth.

---

## Dark Mode & Accessibility

All component base files include:

1. **Dark mode overrides** via `@media (prefers-color-scheme: dark)`
2. **High contrast support** via `@media (prefers-contrast: more)`
3. **Reduced motion support** via `@media (prefers-reduced-motion: reduce)`

These are automatically applied - no JavaScript required.

---

## Adding New Component Tokens

When creating a new component type:

1. Determine if it fits an existing pattern (button-like, input-like, etc.)
2. If yes, use existing tokens
3. If no, consider creating a new component base file:
   - Name: `<pattern>-like.css` (e.g., `card-like.css`)
   - Define tokens: `--dyn-<component>-<property>`
   - Add to `index.css`
   - Document in this README

---

## Questions?

Refer to:
- **Design Tokens Standard:** `/docs/05_Design_Tokens_Standard_v1.md`
- **Phase 2 Status:** `/docs/PHASE2_IMPLEMENTATION_STATUS.md`
- **Foundation Layer:** `/packages/design-tokens/styles/foundations/`

---

**Last Updated:** December 20, 2025  
**Version:** 1.0  
**Maintainer:** Design System Team
