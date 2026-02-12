# DynListView Documentation

## 📌 Overview

**Category:** Molecule
**Status:** Stable

`DynListView` is a flexible list component designed for displaying collections of data. It supports single and multiple selection, custom item rendering, item actions (edit/delete), zebra-striping, and expanded detail views for complex items.

## 🛠 Usage

```tsx
import { DynListView } from '@dyn-ui/react';

const items = [
  { id: '1', label: 'Item 1', description: 'Description for item 1' },
  { id: '2', label: 'Item 2', description: 'Description for item 2' },
];

function Example() {
  return (
    <DynListView
      items={items}
      selectable
      multiSelect
      bordered
      onSelectionChange={(keys, rows) => console.log(keys, rows)}
    />
  );
}
```

### With Actions

```tsx
<DynListView
  items={items}
  actions={[
    {
      key: 'edit',
      title: 'Edit',
      icon: 'edit',
      onClick: (item) => alert(`Editing ${item.label}`),
    },
  ]}
/>
```

## ⚙️ Properties (API)

### Quick Reference

| Prop                | Type                           | Default               | Description                       | Required |
| :------------------ | :----------------------------- | :-------------------- | :-------------------------------- | :------: |
| `items`             | `ListViewItem[]`               | `[]`                  | Items to display in the list.     |    No    |
| `data`              | `ListViewItem[]`               | `[]`                  | Legacy alias for `items`.         |    No    |
| `value`             | `string \| string[]`           | -                     | Controlled selected key(s).       |    No    |
| `defaultValue`      | `string \| string[]`           | -                     | Initial selected key(s).          |    No    |
| `multiSelect`       | `boolean`                      | `false`               | Allow multiple selections.        |    No    |
| `selectable`        | `boolean`                      | `false`               | Enable selection checkboxes.      |    No    |
| `disabled`          | `boolean`                      | `false`               | Disable all interactions.         |    No    |
| `loading`           | `boolean`                      | `false`               | Show loading state.               |    No    |
| `emptyText`         | `string`                       | `'No data available'` | Text shown when list is empty.    |    No    |
| `loadingText`       | `string`                       | `'Loading...'`        | Text shown during loading.        |    No    |
| `selectAllText`     | `string`                       | `'Select All'`        | Label for "select all" checkbox.  |    No    |
| `expandText`        | `string`                       | `'Expand'`            | Label for expand button.          |    No    |
| `collapseText`      | `string`                       | `'Collapse'`          | Label for collapse button.        |    No    |
| `dividers`          | `boolean`                      | `false`               | Show lines between items.         |    No    |
| `striped`           | `boolean`                      | `false`               | Alternating background colors.    |    No    |
| `actions`           | `ListAction[]`                 | `[]`                  | Custom action buttons per item.   |    No    |
| `renderItem`        | `(item, index) => ReactNode`   | -                     | Custom item renderer function.    |    No    |
| `size`              | `'sm' \| 'md' \| 'lg'`         | `'md'`                | Density of the list items.        |    No    |
| `height`            | `number \| string`             | -                     | Fixed height for scrollable list. |    No    |
| `bordered`          | `boolean`                      | `false`               | Show outer border.                |    No    |
| `selectedKeys`      | `string[]`                     | `[]`                  | Array of selected item IDs.       |    No    |
| `itemKey`           | `string \| ((item) => string)` | -                     | Custom field or fn for item key.  |    No    |
| `onChange`          | `(value, items) => void`       | -                     | Selection change handler.         |    No    |
| `onSelectionChange` | `(keys, items) => void`        | -                     | Alternative selection callback.   |    No    |
| `id`                | `string`                       | Generated             | Unique identifier.                |    No    |
| `className`         | `string`                       | -                     | Additional CSS classes.           |    No    |
| `style`             | `CSSProperties`                | -                     | Inline styles.                    |    No    |
| `aria-label`        | `string`                       | -                     | Accessibility label.              |    No    |
| `data-testid`       | `string`                       | `'dyn-listview'`      | Test identifier.                  |    No    |

### Detailed Parameter Documentation

#### `items`

**Description:** Essential data array. Each item should have at least an `id` or `value`.
**Example:** `items={[{ id: 1, label: 'First' }, { id: 2, label: 'Second' }]}`

#### `multiSelect`

**Description:** Turns on checkbox selection and allows multiple items to be selected at once. Only works if `selectable` is also `true` or used via keyboad.
**Example:** `<DynListView items={data} multiSelect selectable />`

#### `selectable`

**Description:** Enables visual selection indicators (checkboxes/radios).
**Example:** `<DynListView items={data} selectable />`

#### `size`

**Description:** Adjusts the vertical padding and text size of list items.

- `sm`: Compact view.
- `md`: Default view.
- `lg`: Spacious view.
  **Example:** `<DynListView size="sm" items={data} />`

#### `actions`

**Description:** Array of action definitions. Renders buttons on the right side of each item.
**Example:**

```tsx
const actions = [
  { key: 'ping', title: 'Ping', onClick: (item) => console.log(item) },
];
<DynListView actions={actions} items={data} />;
```

#### `renderItem`

**Description:** Overrides the default item rendering. Useful for complex custom layouts within the list.
**Example:**

```tsx
renderItem={(item) => (
  <div style={{ color: 'blue' }}>{item.customField}</div>
)}
```

#### `dividers` / `striped`

**Description:**

- `dividers`: Adds a thin border between each list item.
- `striped`: Applies a different background color to every second item (zebra pattern).
  **Example:** `<DynListView dividers striped items={data} />`

#### `height`

**Description:** Sets a fixed height for the container, enabling internal scrolling if content overflows.
**Example:** `<DynListView height={200} items={largeData} />`

#### `onSelectionChange` / `onChange`

**Description:** Both are fired when the user selects or deselects an item. `onSelectionChange` focuses on keys and full objects, while `onChange` follows a signature closer to form inputs.
**Example:** `onSelectionChange={(keys) => setSelection(keys[0])}`

## 🎨 Design Tokens

- **Item Background**: `--dyn-list-view-item-bg`
- **Selected Background**: `--dyn-list-view-item-selected-bg`
- **Hover Background**: `--dyn-list-view-item-hover-bg`
- **Border Color**: `--dyn-list-view-border`
- **Divider Color**: `--dyn-list-view-divider`

## ♿ Accessibility (A11y)

- **Role**: `listbox` (container) and `option` (items).
- **Keyboard Navigation**:
  - `ArrowUp` / `ArrowDown`: Move focus between items.
  - `Enter` / `Space`: Select/Toggles focused item.
  - `Home` / `End`: Jump to first/last item.
- **Attributes**:
  - `aria-multiselectable`: Set based on `multiSelect`.
  - `aria-setsize` / `aria-posinset`: Correctly informs screen readers of list length and position.
  - `aria-busy`: Set during loading state.

## 🔌 Imperative API (Ref)

```tsx
const listRef = useRef<DynListViewRef>(null);

listRef.current?.focus(); // Focuses the list root
listRef.current?.selectAll(); // Selects all items (multiSelect only)
listRef.current?.clearSelection(); // Deselects everything
```
