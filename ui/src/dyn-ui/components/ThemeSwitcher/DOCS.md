# ThemeSwitcher Documentation

## 📌 Overview

**Category:** Molecule / Utility
**Status:** Stable

`ThemeSwitcher` is a utility component that allows users to toggle between Light, Dark, and System theme modes. It interacts with the application's global theme state to apply the corresponding CSS variables and data attributes to the document root.

## 🛠 Usage

### Basic Toggle

```tsx
import { ThemeSwitcher } from '@dyn-ui/react';

function Header() {
  return (
    <header>
      <h1>My App</h1>
      <ThemeSwitcher />
    </header>
  );
}
```

### Controlled Mode

```tsx
<ThemeSwitcher
  theme={currentTheme}
  onChange={(newTheme) => handleThemeChange(newTheme)}
/>
```

## ⚙️ Properties (API)

### ThemeSwitcher Props

| Prop       | Type                        | Default | Description                                     | Required |
| :--------- | :-------------------------- | :------ | :---------------------------------------------- | :------: |
| `theme`    | `'light'\|'dark'\|'system'` | -       | Controlled theme state.                         |    No    |
| `onChange` | `(theme) => void`           | -       | Callback triggered when the user picks a theme. |    No    |

## 🎨 Design Tokens

- **Switch BG**: `--dyn-theme-switcher-bg`
- **Toggle Ball**: `--dyn-theme-switcher-toggle`
- **Active Icon**: `--dyn-theme-switcher-icon-active`

## ♿ Accessibility (A11y)

- **Role**: Uses `role="radiogroup"` or `role="button"` depending on the implementation (typically a button toggle).
- **Labels**: Each mode (Light/Dark/System) is given an explicit `aria-label`.
- **Keyboard**: Accessible via `Tab` and triggered with `Enter` or `Space`.

## 📝 Best Practices

- ✅ Place the `ThemeSwitcher` in a consistent location, like the top-right of the header or footer.
- ✅ Use the `system` option by default to honor the user's OS settings.
- ❌ Don't hide the switcher deep inside a settings menu if your app has strong visual identities for both modes.
- ❌ Avoid adding custom colors to the switcher that clash with the themes themselves.
