# DynTabs Documentation

## 📌 Overview

**Category:** Molecule / Layout
**Status:** Stable

`DynTabs` is a high-performance tabbed navigation component. It organizes content into multiple panels, allowing users to switch between them easily without leaving the page. It supports various visual themes (pills, underlined, bordered), orientations, and advanced features like lazy loading, closable tabs, and keyboard-driven navigation.

## 🛠 Usage

### Basic Usage

```tsx
import { DynTabs } from '@dyn-ui/react';

const items = [
  { value: 'profile', label: 'Profile', content: <ProfileInfo /> },
  { value: 'settings', label: 'Settings', content: <SettingsPanel /> },
  { value: 'activity', label: 'Activity', content: <ActivityLog /> },
];

function MyApp() {
  return <DynTabs items={items} defaultValue="profile" variant="underlined" />;
}
```

### Advanced: Closable & Scrollable

```tsx
<DynTabs
  items={dynamicItems}
  closable
  scrollable
  onTabClose={(id) => handleRemoveTab(id)}
  variant="pills"
/>
```

## ⚙️ Properties (API)

### DynTabs Props

| Prop           | Type                               | Default        | Description                                       | Required |
| :------------- | :--------------------------------- | :------------- | :------------------------------------------------ | :------: |
| `items`        | `DynTabItem[]`                     | `[]`           | Array of configuration for each tab.              |   Yes    |
| `value`        | `string \| number`                 | -              | Current active tab value (Controlled).            |    No    |
| `defaultValue` | `string \| number`                 | -              | Initial active tab value (Uncontrolled).          |    No    |
| `variant`      | `DynTabsVariant`                   | `'default'`    | Visual style (`underlined`, `pills`, `bordered`). |    No    |
| `orientation`  | `'horizontal' \| 'vertical'`       | `'horizontal'` | Primary axis of the tab list.                     |    No    |
| `position`     | `'top'\|'bottom'\|'left'\|'right'` | `'top'`        | Header placement relative to content.             |    No    |
| `size`         | `'sm' \| 'md' \| 'lg'`             | `'md'`         | Scale of tabs and typography.                     |    No    |
| `fitted`       | `boolean`                          | `false`        | Tabs stretch to fill container width.             |    No    |
| `scrollable`   | `boolean`                          | `false`        | Enables horizontal scroll for many tabs.          |    No    |
| `closable`     | `boolean`                          | `false`        | Global toggle for close buttons on tabs.          |    No    |
| `lazy`         | `boolean`                          | `false`        | Only render active tab content to DOM.            |    No    |
| `animated`     | `boolean`                          | `true`         | Enable smooth transitions between panels.         |    No    |
| `addable`      | `boolean`                          | `false`        | Show a plus button for adding new tabs.           |    No    |
| `onChange`     | `(id: string) => void`             | -              | Callback when active tab changes.                 |    No    |
| `onTabClose`   | `(id: string) => void`             | -              | Callback when a tab's close button is clicked.    |    No    |

### DynTabItem Object

| Prop       | Type               | Description                                      |
| :--------- | :----------------- | :----------------------------------------------- |
| `value`    | `string \| number` | **Required.** Unique identifier for the tab.     |
| `label`    | `string`           | **Required.** Text shown in the tab header.      |
| `content`  | `ReactNode \| Fn`  | UI body. Can be a function: `(params) => Node`.  |
| `icon`     | `ReactNode`        | Optional leading icon inside the tab.            |
| `badge`    | `string \| number` | Optional counter or status dot on the tab.       |
| `disabled` | `boolean`          | Prevents interaction with this specific tab.     |
| `closable` | `boolean`          | Item-level override for close button visibility. |

## 🔌 Technical Reference (Ref)

The `DynTabsRef` provides imperative control:

- `setActiveTab(id)`: Programmatically switch tabs.
- `getActiveTab()`: Get current ID.
- `focusTab(id)`: Move keyboard focus.
- `getTabElement(id)`: Returns the HTML Button element.

## 🎨 Design Tokens

- **Active Underline**: `--dyn-tabs-active-underline`
- **Tab Hover BG**: `--dyn-tabs-hover-bg`
- **Selected Text**: `--dyn-tabs-selected-color`
- **Panel Padding**: `--dyn-tabs-panel-padding`

## ♿ Accessibility (A11y)

- **Roles**: Correctly uses `tablist`, `tab`, and `tabpanel`.
- **Landmarks**: Automatically links headers to panels via `aria-controls`.
- **Keyboard**:
  - `ArrowLeft` / `ArrowRight`: Navigate between horizontal tabs.
  - `ArrowUp` / `ArrowDown`: Navigate between vertical tabs.
  - `Home` / `End`: First/Last tab.
  - `Space` / `Enter`: Activate tab (if manual activation is off).

## 📝 Best Practices

- ✅ Use `variant="underlined"` for primary page navigation.
- ✅ Use `variant="pills"` for filtering or secondary navigation sections.
- ✅ Enable `lazy={true}` for content-heavy tabs (e.g., charts or maps).
- ✅ Keep tab labels under 3 words to avoid layout issues in mobile views.
- ❌ Don't use `orientation="vertical"` if the sidebar area is very narrow.
- ❌ Avoid `scrollable={true}` on layouts that already have a global horizontal scroll.
