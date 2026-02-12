# DynButton Documentation

## 📌 Overview

**Category:** Atom
**Status:** Stable

`DynButton` is a standardized button component following the enterprise 3-Layer Token Law. It supports semantic variants ("kinds"), destructive actions, loading states, and responsive behaviors. It adheres to strict accessibility standards including keyboard navigation and ARIA attributes.

## 🛠 Usage

```tsx
import { DynButton } from '@dyn-ui/react';

function Example() {
  return (
    <div style={{ display: 'flex', gap: '8px' }}>
      {/* Primary Action */}
      <DynButton kind="primary" label="Submit" onClick={() => {}} />

      {/* Secondary Action with Icon */}
      <DynButton kind="secondary" label="Settings" icon="settings" />

      {/* Destructive Action */}
      <DynButton kind="primary" label="Delete" danger loading={false} />

      {/* Icon Only */}
      <DynButton kind="tertiary" icon="close" aria-label="Close Modal" />
    </div>
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop               | Type                                     | Default      | Description                         | Required |
| :----------------- | :--------------------------------------- | :----------- | :---------------------------------- | :------: |
| `label`            | `string`                                 | -            | Text label of the button.           |    No    |
| `kind`             | `'primary' \| 'secondary' \| 'tertiary'` | `'primary'`  | Visual hierarchy variant.           |    No    |
| `size`             | `'sm' \| 'md' \| 'lg'`                   | `'md'`       | Button size.                        |    No    |
| `type`             | `'button' \| 'submit' \| 'reset'`        | `'button'`   | HTML button type.                   |    No    |
| `danger`           | `boolean`                                | `false`      | Apply destructive styling.          |    No    |
| `loading`          | `boolean`                                | `false`      | Show loading state.                 |    No    |
| `loadingText`      | `string`                                 | `'Loading…'` | Accessible text during loading.     |    No    |
| `disabled`         | `boolean`                                | `false`      | Disable interactions.               |    No    |
| `fullWidth`        | `boolean`                                | `false`      | Expand button to full width.        |    No    |
| `hideOnMobile`     | `boolean`                                | `false`      | Hide button on mobile viewports.    |    No    |
| `iconOnlyOnMobile` | `boolean`                                | `false`      | Show only icon on mobile.           |    No    |
| `id`               | `string`                                 | -            | Unique identifier.                  |    No    |
| `className`        | `string`                                 | -            | Additional CSS classes.             |    No    |
| `style`            | `CSSProperties`                          | -            | Inline styles.                      |    No    |
| `children`         | `ReactNode`                              | -            | Child elements (alternative label). |    No    |
| `icon`             | `string \| ReactNode`                    | -            | Leading icon.                       |    No    |
| `aria-label`       | `string`                                 | -            | Accessible label.                   |    No    |
| `aria-labelledby`  | `string`                                 | -            | ID of labeling element.             |    No    |
| `aria-describedby` | `string`                                 | -            | ID of description element.          |    No    |
| `aria-expanded`    | `boolean`                                | -            | Disclosure state.                   |    No    |
| `aria-controls`    | `string`                                 | -            | ID of controlled element.           |    No    |
| `aria-pressed`     | `boolean`                                | -            | Toggle state.                       |    No    |
| `role`             | `AriaRole`                               | -            | ARIA role override.                 |    No    |
| `onClick`          | `MouseEventHandler`                      | -            | Click handler.                      |    No    |
| `onBlur`           | `FocusEventHandler`                      | -            | Blur handler.                       |    No    |
| `onKeyDown`        | `KeyboardEventHandler`                   | -            | Key down handler.                   |    No    |

### Detailed Parameter Documentation

#### `kind`

**Type:** `'primary' | 'secondary' | 'tertiary'`
**Default:** `'primary'`

**Description:**
Determines the visual weight of the button.

- `primary`: Main call-to-action (filled).
- `secondary`: Alternative actions (visible but less prominent).
- `tertiary`: Low priority actions (often just text/icon w/o background until hover).

#### `danger`

**Type:** `boolean`
**Default:** `false`

**Description:**
Applies semantic error/destructive styling. Can be combined with any `kind`, but typically used with `primary` for main destructive actions (e.g., "Delete Account").

#### `label` / `children`

**Type:** `string` / `ReactNode`

`DynButton` accepts a `label` prop for the button text. Alternatively, you can pass text as `children`.
Note that complex children (non-text) are supported but `label` is preferred for standard usage to ensure automatic accessible labeling.

#### `icon`

**Type:** `string | ReactNode`

**Description:**
Displays an icon to the left of the text. If strict string names are used, they map to `DynIcon`. You can also pass a raw React Node (SVG).

#### `loading` / `loadingText`

**Type:** `boolean` / `string`

**Description:**
If `true`, the button is disabled and shows a spinner. `loadingText` is announced to screen readers via a live region but hidden visually.

#### `hideOnMobile` / `iconOnlyOnMobile`

**Type:** `boolean`
**Default:** `false`

Responsive utility props:

- `hideOnMobile`: Hides the button entirely on small screens.
- `iconOnlyOnMobile`: Hides the `label` but keeps the `icon` on small screens to save space.

#### Accessibility Props

**Type:** `string` / `boolean` / `AriaRole`

Supports standard ARIA attributes:

- `aria-label`: Essential for icon-only buttons.
- `aria-labelledby`: Reference another element as the label.
- `aria-describedby`: Reference an element describing the button.
- `aria-expanded`: For disclosure buttons.
- `aria-controls`: ID of the controlled element.
- `aria-pressed`: For toggle buttons.
- `role`: Override the default `button` role (use with caution).

## 🎨 Design Tokens

- **Colors**:
  - `--dyn-button-bg`, `--dyn-button-color`, `--dyn-button-border`
  - Fallback to `--dyn-theme-primary` and `--dyn-semantic-text-inverse`
- **Sizing**:
  - `--dyn-button-padding-y`, `--dyn-button-padding-x`
  - `--dyn-button-min-height`
- **Typography**:
  - `--dyn-button-font-size`, `--dyn-button-font-weight`

## ♿ Accessibility (A11y)

- **Role**: `button`.
- **States**:
  - `aria-disabled` is set when `disabled` or `loading`.
  - `aria-busy` is set when `loading`.
- **Keyboard**:
  - Standard `Tab` focus.
  - `Enter` and `Space` triggers click.
- **Labeling**:
  - `aria-label` is automatically computed if `label` is missing but `icon` is present.
  - `loadingText` is announced to screen readers via a live region when `loading` is true.

## 📝 Best Practices

- ✅ **Do** use `loading` state during async operations to prevent double-submissions.
- ✅ **Do** use `type="submit"` when inside a `DynForm`.
- ❌ **Avoid** using `danger` for non-destructive actions just to get a red button; use a custom theme or invalid state instead.
