# DynInput Documentation

## 📌 Overview

**Category:** Molecule  
**Status:** Stable (GOLD STANDARD)

A comprehensive text input component supporting multiple types (text, password, email, number, currency), validation, masking, and icons. Serves as the **reference implementation** for all form field components.

## 🛠 Usage

```tsx
import { DynInput } from '@dyn-ui/react';

function Example() {
  return (
    <DynInput
      label="Email"
      type="email"
      placeholder="Enter your email"
      required
      validation={[{ type: 'email', message: 'Invalid email format' }]}
    />
  );
}
```

### Currency Input

```tsx
<DynInput
  type="currency"
  label="Price"
  currencyConfig={{
    currencyCode: 'EUR',
    precision: 2,
    thousandSeparator: '.',
    decimalSeparator: ',',
  }}
/>
```

### Masked Input

```tsx
<DynInput label="Phone" mask="(99) 9999-9999" placeholder="(00) 0000-0000" />
```

## ⚙️ Properties (API)

| Prop              | Type                                                        | Default  | Description                           | Required |
| :---------------- | :---------------------------------------------------------- | :------- | :------------------------------------ | :------: |
| `name`            | `string`                                                    | -        | Input name attribute.                 |    No    |
| `label`           | `string`                                                    | -        | Label text.                           |    No    |
| `type`            | `'text' \| 'password' \| 'email' \| 'number' \| 'currency'` | `'text'` | Input type.                           |    No    |
| `size`            | `'sm' \| 'md' \| 'lg'`                                      | `'md'`   | Size variant.                         |    No    |
| `value`           | `string \| number`                                          | -        | Controlled value.                     |    No    |
| `placeholder`     | `string`                                                    | -        | Placeholder text.                     |    No    |
| `disabled`        | `boolean`                                                   | `false`  | Disabled state.                       |    No    |
| `readOnly`        | `boolean`                                                   | `false`  | Read-only state.                      |    No    |
| `required`        | `boolean`                                                   | `false`  | Required field indicator.             |    No    |
| `optional`        | `boolean`                                                   | `false`  | Optional field indicator.             |    No    |
| `visible`         | `boolean`                                                   | `true`   | Controls visibility.                  |    No    |
| `help`            | `string`                                                    | -        | Helper text below input.              |    No    |
| `helpText`        | `string`                                                    | -        | Alias for `help`.                     |    No    |
| `errorMessage`    | `string`                                                    | -        | Custom error message (overrides val). |    No    |
| `successMessage`  | `string`                                                    | -        | Success message.                      |    No    |
| `validation`      | `DynValidationRule \| DynValidationRule[]`                  | -        | Validation rules.                     |    No    |
| `mask`            | `string \| DynInputMask`                                    | -        | Input mask pattern.                   |    No    |
| `maskFormatModel` | `boolean`                                                   | `false`  | Include mask characters in value.     |    No    |
| `currencyConfig`  | `CurrencyInputConfig`                                       | -        | Currency formatting config.           |    No    |
| `icon`            | `string \| ReactNode`                                       | -        | Leading icon.                         |    No    |
| `showClearButton` | `boolean`                                                   | `false`  | Show clear button when valued.        |    No    |
| `showSpinButtons` | `boolean`                                                   | `false`  | Show arrows for number/currency.      |    No    |
| `loading`         | `boolean`                                                   | `false`  | Show loading state.                   |    No    |
| `min`             | `number`                                                    | -        | Minimum numeric value.                |    No    |
| `max`             | `number`                                                    | -        | Maximum numeric value.                |    No    |
| `step`            | `number`                                                    | -        | Numeric step increment.               |    No    |
| `onChange`        | `(value: string \| number) => void`                         | -        | Change handler.                       |    No    |
| `onBlur`          | `FocusEventHandler`                                         | -        | Blur handler.                         |    No    |
| `onFocus`         | `FocusEventHandler`                                         | -        | Focus handler.                        |    No    |
| `onValidate`      | `(isValid: boolean, error?: string) => void`                | -        | Validation state callback.            |    No    |
| `onKeyDown`       | `KeyboardEventHandler`                                      | -        | Key down handler.                     |    No    |
| `id`              | `string`                                                    | -        | Unique identifier.                    |    No    |
| `className`       | `string`                                                    | -        | Additional CSS classes.               |    No    |
| `style`           | `CSSProperties`                                             | -        | Inline styles.                        |    No    |
| `data-testid`     | `string`                                                    | -        | Test identifier.                      |    No    |

