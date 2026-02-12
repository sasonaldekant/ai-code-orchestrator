# DynTreeView Documentation

## 📌 Overview

**Category:** Organism / Data Display
**Status:** Stable

`DynTreeView` is a hierarchical data display component used for representing structured information such as file systems, organizational charts, or nested categories. It supports node expansion, selection, check boxes, and integrated search functionality.

## 🛠 Usage

### Basic Hierarchy

```tsx
import { DynTreeView } from '@dyn-ui/react';

const treeData = [
  {
    key: '0',
    title: 'Documents',
    children: [
      { key: '0-0', title: 'Resume.pdf' },
      { key: '0-1', title: 'Invoice.xlsx' },
    ],
  },
  { key: '1', title: 'Photos' },
];

<DynTreeView treeData={treeData} defaultExpandAll />;
```

### Advanced: Checkboxes & Search

```tsx
<DynTreeView
  treeData={treeData}
  checkable
  selectable
  searchable
  onCheck={(keys) => console.log('Checked:', keys)}
  onSelect={(keys) => console.log('Selected:', keys)}
/>
```

## ⚙️ Properties (API)

### DynTreeView Props

| Prop               | Type               | Default | Description                                      | Required |
| :----------------- | :----------------- | :------ | :----------------------------------------------- | :------: |
| `treeData`         | `TreeNode[]`       | `[]`    | **Required.** The hierarchical data source.      |   Yes    |
| `checkable`        | `boolean`          | `false` | Shows checkboxes for node selection.             |    No    |
| `selectable`       | `boolean`          | `true`  | Highlights the active node when clicked.         |    No    |
| `multiple`         | `boolean`          | `false` | Allows multiple nodes to be selected (Ctrl/Cmd). |    No    |
| `searchable`       | `boolean`          | `false` | Displays a search bar above the tree.            |    No    |
| `showLine`         | `boolean`          | `false` | Renders connecting lines between parent/child.   |    No    |
| `showIcon`         | `boolean`          | `true`  | Displays node icons (if provided in `treeData`). |    No    |
| `expandedKeys`     | `string[]`         | -       | Controlled array of expanded node IDs.           |    No    |
| `checkedKeys`      | `string[]`         | -       | Controlled array of checked node IDs.            |    No    |
| `selectedKeys`     | `string[]`         | -       | Controlled array of selected node IDs.           |    No    |
| `defaultExpandAll` | `boolean`          | `false` | Expands all levels on initial mount.             |    No    |
| `height`           | `string \| number` | -       | Fixed height for internal scrolling.             |    No    |
| `checkStrictly`    | `boolean`          | `false` | Prevents check state from cascading to children. |    No    |

### TreeNode Object

| Prop       | Type         | Description                                   |
| :--------- | :----------- | :-------------------------------------------- |
| `key`      | `string`     | **Required.** Unique identifier for the node. |
| `title`    | `string`     | **Required.** Text label shown for the node.  |
| `icon`     | `string`     | Lucide icon name.                             |
| `disabled` | `boolean`    | Greys out the node and blocks all actions.    |
| `children` | `TreeNode[]` | Array of child nodes.                         |

## 🎨 Design Tokens

- **Node Hover**: `--dyn-tree-node-hover-bg`
- **Selected Node**: `--dyn-tree-node-selected-bg`
- **Connector Line**: `--dyn-tree-connector-color`
- **Indentation**: `--dyn-tree-indent` (Standard: 24px)

## ♿ Accessibility (A11y)

- **Roles**: Correctly uses `tree`, `treeitem`, and `group`.
- **States**: `aria-expanded` and `aria-selected` accurately reflect current node status.
- **Keyboard**:
  - `ArrowUp` / `ArrowDown`: Move between visible nodes.
  - `ArrowRight`: Expand node / Move to first child.
  - `ArrowLeft`: Collapse node / Move to parent.
  - `Enter` / `Space`: Toggle select/check state.

## 📝 Best Practices

- ✅ Use `searchable={true}` for trees with more than 3 depths or many items.
- ✅ Always provide unique and stable `key` values for every node.
- ✅ Use `showLine` to help users trace deep hierarchies.
- ❌ Don't deep-nest more than 5 levels if possible for mobile usability.
- ❌ Avoid using `checkable` and `selectable` together if the interactions conflict in your UI.
