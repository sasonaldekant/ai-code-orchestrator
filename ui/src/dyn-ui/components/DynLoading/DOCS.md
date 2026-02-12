# DynLoading Documentation

## 📌 Overview

**Category:** Atom
**Status:** Stable

`DynLoading` is an essential feedback component that informs users of background operations. It supports multiple visual representations including spinners, shimmering skeletons for content placeholders, and full-page overlays.

## 🛠 Usage

```tsx
import { DynLoading } from '@dyn-ui/react';

// Spinner (default)
<DynLoading label="Loading results..." />

// Skeleton for content placeholders
<DynLoading variant="skeleton" width="100%" height="200px" />

// Fullscreen overlay with blur
<DynLoading variant="overlay" blur fixed label="Authenticating..." />
```

## ⚙️ Properties (API)

### Quick Reference

| Prop          | Type                                                        | Default     | Description                 | Required |
| :------------ | :---------------------------------------------------------- | :---------- | :-------------------------- | :------: |
| `variant`     | `'spinner' \| 'skeleton' \| 'overlay' \| 'dots' \| 'pulse'` | `'spinner'` | Visual representation.      |    No    |
| `size`        | `'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl'`                      | `'md'`      | Size of the indicator.      |    No    |
| `color`       | `DynLoadingColor`                                           | `'primary'` | Semantic color theme.       |    No    |
| `label`       | `string`                                                    | -           | Primary loading text.       |    No    |
| `description` | `string`                                                    | -           | Secondary descriptive text. |    No    |
| `blur`        | `boolean`                                                   | `false`     | Blur background (overlay).  |    No    |
| `fixed`       | `boolean`                                                   | `false`     | Fullscreen mode (overlay).  |    No    |
| `width`       | `string \| number`                                          | -           | Skeleton width.             |    No    |
| `height`      | `string \| number`                                          | -           | Skeleton height.            |    No    |
| `circle`      | `boolean`                                                   | `false`     | Skeleton shape.             |    No    |
| `aria-label`  | `string`                                                    | -           | Accessibility label.        |    No    |
| `data-testid` | `string`                                                    | -           | Test identifier.            |    No    |

### Detailed Parameter Documentation

#### `variant`

**Description:** Determines the visual look and behavior of the loading indicator.

- `spinner`: Traditional rotating circle.
- `skeleton`: Content placeholder (shimmering block).
- `overlay`: Modal-like backdrop with a central spinner.
- `dots`: Three animated bouncing dots.
- `pulse`: A single growing/shrinking circle.
  **Example:** `<DynLoading variant="dots" />`

#### `size`

**Description:** Predefined size tokens mapped to dimensions.
**Example:** `<DynLoading size="xl" />`

#### `color`

**Description:** Semantic color theme applied to the spinner, dots, or skeleton shimmer. Supports `primary`, `success`, `danger`, `warning`, `info`, `neutral`, `white`.
**Example:** `<DynLoading color="success" />`

#### `label` / `description`

**Description:**

- `label`: Main text (e.g., "Processing").
- `description`: Sub-text with lower emphasis (e.g., "This might take a few seconds").
  **Example:** `<DynLoading label="Uploading" description="4.2MB / 10MB" />`

#### `blur` / `fixed`

**Description:** These props apply only to the `overlay` variant.

- `blur`: Adds a CSS backdrop-filter blur effect to the background.
- `fixed`: Uses `position: fixed` instead of absolute, making it fullscreen relative to the viewport.
  **Example:** `<DynLoading variant="overlay" fixed blur />`

#### `width` / `height` / `circle`

**Description:** These props apply primarily to the `skeleton` variant to define the shape of the placeholder.
**Example:** `<DynLoading variant="skeleton" circle width={40} height={40} />`

## 🎨 Design Tokens

- **Spinner Color**: `--dyn-loading-spinner-color`
- **Skeleton Shimmer**: `--dyn-loading-skeleton-bg`
- **Overlay Backdrop**: `--dyn-loading-overlay-bg`

## ♿ Accessibility (A11y)

- **Role**:
  - `progressbar` for dots and spinners.
  - `status` (implicit via container) to ensure the message is announced.
- **Attributes**:
  - `aria-busy="true"` is applied to the container.
  - `aria-valuetext` is set to the `label` content.
- **Visuals**: High contrast support for skeleton shimmers.
- **Live Region**: Transitions of `label` are announced to screen readers.

## 📝 Best Practices

- ✅ Use `skeleton` for content loading to reduce perceived wait time.
- ✅ Use `overlay` for blocking operations where user input is not allowed.
- ❌ Don't show loading for very fast operations (<100ms).
- ❌ Avoid using `label` with `skeleton` (the placeholder itself is the label).
