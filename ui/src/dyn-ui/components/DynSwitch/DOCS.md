# DynSwitch Documentation

## 📌 Overview

**Category:** Atom / Form
**Status:** Stable

`DynSwitch` is a toggle component used to represent binary (on/off) states. It provides a more modern visual alternative to checkboxes, especially for settings and immediate actions. It supports semantic colors, multiple sizes, and full form validation.

## 🛠 Usage

### Basic Usage

```tsx
import { DynSwitch } from '@dyn-ui/react';

function MySettings() {
  const [enabled, setEnabled] = useState(false);

  return (
    <DynSwitch
      label="Enable Dark Mode"
      checked={enabled}
      onChange={setEnabled}
    />
  );
}
```

### Color and Size Variants

```tsx
<DynSwitch label="Critical Power" color="danger" size="lg" />
<DynSwitch label="Low Energy" color="success" size="sm" />
```

## ⚙️ Properties (API)

### Quick Reference

| Prop             | Type                   | Default     | Description                         | Required |
| :--------------- | :--------------------- | :---------- | :---------------------------------- | :------: |
| `label`          | `ReactNode`            | -           | Text shown next to the switch.      |    No    |
| `checked`        | `boolean`              | -           | Controlled checked state.           |    No    |
| `defaultChecked` | `boolean`              | `false`     | Initial state for uncontrolled use. |    No    |
| `size`           | `'sm' \| 'md' \| 'lg'` | `'md'`      | Scale of the switch track/thumb.    |    No    |
| `color`          | `DynSwitchColor`       | `'primary'` | Semantic theme color when active.   |    No    |
| `disabled`       | `boolean`              | `false`     | Prevents interaction.               |    No    |
| `required`       | `boolean`              | `false`     | Marks as mandatory (\*).            |    No    |
| `helpText`       | `string`               | -           | Helper message below the switch.    |    No    |
| `errorMessage`   | `string`               | -           | Custom error message text.          |    No    |
| `validation`     | `DynValidationRule[]`  | `[]`        | Rules for the validation system.    |    No    |
| `onChange`       | `(checked) => void`    | -           | State change callback.              |    No    |
| `onBlur`         | `() => void`           | -           | Focus loss callback.                |    No    |
| `id`             | `string`               | Generated   | Unique field ID.                    |    No    |

### Detailed Parameter Documentation

#### `color`

**Description:** Changes the background color of the track when the switch is in the "On" state.

- `primary`: Default theme color.
- `success`: Green (Confirmative/Safe).
- `danger`: Red (Critical/Destructive).
- `warning`: Amber (Attention).
- `info`: Blue (Informative).
  **Example:** `<DynSwitch color="success" label="Safe Mode" />`

#### `size`

**Description:** Defines the physical dimensions.

- `sm`: Compact, best for dense tables.
- `md`: Standard form size.
- `lg`: Large, higher touch-surface for mobile.
  **Example:** `<DynSwitch size="sm" label="Allow Analytics" />`

#### `validation` / `required`

**Description:** Integrates with `useDynFieldValidation`. When `required` is true, the switch must be in the "On" state for the field to be considered valid.
**Example:** `validation={[{ type: 'required', message: 'You must accept the terms.' }]}`

## 🎨 Design Tokens

- **Track Background (Off)**: `--dyn-switch-bg-off`
- **Track Background (On)**: `--dyn-switch-bg-on` (Mapped to theme color)
- **Thumb Color**: `--dyn-switch-thumb-bg`
- **Error Border**: `--dyn-switch-error-border`

## ♿ Accessibility (A11y)

- **Role**: `switch`.
- **States**:
  - `aria-checked` reflects the boolean state.
  - `aria-invalid` provides error feedback.
- **Labels**: Label is linked to the hidden input via `htmlFor` and `id`, and also using `aria-labelledby` for the switch role.
- **Keyboard**:
  - `Space` or `Enter`: Toggle the switch state.

## 📝 Best Practices

- ✅ Use `DynSwitch` for settings that take effect immediately.
- ✅ Use a clear, concise label that describes the "On" state.
- ✅ Prefer `DynSwitch` over `DynCheckbox` for standalone toggles in mobile UIs.
- ❌ Don't use a switch if a checkbox label is more descriptive (e.g., "I agree to tokens").
- ❌ Don't use a switch to indicate selection in a long list (use `DynRadio` or `DynCheckbox`).
- ❌ Avoid using `DynSwitch` inside a traditional form that requires a "Submit" button unless the setting is independent of the form submission.
