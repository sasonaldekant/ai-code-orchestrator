# DynFieldContainer Documentation

## 📌 Overview

**Category:** Molecule (Form)
**Status:** Stable

`DynFieldContainer` is a utility component that wraps form inputs with a consistent label, error message, and helper text handling. It standardizes the layout for all `Dyn*` form fields (`DynInput`, `DynSelect`, `DynDatePicker`, etc.).

## 🛠 Usage

This component is typically used internally by other form components, but can be used directly when wrapping third-party inputs.

```tsx
import { DynFieldContainer } from '@dyn-ui/react';

function Example() {
  return (
    <DynFieldContainer
      label="Username"
      required
      helpText="Must be unique."
      htmlFor="username-input"
    >
      <input id="username-input" className="my-custom-input" />
    </DynFieldContainer>
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop             | Type      | Default | Description                   | Required |
| :--------------- | :-------- | :------ | :---------------------------- | :------: |
| `label`          | `string`  | -       | Field label.                  |    No    |
| `required`       | `boolean` | `false` | Shows required (`*`).         |    No    |
| `optional`       | `boolean` | `false` | Shows `(optional)` text.      |    No    |
| `helpText`       | `string`  | -       | Helper text below input.      |    No    |
| `errorText`      | `string`  | -       | Error message (red).          |    No    |
| `showValidation` | `boolean` | `true`  | Toggle validation display.    |    No    |
| `htmlFor`        | `string`  | -       | ID of wrapped input for a11y. |    No    |
| `id`             | `string`  | -       | Container ID.                 |    No    |
| `className`      | `string`  | -       | Custom classes.               |    No    |

### Detailed Parameter Documentation

#### `label`

**Type:** `string`
**Description:**
Renders a `<label>` element above the children. If `htmlFor` matches the child's ID, clicking the label focuses the input.

#### `errorText` / `helpText`

**Type:** `string`
**Description:**

- `errorText`: Replaces `helpText` with a semantic error message (red color, ARIA alert role).
- `helpText`: Standard guidance text.

#### `required` / `optional`

**Type:** `boolean`
**Description:**

- `required`: Appends a red asterisk (`*`) to the label.
- `optional`: Appends `(optional)` text to the label.

## 🎨 Design Tokens

- **Label Color**: `--dyn-field-label-color`
- **Error Color**: `--dyn-semantic-error-text`
- **Help Text Color**: `--dyn-field-help-text-color`
- **Spacing**: `--dyn-field-gap`

## ♿ Accessibility (A11y)

- **Labeling**: Properly associates `label` with inputs via `htmlFor`.
- **Feedback**:
  - Helpers use `div`; ensure inputs point to them via `aria-describedby`.
  - Errors use `role="alert"` and `aria-live="polite"`.
