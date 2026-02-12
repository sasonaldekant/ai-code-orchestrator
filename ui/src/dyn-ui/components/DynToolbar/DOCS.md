# DynToolbar Documentation

## 📌 Overview

**Category:** Organism / Layout
**Status:** Stable

`DynToolbar` is a container component designed to hold a set of actionable items like buttons, search fields, and dropdowns. It is typically used for page headers, table filters, or editor control bars. It features automatic responsive behavior, allowing overflow items to be moved into a dropdown menu when space is limited.

## 🛠 Usage

### Basic Toolbar

```tsx
import { DynToolbar } from '@dyn-ui/react';

const items = [
  { id: 'add', label: 'New Item', icon: 'plus', action: () => alert('Add') },
  { id: 'edit', label: 'Edit', icon: 'edit' },
  { id: 'sep1', type: 'separator' },
  { id: 'delete', label: 'Delete', icon: 'trash', type: 'button' },
];

<DynToolbar items={items} showLabels={true} variant="default" />;
```

### Advanced: Search & Badges

```tsx
const tools = [
  {
    id: 'search',
    type: 'search',
    placeholder: 'Search...',
    onChange: (v) => filter(v),
  },
  { id: 'notifications', icon: 'bell', badge: { count: 12, color: 'danger' } },
];

<DynToolbar items={tools} variant="minimal" size="sm" />;
```

## ⚙️ Properties (API)

### DynToolbar Props

| Prop                | Type                               | Default     | Description                                 | Required |
| :------------------ | :--------------------------------- | :---------- | :------------------------------------------ | :------: |
| `items`             | `ToolbarItem[]`                    | `[]`        | Configuration list for active items.        |   Yes    |
| `variant`           | `'default'\|'minimal'\|'floating'` | `'default'` | Visual style and container density.         |    No    |
| `size`              | `'sm' \| 'md' \| 'lg'`             | `'md'`      | Scale of icons and buttons.                 |    No    |
| `position`          | `'top' \| 'bottom' ...`            | `'top'`     | Relative or fixed placement on screen.      |    No    |
| `responsive`        | `boolean`                          | `true`      | Automatically hides items on small screens. |    No    |
| `overflowMenu`      | `boolean`                          | `true`      | Shows a menu button for hidden items.       |    No    |
| `overflowThreshold` | `number`                           | `3`         | Max items to show before overflow kicks in. |    No    |
| `showLabels`        | `boolean`                          | `true`      | Toggles text visibility next to icons.      |    No    |
| `onItemClick`       | `(item) => void`                   | -           | Global listener for any item interaction.   |    No    |

### ToolbarItem Object

| Prop        | Type                    | Description                                       |
| :---------- | :---------------------- | :------------------------------------------------ |
| `id`        | `string`                | **Required.** Unique key for the item.            |
| `type`      | `'button'\|'search'...` | Control type (`separator`, `dropdown`, `custom`). |
| `label`     | `string`                | Display text.                                     |
| `icon`      | `string \| ReactNode`   | Lucide name or custom element.                    |
| `badge`     | `ToolbarBadge`          | Badge configuration (number or object).           |
| `action`    | `() => void`            | Click handler for buttons.                        |
| `component` | `ReactNode`             | Custom element for `type: 'custom'`.              |
| `disabled`  | `boolean`               | Greys out the item and blocks action.             |

## 🔌 Technical Reference (Ref)

The `DynToolbarRef` provides methods for dynamic interaction:

- `toggleOverflow()`: Manually open/close the overflow dropdown.
- `refreshLayout()`: Recalculates available space (useful after animations).

## 🎨 Design Tokens

- **Toolbar Background**: `--dyn-toolbar-bg`
- **Separator Color**: `--dyn-toolbar-separator`
- **Item Hover**: `--dyn-toolbar-item-hover-bg`
- **Floating Shadow**: `--dyn-toolbar-floating-shadow`

## ♿ Accessibility (A11y)

- **Role**: Uses native `toolbar` semantic role.
- **Landmarks**: The overflow menu follows the `menu` / `menuitem` interaction pattern.
- **Labels**: Buttons without text (`showLabels={false}`) are automatically given `aria-label` from their `label` property.
- **Keyboard**:
  - `ArrowRight` / `ArrowLeft`: Navigate through items.
  - `Enter` / `Space`: Activate item.

## 📝 Best Practices

- ✅ Use `variant="minimal"` for toolbars inside cards or small sidebars.
- ✅ Group related actions with `separator` type.
- ✅ Set `overflowThreshold` based on the most critical actions of your page.
- ❌ Don't use a toolbar for primary app navigation (use `DynNavbar` or `DynSidebar`).
- ❌ Avoid mixing many custom components in one toolbar to maintain consistency.
