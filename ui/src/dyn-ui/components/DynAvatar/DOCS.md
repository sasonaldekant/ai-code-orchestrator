# DynAvatar Documentation

## 📌 Overview

**Category:** Atom (Display)
**Status:** Stable

`DynAvatar` is a robust component for displaying user profile images, initials, or icons. It handles:

- **Image lifecycle**: Loading, error, and success states.
- **Fallbacks**: Graceful degradation to initials or icons if images fail.
- **Status & Badges**: Integrated support for status indicators and notification badges.
- **Accessibility**: Built-in ARIA support and keyboard interaction.

## 🛠 Usage

```tsx
import { DynAvatar } from '@dyn-ui/react';

function Example() {
  return (
    <div style={{ display: 'flex', gap: '1rem' }}>
      {/* Standard Image Avatar */}
      <DynAvatar
        src="https://i.pravatar.cc/150"
        alt="Jane Doe"
        status="online"
      />

      {/* Initials Fallback */}
      <DynAvatar alt="John Smith" initials="JS" size="lg" badge={5} />

      {/* Custom Icon Fallback */}
      <DynAvatar alt="Anonymous" fallback={<MyCustomIcon />} />
    </div>
  );
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop Name      | Type                                        | Default                   | Description                 | Required |
| :------------- | :------------------------------------------ | :------------------------ | :-------------------------- | :------: |
| `src`          | `string`                                    | -                         | Image source URL.           |    No    |
| `alt`          | `string`                                    | -                         | Accessible description.     | **Yes**  |
| `size`         | `'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl'`      | `'md'`                    | Component size.             |    No    |
| `shape`        | `'circle' \| 'square' \| 'rounded'`         | `'circle'`                | Shape variant.              |    No    |
| `initials`     | `string`                                    | -                         | Explicit text fallack.      |    No    |
| `status`       | `'online' \| 'offline' \| 'away' \| 'busy'` | -                         | Status indicator.           |    No    |
| `badge`        | `ReactNode \| Config`                       | -                         | Notification badge.         |    No    |
| `loading`      | `boolean`                                   | `false`                   | Force loading state.        |    No    |
| `error`        | `boolean`                                   | `false`                   | Force error state.          |    No    |
| `fallback`     | `ReactNode`                                 | `DefaultIcon`             | Custom fallback element.    |    No    |
| `onClick`      | `(event) => void`                           | -                         | Click handler.              |    No    |
| `children`     | `ReactNode`                                 | -                         | Content override.           |    No    |
| `imageLoading` | `'eager' \| 'lazy'`                         | `'eager'`                 | Native img loading.         |    No    |
| `imageProps`   | `ImgHTMLAttributes`                         | -                         | Props for internal img.     |    No    |
| `loadTimeout`  | `number`                                    | `10000`                   | Miliseconds to wait.        |    No    |
| `onImageError` | `(event) => void`                           | -                         | Error callback.             |    No    |
| `errorMessage` | `string`                                    | `'Avatar failed to load'` | Screen reader error text.   |    No    |
| `loadingLabel` | `string`                                    | `'Loading avatar'`        | Screen reader loading text. |    No    |

### Detailed Parameter Documentation

#### Core Props

- **`src`**: `string`
  URL of the avatar image. If this is not provided, or if the image fails to load, the component will display `initials` (if provided), `children`, or the `fallback` icon.

- **`alt`**: `string` (Required)
  Text description of the image. This is crucial for accessibility. If the image fails and no `initials` are provided, the first characters of `alt` may be used as a fallback generation strategy depending on implementation.

- **`size`**: `DynAvatarSize`
  Controls the overall dimensions of the avatar.
  - `xs`: 24px (1.5rem)
  - `sm`: 32px (2rem)
  - `md`: 40px (2.5rem)
  - `lg`: 48px (3rem)
  - `xl`: 64px (4rem)

- **`shape`**: `DynAvatarShape`
  - `circle`: Fully rounded (50% border-radius).
  - `square`: No border radius.
  - `rounded`: Slight border radius (varies by design token).

#### Behavior & State

- **`initials`**: `string`
  String to display when the image is missing or failed. Usually 1-2 characters (e.g., "JD").

- **`status`**: `DynAvatarStatus`
  Renders a status indicator dot at the bottom-right.
  - `online` (Green)
  - `offline` (Gray)
  - `away` (Yellow)
  - `busy` (Red)

- **`badge`**: `DynAvatarBadgeConfig`
  Display a badge at the top-right, useful for notification counts.
  Can be a number (`5`), a string (`"99+"`), a ReactNode, or a config object:

  ```tsx
  badge={{ content: 12, color: 'danger', variant: 'solid' }}
  ```

- **`loadTimeout`**: `number` (Default: `10000`)
  Time in milliseconds to wait for the image to load. If the timeout is reached, the component treats it as an error and shows the fallback.

- **`imageLoading`**: `'eager' | 'lazy'` (Default: `'eager'`)
  Passes the standard `loading` attribute to the internal `<img>` element. Use `'lazy'` for avatars off-screen or in long lists.

- **`imageProps`**: `ImgHTMLAttributes`
  Passes additional props directly to the internal `<img>` element (e.g., `crossOrigin`, `referrerPolicy`).

#### Events & Callbacks

- **`onClick`**: `(event: React.MouseEvent) => void`
  Makes the avatar interactive. When provided, the avatar renders with `role="button"` and `tabIndex={0}`.

- **`onImageError`**: `(event) => void`
  Callback fired when the image fails to load or times out.
  ```tsx
  onImageError={(e) => console.error("Avatar failed:", e)}
  ```

#### Fallbacks & Customization

- **`children`**: `ReactNode`
  Content to render inside the avatar container. Useful for custom text or layouts that override the standard image/initials behavior.

- **`fallback`**: `ReactNode`
  A custom icon or element to display when:
  1. `src` is missing/failed AND
  2. `initials` is not provided AND
  3. `children` is not provided.
     Defaults to a generic user icon.

#### Accessibility & Localization

- **`errorMessage`**: `string`
  Text announced to screen readers when the image fails to load. Default: "Avatar failed to load".

- **`loadingLabel`**: `string`
  Text announced to screen readers while the image is loading. Default: "Loading avatar".

- **`aria-label`, `aria-labelledby`, `aria-describedby`**, `role`:
  Standard ARIA attributes are supported and passed to the root element.

## 🎨 Design Tokens

- **Dimensions**:
  - `--dyn-avatar-size-[size]` (e.g., `--dyn-avatar-size-md`)
  - `--dyn-avatar-font-size-[size]`
- **Colors**:
  - `--dyn-avatar-bg`: Background color for initials/fallback.
  - `--dyn-avatar-text`: Text color for initials.
  - `--dyn-avatar-border`: Border color (often matches surface to create "cutout" effect for status).
- **Status Colors**:
  - `--dyn-avatar-status-online`
  - `--dyn-avatar-status-busy`
  - `--dyn-avatar-status-away`
  - `--dyn-avatar-status-offline`

## ♿ Accessibility (A11y)

- **Semantic Role**:
  - Defaults to `img` role (container acts as image).
  - Switches to `button` if `onClick` is present.
- **Keyboard Support**:
  - Interactive avatars are focusable via `Tab`.
  - `Enter` or `Space` triggers `onClick`.
- **Announcements**:
  - Uses `aria-busy="true"` during loading.
  - Provides text alternatives for all visual states.

## 📝 Best Practices

- ✅ **Do** provide `alt` text describing the person (e.g. "Jane Doe").
- ✅ **Do** use `initials` whenever possible to provide context if the image fails.
- ❌ **Avoid** using `badge` and `status` simultaneously if it creates visual clutter at small sizes (`xs`).
