# DynToast Documentation

## 📌 Overview

**Category:** Organism / Feedback
**Status:** Stable

`DynToast` is a non-obtrusive notification system used to provide feedback on user actions or system events. It operates through a Context-based API, allowing any component in the application tree to trigger localized notifications without managing its own state. The system supports multiple semantic severities, programmable dismissals, and stacked layouts.

## 🛠 Usage

### 1. Root Setup

Wrap your application (usually in `App.tsx` or `_app.tsx`) with the `DynToastProvider`.

```tsx
import { DynToastProvider } from '@dyn-ui/react';

function App() {
  return (
    <DynToastProvider defaultDuration={5000} defaultPosition="top-right">
      <MainLayout />
    </DynToastProvider>
  );
}
```

### 2. Triggering Notifications

Use the `useToast` hook to access the messaging API.

```tsx
import { useToast } from '@dyn-ui/react';

function SaveButton() {
  const toast = useToast();

  const handleSave = () => {
    try {
      // ... save logic
      toast.success('Settings updated successfully');
    } catch (err) {
      toast.error('Failed to save changes', {
        description: 'Please check your connection.',
      });
    }
  };

  return <button onClick={handleSave}>Save</button>;
}
```

## ⚙️ Properties (API)

### DynToastProvider Props

| Prop              | Type               | Default       | Description                                 |
| :---------------- | :----------------- | :------------ | :------------------------------------------ |
| `defaultDuration` | `number`           | `5000`        | Global timeout in ms before auto-dismissal. |
| `defaultPosition` | `DynToastPosition` | `'top-right'` | Default screen corner/edge for toasts.      |
| `maxToasts`       | `number`           | `5`           | Limit of simultaneous notifications.        |

### useToast() API Reference

| Method                | Description                                         |
| :-------------------- | :-------------------------------------------------- |
| `success(msg, opts?)` | Shortcut for a success (Green) notification.        |
| `error(msg, opts?)`   | Shortcut for an error (Red) notification.           |
| `warning(msg, opts?)` | Shortcut for a warning (Amber) notification.        |
| `info(msg, opts?)`    | Shortcut for an info (Blue) notification.           |
| `addToast(item)`      | Generic method for custom notifications.            |
| `removeToast(id)`     | Programmatically closes a specific toast by its ID. |
| `toasts`              | Read-only array of current active toast items.      |

### DynToastItem (Options)

| Option        | Type               | Description                                            |
| :------------ | :----------------- | :----------------------------------------------------- |
| `message`     | `ReactNode`        | **Required.** The primary title of the notification.   |
| `description` | `ReactNode`        | Supplemental details shown below the message.          |
| `duration`    | `number`           | Individual override for auto-dismiss (0 = persistent). |
| `position`    | `DynToastPosition` | Specific position for this toast only.                 |
| `action`      | `Object`           | Render a button with `{ label, onClick }`.             |

## 🎨 Design Tokens

- **Toast BG**: `--dyn-toast-bg`
- **Success Color**: `--dyn-toast-success-color`
- **Error Color**: `--dyn-toast-error-color`
- **Border Radius**: `--dyn-toast-radius`

## ♿ Accessibility (A11y)

- **Portals**: Notifications are rendered via React Portals into a dedicated `#dyn-toast-portal` to avoid CSS stacking context issues.
- **Roles**:
  - Most notifications use `role="status"` with `aria-live="polite"`.
  - Errors automatically use `role="alert"` for immediate screen reader attention.
- **Keyboard**: Users can close the most recent toast using the `Esc` key (if focus management is handled globally).

## 📝 Best Practices

- ✅ Keep messages short (under 10 words).
- ✅ Use `description` for longer technical details or error codes.
- ✅ Provide a clear `action` if the notification informs the user about a reversible mistake (e.g., "Deleted. [Undo]").
- ❌ Don't use toasts for confirmation of critical actions like account deletion (use `DynDialog`).
- ❌ Avoid overlapping multiple toasts in different positions; stick to one or two consistent areas.
- ❌ Don't place important permanent links inside a toast as they disappear.
