# DynBreadcrumb Documentation

## 📌 Overview

**Category:** Molecule
**Status:** Stable

`DynBreadcrumb` is a navigation aid that helps users understand their hierarchy within a website. It supports responsive collapsing, custom separators, automatic JSON-LD structured data for SEO, and controlled/uncontrolled expansion modes.

## 🛠 Usage

```tsx
import { DynBreadcrumb } from '@dyn-ui/react';

function Example() {
  const items = [
    { label: 'Home', href: '/' },
    { label: 'Products', href: '/products' },
    { label: 'Electronics', href: '/products/electronics' },
    { label: 'Laptops', current: true },
  ];

  return <DynBreadcrumb items={items} maxItems={3} />;
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop                   | Type                          | Default        | Description                          | Required |
| :--------------------- | :---------------------------- | :------------- | :----------------------------------- | :------: |
| `items`                | `BreadcrumbItem[]`            | -              | Array of item objects.               |   Yes    |
| `size`                 | `'sm' \| 'md' \| 'lg'`        | `'md'`         | Text size variant.                   |    No    |
| `separator`            | `'slash' \| 'chevron' \| ...` | `'slash'`      | Visual separator style.              |    No    |
| `maxItems`             | `number`                      | `0` (all)      | Max items before collapsing.         |    No    |
| `showEllipsis`         | `boolean`                     | `true`         | Show `...` button when collapsed.    |    No    |
| `expanded`             | `boolean`                     | -              | Controlled expansion state.          |    No    |
| `onItemClick`          | `(item, e) => void`           | -              | Item click handler.                  |    No    |
| `onEllipsisClick`      | `() => void`                  | -              | Ellipsis click handler.              |    No    |
| `linkComponent`        | `ElementType`                 | `'a'`          | Custom link (e.g., Next.js Link).    |    No    |
| `enableStructuredData` | `boolean`                     | `false`        | Add Schema.org microdata properties. |    No    |
| `customSeparator`      | `ReactNode`                   | -              | Custom separator element.            |    No    |
| `navigationLabel`      | `string`                      | `'Breadcrumb'` | ARIA label for the nav element.      |    No    |
| `id`                   | `string`                      | -              | Component ID.                        |    No    |
| `className`            | `string`                      | -              | Custom classes.                      |    No    |
| `style`                | `CSSProperties`               | -              | Custom styles.                       |    No    |

### Detailed Parameter Documentation

#### `items`

**Type:** `BreadcrumbItem[]`
**Required:** Yes

**Structure:**

```ts
interface BreadcrumbItem {
  id?: string;
  label: string;
  href?: string; // If missing, treated as text (or current page)
  current?: boolean; // Marks as active page (aria-current="page")
  icon?: ReactNode; // Leading icon
  showWhenCollapsed?: boolean; // Keep visible even if maxItems is exceeded
  linkProps?: any; // Props expanded onto the link component
}
```

#### `maxItems` / `showEllipsis`

**Type:** `number` / `boolean`
**Default:** `0` / `true`

**Description:**
If the number of items exceeds `maxItems`, the middle items are hidden.

- `maxItems`: The maximum number of visible items. If `0`, all items are shown.
- `showEllipsis`: If `true`, an interactive ellipsis button (`...`) is displayed in place of hidden items. Clicking it expands the breadcrumb.

#### `separator` / `customSeparator`

**Type:** `'slash' | 'chevron' | 'arrow' | 'dot' | 'custom'` / `ReactNode`
**Default:** `'slash'`

**Description:**
Controls the visual separator between items.

- If `separator="custom"`, you must provide the `customSeparator` prop (e.g., `<Icon name="arrow-right" />`).

#### `expanded` / `onEllipsisClick`

**Type:** `boolean` / `() => void`

**Description:**
For controlled expansion logic.

- `expanded`: Forces the breadcrumb to be expanded (`true`) or collapsed (`false`). If undefined, internal state is used.
- `onEllipsisClick`: Callback fired when the ellipsis button is clicked.

#### `linkComponent` / `onItemClick`

**Type:** `ElementType` / `(item, event) => void`
**Default:** `'a'`

**Description:**

- `linkComponent`: Allows replacing the standard `<a>` tag with a client-side router link component (e.g., `next/link` or `react-router-dom/Link`).
- `onItemClick`: Callback fired when any link item is clicked. Useful for analytics or navigation interception.

#### `enableStructuredData`

**Type:** `boolean`
**Default:** `false`

**Description:**
Attributes the rendered HTML with standard Schema.org microdata for `BreadcrumbList`. Useful for SEO if you are not injecting JSON-LD separately.

## 🎨 Design Tokens

`DynBreadcrumb` uses the following component-specific tokens, which map to global semantic tokens:

- **Colors**:
  - `--dyn-breadcrumb-color-link`: Link text color.
  - `--dyn-breadcrumb-color-text`: Static text color.
  - `--dyn-breadcrumb-color-separator`: Separator color.
  - `--dyn-breadcrumb-color-text-current`: Current page text color.
- **Spacing**:
  - `--dyn-breadcrumb-gap`: Space between items and separators.

## ♿ Accessibility (A11y)

- **Role**: `navigation` (via `<nav>`).
- **Structure**: Uses `<ol>` for ordered list semantics.
- **Current Item**: Adds `aria-current="page"` to the active item (or the last item if `href` is missing).
- **Labeling**: Uses `aria-label="Breadcrumb"` (or `navigationLabel` prop).
- **Expansion**: The ellipsis button uses `aria-expanded` and `aria-label` to communicate state.

## 📝 Best Practices

- ✅ **Do** place breadcrumbs at the top of pages for clear hierarchy.
- ✅ **Do** use `maxItems` for deep hierarchies on mobile to prevent wrapping issues.
- ✅ **Do** provide `href` for all parent items to ensure navigability.
- ✅ **Do** use `showWhenCollapsed` for critical intermediate steps that should never be hidden.
