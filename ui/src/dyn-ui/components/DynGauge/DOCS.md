# DynGauge Documentation

## 📌 Overview

**Category:** Data Display
**Status:** Stable

`DynGauge` is a visualization component for displaying a value within a specific range. It supports arc, circle, and linear layouts, along with color ranges, animations, and custom formatting.

## 🛠 Usage

```tsx
import { DynGauge } from '@dyn-ui/react';

function Example() {
  return (
    <div style={{ display: 'flex', gap: '2rem' }}>
      {/* Basic Usage */}
      <DynGauge value={75} label="Server Load" />

      {/* Custom Ranges */}
      <DynGauge
        value={85}
        title="Performance"
        ranges={[
          { from: 0, to: 60, color: '#4caf50', label: 'Good' },
          { from: 60, to: 90, color: '#ff9800', label: 'Warning' },
          { from: 90, to: 100, color: '#f44336', label: 'Critical' },
        ]}
      />

      {/* Linear Type */}
      <DynGauge type="line" value={45} unit="GB" />
    </div>
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop              | Type                          | Default       | Description                          | Required |
| :---------------- | :---------------------------- | :------------ | :----------------------------------- | :------: |
| `value`           | `number`                      | -             | Current value to display.            |   Yes    |
| `min`             | `number`                      | `0`           | Minimum value.                       |    No    |
| `max`             | `number`                      | `100`         | Maximum value.                       |    No    |
| `type`            | `'arc' \| 'circle' \| 'line'` | `'arc'`       | Visual style of the gauge.           |    No    |
| `size`            | `'sm' \| 'md' \| 'lg'`        | `'md'`        | Size variant.                        |    No    |
| `title`           | `string`                      | -             | Gauge title (header).                |    No    |
| `label`           | `string`                      | -             | Alias for title.                     |    No    |
| `subtitle`        | `string`                      | -             | Secondary text.                      |    No    |
| `unit`            | `string`                      | `'%'`         | Unit text appended to value.         |    No    |
| `ranges`          | `GaugeRange[]`                | `[]`          | Color zones (`from`, `to`, `color`). |    No    |
| `thickness`       | `number`                      | `20`          | Stroke width of the gauge.           |    No    |
| `rounded`         | `boolean`                     | `true`        | Round line caps.                     |    No    |
| `animated`        | `boolean`                     | `true`        | Smooth value transitions.            |    No    |
| `showValue`       | `boolean`                     | `true`        | Display the numeric value.           |    No    |
| `showRanges`      | `boolean`                     | `true`        | Show legends for ranges.             |    No    |
| `color`           | `string`                      | -             | Override main gauge color.           |    No    |
| `backgroundColor` | `string`                      | -             | Background track color.              |    No    |
| `format`          | `(value: number) => string`   | -             | Custom value formatter function.     |    No    |
| `id`              | `string`                      | -             | Unique identifier.                   |    No    |
| `className`       | `string`                      | -             | Additional CSS classes.              |    No    |
| `style`           | `CSSProperties`               | -             | Inline styles.                       |    No    |
| `data-testid`     | `string`                      | `'dyn-gauge'` | Test ID.                             |    No    |

### Detailed Parameter Documentation

#### `value`

**Type:** `number`
**Description:**
The primary metric to visualize. It is clamped between `min` and `max`.

#### `ranges`

**Type:** `GaugeRange[]`
**Structure:**

```ts
interface GaugeRange {
  from: number; // Start value
  to: number; // End value
  color: string; // Segment color
  label?: string; // Legend text
}
```

**Description:**
Defines colored zones on the gauge loop. If the current `value` falls within a range, the needle/arc color changes to match that range (unless `color` is explicitly set).

#### `type`

**Type:** `'arc' | 'circle' | 'line'`
**Default:** `'arc'`

- `arc`: Semi-circular gauge (popular for speedometers).
- `circle`: Full 360-degree ring.
- `line`: Horizontal linear progress bar style.

#### `format`

**Type:** `(value: number) => string`
**Description:**
A function to customize how the value is displayed textually. Replaces the default `number + unit` formatting.

## 🎨 Design Tokens

- **Track Color**: `--dyn-gauge-track` (default `#e0e0e0`)
- **Tick Color**: `--dyn-gauge-ticks` (default `#666`)
- **Text Color**: `--dyn-gauge-text-secondary` (default `#666`)

## ♿ Accessibility (A11y)

- **Role**: `progressbar` (standard for range visualizations).
- **Attributes**:
  - `aria-valuenow`: Current value.
  - `aria-valuemin`: Minimum value.
  - `aria-valuemax`: Maximum value.
  - `aria-labelledby`: Linked to the `title` element.
  - `aria-describedby`: Linked to the `subtitle` element.
