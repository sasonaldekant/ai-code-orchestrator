# DynProgress Documentation

## 📌 Overview

**Category:** Atom
**Status:** Stable

`DynProgress` is a horizontal progress indicator used to visualize the completion status of a process or a value within a range. It supports semantic statuses, multiple sizes, indeterminate loading states, and animated striped patterns.

## 🛠 Usage

```tsx
import { DynProgress } from '@dyn-ui/react';

// Basic progress
<DynProgress value={60} />

// With label and percentage
<DynProgress value={45} label="Uploading..." showPercentage />

// Success state
<DynProgress value={100} status="success" label="Complete" />

// Indeterminate (loading)
<DynProgress indeterminate label="Downloading data..." />
```

## ⚙️ Properties (API)

### Quick Reference

| Prop             | Type                   | Default     | Description                      | Required |
| :--------------- | :--------------------- | :---------- | :------------------------------- | :------: |
| `value`          | `number`               | `0`         | Current progress value.          |    No    |
| `min`            | `number`               | `0`         | Minimum value.                   |    No    |
| `max`            | `number`               | `100`       | Maximum value.                   |    No    |
| `status`         | `DynProgressStatus`    | `'default'` | Semantic color theme.            |    No    |
| `size`           | `DynProgressSize`      | `'md'`      | Bar thickness variant.           |    No    |
| `label`          | `string`               | -           | Text shown above the bar.        |    No    |
| `showPercentage` | `boolean`              | `false`     | Display percentage text.         |    No    |
| `indeterminate`  | `boolean`              | `false`     | Continuous loading animation.    |    No    |
| `striped`        | `boolean`              | `false`     | Angled stripe pattern on bar.    |    No    |
| `animated`       | `boolean`              | `false`     | Whether stripes are moving.      |    No    |
| `height`         | `number`               | -           | Custom height in pixels.         |    No    |
| `formatValue`    | `(val, pct) => string` | -           | Custom text formatter for label. |    No    |
| `aria-label`     | `string`               | -           | Accessibility label.             |    No    |
| `className`      | `string`               | -           | Custom CSS classes.              |    No    |

### Detailed Parameter Documentation

#### `status`

**Description:** Defines the color theme of the filled portion.

- `default`: Theme primary color.
- `success`: Green (Feedback positive).
- `error`: Red (Feedback negative).
- `warning`: Amber (Feedback warning).
- `info`: Blue (Feedback info).
  **Example:** `<DynProgress status="error" value={90} />`

#### `size`

**Description:** Mapped to predefined heights.

- `xs`: 4px
- `sm`: 8px
- `md`: 12px (Default)
- `lg`: 16px
- `xl`: 24px
  **Example:** `<DynProgress size="xs" value={50} />`

#### `indeterminate`

**Description:** Use when the exact progress duration is unknown. The bar will show a repeating sliding animation and the `value` prop will be ignored.
**Example:** `<DynProgress indeterminate label="Fetching..." />`

#### `striped` / `animated`

**Description:**

- `striped`: Adds a CSS linear-gradient stripe overlay to the bar.
- `animated`: If `striped` is true, this makes the stripes slide from left to right.
  **Example:** `<DynProgress value={70} striped animated />`

#### `formatValue`

**Description:** Overrides the default percentage display. Receives raw value and calculated percentage.
**Example:** `formatValue={(v) => `${v} of 1024 MB`}`

## 🎨 Design Tokens

- **Track Background**: `--dyn-progress-bg`
- **Bar Background**: `--dyn-progress-bar-bg`
- **Height**: `--dyn-progress-height`
- **Radius**: `--dyn-progress-radius`

## ♿ Accessibility (A11y)

- **Role**: `progressbar`.
- **Attributes**:
  - `aria-valuenow`, `aria-valuemin`, `aria-valuemax` are handled automatically.
  - `aria-busy="true"` is set when `indeterminate` is active.
- **Screen Readers**: Includes a hidden `<span>` describing completion percentage even if `showPercentage` is false.

## 📝 Best Practices

- ✅ Use `status="success"` when a long-running process finishes.
- ✅ Use `indeterminate` for API calls with unknown payload size.
- ✅ Always provide a `label` or `aria-label` to give the progress context.
- ❌ Don't use very large `xl` sizes for simple layout dividers; keep focus on the data.
