---
title: Design Token System
type: reference
category: foundation
version: 1.0.0
last_updated: 2026-02-13
---

# DynUI Design Token System

> **Complete reference for all design tokens**
> **Location**: `packages/design-tokens/styles/foundations/`

## 🎯 3-Layer Architecture

### Overview

```
Layer 1: Foundation Tokens (Global, Immutable)
    ↓ references
Layer 2: Component Tokens (Local, with fallbacks)
    ↓ references  
Layer 3: Theme Overrides (Context-based)
```

### Layer 1: Foundation Tokens

**Scope**: Global `:root`
**Mutability**: Immutable (hardcoded values)
**Location**: `packages/design-tokens/styles/foundations/*.css`

```css
:root {
  /* Hardcoded values - no var() references */
  --dyn-color-primary: #2563eb;
  --dyn-spacing-sm: 8px;
  --dyn-border-radius-md: 8px;
}
```

### Layer 2: Component Tokens

**Scope**: Component `:root` (in `.module.css`)
**Mutability**: Mutable via 3-level fallback
**Pattern**: `var(--component-specific, var(--semantic, hardcoded))`

```css
/* In DynButton.module.css */
:root {
  --dyn-button-bg: var(
    --dyn-button-root-backgroundColor,    /* Component override */
    var(--dyn-theme-primary, #2563eb)     /* Semantic + fallback */
  );
}

.root {
  background-color: var(--dyn-button-bg);
}
```

### Layer 3: Theme Overrides

**Scope**: Media queries, data attributes
**Mutability**: Override Layer 1 tokens only
**Propagation**: Automatic to Layer 2

```css
/* Dark mode overrides */
@media (prefers-color-scheme: dark) {
  :root {
    --dyn-color-primary: #3b82f6;  /* Components auto-update */
    --dyn-color-background: #0f172a;
  }
}
```

## 🎨 Color Tokens

### Primitive Colors

```css
/* Neutrals */
--dyn-color-white: #ffffff;
--dyn-color-black: #000000;

/* Backgrounds */
--dyn-color-background: #ffffff;
--dyn-color-background-secondary: #f8fafc;
--dyn-color-background-hover: #f1f5f9;
--dyn-color-background-selected: #e2e8f0;

/* Surfaces */
--dyn-color-surface: #ffffff;
--dyn-color-surface-subtle: #f3f4f6;
--dyn-color-surface-muted: #e2e8f0;
--dyn-color-surface-disabled: #f1f5f9;
--dyn-color-surface-readonly: #f9fafb;
```

### Text Colors

```css
--dyn-color-text-primary: #111827;
--dyn-color-text-secondary: #475569;
--dyn-color-text-tertiary: #64748b;
--dyn-color-text-disabled: #94a3b8;
--dyn-color-text-placeholder: #94a3b8;
--dyn-color-text-inverse: #f8fafc;
```

### Border Colors

```css
--dyn-color-border: #d0d5dd;
--dyn-color-border-light: #e2e8f0;
--dyn-color-border-subtle: rgba(15, 23, 42, 0.08);
--dyn-color-border-hover: #94a3b8;
--dyn-color-border-disabled: #e2e8f0;
```

### Brand Colors

```css
/* Primary (Blue) */
--dyn-color-primary: #2563eb;
--dyn-color-primary-hover: #1d4ed8;
--dyn-color-primary-active: #1e40af;
--dyn-color-primary-light: #60a5fa;
--dyn-color-primary-dark: #1e3a8a;
--dyn-color-primary-contrast: #ffffff;
--dyn-color-primary-alpha: rgba(37, 99, 235, 0.16);
```

### Status Colors

```css
/* Success (Green) */
--dyn-color-success: #10b981;
--dyn-color-success-hover: #059669;
--dyn-color-success-light: #6ee7b7;
--dyn-color-success-dark: #047857;
--dyn-color-success-contrast: #ffffff;
--dyn-color-success-alpha: rgba(16, 185, 129, 0.16);

/* Warning (Orange) */
--dyn-color-warning: #f59e0b;
--dyn-color-warning-hover: #d97706;
--dyn-color-warning-light: #fcd34d;
--dyn-color-warning-dark: #b45309;
--dyn-color-warning-contrast: #ffffff;
--dyn-color-warning-alpha: rgba(245, 158, 11, 0.16);

/* Info (Sky) */
--dyn-color-info: #0ea5e9;
--dyn-color-info-hover: #0284c7;
--dyn-color-info-light: #38bdf8;
--dyn-color-info-dark: #0369a1;
--dyn-color-info-contrast: #ffffff;
--dyn-color-info-alpha: rgba(14, 165, 233, 0.16);

/* Error/Danger (Red) */
--dyn-color-error: #ef4444;
--dyn-color-error-hover: #dc2626;
--dyn-color-error-light: #fca5a5;
--dyn-color-error-dark: #991b1b;
--dyn-color-error-contrast: #ffffff;
--dyn-color-error-alpha: rgba(239, 68, 68, 0.16);

--dyn-color-danger: #dc2626;
--dyn-color-danger-hover: #b91c1c;
--dyn-color-danger-active: #991b1b;
--dyn-color-danger-light: #fecaca;
--dyn-color-danger-dark: #7f1d1d;
--dyn-color-danger-contrast: #ffffff;
--dyn-color-danger-alpha: rgba(220, 38, 38, 0.16);
```

