# DynMenu Documentation

## 📌 Overview

**Category:** Organism / Navigation
**Status:** Stable

`DynMenu` is a hierarchical navigation component designed for top bars or sidebars. It supports nested menu items, icons, badges, and full keyboard accessibility.

## 🛠 Usage

```tsx
import { DynMenu } from '@dyn-ui/react';

const items = [
  {
    label: 'File',
    children: [
      { label: 'New', icon: 'plus', action: 'file-new' },
      { label: 'Open', icon: 'folder-open', action: 'file-open' },
      { type: 'divider' },
      { label: 'Exit', icon: 'power-off', action: () => window.close() },
    ],
  },
  { label: 'Edit', children: [{ label: 'Undo' }, { label: 'Redo' }] },
];

function Example() {
  return (
    <DynMenu
      items={items}
      orientation="horizontal"
      onAction={(action) => console.log('Action:', action)}
    />
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop          | Type                         | Default        | Description                          | Required |
| :------------ | :--------------------------- | :------------- | :----------------------------------- | :------: |
| `items`       | `MenuItem[]`                 | `[]`           | Array of menu items and submenus.    |   Yes    |
| `menus`       | `MenuItem[]`                 | -              | Legacy alias for `items`.            |    No    |
| `orientation` | `'horizontal' \| 'vertical'` | `'horizontal'` | Layout direction.                    |    No    |
| `onAction`    | `(action: string) => void`   | -              | Generic handler for item clicks.     |    No    |
| `id`          | `string`                     | Generated      | Unique identifier for ARIA controls. |    No    |
| `aria-label`  | `string`                     | -              | Accessibility label.                 |    No    |
| `className`   | `string`                     | -              | Additional CSS classes.              |    No    |
| `data-testid` | `string`                     | `'dyn-menu'`   | Test identifier.                     |    No    |

### Detailed Parameter Documentation

#### `items`

**Description:** The core data structure for the menu. Each `MenuItem` can have a `label`, `icon`, `action`, and `children` for submenus.
**Example:** `items={[{ label: 'Home', action: '/' }]}`

#### `orientation`

**Description:** Defines the layout of the top-level list.

- `horizontal`: Items flow side-by-side (suitable for Navbar).
- `vertical`: Items flow top-to-bottom (suitable for Sidebar).
  **Example:** `<DynMenu orientation="vertical" items={navItems} />`

#### `onAction`

**Description:** A central callback that triggers when a menu item with a `string` action is clicked. If a menu item has a function `action`, it will be executed locally instead.
**Example:** `onAction={(id) => navigate(`/${id}`)}`

#### `MenuItem` Object

| Prop       | Type                     | Description                               |
| :--------- | :----------------------- | :---------------------------------------- |
| `label`    | `string`                 | Text to display.                          |
| `icon`     | `string \| ReactNode`    | Leading icon.                             |
| `action`   | `string \| (() => void)` | Triggers `onAction` or executes directly. |
| `children` | `MenuItem[]`             | Submenu items.                            |
| `disabled` | `boolean`                | Prevents interaction.                     |
| `type`     | `'item' \| 'divider'`    | Renders a separator if 'divider'.         |

## 🎨 Design Tokens

- **Menu Background**: `--dyn-menu-bg`
- **Item Hover**: `--dyn-menu-item-hover-bg`
- **Text Color**: `--dyn-menu-text`
- **Shadow**: `--dyn-menu-shadow`

## ♿ Accessibility (A11y)

- **Roles**: Uses `menubar`, `menu`, and `menuitem` roles for proper assistive technology identification.
- **Keyboard Navigation**:
  - `ArrowRight` / `ArrowLeft`: Navigate top-level items (Horizontal).
  - `ArrowDown` / `ArrowUp`: Navigate items (Vertical) or open submenus.
  - `Enter` / `Space`: Open submenu or trigger action.
  - `Escape`: Close open submenus.
  - `Home` / `End`: Jump to first/last top-level item.
- **Attributes**: `aria-haspopup`, `aria-expanded`, and `aria-controls` are automatically managed for submenus.

## 📝 Best Practices

- ✅ Use `vertical` orientation for lateral sidebars.
- ✅ Group related actions using dividers.
- ✅ Keep submenu depth to 1 level for better UX.
- ❌ Don't use very long labels (keep them 1-2 words).
