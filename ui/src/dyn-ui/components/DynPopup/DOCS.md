# DynPopup Documentation

## 📌 Overview

**Category:** Molecule / Overlay
**Status:** Stable

`DynPopup` is a floating action menu component, often referred to as a "Kebab" or "Context" menu. It displays a list of clickable actions or custom content positioned relative to a trigger element.

## 🛠 Usage

```tsx
import { DynPopup } from '@dyn-ui/react';

const items = [
  { id: 'view', label: 'View Details', icon: 'eye', onClick: () => {} },
  { id: 'edit', label: 'Edit record', icon: 'edit', onClick: () => {} },
  { id: 'sep', divider: true },
  {
    id: 'del',
    label: 'Delete',
    icon: 'trash',
    danger: true,
    onClick: () => {},
  },
];

function Example() {
  return <DynPopup items={items} placement="bottom-end" />;
}
```

### With Custom Trigger

```tsx
<DynPopup trigger={<DynButton label="Show Actions" />} items={items} />
```

## ⚙️ Properties (API)

### Quick Reference

| Prop           | Type                | Default        | Description                           | Required |
| :------------- | :------------------ | :------------- | :------------------------------------ | :------: |
| `trigger`      | `ReactNode`         | Kebab Icon     | Element that opens the popup.         |    No    |
| `items`        | `DynPopupItem[]`    | `[]`           | List of menu actions.                 |    No    |
| `children`     | `ReactNode`         | -              | Custom content (overrides items).     |    No    |
| `open`         | `boolean`           | -              | Controlled open state.                |    No    |
| `defaultOpen`  | `boolean`           | `false`        | Initial open state.                   |    No    |
| `onOpenChange` | `(open) => void`    | -              | Visibility callback.                  |    No    |
| `placement`    | `DynPopupPlacement` | `'bottom-end'` | Overlay position relative to trigger. |    No    |
| `offset`       | `number`            | `4`            | Gap between trigger and menu (px).    |    No    |
| `usePortal`    | `boolean`           | `true`         | Render in a React Portal.             |    No    |
| `aria-label`   | `string`            | -              | Accessibility label.                  |    No    |
| `id`           | `string`            | Generated      | Unique ID for ARIA.                   |    No    |

### Detailed Parameter Documentation

#### `items`

**Description:** Array of action objects. If a `divider: true` is provided, a horizontal separator line is rendered.
**Example:** `items={[{ id: '1', label: 'Action' }]}`

#### `DynPopupItem` Object

| Prop       | Type        | Description                              |
| :--------- | :---------- | :--------------------------------------- |
| `id`       | `string`    | Unique key for the item.                 |
| `label`    | `string`    | Display text.                            |
| `icon`     | `ReactNode` | Leading icon.                            |
| `disabled` | `boolean`   | Prevents click and applies dimmed style. |
| `danger`   | `boolean`   | Applies red/alert styling to text/icon.  |
| `divider`  | `boolean`   | Renders a separator instead of a button. |

#### `placement`

**Description:** Controls where the popup appears relative to the trigger.

- `top-start` / `top-end`
- `bottom-start` / `bottom-end` (Default)
- `left-start` / `left-end`
- `right-start` / `right-end`

#### `trigger`

**Description:** If not provided, the component renders a standard vertical three-dots (Kebab) SVG. If provided, the provided node becomes the clickable trigger.

## 🎨 Design Tokens

- **Background**: `--dyn-popup-bg`
- **Item Hover**: `--dyn-popup-item-hover-bg`
- **Border**: `--dyn-popup-border`
- **Shadow**: `--dyn-popup-shadow`

## ♿ Accessibility (A11y)

- **Roles**: Uses `menu` and `menuitem` roles.
- **Attributes**:
  - Trigger has `aria-haspopup="true"`.
  - `aria-expanded` reflects current visibility.
  - Separators have `role="separator"`.
- **Keyboard**:
  - `Enter` / `Space`: Toggle popup.
  - `Escape`: Close popup.
  - _Clicking an item automatically closes the popup._

## 📝 Best Practices

- ✅ Use `danger: true` for destructive items like "Delete".
- ✅ Use `placement="bottom-end"` (default) when the trigger is on the far right of the screen.
- ✅ Group related actions with `divider: true`.
- ❌ Don't use `DynPopup` for complex navigation (use `DynMenu`).
- ❌ Don't use `DynPopup` for forms (use `DynDialog`).
