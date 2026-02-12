# DynDropdown Documentation

## 📌 Overview

**Category:** Molecule / Overlay
**Status:** Stable

`DynDropdown` is a flexible overlay component that displays a list of actions or custom content relative to a trigger element. It supports portal rendering, multiple placements, and both click/hover interactions.

## 🛠 Usage

```tsx
import { DynDropdown, DynButton } from '@dyn-ui/react';

const items = [
  { id: 'profile', label: 'My Profile', icon: 'user' },
  { id: 'settings', label: 'Settings', icon: 'settings' },
  { id: 'div', type: 'divider' },
  { id: 'logout', label: 'Log Out', className: 'text-danger' },
];

function Example() {
  return (
    <DynDropdown
      trigger={<DynButton label="Options" />}
      items={items}
      onItemClick={(item) => console.log('Action:', item.id)}
    />
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop                  | Type                      | Default          | Description                          | Required |
| :-------------------- | :------------------------ | :--------------- | :----------------------------------- | :------: |
| `trigger`             | `ReactNode`               | -                | Element that toggles the dropdown.   |   Yes    |
| `items`               | `DynDropdownItem[]`       | `[]`             | Array of menu items.                 |    No    |
| `children`            | `ReactNode`               | -                | Custom content (overrides items).    |    No    |
| `isOpen`              | `boolean`                 | -                | Controlled open state.               |    No    |
| `defaultOpen`         | `boolean`                 | `false`          | Initial open state.                  |    No    |
| `onOpenChange`        | `(open: boolean) => void` | -                | Open state callback.                 |    No    |
| `placement`           | `DynDropdownPlacement`    | `'bottom-start'` | Menu position relative to trigger.   |    No    |
| `offset`              | `number`                  | `8`              | Gap between trigger and menu (px).   |    No    |
| `triggerType`         | `'click' \| 'hover'`      | `'click'`        | Primary interaction mode.            |    No    |
| `closeOnItemClick`    | `boolean`                 | `true`           | Close menu when an item is selected. |    No    |
| `closeOnOutsideClick` | `boolean`                 | `true`           | Close menu when clicking outside.    |    No    |
| `onItemClick`         | `(item, event) => void`   | -                | Callback for item selection.         |    No    |
| `usePortal`           | `boolean`                 | `true`           | Render menu in a React Portal.       |    No    |
| `disabled`            | `boolean`                 | `false`          | Disable the dropdown trigger.        |    No    |
| `triggerWrapper`      | `'button' \| 'div'`       | `'button'`       | Element wrapping the trigger.        |    No    |
| `triggerRole`         | `string`                  | -                | Custom ARIA role for trigger.        |    No    |
| `fullWidth`           | `boolean`                 | `false`          | Match menu width to trigger width.   |    No    |
| `className`           | `string`                  | -                | Custom container classes.            |    No    |
| `id`                  | `string`                  | Generated        | Unique ID for ARIA association.      |    No    |

### Detailed Parameter Documentation

#### `items`

**Description:** Array of objects defining the menu structure. Each item can be a standard button or a separator (`type: 'divider'`).
**Example:** `items={[{ id: '1', label: 'Item 1' }]}`

#### `placement`

**Description:** Positions the dropdown menu relative to the trigger element using Popper-like logic.

- `bottom-start` (Default)
- `bottom-end`
- `top-start`
- `top-end`
- `left-start`
- `right-start`
  **Example:** `<DynDropdown placement="right-start" trigger={...} />`

#### `triggerWrapper` / `triggerRole`

**Description:**

- `triggerWrapper`: By default, the trigger is wrapped in a `<button>` for accessibility. If your trigger content is already a button or contains interactive elements, change this to `'div'`.
- `triggerRole`: Allows overriding the role of the trigger element (e.g., setting it to `'none'` if the child is already a semantic button).
  **Example:** `<DynDropdown triggerWrapper="div" triggerRole="none" ... />`

#### `triggerType`

**Description:** Interaction that opens the menu.

- `click`: Opens on click/touch (Best for accessibility).
- `hover`: Opens on mouse enter (Recommended for tool-style menus).
  **Example:** `<DynDropdown triggerType="hover" ... />`

#### `fullWidth`

**Description:** If `true`, the dropdown panel will have the exact same width as the trigger element. Common for select-style dropdowns.
**Example:** `<DynDropdown fullWidth trigger={<div style={{ width: 400 }}>Trigger</div>} ... />`

#### `usePortal`

**Description:** Renders the dropdown content via `React.createPortal` into the document body. This prevents the menu from being clipped by containers with `overflow: hidden`.
**Example:** `<DynDropdown usePortal={false} ... />`

## 🎨 Design Tokens

- **Background**: `--dyn-dropdown-bg`
- **Border**: `--dyn-dropdown-border`
- **Shadow**: `--dyn-dropdown-shadow`
- **Item Hover**: `--dyn-dropdown-item-hover-bg`
- **Separator**: `--dyn-dropdown-divider`

## ♿ Accessibility (A11y)

- **Roles**: Uses `menu` and `menuitem` roles.
- **Attributes**:
  - Trigger has `aria-haspopup="true"`.
  - `aria-expanded` reflects the Current state.
  - `aria-controls` links the trigger to the menu.
- **Keyboard**:
  - `Enter` / `Space`: Toggle menu.
  - `Escape`: Close menu.
  - _Note: Arrow key navigation within the menu is currently managed by native focus management._

## 🔌 Imperative API (Ref)

```tsx
const dropdownRef = useRef<DynDropdownRef>(null);

dropdownRef.current?.open(); // Manually open
dropdownRef.current?.close(); // Manually close
dropdownRef.current?.toggle(); // Toggle state
```

## 📝 Best Practices

- ✅ Use `triggerType="click"` for important actions.
- ✅ Always provide icons for menu items to improve scannability.
- ✅ Leave `usePortal` enabled to avoid layout clipping.
- ❌ Avoid putting forms or high-input content inside `DynDropdown`. Use `DynPopup` or `DynDialog` for complex content.
