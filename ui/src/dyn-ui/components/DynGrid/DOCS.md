# DynGrid Documentation

## 📌 Overview

**Category:** Data Display
**Status:** Stable

`DynGrid` is a robust data table component designed for displaying structured data. It supports sorting, pagination, row selection, custom column rendering, and responsive sizing.

## 🛠 Usage

```tsx
import { DynGrid } from '@dyn-ui/react';

const columns = [
  { key: 'id', title: 'ID', width: 50 },
  { key: 'name', title: 'Name', sortable: true },
  { key: 'role', title: 'Role', render: (val) => <b>{val}</b> },
];

const data = [
  { id: 1, name: 'Alice', role: 'Admin' },
  { id: 2, name: 'Bob', role: 'User' },
];

function Example() {
  return (
    <DynGrid
      columns={columns}
      data={data}
      bordered
      hoverable
      selectable="multiple"
    />
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop                | Type                                | Default               | Description                  | Required |
| :------------------ | :---------------------------------- | :-------------------- | :--------------------------- | :------: |
| `columns`           | `DynGridColumn[]`                   | -                     | Column definitions.          |   Yes    |
| `data`              | `Record<string, unknown>[]`         | -                     | Data source array.           |   Yes    |
| `loading`           | `boolean`                           | `false`               | Show loading spinner.        |    No    |
| `size`              | `'sm' \| 'md' \| 'lg'`              | `'md'`                | Density of the table.        |    No    |
| `bordered`          | `boolean`                           | `true`                | Show full borders.           |    No    |
| `striped`           | `boolean`                           | `false`               | Zebra-striping rows.         |    No    |
| `hoverable`         | `boolean`                           | `true`                | Highlight row on hover.      |    No    |
| `sortable`          | `boolean`                           | `true`                | Enable column sorting.       |    No    |
| `filterable`        | `boolean`                           | `false`               | Enable filtering (reserved). |    No    |
| `selectable`        | `boolean \| 'single' \| 'multiple'` | `false`               | Selection mode.              |    No    |
| `selectedKeys`      | `string[]`                          | `[]`                  | Controlled selected keys.    |    No    |
| `onSelectionChange` | `(keys, rows) => void`              | -                     | Selection handler.           |    No    |
| `onSort`            | `(col, dir) => void`                | -                     | Sort handler.                |    No    |
| `onFilter`          | `(filters) => void`                 | -                     | Filter handler.              |    No    |
| `pagination`        | `DynGridPagination`                 | -                     | Pagination config.           |    No    |
| `emptyText`         | `ReactNode`                         | `'No data available'` | Content for empty state.     |    No    |
| `id`                | `string`                            | -                     | Unique identifier.           |    No    |
| `className`         | `string`                            | -                     | Additional CSS classes.      |    No    |
| `style`             | `CSSProperties`                     | -                     | Inline styles.               |    No    |
| `data-testid`       | `string`                            | `'dyn-grid'`          | Test ID.                     |    No    |

### Detailed Parameter Documentation

#### `columns`

**Type:** `DynGridColumn[]`
**Structure:**

```ts
interface DynGridColumn {
  key: string; // Unique key pointing to data index
  title: ReactNode; // Reader title
  width?: string | number; // Fixed width
  minWidth?: string | number;
  sortable?: boolean; // Enable sorting for this column
  align?: 'left' | 'center' | 'right';
  render?: (value: any, record: any, index: number) => ReactNode; // Custom cell renderer
}
```

#### `selectable`

**Type:** `boolean | 'single' | 'multiple'`
**Default:** `false`
**Description:**
Controls the row selection mode.

- `false`: No selection.
- `'single'`: Radio button selection (one row at a time).
- `'multiple'` (or `true`): Checkbox selection (multiple rows).

#### `pagination`

**Type:** `DynGridPagination`
**Structure:**

```ts
interface DynGridPagination {
  current: number; // Current page (1-based)
  pageSize: number; // Items per page
  total: number; // Total items count
  onChange?: (page, pageSize) => void;
  showTotal?: (total, range) => ReactNode;
}
```

## 🎨 Design Tokens

- **Border Color**: `--dyn-grid-border-color`
- **Header BG**: `--dyn-grid-header-bg`
- **Row Hover**: `--dyn-grid-row-hover-bg`
- **Selected Row**: `--dyn-grid-row-selected-bg`
- **Cell Padding**: `--dyn-grid-cell-padding`

## ♿ Accessibility (A11y)

- **Role**: `table`
- **Structure**: Uses semantic `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>`.
- **Sorting**: Adds `aria-sort` to sortable headers.
- **Selection**: Uses checkboxes/radios with `aria-label` for row selection.
- **Loading**: Loading state uses `role="status"` and `aria-live="polite"`.
