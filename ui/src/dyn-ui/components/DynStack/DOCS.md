# DynStack Documentation

## 📌 Overview

**Category:** Layout
**Status:** Stable

`DynStack` is a fundamental layout utility used to arrange child elements in a vertical or horizontal line with consistent spacing. It abstracts Flexbox and provides a simple API for common distribution patterns.

## 🛠 Usage

### Basic Vertical Stack (Form Layout)

```tsx
import { DynStack } from '@dyn-ui/react';

function MyForm() {
  return (
    <DynStack gap="lg">
      <DynInput label="First Name" />
      <DynInput label="Last Name" />
      <DynButton type="primary">Save</DynButton>
    </DynStack>
  );
}
```

### Horizontal Toolbar with Alignment

```tsx
<DynStack direction="horizontal" gap="sm" align="center" justify="between">
  <h1>Page Title</h1>
  <DynStack direction="horizontal" gap="xs">
    <DynButton>Cancel</DynButton>
    <DynButton kind="primary">Save</DynButton>
  </DynStack>
</DynStack>
```

### Polymorphic Element

```tsx
<DynStack as="nav" direction="vertical" gap="none">
  <a href="/">Home</a>
  <a href="/about">About</a>
</DynStack>
```

## ⚙️ Properties (API)

### Quick Reference

| Prop        | Type                | Default      | Description                             | Required |
| :---------- | :------------------ | :----------- | :-------------------------------------- | :------: |
| `direction` | `DynStackDirection` | `'vertical'` | Primary axis flow.                      |    No    |
| `gap`       | `DynStackGap`       | `'md'`       | Spacing between items.                  |    No    |
| `align`     | `DynStackAlign`     | `'stretch'`  | Cross-axis item alignment.              |    No    |
| `justify`   | `DynStackJustify`   | `'start'`    | Main-axis item distribution.            |    No    |
| `wrap`      | `boolean`           | `false`      | Allow items to wrap to next row/column. |    No    |
| `flex`      | `string \| number`  | -            | Shortcut for the `flex` CSS property.   |    No    |
| `as`        | `ElementType`       | `'div'`      | Render as a different HTML tag.         |    No    |
| `children`  | `ReactNode`         | -            | Items to be stacked.                    |    No    |

### Detailed Parameter Documentation

#### `direction`

**Description:** Defines the flex-direction. Supports standard and reverse directions.

- `vertical` / `horizontal`
- `reverse` (vertical-reverse)
- `horizontal-reverse`
  **Example:** `<DynStack direction="horizontal-reverse" ... />`

#### `gap`

**Description:** Mapped to the design system's spacing tokens.

- `none`, `2xs`, `xs`, `sm`, `md`, `lg`, `xl`, `2xl`, `3xl`, `4xl`
  **Example:** `<DynStack gap="3xl" ... />`

#### `align` / `justify`

**Description:**

- `align` (Cross-axis): `start`, `center`, `end`, `stretch`, `baseline`.
- `justify` (Main-axis): `start`, `center`, `end`, `between`, `around`, `evenly`.
  **Example:** `<DynStack align="center" justify="between" ... />`

#### `as`

**Description:** Allows semantic HTML rendering while maintaining layout props.
**Example:** `<DynStack as="section" ... />` or `<DynStack as="nav" ... />`

## 🎨 Design Tokens

- **Default Gap**: `var(--dyn-spacing-md)`
- **Gap Tokens**: Mapped to `--dyn-spacing-*` system.

## ♿ Accessibility (A11y)

- **Semantic HTML**: Use the `as` prop to render `<nav>`, `<section>`, or `<ul>` when appropriate.
- **Focus Order**: The stack preserves the natural DOM order of its children, ensuring predictable tab navigation.

## 📝 Best Practices

- ✅ Use `DynStack` for simple one-dimensional layouts (rows or columns).
- ✅ Use `gap` instead of manual margins on child elements.
- ✅ Combine nested `DynStack` components for common UI patterns (e.g., a header with left-aligned title and right-aligned actions).
- ❌ Don't use `DynStack` for complex 2D grids (use `DynGrid`).
- ❌ Avoid `gap="none"` unless you are implementing custom child borders or dividers.
