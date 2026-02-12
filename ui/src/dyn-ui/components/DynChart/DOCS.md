# DynChart Documentation

## 📌 Overview

**Category:** Organism
**Status:** Stable

`DynChart` is a versatile data visualization component that renders Line, Bar, Pie, and Area charts using HTML5 Canvas. It features built-in responsiveness, interactive tooltips, legends, and full Design Token integration. It is designed to be accessible, supporting screen readers via proper ARIA roles and descriptions.

## 🛠 Usage

```tsx
import { DynChart } from '@dyn-ui/react';

function Example() {
  const data = [
    { label: 'Jan', value: 100 },
    { label: 'Feb', value: 120 },
    { label: 'Mar', value: 90 },
  ];

  return (
    <DynChart
      type="bar"
      title="Monthly Sales"
      data={data}
      width={600}
      height={300}
    />
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop              | Type                                 | Default            | Description                               | Required |
| :---------------- | :----------------------------------- | :----------------- | :---------------------------------------- | :------: |
| `type`            | `'line' \| 'bar' \| 'pie' \| 'area'` | `'line'`           | Chart visualization variant               |    No    |
| `data`            | `DynChartData`                       | `[]`               | Data points or series to render           |    No    |
| `title`           | `string`                             | -                  | Primary chart title                       |    No    |
| `subtitle`        | `string`                             | -                  | Secondary chart subtitle                  |    No    |
| `width`           | `number`                             | `400`              | Canvas width in pixels                    |    No    |
| `height`          | `number`                             | `300`              | Canvas height in pixels                   |    No    |
| `colors`          | `string[]`                           | `['#0066cc', ...]` | Custom color palette                      |    No    |
| `showLegend`      | `boolean`                            | `true`             | Toggle legend visibility                  |    No    |
| `showTooltip`     | `boolean`                            | `true`             | Toggle tooltip interactions               |    No    |
| `showGrid`        | `boolean`                            | `true`             | Toggle grid lines (except Pie)            |    No    |
| `xAxis`           | `ChartAxis`                          | -                  | X-axis configuration                      |    No    |
| `yAxis`           | `ChartAxis`                          | -                  | Y-axis configuration                      |    No    |
| `ariaDescription` | `string`                             | -                  | Accessible description for screen readers |    No    |

### Detailed Parameter Documentation

#### `type`

**Type:** `'line' | 'bar' | 'pie' | 'area'`
**Default:** `'line'`
**Required:** No

**Description:**
Determines the visualization style of the chart.

**Possible Values:**

- `line` - Connects data points with lines. Best for trends over time.
- `bar` - Displays data as vertical bars. Best for comparing categories.
- `pie` - Displays data as slices of a circle. Best for part-to-whole relationships.
- `area` - Similar to line chart but fills the area below the line.

**Example:**

```tsx
<DynChart type="pie" data={pieData} />
```

#### `data`

**Type:** `ChartDataPoint[] | ChartSeries[]`
**Default:** `[]`
**Required:** No

**Description:**
The core data to be visualized. Can be a simple array of points (for single series) or an array of series objects (for multi-series charts).

**Structure:**

- **ChartDataPoint**: `{ label?: string; value: number; color?: string; }`
- **ChartSeries**: `{ name: string; data: ChartDataPoint[]; color?: string; }`

**Example:**

```tsx
// Simple Data
<DynChart
  data={[
    { label: 'A', value: 10 },
    { label: 'B', value: 20 }
  ]}
/>

// Multi-series Data
<DynChart
  data={[
    { name: 'Series 1', data: [{ value: 10 }, { value: 20 }] },
    { name: 'Series 2', data: [{ value: 15 }, { value: 25 }] }
  ]}
