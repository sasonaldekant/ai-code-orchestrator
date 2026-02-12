# DynPage Documentation

## 📌 Overview

**Category:** Template / Layout
**Status:** Stable

`DynPage` is a high-level layout component designed to standardize the structure of application pages. It handles breadcrumbs, titles, subtitles, page-level actions, and global states like loading and errors.

## 🛠 Usage

```tsx
import { DynPage } from '@dyn-ui/react';

function MyPage() {
  const actions = [
    {
      key: 'save',
      title: 'Save Changes',
      type: 'primary',
      onClick: () => save(),
    },
    { key: 'cancel', title: 'Cancel', onClick: () => back() },
  ];

  const breadcrumbs = [
    { title: 'Dashboard', href: '/dashboard' },
    { title: 'User Settings' },
  ];

  return (
    <DynPage
      title="User Profile"
      subtitle="Manage your personal information and security settings."
      actions={actions}
      breadcrumbs={breadcrumbs}
    >
      <section>{/* Page Content Goes Here */}</section>
    </DynPage>
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop          | Type                            | Default  | Description                          | Required |
| :------------ | :------------------------------ | :------- | :----------------------------------- | :------: |
| `title`       | `string`                        | -        | Main page heading (H1).              |   Yes    |
| `subtitle`    | `string`                        | -        | Description text below title.        |    No    |
| `breadcrumbs` | `DynPageBreadcrumb[]`           | `[]`     | Navigation path at the top.          |    No    |
| `actions`     | `DynPageAction[]`               | `[]`     | Buttons shown in header.             |    No    |
| `children`    | `ReactNode`                     | -        | Main content area.                   |   Yes    |
| `loading`     | `boolean`                       | `false`  | Replaces content with a spinner.     |    No    |
| `error`       | `string \| ReactNode`           | -        | Replaces content with error message. |    No    |
| `size`        | `'sm' \| 'md' \| 'lg'`          | `'md'`   | Page max-width constraint.           |    No    |
| `padding`     | `LayoutSpacing`                 | `'md'`   | Internal container padding.          |    No    |
| `background`  | `'none' \| 'surface' \| 'page'` | `'page'` | Page background style.               |    No    |

### Detailed Parameter Documentation

#### `actions`

**Description:** Array of objects mapped to `DynButton` components in the top-right corner.
**Example:** `actions={[{ key: 'add', title: 'Add New', icon: 'plus', onClick: () => {} }]}`

#### `breadcrumbs`

**Description:** Renders a breadcrumb list above the title. Supports both `href` (anchors) and `onClick` (SPA navigation).
**Example:** `breadcrumbs={[{ title: 'Home', href: '/' }, { title: 'Settings' }]}`

#### `background`

**Description:**

- `none`: Transparent.
- `surface`: Content area card background (Standard component background).
- `page`: Global application page background (usually slightly offset from surface).

#### `size`

**Description:** Controls the max-width of the content container to maintain readability on ultra-wide screens.

- `sm`: ~800px
- `md`: ~1200px
- `lg`: ~1600px

## 🎨 Design Tokens

- **Page Background**: `--dyn-page-bg`
- **Surface Background**: `--dyn-page-surface-bg`
- **Header Border**: `--dyn-page-header-border`
- **Title Color**: `--dyn-page-title-color`

## ♿ Accessibility (A11y)

- **Semantic HTML**: Uses `<header>`, `<main>`, and `<nav>` for logical page landmarks.
- **Hierarchy**: The `title` prop is automatically rendered as an `<h1>`.
- **Breadcrumbs**: Wrapped in `<nav aria-label="Breadcrumb">` with list structure according to W3C patterns.

## 📝 Best Practices

- ✅ Use `subtitle` to provide context for complex pages.
- ✅ Place primary actions (Save, Submit) as the first item in the `actions` array.
- ✅ Use `loading` prop for initial data fetching rather than internal spinners.
- ❌ Don't use `DynPage` inside another `DynPage`.
