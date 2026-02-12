# DynTable Documentation

## 📌 Overview

**Category:** Organism / Data Display
**Status:** Stable

`DynTable` is a highly flexible, enterprise-grade data grid component. It is built to handle large datasets with features such as sorting, pagination, multi-select, and custom row actions. It utilizes a modular sub-system for rendering different data types (currency, date, icons) and is fully themeable through design tokens.

## 🛠 Usage

### Basic Table

```tsx
import { DynTable } from '@dyn-ui/react';

const columns = [
  { key: 'id', title: 'ID', width: 80 },
  { key: 'name', title: 'Full Name', sortable: true },
  { key: 'role', title: 'User Role' },
  { key: 'joined', title: 'Joined Date', type: 'date' },
];

const data = [
  { id: '1', name: 'Alice Freeman', role: 'Admin', joined: '2023-01-15' },
  { id: '2', name: 'Bob Vance', role: 'Editor', joined: '2023-02-20' },
];

<DynTable columns={columns} data={data} />;
```

### Advanced: Actions & Selection

```tsx
<DynTable
  columns={columns}
  data={data}
  selectable="multiple"
  onSelectionChange={(keys) => console.log('Selected:', keys)}
  actions={[
    {
      key: 'edit',
      title: 'Edit',
      icon: 'edit',
      onClick: (row) => openModal(row),
    },
    {
      key: 'del',
      title: 'Delete',
      type: 'danger',
      onClick: (row) => deleteRow(row.id),
    },
  ]}
/>
```

## ⚙️ Properties (API)

### DynTable Props

| Prop           | Type                        | Default | Description                                   | Required |
| :------------- | :-------------------------- | :------ | :-------------------------------------------- | :------: |
| `data`         | `any[]`                     | `[]`    | The array of objects to display in the table. |   Yes    |
| `columns`      | `DynTableColumn[]`          | `[]`    | Configuration for each column.                |   Yes    |
| `actions`      | `TableAction[]`             | -       | Global row actions shown in the last column.  |    No    |
| `loading`      | `boolean`                   | `false` | Displays a loading overlay.                   |    No    |
| `size`         | `'sm' \| 'md' \| 'lg'`      | `'md'`  | Row density.                                  |    No    |
| `bordered`     | `boolean`                   | `false` | Adds borders around cells and the table.      |    No    |
| `striped`      | `boolean`                   | `false` | Alternates background color for rows.         |    No    |
| `hoverable`    | `boolean`                   | `true`  | Highlights row on mouse hover.                |    No    |
| `selectable`   | `TableSelectionType`        | `false` | Enables single/multiple row selection.        |    No    |
| `selectedKeys` | `string[]`                  | `[]`    | Controlled array of selected row IDs.         |    No    |
| `rowKey`       | `string \| (row) => string` | `'id'`  | Field name used as unique identifier.         |    No    |
| `pagination`   | `TablePagination`           | -       | Configures page numbers, size, and total.     |    No    |
| `sortBy`       | `{column, direction}`       | -       | Controlled sort state.                        |    No    |
| `emptyText`    | `string`                    | -       | Custom text when `data` is empty.             |    No    |
| `height`       | `number \| string`          | -       | Fixed height for internal scrolling.          |    No    |

### DynTableColumn Object

| Prop       | Type                        | Description                                      |
| :--------- | :-------------------------- | :----------------------------------------------- |
| `key`      | `string`                    | **Required.** The path to the data field.        |
| `title`    | `string`                    | **Required.** Text shown in the column header.   |
| `type`     | `TableCellType`             | Semantic data type (`currency`, `date`, `link`). |
| `align`    | `'left'\|'center'\|'right'` | Text alignment within cells.                     |
| `width`    | `string \| number`          | Custom fixed width.                              |
| `sortable` | `boolean`                   | Enables clicking the header to sort by this key. |
| `render`   | `(val, row) => Node`        | Custom renderer for cell content.                |

## 🔌 Technical Reference (Data Types)

The `type` property in `DynTableColumn` automates formatting:

- `currency`: Localized money format.
- `date` / `datetime`: Formatted strings based on system locale.
- `boolean`: Renders a badge or checkmark.
- `link`: Renders an `<a>` tag (expects value to be the URL).

## 🎨 Design Tokens

- **Header Text**: `--dyn-table-header-color`
- **Cell Border**: `--dyn-table-border-color`
- **Row Hover**: `--dyn-table-row-hover-bg`
- **Striped Row**: `--dyn-table-row-striped-bg`
- **Selection Color**: `--dyn-table-row-selected-bg`

For a full list of over 50+ table tokens, see [DESIGN_TOKENS.md](./DESIGN_TOKENS.md).

## ♿ Accessibility (A11y)

- **Native Semantics**: Uses `<table>`, `<thead>`, `<tbody>`, and `<tr>`.
- **Landmarks**: Columns utilize `scope="col"` on headers.
- **Roles**: Manage sortable columns with `aria-sort="ascending|descending"`.
- **Contrast**: Ensuring high contrast for active/selected rows in both light and dark modes.

## 📚 Related Documentation

- [Implementation Guide](./IMPLEMENTATION_GUIDE.md) - Best for deep dives into performance and custom filtering.
- [Design Tokens](./DESIGN_TOKENS.md) - Complete CSS variable mapping.

## 📝 Best Practices

- ✅ Always provide a stable `rowKey` (don't rely on array index).
- ✅ Use `fixed` table layout for large datasets with many columns.
- ✅ Combine `loading={true}` with server-side pagination for best UX.
- ❌ Don't render too many complex components within `render` functions; prefer simple nodes.
- ❌ Avoid `selectable="multiple"` on tables without pagination to prevent memory issues.