/>
```

#### `width` / `height`

**Type:** `number`
**Default:** `width: 400`, `height: 300`
**Required:** No

**Description:**
Sets the logic dimensions of the canvas. The chart will scale visually but these define the coordinate space and aspect ratio.

**Notes:**

- Ensure `width` and `height` provide enough space for labels and legends.
- Pie charts use `min(width, height)` to determine radius.

#### `colors`

**Type:** `string[]`
**Default:** `['#0066cc', '#00b248', '#f44336', '#ff9800', '#9c27b0']`
**Required:** No

**Description:**
An array of hex color strings used to color the chart series or slices. If specific colors are not provided in `data` items, colors are cycled from this palette.

**Example:**

```tsx
<DynChart
  colors={['#FF0000', '#00FF00', '#0000FF']}
  data={...}
/>
```

#### `xAxis` / `yAxis`

**Type:** `ChartAxis`
**Required:** No

Configuration for the X and Y axes.

**Structure:**

```ts
interface ChartAxis {
  title?: string;
  min?: number; // Force minimum value
  max?: number; // Force maximum value
  format?: (value: number) => string; // Custom label formatter
}
```

**Example:**

```tsx
<DynChart
  xAxis={{ title: 'Month' }}
  yAxis={{ title: 'Revenue ($)', min: 0 }}
  data={...}
/>
```

#### `id` / `className` / `style`

**Type:** `string` / `string` / `CSSProperties`

Standard HTML attributes for customization. `id` allows linking external labels (though `aria-labelledby` is handled automatically).

#### `children`

**Type:** `ReactNode`

Rendered below the chart canvas. Useful for adding custom legends, data tables, or distinct footnotes.

#### `data-testid`

**Type:** `string`
**Default:** `'dyn-chart'` (or derived from defaults)

Used for automated testing.

#### `ariaDescription`

**Type:** `string`
**Default:** -
**Required:** No

**Description:**
Provides a long text description of the chart's content, trends, or purpose. This is essential for users who cannot see the visual chart. It is rendered in a `<figcaption>` element but can be visually hidden or styled.

**Example:**

```tsx
<DynChart
  title="Revenue 2023"
  ariaDescription="Bar chart showing revenue peaking in Q4 with a 20% increase over Q3."
  data={...}
/>
```

## 🎨 Design Tokens

This component uses the following design tokens for styling:

- **Background**: `--dyn-chart-bg` (default: `--dyn-semantic-background`)
- **Border**: `--dyn-chart-border` (default: `--dyn-semantic-border`)
- **Text**:
  - `--dyn-chart-text-primary` (default: `--dyn-semantic-text`)
  - `--dyn-chart-text-secondary` (default: `--dyn-semantic-text-secondary`)
  - `--dyn-chart-font-size` (default: `--dyn-font-size-xs`)
  - `--dyn-chart-contrast-text` (default: `var(--dyn-base-white)`)
- **Grid/Axis**:
  - `--dyn-chart-grid` (default: `--dyn-semantic-border-subtle`)
  - `--dyn-chart-axis` (default: `--dyn-semantic-border-strong`)
- **Radius**: `--dyn-chart-radius` (default: `--dyn-border-radius-md`)

### Customization

Override these tokens in your theme or local CSS:

```css
.my-custom-chart-theme {
  --dyn-chart-grid: dashed 1px #ccc;
  --dyn-chart-bg: #f9f9f9;
}
```

## ♿ Accessibility (A11y)

- **Role**: `img` (Canvas element)
- **Structure**: Uses `<figure>` and `<figcaption>` for semantic grouping.
- **Labels**:
  - `aria-labelledby` links the `canvas` to the chart `title`.
  - `aria-describedby` links the `canvas` to `subtitle` and `ariaDescription`.
- **Tooltips**: Not accessible via keyboard (current limitation), but data should be accessible via `ariaDescription` or accompanying table.
- **Contrast**: Text colors use semantic tokens compliant with WCAG/APCA rules in standard themes.

## 📝 Best Practices

- ✅ **Do** provide a clear `title` and `ariaDescription` for every chart.
- ✅ **Do** use `type="bar"` for categorical data and `type="line"` for continuous time data.
- ❌ **Avoid** overloading a Pie chart with more than 5-7 slices (it becomes unreadable).
- ❌ **Avoid** relying solely on color to convey meaning; ensure labels or legends are clear.
