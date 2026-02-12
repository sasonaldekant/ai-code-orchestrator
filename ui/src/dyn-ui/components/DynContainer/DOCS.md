# DynContainer Documentation

## 📌 Overview

**Category:** Molecule (Layout)
**Status:** Stable

`DynContainer` is a versatile layout component that wraps content with standardized padding, background, borders, and spacing. It includes optional header functionality (title/subtitle) and supports both fluid and fixed layouts.

## 🛠 Usage

```tsx
import { DynContainer, DynButton } from '@dyn-ui/react';

function Example() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Standard Card-like Container */}
      <DynContainer
        title="Account Settings"
        subtitle="Manage your profile information"
        background="surface"
        bordered
      >
        <div>User content goes here...</div>
        <DynButton>Save Changes</DynButton>
      </DynContainer>

      {/* Horizontal Layout */}
      <DynContainer direction="horizontal" spacing="sm" background="card">
        <div>Item 1</div>
        <div>Item 2</div>
        <div>Item 3</div>
      </DynContainer>
    </div>
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop         | Type                            | Default      | Description                | Required |
| :----------- | :------------------------------ | :----------- | :------------------------- | :------: |
| `title`      | `string`                        | -            | Header title.              |    No    |
| `subtitle`   | `string`                        | -            | Header subtitle.           |    No    |
| `direction`  | `'vertical' \| 'horizontal'`    | `'vertical'` | Flex direction of content. |    No    |
| `align`      | `'start' \| 'center' \| ...`    | -            | Cross-axis alignment.      |    No    |
| `justify`    | `'start' \| 'center' \| ...`    | -            | Main-axis alignment.       |    No    |
| `background` | `'none' \| 'surface' \| 'card'` | `'surface'`  | Background style.          |    No    |
| `bordered`   | `boolean`                       | `true`       | Show border.               |    No    |
| `shadow`     | `boolean`                       | `false`      | Show shadow.               |    No    |
| `size`       | `'sm' \| 'md' \| 'lg'`          | `'md'`       | Padding size.              |    No    |
| `spacing`    | `SpacingToken`                  | `'md'`       | Gap between children.      |    No    |
| `layout`     | `'fluid' \| 'fixed'`            | `'fluid'`    | Width behavior.            |    No    |
| `maxWidth`   | `string \| number \| Token`     | -            | Max-width constraint.      |    No    |
| `height`     | `string \| number`              | -            | Fixed height.              |    No    |
| `padding`    | `SpacingToken`                  | -            | Padding override.          |    No    |
| `margin`     | `SpacingToken`                  | -            | Margin override.           |    No    |
| `noBorder`   | `boolean`                       | `false`      | Force no border.           |    No    |
| `noPadding`  | `boolean`                       | `false`      | Force no padding.          |    No    |
| `className`  | `string`                        | -            | Custom classes.            |    No    |
| `layout`     | `'fluid' \| 'fixed'`            | `'fluid'`    | Width behavior.            |    No    |
| `maxWidth`   | `string \| number \| Token`     | -            | Max-width constraint.      |    No    |

### Detailed Parameter Documentation

#### `title` / `subtitle`

**Type:** `string`

**Description:**
If provided, renders a header section at the top of the container with a bottom border, separating it from the main content.

#### `direction`

**Type:** `'vertical' | 'horizontal'`
**Default:** `'vertical'`

**Description:**
Controls the flex direction of the main content area.

- `vertical`: Stacks children via `flex-direction: column`.
- `horizontal`: Arranges children via `flex-direction: row` (supports wrapping).

#### `layout` / `maxWidth`

**Type:** `'fluid' | 'fixed'` / `string | number | Token`

**Description:**

- `layout="fixed"`: Automatically sets `margin: 0 auto` and `maxWidth: 64rem` (approx 1024px).
- `maxWidth`: Can accept tokens (`xs`, `sm`, `md`, `lg`, `xl`, `full`) or raw values (`600px`).

#### `spacing` / `size`

**Type:** `SpacingToken` (`'none'`, `'xs'`, `'sm'`, `'md'`, `'lg'`, etc.)

**Description:**

- `size`: Controls the **padding** around the content.
- `spacing`: Controls the **gap** between children elements.

## 🎨 Design Tokens

- **Colors**:
  - `--dyn-container-bg-val`: Maps to `background` prop.
  - `--dyn-container-border`: Maps to `bordered` prop.
  - `--dyn-container-typography-title-color`
- **Sizing**:
  - `--dyn-container-padding-val`: based on `size`.
  - `--dyn-container-gap-val`: based on `spacing`.
  - `--dyn-border-radius-lg`: standard radius.

## ♿ Accessibility (A11y)

- **Structure**: Uses standard `div` elements.
- **Headings**: `title` renders as `<h2>`, `subtitle` as `<p>`. ensure this hierarchy fits your page structure or use manual headings inside `children` if needed.
- **Landmarks**: Can be used with `role="region"` and `aria-label` for landmark navigation if conceptually distinct.

## 📝 Best Practices

- ✅ **Do** use for grouping related form fields or content sections.
- ✅ **Do** use `maxWidth="sm"` for centered forms to improve readability.
- ❌ **Avoid** nesting containers deeply; use `DynBox` or `DynFlex` for internal layout instead.
