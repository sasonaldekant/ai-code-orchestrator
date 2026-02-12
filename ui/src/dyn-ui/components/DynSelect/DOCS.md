# DynSelect Documentation

## 📌 Overview

**Category:** Molecule / Form
**Status:** Stable

`DynSelect` is a high-performance dropdown selection component. It supports single-choice, multiple-choice (with tags), searching, and grouping. It is fully integrated with the `useDynFieldValidation` system and uses `DynFieldContainer` for standard form layouts.

## 🛠 Usage

### Basic Selection

```tsx
import { DynSelect } from '@dyn-ui/react';

const options = [
  { value: 'hr', label: 'Croatia' },
  { value: 'rs', label: 'Serbia' },
  { value: 'me', label: 'Montenegro' },
];

function Example() {
  return (
    <DynSelect
      label="Country"
      options={options}
      placeholder="Select your country"
      onChange={(val) => console.log(val)}
    />
  );
}
```

### Multiple & Searchable

```tsx
<DynSelect
  label="Skills"
  options={skills}
  multiple
  searchable
  clearable
  placeholder="Start typing..."
/>
```

## ⚙️ Properties (API)

### Quick Reference

| Prop                | Type                   | Default       | Description                          | Required |
| :------------------ | :--------------------- | :------------ | :----------------------------------- | :------: |
| `options`           | `DynSelectOption[]`    | `[]`          | List of selectable items.            |   Yes    |
| `value`             | `T \| T[]`             | -             | Controlled value(s).                 |    No    |
| `defaultValue`      | `T \| T[]`             | -             | Initial value(s).                    |    No    |
| `onChange`          | `(val) => void`        | -             | Selection callback.                  |    No    |
| `multiple`          | `boolean`              | `false`       | Allow selecting multiple items.      |    No    |
| `searchable`        | `boolean`              | `false`       | Filter options via text input.       |    No    |
| `clearable`         | `boolean`              | `false`       | Show 'X' button to clear value.      |    No    |
| `label`             | `string`               | -             | Field label text.                    |    No    |
| `placeholder`       | `string`               | `'Select...'` | Empty state text.                    |    No    |
| `size`              | `'sm' \| 'md' \| 'lg'` | `'md'`        | Input density.                       |    No    |
| `disabled`          | `boolean`              | `false`       | Disable all interactions.            |    No    |
| `readOnly`          | `boolean`              | `false`       | Prevent change, keep focusable.      |    No    |
| `loading`           | `boolean`              | `false`       | Show spinner icon.                   |    No    |
| `required`          | `boolean`              | `false`       | Mark as mandatory (\*).              |    No    |
| `validation`        | `DynValidationRule[]`  | `[]`          | Validation rules array.              |    No    |
| `helpText`          | `string`               | -             | Helper text below input.             |    No    |
| `errorText`         | `string`               | -             | Forced error message.                |    No    |
| `searchPlaceholder` | `string`               | `'Search...'` | Placeholder in search box.           |    No    |
| `noOptionsMessage`  | `ReactNode`            | `'No...'`     | Shown when filtering yields nothing. |    No    |
| `maxMenuHeight`     | `number \| string`     | -             | Constrain dropdown list height.      |    No    |

### Detailed Parameter Documentation

#### `value` / `onChange`

**Description:** Communicates the raw `value` from the option objects. If `multiple={true}`, these props expect/return an array of values.
**Example:**

```tsx
const [val, setVal] = useState(['react', 'vue']);
<DynSelect multiple value={val} onChange={setVal} ... />
```

#### `options` (`DynSelectOption` Object)

| Prop       | Type            | Description                                 |
| :--------- | :-------------- | :------------------------------------------ |
| `value`    | `string \| num` | Unique identifier for the option.           |
| `label`    | `string`        | Display text shown in the list and trigger. |
| `disabled` | `boolean`       | Prevents selecting this specific option.    |
| `icon`     | `ReactNode`     | Optional leading icon.                      |
| `group`    | `string`        | Category label (used with `groups` prop).   |

#### `searchable`

**Description:** Renders a text input inside the dropdown. It filters options locally by default using a case-insensitive string match on the `label`.
**Example:** `<DynSelect searchable searchPlaceholder="Type to filter..." />`

#### `multiple`

**Description:** When active, selected options are displayed inside the trigger area as "Tags" with their own clear buttons. The dropdown remains open for multiple clicks unless closed manually.

#### `validation`

**Description:** Full integration with the DynUI field validation system. It supports `required`, custom regex, and manual `onValidate` callbacks.
**Example:** `validation={[{ type: 'required', message: 'Selection is required.' }]}`

## 🎨 Design Tokens

- **Background**: `--dyn-select-bg`
- **Focus Border**: `--dyn-select-border-focus`
- **Option Hover**: `--dyn-select-option-hover`
- **Selected Text**: `--dyn-select-selected-color`

## ♿ Accessibility (A11y)

- **Role**: `combobox` for the trigger, `listbox` for the menu, and `option` for items.
- **States**: Correctly manages `aria-expanded`, `aria-haspopup`, and `aria-selected`.
- **Keyboard**:
  - `Enter` / `Space` / `ArrowDown`: Open menu.
  - `Escape`: Close menu.
  - `Tab` / `Shift+Tab`: Focus management (Portal-safe focus release).

## 🔌 Imperative API (Ref)

```tsx
const selectRef = useRef<DynSelectRef>(null);

selectRef.current?.open(); // Programmatically open dropdown
selectRef.current?.clear(); // Unset all values
selectRef.current?.validate(); // Manual validation trigger
```

## 🧩 Related Components

- [DynDropdown](../DynDropdown/DOCS.md) - The underlying popup engine.
- [DynInput](../DynInput/DOCS.md) - Sister form component for text entry.
- [DynRadio](../DynRadio/DOCS.md) - Alternative for few options.
