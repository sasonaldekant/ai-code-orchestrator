# DynModal Documentation

## 📌 Overview

**Category:** Organism / Overlay
**Status:** Stable

`DynModal` is a robust dialog component used for critical user interactions, confirmations, and displaying focused content. It features a backdrop, focus trapping, and semi-automated accessibility management.

## 🛠 Usage

```tsx
import { DynModal, DynButton } from '@dyn-ui/react';

function Example() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <DynButton onClick={() => setIsOpen(true)}>Open Modal</DynButton>

      <DynModal
        isOpen={isOpen}
        title="Settings"
        onClose={() => setIsOpen(false)}
        footer={
          <DynButton variant="primary" onClick={() => setIsOpen(false)}>
            Close
          </DynButton>
        }
      >
        <p>Your changes have been saved successfully.</p>
      </DynModal>
    </>
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop                   | Type                             | Default   | Description                            | Required |
| :--------------------- | :------------------------------- | :-------- | :------------------------------------- | :------: |
| `isOpen`               | `boolean`                        | -         | Visibility of the modal.               |   Yes    |
| `onClose`              | `() => void`                     | -         | Callback fired when closing requested. |   Yes    |
| `title`                | `ReactNode`                      | -         | Header text/node.                      |    No    |
| `children`             | `ReactNode`                      | -         | Body content.                          |   Yes    |
| `footer`               | `ReactNode`                      | -         | Action area at bottom.                 |    No    |
| `size`                 | `'sm' \| 'md' \| 'lg' \| 'full'` | `'md'`    | Modal width variant.                   |    No    |
| `fullscreen`           | `boolean`                        | `false`   | Spans entire viewport.                 |    No    |
| `centered`             | `boolean`                        | `true`    | Vertically and horizontally centered.  |    No    |
| `closeOnBackdropClick` | `boolean`                        | `true`    | Close when clicking the overlay.       |    No    |
| `closeOnEsc`           | `boolean`                        | `true`    | Close when pressing Escape.            |    No    |
| `showCloseButton`      | `boolean`                        | `true`    | Show "X" button in header.             |    No    |
| `loading`              | `boolean`                        | `false`   | Show loading state inside modal.       |    No    |
| `portalContainer`      | `HTMLElement`                    | `body`    | Render target element.                 |    No    |
| `className`            | `string`                         | -         | Additional body classes.               |    No    |
| `id`                   | `string`                         | Generated | Modal ID for ARIA.                     |    No    |

### Detailed Parameter Documentation

#### `isOpen`

**Description:** Essential boolean to control rendering. It is recommended to handle this via state.
**Example:** `<DynModal isOpen={visible} ... />`

#### `onClose`

**Description:** This handler should set `isOpen` to `false`. It is triggered by the Close Button, Backdrop Click (if enabled), and Escape key (if enabled).
**Example:** `onClose={() => setVisible(false)}`

#### `size`

**Description:** Defines the maximum width of the modal container.

- `sm`: 320px
- `md`: 560px (default)
- `lg`: 800px
- `full`: 100% (with margins)
  **Example:** `<DynModal size="lg" ... />`

#### `centered`

**Description:** If `true`, the modal is positioned in the exact middle of the screen. If `false`, it appears near the top with a standard margin.
**Example:** `<DynModal centered={false} ... />`

#### `fullscreen`

**Description:** Completely fills the browser window, removing borders and shadows. Useful for complex forms or editors.
**Example:** `<DynModal fullscreen ... />`

#### `footer`

**Description:** A dedicated slot at the bottom of the modal, usually containing action buttons.
**Example:**

```tsx
<DynModal footer={<DynButton>Execute</DynButton>} ... />
```

## 🎨 Design Tokens

- **Backdrop Color**: `--dyn-modal-backdrop`
- **Surface Color**: `--dyn-modal-bg`
- **Border Radius**: `--dyn-modal-radius`
- **Shadow**: `--dyn-modal-shadow`

## ♿ Accessibility (A11y)

- **Role**: `dialog` with `aria-modal="true"`.
- **Focus Management**:
  - **Focus Trap**: User cannot tab out of the modal while it is open.
  - **Initial Focus**: Automatically focuses the first interactive element or the close button.
  - **Restore Focus**: Returns focus to the element that triggered the modal upon closing.
- **Labels**: Header text is automatically linked via `aria-labelledby`.

## 📝 Best Practices

- ✅ Use `footer` for primary/secondary action buttons.
- ✅ Keep Titles concise and descriptive.
- ✅ Disable `closeOnBackdropClick` for security-sensitive forms.
- ❌ Avoid nesting multiple modals; consider a wizard pattern instead.
