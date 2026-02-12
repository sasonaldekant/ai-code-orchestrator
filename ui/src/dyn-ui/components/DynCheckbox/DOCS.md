# DynCheckbox Documentation

## 📌 Overview

**Category:** Atom (Form)
**Status:** Stable

`DynCheckbox` is a form component that allows users to select one or more options from a set, or toggle a single setting. It supports validation, indeterminate states, and integrates with the `DynFieldContainer`.

## 🛠 Usage

```tsx
import { DynCheckbox } from '@dyn-ui/react';

function Example() {
  return (
    <>
      {/* Simple toggle */}
      <DynCheckbox label="I agree to terms" />

      {/* Required with validation */}
      <DynCheckbox
        label="Subscribe to newsletter"
        required
        onChange={(checked) => console.log(checked)}
      />

      {/* Indeterminate (e.g. for 'Select All') */}
      <DynCheckbox label="Select All" indeterminate={true} />
    </>
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop            | Type                         | Default | Description                      | Required |
| :-------------- | :--------------------------- | :------ | :------------------------------- | :------: |
| `name`          | `string`                     | -       | Form field name.                 |    No    |
| `label`         | `string`                     | -       | Primary label text.              |    No    |
| `checked`       | `boolean`                    | `false` | Controlled state.                |    No    |
| `indeterminate` | `boolean`                    | `false` | Visual indeterminate state.      |    No    |
| `disabled`      | `boolean`                    | `false` | Disables interaction.            |    No    |
| `readonly`      | `boolean`                    | `false` | Prevent changes but allow focus. |    No    |
| `required`      | `boolean`                    | `false` | Marks as required (\*).          |    No    |
| `optional`      | `boolean`                    | `false` | Shows (optional) label info.     |    No    |
| `size`          | `'sm' \| 'md' \| 'lg'`       | `'md'`  | Size variant.                    |    No    |
| `helpText`      | `string`                     | -       | Helper text below input.         |    No    |
| `errorMessage`  | `string`                     | -       | Force error state message.       |    No    |
| `visible`       | `boolean`                    | `true`  | Controls visibility.             |    No    |
| `onChange`      | `(checked: boolean) => void` | -       | Change callback.                 |    No    |
| `onBlur`        | `() => void`                 | -       | Blur handler.                    |    No    |
| `onFocus`       | `FocusEventHandler`          | -       | Focus handler.                   |    No    |
| `id`            | `string`                     | -       | Unique ID.                       |    No    |

### Detailed Parameter Documentation

#### `label`

**Type:** `string`
**Description:**
The text label displayed next to the checkbox. Clicking the label toggles the checkbox.

#### `indeterminate`

**Type:** `boolean`
**Default:** `false`

**Description:**
Sets the checkbox to an indeterminate state (visually distinct from checked/unchecked). This is purely visual and does not affect the `checked` value, but `aria-checked` will be set to `"mixed"`.

#### `validation` / `errorMessage`

**Type:** `ValidationRule[]` / `string`

**Description:**
Built-in validation support via `useDynFieldValidation`. Providing `errorMessage` forces an invalid state.

## 🎨 Design Tokens

- **Colors**:
  - `--dyn-checkbox-bg` (default: `--dyn-semantic-input-bg`)
  - `--dyn-checkbox-bg-checked` (default: `--dyn-theme-primary`)
  - `--dyn-checkbox-border` (default: `--dyn-semantic-input-border`)
- **Sizing**:
  - `--dyn-checkbox-size` (controlled by size prop)
  - `--dyn-checkbox-border-radius` (default: `--dyn-border-radius-xs`)

## ♿ Accessibility (A11y)

- **Role**: Native `<input type="checkbox">` is used visually hidden.
- **States**:
  - `aria-checked` reflects `true`, `false`, or `"mixed"`.
  - `aria-invalid` is set when error is present.
  - `aria-required` is set when required.
- **Keyboard**:
  - Standard `Space` key support.
  - Focus ring visibility on the custom checkbox element key.

## 📝 Best Practices

- ✅ **Do** use `indeterminate` for parent checkboxes in a nested list.
- ✅ **Do** provide `label` for click target size and accessibility.
- ❌ **Avoid** using checkboxes for immediate actions (use `DynSwitch` or `DynButton`).
