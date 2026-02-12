# DynRadio & DynRadioGroup Documentation

## 📌 Overview

**Category:** Molecule / Form
**Status:** Stable

`DynRadio` and `DynRadioGroup` provide a set of mutually exclusive options where users can select exactly one choice. `DynRadioGroup` manages the selection state, naming, and layout (orientation) of its child `DynRadio` components.

## 🛠 Usage

### Basic Group

```tsx
import { DynRadioGroup, DynRadio } from '@dyn-ui/react';

function Example() {
  const [size, setSize] = useState('md');

  return (
    <DynRadioGroup label="Choose Size" value={size} onChange={setSize}>
      <DynRadio value="sm" label="Small" />
      <DynRadio value="md" label="Medium" />
      <DynRadio value="lg" label="Large" />
    </DynRadioGroup>
  );
}
```

### Using Options Data

```tsx
const options = [
  { value: 'email', label: 'Email Notifications' },
  { value: 'sms', label: 'SMS Alerts' },
  { value: 'none', label: 'None', disabled: true },
];

<DynRadioGroup
  label="Delivery Method"
  options={options}
  direction="horizontal"
/>;
```

## ⚙️ Properties (API)

### DynRadioGroup

| Prop           | Type                         | Default      | Description                              | Required |
| :------------- | :--------------------------- | :----------- | :--------------------------------------- | :------: |
| `name`         | `string`                     | Generated    | Shared name for the radio group.         |    No    |
| `value`        | `string`                     | -            | Currently selected value.                |    No    |
| `defaultValue` | `string`                     | -            | Initial value for uncontrolled group.    |    No    |
| `label`        | `ReactNode`                  | -            | Group title (Legend).                    |    No    |
| `direction`    | `'vertical' \| 'horizontal'` | `'vertical'` | Layout orientation of items.             |    No    |
| `options`      | `DynSelectOption[]`          | -            | Render radios from data array.           |    No    |
| `helpText`     | `string`                     | -            | Helper text below the group.             |    No    |
| `errorMessage` | `string`                     | -            | Error message displayed when invalid.    |    No    |
| `required`     | `boolean`                    | `false`      | Marks the group as mandatory (\*).       |    No    |
| `validation`   | `DynValidationRule[]`        | -            | Rules for the `useInputValidation` hook. |    No    |
| `onChange`     | `(value: string) => void`    | -            | Callback when selection changes.         |    No    |
| `onValidate`   | `(isValid, msg) => void`     | -            | Callback for validation results.         |    No    |
| `id`           | `string`                     | Generated    | Group identifier.                        |    No    |
| `className`    | `string`                     | -            | Custom wrapper classes.                  |    No    |

### DynRadio (Item)

| Prop          | Type                     | Default | Description                               | Required |
| :------------ | :----------------------- | :------ | :---------------------------------------- | :------: |
| `value`       | `string`                 | -       | The value submitted when selected.        |   Yes    |
| `label`       | `ReactNode`              | -       | Text or element next to the radio.        |    No    |
| `disabled`    | `boolean`                | `false` | Prevents selection/interaction.           |    No    |
| `description` | `ReactNode`              | -       | Detailed text below the label.            |    No    |
| `error`       | `boolean`                | `false` | Apply error styles to this specific item. |    No    |
| `onChange`    | `(checked, val) => void` | -       | Item-level change callback.               |    No    |

### Detailed Parameter Documentation

#### `direction`

**Description:** Controls the flow of radio items.

- `vertical`: (Default) Stacked on top of each other. Best for mobile and many options.
- `horizontal`: Side-by-side. Use only for 2-3 short options.
  **Example:** `<DynRadioGroup direction="horizontal" ... />`

#### `options`

**Description:** A convenient way to render multiple radios without writing each `<DynRadio>` tag manually. It accepts objects with `label`, `value`, and `disabled` properties.
**Example:**

```tsx
<DynRadioGroup
  options={[
    { value: '1', label: 'One' },
    { value: '2', label: 'Two' },
  ]}
/>
```

#### `validation`

**Description:** Integrates with the `useDynFieldValidation` system. You can pass rules like `required` or custom logic.
**Example:** `validation={[{ type: 'required', message: 'Pick one!' }]}`

## 🎨 Design Tokens

- **Radio Border**: `--dyn-radio-border`
- **Radio Checked**: `--dyn-radio-checked-bg`
- **Group Label**: `--dyn-radio-group-label-color`
- **Error Border**: `--dyn-radio-error-border`

## ♿ Accessibility (A11y)

- **Role**: `radiogroup` for the container and `radio` for individual items.
- **Labels**: `DynRadioGroup` uses `<fieldset>` and `<legend>` for proper semantic grouping.
- **Keyboard**:
  - `ArrowUp` / `ArrowDown` / `ArrowLeft` / `ArrowRight`: Navigate and select between radios in the group.
  - `Tab`: Focuses the currently selected radio (or first if none).

## 📝 Best Practices

- ✅ Group related choices using `DynRadioGroup`.
- ✅ Provide a clear `label` for the whole group.
- ✅ Use `direction="horizontal"` only when labels are short and items are few.
- ❌ Don't use Radios if the user can select multiple options (use `DynCheckbox`).
- ❌ Don't use Radios for a single binary choice (use `DynCheckbox` or `DynSwitch`).