### Focus States

```css
--dyn-color-focus-ring: rgba(37, 99, 235, 0.35);
```

## 📏 Spacing Tokens

```css
/* T-shirt sizing */
--dyn-spacing-none: 0;
--dyn-spacing-2xs: 2px;
--dyn-spacing-xs: 4px;     /* Label gap, cell padding */
--dyn-spacing-sm: 8px;     /* Grid gap, component spacing */
--dyn-spacing-md: 16px;    /* Section spacing */
--dyn-spacing-lg: 24px;    /* Large spacing */
--dyn-spacing-xl: 32px;    /* Extra large */
--dyn-spacing-2xl: 40px;   /* Container padding */
--dyn-spacing-3xl: 48px;   /* Page sections */
--dyn-spacing-4xl: 56px;   /* Hero sections */
```

### Spacing Usage Guide

| Token | Value | Common Use Cases |
|-------|-------|------------------|
| `none/0` | 0 | Reset spacing |
| `2xs` | 2px | Micro spacing, tight groups |
| `xs` | 4px | **Label gap, cell padding** |
| `sm` | 8px | **Grid gap, component spacing (DEFAULT)** |
| `md` | 16px | Section spacing, between groups |
| `lg` | 24px | Large sections |
| `xl` | 32px | Page margins |
| `2xl` | 40px | Container padding |
| `3xl` | 48px | Page sections |
| `4xl` | 56px | Hero/landing sections |

## 🔤 Typography Tokens

### Font Families

```css
--dyn-font-family-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--dyn-font-family-mono: 'Monaco', 'Courier New', monospace;
```

### Font Sizes

```css
--dyn-font-size-xs: 11px;
--dyn-font-size-sm: 12px;
--dyn-font-size-base: 14px;
--dyn-font-size-md: 14px;
--dyn-font-size-lg: 16px;
--dyn-font-size-xl: 18px;
--dyn-font-size-2xl: 20px;
--dyn-font-size-3xl: 24px;
--dyn-font-size-4xl: 30px;
```

### Font Weights

```css
--dyn-font-weight-normal: 400;
--dyn-font-weight-medium: 500;
--dyn-font-weight-semibold: 550;
--dyn-font-weight-bold: 600;
```

### Line Heights

```css
--dyn-line-height-tight: 1.2;
--dyn-line-height-normal: 1.5;
--dyn-line-height-relaxed: 1.75;
```

## 🔲 Border Tokens

### Border Radius

```css
--dyn-border-radius-none: 0;
--dyn-border-radius-sm: 4px;
--dyn-border-radius-md: 8px;
--dyn-border-radius-lg: 12px;
--dyn-border-radius-xl: 16px;
--dyn-border-radius-full: 9999px;
```

### Border Widths

```css
--dyn-border-width-thin: 1px;
--dyn-border-width-medium: 2px;
--dyn-border-width-thick: 4px;
```

## 📊 Sizing Tokens

### Component Heights

```css
/* Form controls */
--dyn-size-height-sm: 32px;
--dyn-size-height-md: 40px;
--dyn-size-height-lg: 48px;

/* Icons */
--dyn-size-icon-sm: 16px;
--dyn-size-icon-md: 20px;
--dyn-size-icon-lg: 24px;

/* Avatars */
--dyn-size-avatar-sm: 32px;
--dyn-size-avatar-md: 40px;
--dyn-size-avatar-lg: 48px;
--dyn-size-avatar-xl: 64px;
```

## ⏱️ Animation Tokens

### Durations

```css
--dyn-duration-instant: 0ms;
--dyn-duration-fast: 150ms;
--dyn-duration-normal: 250ms;
--dyn-duration-slow: 350ms;
--dyn-duration-slower: 500ms;
```

### Easing Functions

```css
--dyn-easing-standard: cubic-bezier(0.4, 0.0, 0.2, 1);
--dyn-easing-emphasized: cubic-bezier(0.0, 0.0, 0.2, 1);
--dyn-easing-decelerated: cubic-bezier(0.0, 0.0, 0.2, 1);
--dyn-easing-accelerated: cubic-bezier(0.4, 0.0, 1, 1);
```

