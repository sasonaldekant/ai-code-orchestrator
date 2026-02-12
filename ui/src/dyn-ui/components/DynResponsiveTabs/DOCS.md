# DynResponsiveTabs Documentation

## 📌 Overview

**Category:** Organism / Layout
**Status:** Stable

`DynResponsiveTabs` is a versatile navigation and content organization component. On large screens, it renders as standard horizontal or vertical tabs. On mobile devices or within narrow containers, it automatically transforms into an accordion layout to maintain usability.

## 🛠 Usage

```tsx
import { DynResponsiveTabs } from '@dyn-ui/react';

const tabs = [
  {
    label: 'General',
    icon: 'info',
    content: <div>General Settings Content</div>,
  },
  {
    label: 'Security',
    icon: 'shield',
    content: <div>Security Settings Content</div>,
  },
  {
    label: 'Advanced',
    icon: 'settings',
    content: <div>Advanced Settings Content</div>,
    disabled: true,
  },
];

function Example() {
  return (
    <DynResponsiveTabs
      tabs={tabs}
      responsive
      breakpoint={640}
      defaultActive={0}
    />
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop               | Type                         | Default          | Description                            | Required |
| :----------------- | :--------------------------- | :--------------- | :------------------------------------- | :------: |
| `tabs`             | `DynResponsiveTabItem[]`     | `[]`             | Array of labels and content nodes.     |   Yes    |
| `activeTab`        | `number`                     | -                | Controlled active index.               |    No    |
| `defaultActive`    | `number`                     | `0`              | Initial active index.                  |    No    |
| `orientation`      | `'horizontal' \| 'vertical'` | `'horizontal'`   | Tab strip direction.                   |    No    |
| `responsive`       | `boolean`                    | `true`           | Enable transition to accordion.        |    No    |
| `breakpoint`       | `number`                     | `768`            | Width (px) to switch to accordion.     |    No    |
| `allowCollapse`    | `boolean`                    | `false`          | Allow closing active accordion item.   |    No    |
| `onTabChange`      | `(index: number) => void`    | -                | Callback for selection (Controlled).   |    No    |
| `onChange`         | `(index: number) => void`    | -                | Callback for selection (Uncontrolled). |    No    |
| `expandIcon`       | `string \| ReactNode`        | `'chevron-down'` | Icon for collapsed accordion item.     |    No    |
| `collapseIcon`     | `string \| ReactNode`        | `'chevron-up'`   | Icon for expanded accordion item.      |    No    |
| `tabIdentifier`    | `string`                     | -                | Unique ID for nested tab styling.      |    No    |
| `disableAnimation` | `boolean`                    | `false`          | Turn off visual transitions.           |    No    |
| `aria-label`       | `string`                     | -                | Accessibility label for the list.      |    No    |

### Detailed Parameter Documentation

#### `tabs`

**Description:** Each tab item requires a `label` and `content`. `icon` and `disabled` are optional.
**Example:** `tabs={[{ label: 'Home', content: <Home /> }]}`

#### `responsive` / `breakpoint`

**Description:**

- `responsive`: If set to `true`, the component monitors window width.
- `breakpoint`: The pixel threshold where the layout flips from Tabs to Accordion.
  **Example:** `<DynResponsiveTabs responsive breakpoint={1024} ... />`

#### `orientation`

**Description:** Applies primarily to the desktop Tabs view.

- `horizontal`: Tabs appear in a row at the top.
- `vertical`: Tabs appear in a column on the left (sidebar style).
  **Example:** `<DynResponsiveTabs orientation="vertical" ... />`

#### `allowCollapse`

**Description:** Only affects Accordion mode. If `true`, clicking an already open accordion header will close it, leaving all items collapsed. If `false`, one item is always open.
**Example:** `<DynResponsiveTabs allowCollapse ... />`

#### `tabIdentifier`

**Description:** Crucial for nested tabs. It adds a scope class to avoid CSS collisions and allows the design system to apply different styles to nested layers (e.g., secondary tab coloring).
**Example:** `<DynResponsiveTabs tabIdentifier="sub-settings" ... />`

## 🎨 Design Tokens

- **Tab Active Border**: `--dyn-tabs-active-border`
- **Tab Hover BG**: `--dyn-tabs-hover-bg`
- **Accordion Border**: `--dyn-tabs-accordion-border`
- **Panel Padding**: `--dyn-tabs-panel-padding`

## ♿ Accessibility (A11y)

- **Roles**: Correctly uses `tablist`, `tab`, and `tabpanel` roles in tab mode. Switches to `button` with `aria-expanded` in accordion mode.
- **Keyboard Navigation (Tabs)**:
  - `ArrowRight` / `ArrowLeft`: Navigate through tabs.
  - `Home` / `End`: Jump to first/last tab.
  - `Enter` / `Space`: Select tab.
- **Automatic Association**: `aria-controls` and `aria-labelledby` are automatically linked between headers and panels using stable IDs.

## 📝 Best Practices

- ✅ Use `vertical` orientation for deep navigation or many tab items (>6).
- ✅ Keep tab labels short (1-2 words).
- ✅ Use `tabIdentifier` whenever nesting tabs inside other tabs.
- ❌ Avoid using `responsive={false}` unless you are strictly building for a specific desktop-only layout.
