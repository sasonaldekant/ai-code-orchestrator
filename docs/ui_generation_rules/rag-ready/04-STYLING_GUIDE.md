---
title: Styling Guide
type: guide
category: foundation
version: 1.0.0
last_updated: 2026-02-13
---

# DynUI Styling Guide

> **How to customize and style DynUI components**

## 🎯 Core Principles

### 1. Token-First Approach

**Always use design tokens**, never hardcode values.

```css
/* ❌ WRONG */
.myButton {
  color: #2563eb;
  padding: 16px;
  border-radius: 8px;
}

/* ✅ CORRECT */
.myButton {
  color: var(--dyn-color-primary);
  padding: var(--dyn-spacing-md);
  border-radius: var(--dyn-border-radius-md);
}
```

### 2. 3-Level Fallback Pattern

Component tokens should use fallback chain:

```css
:root {
  --component-property: var(
    --component-override,           /* Level 1: Component override */
    var(--semantic-token, value)    /* Level 2: Semantic + fallback */
  );
}
```

### 3. CSS Modules

Use CSS Modules for component-scoped styles:

```tsx
// Component.module.css
:root {
  --dyn-mycomponent-bg: var(--dyn-color-surface, #ffffff);
}

.root {
  background-color: var(--dyn-mycomponent-bg);
}

// Component.tsx
import styles from './Component.module.css';

function MyComponent() {
  return <div className={styles.root}>Content</div>;
}
```

## 🎨 Customization Methods

### Method 1: CSS Variables (Recommended)

Override tokens at runtime:

```tsx
<DynButton
  style={{
    '--dyn-button-bg': 'var(--dyn-color-success)',
    '--dyn-button-padding-x': 'var(--dyn-spacing-lg)'
  } as CSSProperties}
>
  Custom Button
</DynButton>
```

### Method 2: className Prop

Add custom classes:

```tsx
// In your CSS
.customButton {
  background: linear-gradient(to right, #667eea, #764ba2);
}

// In component
<DynButton className="customButton">
  Gradient Button
</DynButton>
```

### Method 3: Inline Styles with Tokens

Direct styling with token variables:

```tsx
<DynBox
  style={{
    backgroundColor: 'var(--dyn-color-surface)',
    padding: 'var(--dyn-spacing-lg)',
    borderRadius: 'var(--dyn-border-radius-md)',
    border: '1px solid var(--dyn-color-border)'
  }}
>
  Content
</DynBox>
```

### Method 4: Theme Overrides

Global theme customization:

```css
/* global.css */
:root {
  /* Override foundation tokens */
  --dyn-color-primary: #8b5cf6;        /* Purple instead of blue */
  --dyn-spacing-sm: 12px;              /* Larger default gap */
  --dyn-border-radius-md: 12px;        /* More rounded */
}

/* Dark mode custom */
@media (prefers-color-scheme: dark) {
  :root {
    --dyn-color-primary: #a78bfa;
  }
}
```

## 📝 Common Styling Patterns

### Pattern 1: Card with Shadow

```tsx
<DynBox
  padding="md"
  style={{
    backgroundColor: 'var(--dyn-color-surface)',
    borderRadius: 'var(--dyn-border-radius-md)',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
  }}
>
  Card content
</DynBox>
```

### Pattern 2: Gradient Background

```css
/* CustomButton.module.css */
.gradientButton {
  background: linear-gradient(
    135deg,
    var(--dyn-color-primary),
    var(--dyn-color-primary-hover)
  );
  color: var(--dyn-color-primary-contrast);
}
```

```tsx
<DynButton className={styles.gradientButton}>
  Gradient Button
</DynButton>
```

### Pattern 3: Responsive Padding

```tsx
<DynBox
  style={{
    padding: 'var(--dyn-spacing-sm)'
  }}
  className="responsivePadding"
>
  Content
</DynBox>
```

```css
.responsivePadding {
  padding: var(--dyn-spacing-sm);
}

@media (min-width: 768px) {
  .responsivePadding {
    padding: var(--dyn-spacing-md);
  }
}

@media (min-width: 1024px) {
  .responsivePadding {
    padding: var(--dyn-spacing-lg);
  }
}
```

### Pattern 4: Status-Based Styling

