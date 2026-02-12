# DynIcon Documentation

## 📌 Overview

**Category:** Atom
**Status:** Stable

`DynIcon` is a universal icon component that supports internal SVG registry, Font Awesome classes, custom mapped dictionaries, and raw React nodes. It handles sizing, coloring, and transformations uniformly.

## 🛠 Usage

```tsx
import { DynIcon } from '@dyn-ui/react';

function Example() {
  return (
    <div style={{ display: 'flex', gap: '8px' }}>
      {/* Registry Icon */}
      <DynIcon icon="check" tone="success" />

      {/* Sizing */}
      <DynIcon icon="settings" size="lg" spin />

      {/* Custom Color */}
      <DynIcon icon="warning" color="#f50" strokeWidth={2} />
    </div>
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop          | Type                                           | Default | Description                    | Required |
| :------------ | :--------------------------------------------- | :------ | :----------------------------- | :------: |
| `icon`        | `string \| ReactNode`                          | -       | Icon key, class, or element.   |    No    |
| `size`        | `DynIconSizeToken \| number \| string`         | `'md'`  | Size of the icon.              |    No    |
| `tone`        | `'success' \| 'warning' \| 'danger' \| 'info'` | -       | Semantic color preset.         |    No    |
| `color`       | `string`                                       | -       | Custom color override.         |    No    |
| `strokeWidth` | `number \| string`                             | -       | SVG stroke width (1-4).        |    No    |
| `mirror`      | `'horizontal' \| 'vertical' \| 'both'`         | -       | Flip transformation.           |    No    |
| `spin`        | `boolean`                                      | `false` | continuous rotation animation. |    No    |
| `disabled`    | `boolean`                                      | `false` | Disable interactions/styles.   |    No    |
| `children`    | `ReactNode`                                    | -       | Fallback content.              |    No    |
| `id`          | `string`                                       | -       | Unique identifier.             |    No    |
| `className`   | `string`                                       | -       | Additional CSS classes.        |    No    |
| `style`       | `CSSProperties`                                | -       | Inline styles.                 |    No    |
| `onClick`     | `MouseEventHandler`                            | -       | Click handler.                 |    No    |
| `data-testid` | `string`                                       | -       | Test identifier.               |    No    |

### Detailed Parameter Documentation

#### `icon`

**Type:** `string | ReactNode`
**Description:**
The primary identifier. It attempts to resolve in the following order:

1.  **Internal Registry**: Checks `icons.ts` for SVG definitions.
2.  **Icon Dictionary**: Checks provided context dictionary (e.g. for remapping).
3.  **Class Name**: If string contains spaces or known prefixes (e.g. `fa `).
4.  **React Node**: Renders directly if an element is passed.

#### `size`

**Type:** `'xs' | 'sm' | 'md' | 'lg' | 'xl' | number | string`
**Default:** `'md'`
**Description:**

- **Tokens**: Maps to standardized pixel sizes from the design system.
- **Number**: Sets `width`, `height`, and `fontSize` in pixels.
- **String**: Sets raw CSS value (e.g. `'2em'`).

#### `tone`

**Type:** `'success' | 'warning' | 'danger' | 'info'`
**Description:**
Applies a semantic system color to the icon. Overridden by `color` prop if both are present.

## 🎨 Design Tokens

- **Sizes**:
  - `xs`: 12px
  - `sm`: 16px
  - `md`: 24px (default)
  - `lg`: 32px
  - `xl`: 48px
- **Colors**:
  - Uses `currentColor` by default unless `tone` or `color` is specified.
  - Tones map to `--dyn-semantic-*` tokens.

## ♿ Accessibility (A11y)

- **Role**:
  - Defaults to `img` (static) or `button` (interactive/onClick).
  - Can be overridden via `role` prop.
- **Hiding**:
  - Automatically sets `aria-hidden="true"` if no label is provided and not interactive.
  - If `aria-label` is present, it will be exposed to screen readers.