### Detailed Parameter Documentation

#### `name`

**Description:** The name attribute of the input element, used for form identification. Also used as the default ID if `id` is not provided.
**Example:** `<DynInput name="user_email" />`

#### `label`

**Description:** Text label displayed above the input.
**Example:** `<DynInput label="Username" />`

#### `type`

**Description:** Specifies the behavior and formatting of the input.

- `text`: Standard text input.
- `password`: Masked characters for sensitive data.
- `email`: Enforces email format validation.
- `number`: Native numeric input behavior.
- `currency`: Specialized formatting for monetary values.
  **Example:** `<DynInput type="password" label="Password" />`

#### `size`

**Description:** Defines the padding and font-size of the input based on design tokens.

- `sm`: Small density.
- `md`: Standard/Medium density (default).
- `lg`: Large/High density.
  **Example:** `<DynInput size="lg" label="Search" />`

#### `value`

**Description:** The controlled value of the input.
**Example:** `<DynInput value={formState.email} onChange={handleEmailChange} />`

#### `placeholder`

**Description:** Hint text displayed when the input is empty.
**Example:** `<DynInput placeholder="e.g. john@doe.com" />`

#### `disabled`

**Description:** If `true`, prevents user interaction and applies disabled styling.
**Example:** `<DynInput disabled label="Locked Field" value="Cannot edit me" />`

#### `readOnly` / `readonly`

**Description:** If `true`, the value cannot be modified, but it can still be focused and selected.
**Example:** `<DynInput readOnly label="Reference ID" value="123456" />`

#### `required`

**Description:** If `true`, a red asterisk is shown and validation will fail if empty.
**Example:** `<DynInput required label="First Name" />`

#### `optional`

**Description:** If `true`, displays an "(optional)" hint next to the label.
**Example:** `<DynInput optional label="Middle Name" />`

#### `visible`

**Description:** Controls whether the component is rendered in the DOM.
**Example:** `<DynInput visible={showAddressFields} label="City" />`

#### `help` / `helpText`

**Description:** Explanatory text displayed below the input.
**Example:** `<DynInput help="Password must be at least 8 characters long." />`

#### `errorMessage`

**Description:** An external error message. If provided, it overrides internal validation messages.
**Example:** `<DynInput errorMessage="This email is already taken" />`

#### `successMessage`

**Description:** Message shown when the input is valid.
**Example:** `<DynInput successMessage="Domain is available!" />`

#### `validation`

**Description:** A single rule or array of rules for validation. Supports objects with `type`, `value`, and `message`.
**Example:**

```tsx
<DynInput
  validation={[
    { type: 'required', message: 'Field is required' },
    { type: 'minLength', value: 5, message: 'Too short' },
  ]}
/>
```

#### `mask`

**Description:** Enforces a specific input pattern (e.g., phone, license plates).
**Example:** `<DynInput mask="(99) 9999-9999" placeholder="(00) 0000-0000" />`

#### `maskFormatModel`

**Description:** If `true`, the `onChange` callback will receive the value including mask characters. If `false` (default), only raw digits/characters are returned.
**Example:** `<DynInput mask="99-99" maskFormatModel={true} />`

#### `currencyConfig`

**Description:** Configuration Object for `type="currency"`.
**Example:**

```tsx
<DynInput
  type="currency"
  currencyConfig={{
    currencyCode: 'USD',
    symbol: '$',
    precision: 2,
  }}
/>
```