```tsx
function StatusBadge({ status }: { status: 'active' | 'pending' | 'inactive' }) {
  const colorMap = {
    active: 'success',
    pending: 'warning',
    inactive: 'info'
  };
  
  return (
    <DynBadge color={colorMap[status]} size="sm">
      {status}
    </DynBadge>
  );
}
```

### Pattern 5: Hover Effects

```css
.hoverCard {
  transition: transform var(--dyn-duration-normal) var(--dyn-easing-standard),
              box-shadow var(--dyn-duration-normal) var(--dyn-easing-standard);
}

.hoverCard:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
```

## 🔧 Advanced Techniques

### Technique 1: Component Variants

```css
/* MyComponent.module.css */
:root {
  --mycomponent-bg: var(--dyn-color-surface);
  --mycomponent-text: var(--dyn-color-text-primary);
}

.root {
  background-color: var(--mycomponent-bg);
  color: var(--mycomponent-text);
}

/* Variant classes */
.variantPrimary {
  --mycomponent-bg: var(--dyn-color-primary);
  --mycomponent-text: var(--dyn-color-primary-contrast);
}

.variantSuccess {
  --mycomponent-bg: var(--dyn-color-success);
  --mycomponent-text: var(--dyn-color-success-contrast);
}
```

### Technique 2: Size Scaling

```css
:root {
  --mycomponent-size: 1;
}

.sizeSm {
  --mycomponent-size: 0.875;
}

.sizeLg {
  --mycomponent-size: 1.125;
}

.root {
  font-size: calc(var(--dyn-font-size-base) * var(--mycomponent-size));
  padding: calc(var(--dyn-spacing-sm) * var(--mycomponent-size));
}
```

### Technique 3: Dark Mode Aware Components

```tsx
function ThemeAwareComponent() {
  return (
    <DynBox
      style={{
        backgroundColor: 'var(--dyn-color-surface)',
        color: 'var(--dyn-color-text-primary)',
        border: '1px solid var(--dyn-color-border)'
      }}
    >
      {/* Automatically adapts to dark mode */}
    </DynBox>
  );
}
```

## ⚠️ Common Mistakes

### Mistake 1: Hardcoded Values

```tsx
// ❌ WRONG
<div style={{ color: '#2563eb', padding: '16px' }}>

// ✅ CORRECT
<DynBox 
  style={{ 
    color: 'var(--dyn-color-primary)',
    padding: 'var(--dyn-spacing-md)'
  }}
>
```

### Mistake 2: Inline RGB/HEX Colors

```css
/* ❌ WRONG */
.error {
  background-color: #ef4444;
}

/* ✅ CORRECT */
.error {
  background-color: var(--dyn-color-error);
}
```

### Mistake 3: Magic Numbers

```css
/* ❌ WRONG */
.container {
  padding: 23px;
  gap: 17px;
}

/* ✅ CORRECT */
.container {
  padding: var(--dyn-spacing-lg);  /* 24px */
  gap: var(--dyn-spacing-md);      /* 16px */
}
```

### Mistake 4: Breaking 3-Level Pattern

```css
/* ❌ WRONG - Only 1 level */
:root {
  --dyn-button-bg: #2563eb;
}

/* ✅ CORRECT - 3-level fallback */
:root {
  --dyn-button-bg: var(
    --dyn-button-root-backgroundColor,
    var(--dyn-theme-primary, #2563eb)
  );
}
```

## 📋 Style Checklist

Before committing styles:

- [ ] All colors use `--dyn-color-*` tokens
- [ ] All spacing uses `--dyn-spacing-*` tokens
- [ ] All border radius uses `--dyn-border-radius-*` tokens
- [ ] All component tokens use 3-level fallback
- [ ] No hardcoded pixel values (except as final fallback)
- [ ] CSS class names use camelCase
- [ ] Dark mode tested and working
- [ ] Responsive behavior verified

## 🔗 Related Documentation

- [Design Tokens](02-DESIGN_TOKENS.md) - Complete token reference
- [Quick Start](01-QUICK_START.md) - Basic usage
- [Code Examples](05-CODE_EXAMPLES.md) - Real-world patterns

---

**Remember**: Tokens first, always.
