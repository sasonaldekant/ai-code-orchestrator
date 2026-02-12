# DynBox Documentation

## 📌 Overview

**Category:** Atom (Primitive)
**Status:** Stable

`DynBox` is the fundamental building block of the DynUI system. It is a polymorphic, atomic component that exposes design tokens as props, allowing you to build custom layouts and components without writing custom CSS. It supports flexbox, grid, spacing, positioning, styling, and accessibility features out of the box while enforcing the design system's token usage.

## 🛠 Usage

```tsx
import { DynBox, DynIcon } from '@dyn-ui/react';

function Example() {
  return (
    <DynBox
      as="section"
      bg="surface"
      p="md"
      radius="md"
      shadow="sm"
      border="default"
      display="flex"
      align="center"
      gap="sm"
    >
      <DynBox bg="primary" p="xs" radius="full">
        <DynIcon name="star" color="white" />
      </DynBox>
      <DynBox>
        <DynBox as="h3" m="0" color="default">
          Card Title
        </DynBox>
        <DynBox as="p" m="0" color="muted">
          Subtitle text here
        </DynBox>
      </DynBox>
    </DynBox>
  );
}
```

## ⚙️ Properties (API)

`DynBox` accepts all standard HTML attributes plus the following style props.

### Quick Reference

| Prop               | Type                | Default     | Description                      |
| :----------------- | :------------------ | :---------- | :------------------------------- |
| `as`               | `ElementType`       | `div`       | Render as a specific HTML tag.   |
| `display`          | `BoxDisplay`        | -           | CSS display property.            |
| `p`, `px`, `py`... | `SpacingSize`       | -           | Padding variants.                |
| `m`, `mx`, `my`... | `SpacingSize`       | -           | Margin variants.                 |
| `bg`               | `BackgroundVariant` | -           | Background color token.          |
| `color`            | `ColorVariant`      | -           | Text color token.                |
| `border`           | `BorderVariant`     | -           | Border style variant.            |
| `radius`           | `BorderRadius`      | -           | Border radius token.             |
| `interactive`      | `boolean`           | `false`     | Enables interactive styles/a11y. |
| `id`               | `string`            | -           | Unique identifier.               |
| `data-testid`      | `string`            | `'dyn-box'` | Test ID for automated testing.   |

### Detailed Parameter Documentation

#### Layout & Sizing

| Prop                     | Type                           | Description                                  |
| :----------------------- | :----------------------------- | :------------------------------------------- |
| `display`                | `BoxDisplay`                   | `block`, `flex`, `grid`, `inline-flex`, etc. |
| `width` / `height`       | `string \| number`             | Dynamic width/height. Numbers are pixels.    |
| `minWidth` / `minHeight` | `string \| number`             | Minimum dimensions.                          |
| `maxWidth` / `maxHeight` | `string \| number`             | Maximum dimensions.                          |
| `overflow`               | `'visible' \| 'hidden' \| ...` | Overflow behavior.                           |

#### Flexbox & Grid

| Prop                  | Type                | Description                              |
| :-------------------- | :------------------ | :--------------------------------------- |
| `direction`           | `'row' \| 'column'` | Flex direction (alias: `flexDirection`). |
| `align`               | `AlignItems`        | `align-items` CSS property.              |
| `justify`             | `JustifyContent`    | `justify-content` CSS property.          |
| `wrap`                | `FlexWrap`          | `flex-wrap` CSS property.                |
| `gap`                 | `SpacingSize`       | `gap` CSS property using spacing tokens. |
| `gridTemplateColumns` | `string`            | Grid columns definition.                 |
| `gridTemplateRows`    | `string`            | Grid rows definition.                    |
| `gridTemplateAreas`   | `string`            | Grid areas definition.                   |

**Example:**

```tsx
<DynBox display="flex" justify="space-between" align="center" gap="md">
  <DynBox>Left</DynBox>
  <DynBox>Right</DynBox>
</DynBox>
```

#### Spacing

Spacing props accept token keys (`'xs'`, `'md'`, `'xl'`, etc.) as well as `'0'`, `'none'`, and `'auto'`.

| Prop                      | Type          | Description                    |
| :------------------------ | :------------ | :----------------------------- |
| `p` / `padding`           | `SpacingSize` | Padding on all sides.          |
| `px` / `py`               | `SpacingSize` | Horizontal / Vertical padding. |
| `pt` / `pr` / `pb` / `pl` | `SpacingSize` | Top/Right/Bottom/Left padding. |
| `m` / `margin`            | `SpacingSize` | Margin on all sides.           |
| `mx` / `my`               | `SpacingSize` | Horizontal / Vertical margin.  |
| `mt` / `mr` / `mb` / `ml` | `SpacingSize` | Top/Right/Bottom/Left margin.  |

