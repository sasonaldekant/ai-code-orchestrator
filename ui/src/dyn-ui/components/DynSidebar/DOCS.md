# DynSidebar Documentation

## 📌 Overview

**Category:** Organism / Navigation
**Status:** Stable

`DynSidebar` is a vertical navigation container designed for primary application shell layouts. It supports hierarchical navigation items, custom headers/footers, and a collapsible state for maximizing screen real estate.

## 🛠 Usage

```tsx
import { DynSidebar } from '@dyn-ui/react';

const items = [
  { id: 'dash', label: 'Dashboard', icon: 'home', onClick: () => {} },
  { id: 'users', label: 'Users', icon: 'users', onClick: () => {} },
];

const footerItems = [{ id: 'settings', label: 'Settings', icon: 'settings' }];

function Layout() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <DynSidebar
        header={<Logo />}
        items={items}
        footerItems={footerItems}
        collapsed={collapsed}
        onCollapseChange={setCollapsed}
      />
      <main>Page Content</main>
    </div>
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop               | Type                  | Default | Description                            | Required |
| :----------------- | :-------------------- | :------ | :------------------------------------- | :------: |
| `items`            | `DynSidebarItem[]`    | `[]`    | Main navigation links.                 |    No    |
| `footerItems`      | `DynSidebarItem[]`    | `[]`    | Links shown at the bottom.             |    No    |
| `header`           | `ReactNode`           | -       | Branding or avatar Area.               |    No    |
| `collapsed`        | `boolean`             | `false` | Shrink to icons only.                  |    No    |
| `onCollapseChange` | `(collapsed) => void` | -       | Triggered when toggling width.         |    No    |
| `activeId`         | `string`              | -       | Highlight the current page by item ID. |    No    |
| `open`             | `boolean`             | `false` | Visibility on mobile overlay.          |    No    |
| `onOpenChange`     | `(open) => void`      | -       | Mobile toggle callback.                |    No    |
| `onItemClick`      | `(item) => void`      | -       | Global callback for any item click.    |    No    |

### Detailed Parameter Documentation

#### `items` / `footerItems` (`DynSidebarItem` Object)

**Description:** Defines individual navigation rows.
| Prop | Type | Description |
| :--------- | :--------- | :------------------------------------------- |
| `id` | `string` | Unique key and active state matcher. |
| `label` | `string` | Text shown next to icon (hidden when collapsed).|
| `icon` | `Node\|Str`| Icon name or custom React element. |
| `onClick` | `() => void`| Specific action for this item. |
| `disabled` | `boolean` | Renders item as non-clickable and dimmed. |

#### `collapsed`

**Description:** When `true`, the sidebar width reduces to ~64px, and only icons are visible. Tooltips are automatically added to icons using the `title` attribute for accessibility.
**Example:** `<DynSidebar collapsed={true} ... />`

#### `activeId`

**Description:** Visually highlights the item matching the ID. This is typically synced with your router's current path or state.
**Example:** `<DynSidebar activeId="users" ... />`

## 🎨 Design Tokens

- **Width**: `--dyn-sidebar-width` (default 260px)
- **Collapsed Width**: `--dyn-sidebar-collapsed-width` (default 64px)
- **Background**: `--dyn-sidebar-bg`
- **Active BG**: `--dyn-sidebar-item-active-bg`
- **Text Color**: `--dyn-sidebar-text`

## ♿ Accessibility (A11y)

- **Semantic HTML**: Uses `<aside>` as the container and `<nav>` for the links.
- **Roles**: Navigation items are `button` elements (or can be treated as links if `onClick` navigates).
- **Aria attributes**:
  - `aria-label` provides the item name to screen readers even when labels are visually hidden in collapsed mode.
- **Focus**: Standard tab order is preserved.

## 📝 Best Practices

- ✅ Use `footerItems` for secondary actions like "Logout" or "Settings".
- ✅ Keep `label` strings short to prevent overflow on medium screens.
- ✅ Always provide an `icon` for items if you plan to use `collapsed` mode.
- ❌ Don't put large complex components inside the sidebar; stick to simple icon+text rows.
