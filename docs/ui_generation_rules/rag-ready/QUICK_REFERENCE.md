---
title: Quick Reference
type: cheatsheet
category: reference
version: 1.1.0
last_updated: 2026-02-21
---

# DynUI Quick Reference

> **One-page cheat sheet for AI agents**

## ⚡ Import Pattern

```tsx
import { ComponentName } from '@dyn-ui/react';
```

## 🎯 Core Rules (MUST FOLLOW)

1. **NEVER hardcode** - Always use tokens
2. **3-level fallback** - `var(--component-override, var(--semantic, fallback))`
3. **Default size** - `md` (40px for forms)
4. **Default spacing** - `sm` (8px)
5. **Form width** - 100% by default

## 🎨 Essential Tokens

### Colors

```css
/* Brand */
--dyn-color-primary: #2563eb;
--dyn-color-success: #10b981;
--dyn-color-danger: #dc2626;
--dyn-color-warning: #f59e0b;
--dyn-color-info: #0ea5e9;

/* Surfaces */
--dyn-color-background: #ffffff;
--dyn-color-surface: #ffffff;
--dyn-color-text-primary: #111827;
--dyn-color-border: #d0d5dd;
```

### Spacing

```css
--dyn-spacing-xs: 4px; /* Label gap, cell padding */
--dyn-spacing-sm: 8px; /* Grid gap, DEFAULT */
--dyn-spacing-md: 16px; /* Section spacing */
--dyn-spacing-lg: 24px; /* Large spacing */
```

### Sizes

```css
--dyn-size-height-sm: 32px;
--dyn-size-height-md: 40px; /* DEFAULT */
--dyn-size-height-lg: 48px;
```

### Border Radius

```css
--dyn-border-radius-sm: 4px;
--dyn-border-radius-md: 8px; /* DEFAULT */
--dyn-border-radius-lg: 12px;
```

### Grid Span

```css
--dyn-grid-span-full: span 12; /* 1 per row */
--dyn-grid-span-half: span 6; /* 2 per row */
--dyn-grid-span-third: span 4; /* 3 per row */
--dyn-grid-span-quarter: span 3; /* 4 per row */
```

### Form Layout

```css
--dyn-form-maxWidth-standard: 720px;
--dyn-form-field-gap: 16px;
--dyn-form-section-gap: 48px;
--dyn-form-layout-columns: 12;
```

## 📦 Component Quick Ref

### Layout

```tsx
<DynBox gap="sm" padding="md" display="flex" align="center">
<DynFlex direction="row" justify="between" gap="sm">
<DynContainer maxWidth="lg" padding="md">
<DynStack direction="vertical" gap="sm">
<DynGrid columns={{ mobile: 1, desktop: 3 }} gap="md">
```

### Forms

```tsx
<DynButton color="primary" size="md" loading={false}>
<DynInput type="text" size="md" placeholder="..." error="...">
<DynSelect size="md" options={[...]}>
<DynCheckbox checked={true} color="primary">
<DynFieldContainer label="Name" required error="...">
```

### Display

```tsx
<DynAvatar src="..." size="md" badge={{ count: 5 }}>
<DynBadge color="success" size="sm">Active</DynBadge>
<DynProgress value={75} max={100}>
<DynToast message="Success!" type="success">
```

### Data

```tsx
<DynTable columns={[...]} data={[...]} size="md" striped hoverable>
<DynChart type="bar" data={[...]}>
```

### Advanced

```tsx
<DynModal open={true} onClose={() => {}} size="md" title="...">
<DynDialog open={true} title="..." actions={<>...</>}>
<DynDatePicker value={date} onChange={setDate}>
```

## 📝 Common Patterns

### Simple Form

```tsx
<DynBox gap="md" direction="vertical">
  <DynFieldContainer label="Email" required>
    <DynInput type="email" size="md" />
  </DynFieldContainer>
  <DynButton color="primary" size="md" type="submit">
    Submit
  </DynButton>
</DynBox>
```

### Card

```tsx
<DynBox
  padding="md"
  style={{
    backgroundColor: 'var(--dyn-color-surface)',
    borderRadius: 'var(--dyn-border-radius-md)',
    border: '1px solid var(--dyn-color-border)',
  }}
>
  Content
</DynBox>
```

### Flex Row

```tsx
<DynBox display="flex" align="center" gap="sm">
  <DynAvatar size="md" />
  <span>John Doe</span>
</DynBox>
```

### Grid Layout

```tsx
<DynGrid columns={{ mobile: 1, tablet: 2, desktop: 3 }} gap="md">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</DynGrid>
```

## 🔍 Size Scale

| Size | Form Height | Spacing | Use Case    |
| ---- | ----------- | ------- | ----------- |
| `sm` | 32px        | 8px     | Compact UI  |
| `md` | 40px        | 16px    | **Default** |
| `lg` | 48px        | 24px    | Prominent   |

## 🎨 Color Variants

| Variant   | Token                 | Hex     | Use           |
| --------- | --------------------- | ------- | ------------- |
| `primary` | `--dyn-color-primary` | #2563eb | Main actions  |
| `success` | `--dyn-color-success` | #10b981 | Positive      |
| `danger`  | `--dyn-color-danger`  | #dc2626 | Destructive   |
| `warning` | `--dyn-color-warning` | #f59e0b | Caution       |
| `info`    | `--dyn-color-info`    | #0ea5e9 | Informational |

## ❌ Common Mistakes

```tsx
// ❌ WRONG
<div style={{ color: '#2563eb', padding: '16px' }}>

// ✅ CORRECT
<DynBox style={{
  color: 'var(--dyn-color-primary)',
  padding: 'var(--dyn-spacing-md)'
}}>
```

```tsx
// ❌ WRONG - Hardcoded size
<DynButton style={{ height: '40px' }}>

// ✅ CORRECT - Use size prop
<DynButton size="md">
```

```css
/* ❌ WRONG - No fallback */
:root {
  --btn-bg: var(--dyn-color-primary);
}

/* ✅ CORRECT - 3-level fallback */
:root {
  --dyn-button-bg: var(
    --dyn-button-root-backgroundColor,
    var(--dyn-theme-primary, #2563eb)
  );
}
```

## 📖 Need More Info?

| Question          | Check Document                                     |
| ----------------- | -------------------------------------------------- |
| How do I...       | [01-QUICK_START.md](01-QUICK_START.md)             |
| What token for... | [02-DESIGN_TOKENS.md](02-DESIGN_TOKENS.md)         |
| Component API     | [03-COMPONENT_CATALOG.md](03-COMPONENT_CATALOG.md) |
| Styling pattern   | [04-STYLING_GUIDE.md](04-STYLING_GUIDE.md)         |
| Code example      | [05-CODE_EXAMPLES.md](05-CODE_EXAMPLES.md)         |

---

**Remember**: Token-first, always.