**Available Sizes:** `none`, `0`, `2xs`, `xs`, `sm`, `md`, `lg`, `xl`, `2xl`, `3xl`, `4xl`, `auto`.

#### Styling

| Prop                | Type                             | Description                                          |
| :------------------ | :------------------------------- | :--------------------------------------------------- |
| `bg` / `background` | `BackgroundVariant`              | e.g. `'surface'`, `'primary'`, `'success-surface'`.  |
| `color`             | `ColorVariant`                   | e.g. `'primary'`, `'danger-text'`, `'success-text'`. |
| `border`            | `BorderVariant`                  | e.g. `'default'`, `'danger'`, `'success-border'`.    |
| `radius`            | `BorderRadius`                   | e.g. `'sm'`, `'md'`, `'full'`.                       |
| `shadow`            | `'none' \| 'sm' \| 'md' \| 'lg'` | Box shadow variant.                                  |

**Semantic Light Tokens:**
New light semantic tokens are available for accessible backgrounds:

- Backgrounds: `'danger-surface'`, `'success-surface'`, `'warning-surface'`, `'info-surface'`
- Borders: `'danger-border'`, `'success-border'`, `'warning-border'`, `'info-border'`
- Text: `'danger-text'`, `'success-text'`, `'warning-text'`, `'info-text'`

#### Positioning

| Prop                                | Type               | Description                                     |
| :---------------------------------- | :----------------- | :---------------------------------------------- |
| `position`                          | `BoxPosition`      | CSS position (e.g. `'absolute'`, `'relative'`). |
| `top` / `right` / `bottom` / `left` | `string \| number` | Position offsets.                               |
| `zIndex`                            | `number`           | Z-index stack order.                            |

#### Visibility & Responsiveness

| Prop            | Type      | Description                                 |
| :-------------- | :-------- | :------------------------------------------ |
| `hideOnMobile`  | `boolean` | CSS `display: none` on mobile breakpoints.  |
| `hideOnTablet`  | `boolean` | CSS `display: none` on tablet breakpoints.  |
| `hideOnDesktop` | `boolean` | CSS `display: none` on desktop breakpoints. |
| `mobileOnly`    | `boolean` | Shows ONLY on mobile.                       |
| `tabletOnly`    | `boolean` | Shows ONLY on tablet.                       |
| `desktopOnly`   | `boolean` | Shows ONLY on desktop.                      |

#### Accessibility & Interactivity

| Prop                 | Type                      | Description                                                             |
| :------------------- | :------------------------ | :---------------------------------------------------------------------- |
| `as`                 | `ElementType`             | Render as a specific HTML tag (e.g. `'section'`, `'span'`, `'button'`). |
| `interactive`        | `boolean`                 | Adds hover effects, keyboard focus styles, and role management.         |
| `focusOnMount`       | `boolean`                 | Auto-focus element when mounted.                                        |
| `ariaLiveMessage`    | `string`                  | Text to announce via a hidden live region.                              |
| `ariaLivePoliteness` | `'polite' \| 'assertive'` | Politeness setting for live region. Default `'polite'`.                 |

## 🎨 Design Tokens

`DynBox` maps its props directly to the global design token system.

- **Spacing**: Maps `xs`, `md`, etc. to `--dyn-spacing-*`.
- **Colors**: Maps `primary`, `surface`, etc. to `--dyn-theme-*` and `--dyn-semantic-*`.
- **Radius**: Maps `sm`, `lg`, etc. to `--dyn-border-radius-*`.

## ♿ Accessibility (A11y)

- **Polymorphism**: Use `as` to render semantic HTML (e.g., `as="nav"` for navigation, `as="main"` for primary content).
- **Interactivity**:
  - When `interactive` is true, `role="button"` (if not specified) and `tabIndex="0"` are automatically set.
  - Automatically handles `Enter` and `Space` keypresses for `onClick` events on non-button elements.
- **Live Regions**: Built-in support for live announcements via `ariaLiveMessage` for status updates.
- **Roles**: Supports all ARIA roles (e.g. `alert`, `status`, `article`) passed as props.

## 📝 Best Practices

- ✅ **Do** use `DynBox` for ALL custom layouts instead of writing `div` with `className`.
- ✅ **Do** use semantic tags via the `as` prop (e.g., `<DynBox as="main">`).
- ✅ **Do** prefer token-based spacing (`p="md"`) over hardcoded values (`p="16px"`) to ensure consistency.
- ✅ **Do** use the new semantic tokens (`danger-surface`, `danger-text`) for alert boxes instead of hardcoded colors.
- ❌ **Avoid** using `style` prop directly; use the provided props to ensure token usage.
