# DynAppbar Documentation

## 📌 Overview

**Category:** Organism
**Status:** Stable

`DynAppbar` is a top-level navigation container that displays branding, titles, navigation controls, and actions. It supports responsive layouts, positioning (static, sticky, fixed), and flexible content slots (left, center, right).

## 🛠 Usage

```tsx
import { DynAppbar, DynButton, DynIcon } from '@dyn-ui/react';

function Example() {
  return (
    <DynAppbar
      position="sticky"
      title="Dashboard"
      leftContent={<DynButton variant="ghost" icon={<DynIcon name="menu" />} />}
      rightContent={<DynButton variant="primary">Log out</DynButton>}
    />
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop               | Type                                                 | Default        | Description                         | Required |
| :----------------- | :--------------------------------------------------- | :------------- | :---------------------------------- | :------: |
| `title`            | `ReactNode`                                          | -              | Branding title or element           |    No    |
| `leftContent`      | `ReactNode`                                          | -              | Content on the left (before title)  |    No    |
| `centerContent`    | `ReactNode`                                          | -              | Content centered in the bar         |    No    |
| `rightContent`     | `ReactNode`                                          | -              | Content aligned to the right        |    No    |
| `position`         | `'static' \| 'sticky' \| 'fixed'`                    | `'static'`     | Positioning behavior                |    No    |
| `size`             | `'sm' \| 'md' \| 'lg'`                               | `'md'`         | Size variant                        |    No    |
| `variant`          | `'primary' \| 'secondary' \| 'surface' \| 'inverse'` | `'primary'`    | Color variant                       |    No    |
| `loading`          | `boolean`                                            | `false`        | Shows loading progress bar          |    No    |
| `children`         | `ReactNode`                                          | -              | Alias for center content            |    No    |
| `id`               | `string`                                             | -              | Unique identifier                   |    No    |
| `className`        | `string`                                             | -              | Additional CSS classes              |    No    |
| `style`            | `CSSProperties`                                      | -              | Inline styles                       |    No    |
| `role`             | `string`                                             | `'banner'`     | ARIA role for the header            |    No    |
| `aria-label`       | `string`                                             | -              | Accessible label                    |    No    |
| `aria-labelledby`  | `string`                                             | -              | ID of element labeling the appbar   |    No    |
| `aria-describedby` | `string`                                             | -              | ID of element describing the appbar |    No    |
| `data-testid`      | `string`                                             | `'dyn-appbar'` | Test ID for automated testing       |    No    |

### Detailed Parameter Documentation

#### `title`

**Type:** `ReactNode`
**Required:** No

**Description:**
The main title or branding of the application bar. If a string is provided, it is wrapped in an `<h3>` element with standard styling. If a React Node is provided, it is rendered as-is.

**Example:**

```tsx
// String title
<DynAppbar title="My App" />

// Custom element title
<DynAppbar title={<img src="/logo.png" alt="Logo" />} />
```

#### `position`

**Type:** `'static' | 'sticky' | 'fixed'`
**Default:** `'static'`
**Required:** No

**Description:**
Controls the CSS positioning of the app bar.

- `static`: Default flow.
- `sticky`: Sticks to the top of the viewport when scrolling (requires top: 0 support).
- `fixed`: Fixed to the top of the viewport, removed from flow.

**Example:**

```tsx
<DynAppbar position="fixed" />
```

#### `leftContent` / `rightContent` / `centerContent`

**Type:** `ReactNode`
**Required:** No

**Description:**
Slots for adding controls or actions:

- `leftContent`: Typically used for navigation drawers, back buttons, or logos.
- `centerContent`: Used for search bars or central navigation links.
- `rightContent`: Used for user profiles, notifications, or global actions.

**Example:**

```tsx
<DynAppbar
  leftContent={<BackButton />}
  centerContent={<SearchBar />}
  rightContent={<ProfileAvatar />}
/>
```

#### `children`

**Type:** `ReactNode`
**Required:** No

**Description:**
Alias for `centerContent`. Any children provided to the component will be rendered in the center slot.

#### `id`, `className`, `style`

**Type:** `string`, `string`, `CSSProperties`
**Required:** No

**Description:**
Standard HTML attributes for customization. `className` is appended to the root container classes. `id` and `style` are applied directly to the root `<header>` element.

#### `data-testid`

**Type:** `string`
**Default:** `'dyn-appbar'`
**Required:** No

**Description:**
A unique identifier for automated testing (e.g., with React Testing Library).

#### `size`

**Type:** `'sm' | 'md' | 'lg'`
**Default:** `'md'`
**Required:** No

**Description:**
Controls the height and padding of the app bar.

- `sm`: 3.5rem (56px) - Compact.
- `md`: 4.0rem (64px) - Balanced.
- `lg`: 5.0rem (80px) - Prominent.

#### `variant`

**Type:** `'primary' | 'secondary' | 'surface' | 'inverse'`
**Default:** `'primary'`
**Required:** No

**Description:**
Controls the color theme of the app bar.

- `primary`: Uses primary brand color (white text).
- `secondary`: Uses secondary color (white text).
- `surface`: Uses surface background (standard text, bordered).
- `inverse`: Uses dark background (white text).

#### `loading`

**Type:** `boolean`
**Default:** `false`
**Required:** No

**Description:**
When `true`, displays a progress indicator bar at the bottom of the app bar. The bar uses `currentColor` for the progress indicator.

#### Accessibility Props (`role`, `aria-*`)

**Type:** `string`
**Required:** No

**Description:**

- `role`: Defaults to explicit `<header>` semantics (banner region).
- `aria-label`, `aria-labelledby`, `aria-describedby`: Standard ARIA attributes to improve screen reader accessibility.

## 🎨 Design Tokens

This component uses the following design tokens:

- **Dimensions**:
  - `--dyn-appbar-height` (4rem)
  - `--dyn-appbar-height-mobile` (3.5rem)
  - `--dyn-appbar-padding-x` (default: `--dyn-spacing-lg`)
- **Colors**:
  - `--dyn-appbar-bg` (default: `--dyn-theme-primary`)
  - `--dyn-appbar-color` (default: `--dyn-semantic-text-inverse`)
  - `--dyn-appbar-border` (default: `--dyn-semantic-border`)
- **Shadow**:
  - `--dyn-appbar-shadow` (default: `--dyn-elevation-medium`)
- **Typography**:
  - `--dyn-appbar-title-size` (default: `--dyn-font-size-lg`)

### Customization

```css
.my-transparent-appbar {
  --dyn-appbar-bg: transparent;
  --dyn-appbar-shadow: none;
  --dyn-appbar-color: var(--dyn-semantic-text);
}
```

## ♿ Accessibility (A11y)

- **Role**: `banner` (implicit via `<header>` tag).
- **Structure**: Uses semantic flexbox layout.
- **Headings**: Title uses `<h3>` by default; ensure this fits your page outline or provide a custom node with the correct heading level.

## 📝 Best Practices

- ✅ **Do** use `position="sticky"` for most dashboard layouts.
- ✅ **Do** ensure contrast if customizing `--dyn-appbar-bg`.
- ❌ **Avoid** placing too many actions in `rightContent` on mobile views.
