# DynLabel Documentation

## 📌 Overview

**Category:** Atom
**Status:** Stable

`DynLabel` is a standardized text component primarily used for labeling form inputs. It manages proper accessibility associations (`htmlFor`) and visual indicators for required/optional states.

## 🛠 Usage

```tsx
import { DynLabel } from '@dyn-ui/react';

function Example() {
  return (
    <>
      <DynLabel htmlFor="email-input" required>
        Email Address
      </DynLabel>
      <input id="email-input" type="email" />
    </>
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop        | Type            | Default | Description                 | Required |
| :---------- | :-------------- | :------ | :-------------------------- | :------: |
| `children`  | `ReactNode`     | -       | Label text content.         |   Yes    |
| `htmlFor`   | `string`        | -       | ID of the associated input. |    No    |
| `required`  | `boolean`       | `false` | Shows required (`*`).       |    No    |
| `optional`  | `boolean`       | `false` | Shows `(optional)` text.    |    No    |
| `disabled`  | `boolean`       | `false` | Dimmed/disabled styling.    |    No    |
| `helpText`  | `string`        | -       | Additional helper text.     |    No    |
| `className` | `string`        | -       | Additional CSS classes.     |    No    |
| `style`     | `CSSProperties` | -       | Inline styles.              |    No    |
| `id`        | `string`        | -       | Component ID.               |    No    |

### Detailed Parameter Documentation

#### `htmlFor`

**Type:** `string`
**Description:**
The ID of the form element this label corresponds to. If provided, renders a `<label>` element; otherwise renders a `<span>`.

#### `required` / `optional`

**Type:** `boolean`
**Description:**

- `required`: Appends a red asterisk (`*`) inside the label.
- `optional`: Appends `(optional)` text.
  _Note: Do not use both simultaneously._

#### `helpText`

**Type:** `string`
**Description:**
Renders a block of text below the label content. It is automatically associated with the input if `htmlFor` provided via `aria-describedby` logic implies hierarchy (though `DynFieldContainer` usually handles this better).

## 🎨 Design Tokens

- **Valid Color**: `--dyn-label-color`
- **Disabled Color**: `--dyn-disabled-color`
- **Required Indicator**: `--dyn-semantic-error-text`

## ♿ Accessibility (A11y)

- **Associations**: Standard `<label for="id">` behavior.
- **Indicators**: Visual indicators are usually hidden from screen readers (`aria-hidden="true"`) if the input itself has `aria-required`, to avoid double announcement, but this implementation exposes them visually.
