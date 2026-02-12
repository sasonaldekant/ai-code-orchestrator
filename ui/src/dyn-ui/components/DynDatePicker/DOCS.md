# DynDatePicker Documentation

## 📌 Overview

**Category:** Molecule / Form
**Status:** Stable

`DynDatePicker` is a robust date input component with a dropdown calendar. It handles date formatting, validation, range constraints (`min`/`max`), and localization. It integrates seamlessly with `DynFieldContainer` for standard form layouts.

## 🛠 Usage

```tsx
import { DynDatePicker } from '@dyn-ui/react';

function Example() {
  return (
    <>
      {/* Basic usage */}
      <DynDatePicker
        label="Date of Birth"
        onChange={(isoDate) => console.log(isoDate)}
      />

      {/* With Limits and Custom Format */}
      <DynDatePicker
        label="Trip Date"
        min="2024-01-01"
        max="2024-12-31"
        format="MM/dd/yyyy"
        required
      />
    </>
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop           | Type                    | Default        | Description                       | Required |
| :------------- | :---------------------- | :------------- | :-------------------------------- | :------: |
| `name`         | `string`                | -              | Form field name.                  |    No    |
| `value`        | `string`                | -              | Current ISO Date (YYYY-MM-DD).    |    No    |
| `defaultValue` | `string`                | -              | Initial ISO Date (YYYY-MM-DD).    |    No    |
| `onChange`     | `(val: string) => void` | -              | Callback with ISO string.         |    No    |
| `format`       | `string`                | `'dd/MM/yyyy'` | Visual input display format.      |    No    |
| `label`        | `string`                | -              | Visible field label.              |    No    |
| `placeholder`  | `string`                | `'dd/mm/yyyy'` | Text when empty.                  |    No    |
| `min`          | `string`                | -              | Earliest ISO date (YYYY-MM-DD).   |    No    |
| `max`          | `string`                | -              | Latest ISO date (YYYY-MM-DD).     |    No    |
| `size`         | `'sm' \| 'md' \| 'lg'`  | `'md'`         | Input field density.              |    No    |
| `disabled`     | `boolean`               | `false`        | Prevents all interactions.        |    No    |
| `readonly`     | `boolean`               | `false`        | Prevents change but allows focus. |    No    |
| `required`     | `boolean`               | `false`        | Marks as mandatory (\*).          |    No    |
| `optional`     | `boolean`               | `false`        | Displays "(Optional)".            |    No    |
| `helpText`     | `string`                | -              | Helper message below input.       |    No    |
| `errorText`    | `string`                | -              | Explicit error message.           |    No    |
| `weekStartsOn` | `0 \| 1`                | `1`            | Start day (0=Su, 1=Mo).           |    No    |
| `monthNames`   | `string[]`              | (English)      | Custom month labels.              |    No    |
| `weekdayNames` | `string[]`              | (English)      | Custom weekday labels (Su-Sa).    |    No    |
| `todayText`    | `string`                | `'Today'`      | "Today" button label.             |    No    |
| `clearText`    | `string`                | `'Clear'`      | "Clear" button label.             |    No    |
| `id`           | `string`                | Generated      | Unique field ID.                  |    No    |
| `data-testid`  | `string`                | -              | Test identifier.                  |    No    |

### Detailed Parameter Documentation

#### `value` / `onChange`

**Description:** The component strictly uses ISO 8601 (`YYYY-MM-DD`) for its data layer. This ensures that regardless of the visual `format` (e.g., 'MM/DD/YYYY'), your application state remains consistent and timezone-independent.
**Example:**

```tsx
const [date, setDate] = useState('2024-12-25');
<DynDatePicker value={date} onChange={setDate} />;
```

#### `format`

**Description:** Controls how the date is presented to the user in the text input. The parser supports common separators (`/`, `.`, `-`).

- `dd/MM/yyyy` (Default)
- `MM/dd/yyyy`
- `yyyy-MM-dd`
  **Example:** `<DynDatePicker format="MM.dd.yyyy" />`

#### `min` / `max`

**Description:** Constrains the selection range. Dates outside this range will be disabled in the calendar and will trigger validation errors if typed manually.
**Example:** `<DynDatePicker min="2024-01-01" max="2024-12-31" />`

#### `localization` (`monthNames`, `weekdayNames`, etc.)

**Description:** Allows full translation of the calendar UI.

- `weekStartsOn`: Set to `0` for US-style (Sunday) or `1` for ISO-style (Monday).
- `monthNames`: Array of 12 strings.
- `weekdayNames`: Array of 7 strings (starts with Sunday index 0).
  **Example:**

```tsx
<DynDatePicker
  todayText="Danas"
  clearText="Obriši"
  weekStartsOn={1}
  monthNames={['Januar', 'Februar', ...]}
/>
```

#### `size`

**Description:** Adjusts vertical padding and font size of the input.
**Example:** `<DynDatePicker size="sm" label="Compact Date" />`

#### `required` / `optional`

**Description:**

- `required`: Adds a semantic `*` and `aria-required` attribute.
- `optional`: Adds a subtle `(Optional)` text next to the label.
  **Example:** `<DynDatePicker required label="Event Date" />`

## 🎨 Design Tokens

- **Colors**:
  - `--dyn-date-picker-bg`
  - `--dyn-date-picker-border-focus`
  - `--dyn-datePicker-day-selected-bg` (Matches primary theme)
- **Sizing**:
  - `--dyn-datePicker-day-size`
  - `--dyn-datePicker-calendar-width`

## ♿ Accessibility (A11y)

- **Role**: `combobox` for the input, with a `dialog` or `grid` for the calendar popup.
- **Keyboard Navigation**:
  - `Arrow Keys`: Move focus between days in the calendar.
  - `PageUp` / `PageDown`: Switch months.
  - `Enter`: Select the focused day.
  - `Escape`: Close the calendar without selection.
- **ARIA**:
  - Uses `aria-haspopup="dialog"` and `aria-expanded` to communicate state.
  - Properly links labels and help text using `aria-labelledby` and `aria-describedby`.

## 🔌 Imperative API (Ref)

```tsx
const dateRef = useRef<DynDatePickerRef>(null);

dateRef.current?.focus(); // Sets focus to input
dateRef.current?.clear(); // Clears selection
dateRef.current?.validate(); // Triggers manual validation
```

## 📝 Best Practices

- ✅ Use ISO strings (`YYYY-MM-DD`) for all state management.
- ✅ Match the `format` to the user's local convention.
- ✅ Provide `min` and `max` constraints to prevent logical errors in forms.
- ❌ Avoid Date objects as props; the component performs its own parsing.
