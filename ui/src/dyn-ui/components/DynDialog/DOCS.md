# DynDialog Documentation

## 📌 Overview

**Category:** Organism (Modal-based)
**Status:** Stable

`DynDialog` is an imperative, promise-based component for handling system alerts, confirmations, and prompts. It leverages `DynModal` internally but simplifies the API for transactional user interactions via a `ref`.

## 🛠 Usage

## 🛠 Usage

`DynDialog` can be used in two ways:

1. **Hook-based (Recommended)**: Wrap your app in `DynDialogProvider` and use the `useDialog` hook.
2. **Ref-based**: Render `DynDialog` locally and control it via ref (legacy/isolated usage).

### Hook-based (Context)

```tsx
// 1. Wrap your app
import { DynDialogProvider } from '@dyn-ui/react';

function App() {
  return (
    <DynDialogProvider>
      <MainContent />
    </DynDialogProvider>
  );
}

// 2. Use the hook
import { useDialog, DynButton } from '@dyn-ui/react';

function Example() {
  const { confirm, alert, prompt } = useDialog();

  const handleDelete = async () => {
    const isConfirmed = await confirm({
      title: 'Delete User',
      message: 'This action cannot be undone.',
      confirmLabel: 'Delete',
      cancelLabel: 'Cancel',
    });

    if (isConfirmed) {
      await alert('Deleted successfully!');
    }
  };

  return (
    <DynButton onClick={handleDelete} danger>
      Delete
    </DynButton>
  );
}
```

### Ref-based (Component)

```tsx
import { DynDialog, DynDialogRef, DynButton } from '@dyn-ui/react';
import { useRef } from 'react';

function Example() {
  const dialogRef = useRef<DynDialogRef>(null);

  const handleAction = async () => {
    await dialogRef.current?.alert('Hello!');
  };

  return (
    <>
      <DynDialog ref={dialogRef} />
      <DynButton onClick={handleAction}>Show Alert</DynButton>
    </>
  );
}
```

## ⚙️ API (Methods)

The component does not expose standard props (other than `ref`). Interaction is done via the `DynDialogRef` interface.

### `confirm(config)`

Returns `Promise<boolean>`. Resolves to `true` if confirmed, `false` if cancelled.

**Config Object:**
| Property | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `message` | `string` | - | The main body text. |
| `title` | `string` | - | Modal header title. |
| `confirmLabel` | `string` | `'OK'` | Primary button text. |
| `cancelLabel` | `string` | `'Cancel'` | Secondary button text. |
| `placeholder` | `string` | - | (Unused in confirm). |

### `alert(message, title?)`

Returns `Promise<void>`.
Displays a message with a single "OK" button. Resolves when the user closes the dialog.

### `prompt(message, title?, defaultValue?)`

Returns `Promise<string | null>`.
Displays an input field. Resolves to the input string if confirmed, or `null` if cancelled.

## 🎨 Design Tokens

Since it uses `DynModal`, `DynButton`, and `DynInput`, it inherits all their tokens.

- **Background**: `--dyn-modal-bg`
- **Text**: `--dyn-dialog-text-color`
- **Spacing**: `--dyn-dialog-gap`

## ♿ Accessibility (A11y)

- **Focus**: Trap focus within the dialog (inherited from `DynModal`).
- **Keys**:
  - `Escape`: Closes and resolves to `false`/`null`.
  - `Enter`: Confirms (in `prompt`, focuses the button in others).
- **Role**: `dialog` or `alertdialog`.

## 📝 Best Practices

- ✅ **Do** place `DynDialog` high in the tree to ensure it appears above other content.
- ✅ **Do** use `await` to handle the asynchronous nature of user input.
- ❌ **Avoid** using `DynDialog` for complex forms; it is designed for simple transactional steps.