#### `icon`

**Description:** An icon to display inside the input box (usually on the left).
**Example:** `<DynInput icon="user" label="User" />`

#### `showClearButton` / `showCleanButton`

**Description:** Displays a 'clear' (X) button when the input has content.
**Example:** `<DynInput showClearButton label="Search" />`

#### `showSpinButtons`

**Description:** Shows increment/decrement arrows for `number` or `currency` types.
**Example:** `<DynInput type="number" showSpinButtons step={10} />`

#### `loading`

**Description:** Displays a loading spinner or state (if implemented by the container).
**Example:** `<DynInput loading label="Validating..." />`

#### `min` / `max` / `step`

**Description:** Standard numeric constraints for `type="number"` or `type="currency"`.
**Example:** `<DynInput type="number" min={0} max={100} step={5} />`

#### `onChange`

**Description:** Callback fired when the value changes.
**Example:** `onChange={(val) => console.log('New Value:', val)}`

#### `onValidate`

**Description:** Callback fired whenever validation state changes.
**Example:** `onValidate={(isValid, error) => setFormValid(isValid)}`

#### `onBlur` / `onFocus`

**Description:** Standard focus event handlers.
**Example:** `onBlur={(e) => log('Lost focus')}`

#### `id`

**Description:** Unique DOM identifier.
**Example:** `<DynInput id="unique-email-field" />`

#### `className` / `style`

**Description:** Standard props for adding custom CSS classes or inline styles.
**Example:** `<DynInput className="my-custom-margin" style={{ maxWidth: 400 }} />`

#### `data-testid`

**Description:** Attribute for automated testing.
**Example:** `<DynInput data-testid="login-password-input" />`

## 🎨 Design Tokens

### Component Tokens

| Token                      | Default Value                          | Description        |
| -------------------------- | -------------------------------------- | ------------------ |
| `--dyn-input-bg`           | `var(--dyn-semantic-input-bg)`         | Background color   |
| `--dyn-input-color`        | `var(--dyn-semantic-text)`             | Text color         |
| `--dyn-input-border`       | `var(--dyn-semantic-input-border)`     | Border color       |
| `--dyn-input-border-focus` | `var(--dyn-theme-primary)`             | Focus border color |
| `--dyn-input-placeholder`  | `var(--dyn-semantic-text-secondary)`   | Placeholder color  |
| `--dyn-input-error`        | `var(--dyn-feedback-negative-default)` | Error state color  |
| `--dyn-input-radius`       | `var(--dyn-border-radius-md)`          | Border radius      |

### Customization

```css
.my-custom-input {
  --dyn-input-border-focus: #8b5cf6; /* Purple focus */
}
```

## ♿ Accessibility (A11y)

- **Role**: Native `<input>` element
- **Labeling**: Uses `<label>` with `htmlFor` association
- **Keyboard**:
  - `Tab`: Focuses the input
  - `Escape`: Clears input (if clear button visible)
- **ARIA Attributes**:
  - `aria-invalid`: Set when validation fails
  - `aria-required`: Set when required
  - `aria-describedby`: Links to help/error text

## 🔌 Imperative API (Ref)

```tsx
const inputRef = useRef<DynInputRef>(null);

// Available methods:
inputRef.current?.focus();
inputRef.current?.blur();
inputRef.current?.clear();
inputRef.current?.validate();
inputRef.current?.clearError();
inputRef.current?.getValue();
inputRef.current?.setValue('new value');
```

## 🧩 Related Components

- [DynFieldContainer](../DynFieldContainer/DOCS.md) - Wrapper used internally
- [DynTextArea](../DynTextArea/DOCS.md) - Multi-line variant

## 📝 Best Practices

- ✅ Always provide a `label` for accessibility
- ✅ Use `validation` prop for form validation
- ✅ Use `type="currency"` with `currencyConfig` for monetary values
- ❌ Don't use `type="number"` for phone numbers (use mask instead)