## 🎭 Opacity Tokens

```css
--dyn-opacity-disabled: 0.4;
--dyn-opacity-hover: 0.8;
--dyn-opacity-subtle: 0.6;
--dyn-opacity-focus: 0.12;
```

## 📍 Z-Index Tokens

```css
--dyn-z-index-base: 0;
--dyn-z-index-dropdown: 1000;
--dyn-z-index-sticky: 1100;
--dyn-z-index-fixed: 1200;
--dyn-z-index-overlay: 1300;
--dyn-z-index-modal: 1400;
--dyn-z-index-popover: 1500;
--dyn-z-index-tooltip: 1600;
```

## 🌙 Dark Mode Overrides

```css
@media (prefers-color-scheme: dark) {
  :root {
    /* Backgrounds */
    --dyn-color-background: #0f172a;
    --dyn-color-background-secondary: #1e293b;
    --dyn-color-surface: #1a1f35;
    
    /* Text */
    --dyn-color-text-primary: #f1f5f9;
    --dyn-color-text-secondary: #cbd5f5;
    --dyn-color-text-tertiary: #a0aec0;
    
    /* Borders */
    --dyn-color-border: #334155;
    --dyn-color-border-light: #475569;
    
    /* Brand */
    --dyn-color-primary: #3b82f6;
    --dyn-color-primary-hover: #2563eb;
    
    /* Status */
    --dyn-color-success: #34d399;
    --dyn-color-warning: #fbbf24;
    --dyn-color-info: #38bdf8;
    --dyn-color-error: #f87171;
    --dyn-color-danger: #f87171;
  }
}
```

## 📝 Naming Convention

```
--dyn-[category]-[property]-[variant]
     │       │          │
   prefix  what it is  specific type
```

### Examples

```css
--dyn-color-primary          /* category: color, property: primary */
--dyn-color-primary-hover    /* + variant: hover */
--dyn-spacing-sm             /* category: spacing, property: sm */
--dyn-border-radius-md       /* category: border-radius, property: md */
```

## ⚙️ Usage in Components

### CSS Modules Pattern

```css
/* DynButton.module.css */
:root {
  /* Define component tokens with 3-level fallback */
  --dyn-button-bg: var(
    --dyn-button-root-backgroundColor,
    var(--dyn-theme-primary, #2563eb)
  );
  
  --dyn-button-padding-x: var(
    --dyn-button-root-paddingX,
    var(--dyn-spacing-md, 16px)
  );
  
  --dyn-button-border-radius: var(
    --dyn-button-root-borderRadius,
    var(--dyn-border-radius-md, 8px)
  );
}

.root {
  background-color: var(--dyn-button-bg);
  padding: 0 var(--dyn-button-padding-x);
  border-radius: var(--dyn-button-border-radius);
}

/* Size variants */
.sizeSm {
  height: var(--dyn-size-height-sm, 32px);
}

.sizeMd {
  height: var(--dyn-size-height-md, 40px);
}

.sizeLg {
  height: var(--dyn-size-height-lg, 48px);
}

/* Color variants */
.colorSuccess {
  --dyn-button-bg: var(--dyn-color-success, #10b981);
}

.colorDanger {
  --dyn-button-bg: var(--dyn-color-danger, #dc2626);
}
```

### Inline Styles Pattern

```tsx
// ✅ CORRECT - Use tokens
<DynBox 
  style={{
    backgroundColor: 'var(--dyn-color-surface)',
    padding: 'var(--dyn-spacing-md)',
    borderRadius: 'var(--dyn-border-radius-md)'
  }}
/>

// ❌ WRONG - Hardcoded values
<DynBox 
  style={{
    backgroundColor: '#ffffff',
    padding: '16px',
    borderRadius: '8px'
  }}
/>
```

## 🔍 Token Lookup Table

### Quick Reference

| Need | Use Token | Value |
|------|-----------|-------|
| Primary color | `--dyn-color-primary` | #2563eb |
| Background | `--dyn-color-background` | #ffffff |
| Text | `--dyn-color-text-primary` | #111827 |
| Border | `--dyn-color-border` | #d0d5dd |
| Grid gap | `--dyn-spacing-sm` | 8px |
| Padding | `--dyn-spacing-md` | 16px |
| Border radius | `--dyn-border-radius-md` | 8px |
| Input height (md) | `--dyn-size-height-md` | 40px |
| Transition | `--dyn-duration-normal` | 250ms |

## 🔗 Related Documentation

- [Styling Guide](04-STYLING_GUIDE.md) - How to apply tokens
- [Component Catalog](03-COMPONENT_CATALOG.md) - Components using these tokens
- [Code Examples](05-CODE_EXAMPLES.md) - Token usage in context

---

**Remember**: Never hardcode. Always use tokens with fallbacks.
