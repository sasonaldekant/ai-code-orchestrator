# DynDivider Documentation

## 📌 Overview

**Category:** Atom (Layout)
**Status:** Stable

`DynDivider` is a layout primitive used to visually separate content. It supports both horizontal and vertical orientations, text labels, and various line styles.

## 🛠 Usage

```tsx
import { DynDivider } from '@dyn-ui/react';

function Example() {
  return (
    <div>
      <p>Section A</p>

      {/* Simple Divider */}
      <DynDivider />

      <p>Section B</p>

      {/* Divider with Label */}
      <DynDivider label="OR" labelPosition="center" />

      {/* Styled Divider */}
      <DynDivider lineStyle="dashed" color="primary" thickness="medium" />
    </div>
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop            | Type                                     | Default        | Description                  | Required |
| :-------------- | :--------------------------------------- | :------------- | :--------------------------- | :------: |
| `direction`     | `'horizontal' \| 'vertical'`             | `'horizontal'` | Orientaton.                  |    No    |
| `label`         | `string`                                 | -              | Optional text in the middle. |    No    |
| `children`      | `ReactNode`                              | -              | Alternative to `label`.      |    No    |
| `labelPosition` | `'left' \| 'center' \| 'right'`          | `'center'`     | Text alignment.              |    No    |
| `thickness`     | `'thin' \| 'medium' \| 'thick'`          | `'thin'`       | Line weight.                 |    No    |
| `lineStyle`     | `'solid' \| 'dashed' \| 'dotted'`        | `'solid'`      | CSS border style.            |    No    |
| `color`         | `'default' \| 'primary' \| 'subtle' ...` | `'default'`    | Semantic color.              |    No    |
| `spacing`       | `LayoutSpacing`                          | `'md'`         | Margin around divider.       |    No    |
| `className`     | `string`                                 | -              | Custom classes.              |    No    |
| `id`            | `string`                                 | -              | Unique ID.                   |    No    |

### Detailed Parameter Documentation

#### `label`

**Type:** `string`
**Description:**
If provided, the divider line splits to accommodate the text.
Use `labelPosition` to align the text to the left, center, or right.

#### `direction`

**Type:** `'horizontal' | 'vertical'`

**Description:**

- `horizontal`: Occupies width and breaks vertical flow.
- `vertical`: Occupies height (needs parent height or flex context) to separate horizontal elements.

## 🎨 Design Tokens

- **Colors**:
  - `--dyn-divider-color`: Line color.
  - `--dyn-divider-text-color`: Label text color.
- **Sizing**:
  - `--dyn-divider-spacing`: Maps to `spacing` prop.
  - `--dyn-divider-thickness`: Maps to `thickness`.

## ♿ Accessibility (A11y)

- **Role**: `separator`.
- **Properties**:
  - `aria-orientation` set automatically based on direction.
  - `aria-labelledby` points to the user label if present.

## 📝 Best Practices

- ✅ **Do** use `color="subtle"` for low-contrast UI separation.
- ✅ **Do** use `vertical` dividers inside flex containers (e.g. toolbars).
- ❌ **Avoid** using dividers purely for spacing; use margin/padding utilities on the content instead.
