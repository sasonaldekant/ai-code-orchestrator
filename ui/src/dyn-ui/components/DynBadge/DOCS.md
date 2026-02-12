# DynBadge Documentation

## 📌 Overview

**Category:** Atom
**Status:** Stable

`DynBadge` displays counts, status indicators, and semantic labels using design tokens and accessibility best practices. It supports multiple variants (solid, soft, outline, dot), sizes, colors, and positions (including center). It is fully token-compliant and supports dark mode automatically.

## 🛠 Usage

```tsx
import { DynBadge } from '@dyn-ui/react';

function Example() {
  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <DynBadge count={5} color="danger">
        <button>Notifications</button>
      </DynBadge>

      <DynBadge variant="dot" position="topRight" color="success">
        <div className="avatar" />
      </DynBadge>
    </div>
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop               | Type                                        | Default     | Description                                         | Required |
| :----------------- | :------------------------------------------ | :---------- | :-------------------------------------------------- | :------: |
| `children`         | `ReactNode`                                 | -           | Badge content. Ignored if count is set.             |    No    |
| `count`            | `number`                                    | -           | Numeric value to display.                           |    No    |
| `maxCount`         | `number`                                    | `99`        | Max number to display before showing + (e.g., 99+). |    No    |
| `showZero`         | `boolean`                                   | `false`     | Whether to display the badge when the count is 0.   |    No    |
| `variant`          | `'solid' \| 'soft' \| 'outline' \| 'dot'`   | `'solid'`   | Visual style variant.                               |    No    |
| `color`            | `'primary' \| 'secondary' \| 'success' ...` | `'primary'` | Semantic color token.                               |    No    |
| `size`             | `'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl'`      | `'md'`      | Size of the badge.                                  |    No    |
| `position`         | `'topRight' \| 'topLeft' \| ...`            | -           | Absolute position relative to parent.               |    No    |
| `animated`         | `boolean`                                   | `false`     | Enable entrance animation.                          |    No    |
| `pulse`            | `boolean`                                   | `false`     | Enable pulsing animation.                           |    No    |
| `loading`          | `boolean`                                   | `false`     | Loading state (triggers pulse).                     |    No    |
| `startIcon`        | `ReactNode`                                 | -           | Icon element to display before badge text.          |    No    |
| `endIcon`          | `ReactNode`                                 | -           | Icon element to display after badge text.           |    No    |
| `invisible`        | `boolean`                                   | `false`     | Whether badge is invisible but in DOM.              |    No    |
| `onClick`          | `(e) => void`                               | -           | Click handler.                                      |    No    |
| `id`               | `string`                                    | -           | Unique identifier.                                  |    No    |
| `className`        | `string`                                    | -           | Additional CSS classes.                             |    No    |
| `style`            | `CSSProperties`                             | -           | Inline styles.                                      |    No    |
| `role`             | `string`                                    | `'status'`  | ARIA role for the badge.                            |    No    |
| `aria-label`       | `string`                                    | -           | Accessible label for screen readers.                |    No    |
| `countDescription` | `string`                                    | -           | Accessible description announced for count badges.  |    No    |

### Detailed Parameter Documentation

#### `variant`

**Type:** `'solid' | 'soft' | 'outline' | 'dot'`
**Default:** `'solid'`

Controls the visual appearance:

- `solid`: Filled background (default).
- `soft`: Light background with darker text.
- `outline`: Bordered with transparent background.
- `dot`: Small circular indicator, typically used for status.

#### `color`

**Type:** `'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info' | 'neutral'`
**Default:** `'primary'`

Semantic color variants using design tokens.

#### `position`

**Type:** `'topRight' | 'topLeft' | 'bottomRight' | 'bottomLeft' | 'center'`
**Default:** `undefined`

Controls the absolute positioning of the badge relative to its parent container. Useful for status indicators and notification overlays.

#### `count` / `maxCount` / `showZero` / `countDescription`

**Type:** `number`, `number`, `boolean`, `string`

Used for numeric badges.

- `count`: The number to display.
- `maxCount`: The threshold at which numbers become clipped (e.g., `99+`). Defaults to `99`.
- `showZero`: If `true`, the badge renders even if `count` is `0`.
- `countDescription`: Accessible text appended to the count (e.g., "5 _Unread Messages_"). Essential for screen readers to provide context.

#### `animated` / `pulse` / `loading`

**Type:** `boolean`

- `animated`: Applies a smooth entrance animation.
- `pulse`: Applies a continuous pulsing animation, useful for critical notifications or active statuses.
- `loading`: Sets the badge to a loading state, which triggers a pulsing animation and sets `aria-busy="true"`.

#### `startIcon` / `endIcon`

**Type:** `ReactNode`

Slots for icons integrated directly into the badge layout.

#### `size`

**Type:** `'xs' | 'sm' | 'md' | 'lg' | 'xl'`
**Default:** `'md'`

Controls the scale of the badge. Larger sizes increase font-size and padding, while smaller sizes are more compact.

#### `children`

**Type:** `ReactNode`
**Required:** No

**Description:**
The content to display inside the badge. This is ignored if `count` is provided. Typically used for text labels like "New" or "Beta".

#### `invisible`

**Type:** `boolean`
**Default:** `false`
**Required:** No

**Description:**
If `true`, the badge is hidden visually but remains in the DOM to maintain layout stability or accessibility (depending on implementation).

#### `onClick`

**Type:** `(event: React.MouseEvent) => void`
**Required:** No

**Description:**
If provided, the badge becomes interactive:

- It gains `role="button"` (unless overridden).
- It becomes focusable via keyboard (`tabIndex={0}`).
- It responds to `Enter` and `Space` keys.
- It shows a pointer cursor on hover.

#### `id`, `className`, `style`

**Type:** `string`, `string`, `CSSProperties`
**Required:** No

**Description:**
Standard HTML attributes for customization:

- `id`: A unique identifier for the element.
- `className`: Additional CSS classes to apply.
- `style`: Inline CSS styles.

#### `data-testid`

**Type:** `string`
**Default:** `'dyn-badge'`
**Required:** No

**Description:**
A unique identifier for automated testing (e.g., with React Testing Library).

#### Accessibility Props (`role`, `aria-*`)

**Type:** `string`
**Required:** No

**Description:**

- `role`: Manually override the ARIA role. Defaults to `status` (or `button` if clickable).
- `aria-label`: A text label for screen readers. Essential if the visual content is not self-explanatory (e.g., a dot variant).

## 🎨 Design Tokens

### Component Tokens

| Token                   | Default Value                   | Description        |
| ----------------------- | ------------------------------- | ------------------ |
| `--dyn-badge-bg`        | `var(--dyn-neutral-light-100)`  | Background color   |
| `--dyn-badge-color`     | `var(--dyn-semantic-text)`      | Text color         |
| `--dyn-badge-radius`    | `var(--dyn-border-radius-full)` | Border radius      |
| `--dyn-badge-font-size` | `var(--dyn-font-size-xs)`       | Font size          |
| `--dyn-badge-padding-x` | `var(--dyn-spacing-xs)`         | Horizontal padding |

### Variant Overrides

The component maps semantic colors (e.g. `primary`) to theme tokens (e.g. `--dyn-theme-primary`) automatically.

```css
.my-custom-badge {
  /* Override padding for just this instance */
  --dyn-badge-padding-x: 20px;
}
```

## ♿ Accessibility (A11y)

- **Role**: Defaults to `status`. Returns `button` if `onClick` is provided.
- **Labeling**:
  - Automatically generates `aria-label` based on content and context (e.g. "Alert: 5 items").
  - Accepts `aria-label` prop for manual override.
  - `countDescription`: Adds semantic context to numeric badges (e.g., "5 _Unread Messages_").
- **Keyboard**:
  - `Enter` / `Space`: Triggers `onClick` if provided.
- **Live Region**: `aria-live` defaults to `polite` for dynamic updates.

## 📝 Best Practices

- ✅ Use `maxCount` to avoid breaking layout with large numbers.
- ✅ Use `variant="dot"` for subtle status indicators without numbers.
- ✅ Use `startIcon`/`endIcon` for status badges (e.g., "Verified" with a checkmark).
- ❌ Do not use for primary navigation links (use Buttons or Links).
