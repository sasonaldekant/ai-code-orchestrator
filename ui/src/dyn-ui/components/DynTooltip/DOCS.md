# DynTooltip Documentation

## 📌 Overview

**Category:** Molecule / Feedback
**Status:** Stable

`DynTooltip` is a small informational popover used to provide context or labels for interactive elements (like icons or buttons) when they are hovered, focused, or clicked. It helps reduce interface clutter while keeping the system accessible and descriptive.

## 🛠 Usage

### Basic Usage

```tsx
import { DynTooltip, DynButton, DynIcon } from '@dyn-ui/react';

<DynTooltip content="Delete this record" position="top">
  <DynButton variant="danger">
    <DynIcon icon="trash" />
  </DynButton>
</DynTooltip>;
```

### Advanced: Custom Content & Click Trigger

```tsx
<DynTooltip
  content={
    <div style={{ padding: '8px' }}>
      <strong>Status:</strong> Active
      <p>Last seen 5 mins ago</p>
    </div>
  }
  trigger="click"
  interactive
>
  <button>Click for Details</button>
</DynTooltip>
```

## ⚙️ Properties (API)

### DynTooltip Props

| Prop           | Type                      | Default   | Description                                          | Required |
| :------------- | :------------------------ | :-------- | :--------------------------------------------------- | :------: |
| `content`      | `string \| ReactNode`     | -         | **Required.** The information shown in the bubble.   |   Yes    |
| `children`     | `ReactElement`            | -         | **Required.** The element that triggers the tooltip. |   Yes    |
| `position`     | `TooltipPosition`         | `'top'`   | Placement relative to the trigger.                   |    No    |
| `trigger`      | `TooltipTrigger`          | `'hover'` | Activation method (`hover`, `click`, `focus`).       |    No    |
| `delay`        | `number`                  | `200`     | Time in ms before the tooltip appears.               |    No    |
| `disabled`     | `boolean`                 | `false`   | Prevents the tooltip from showing.                   |    No    |
| `interactive`  | `boolean`                 | `false`   | Allows the mouse to enter the tooltip content.       |    No    |
| `visible`      | `boolean`                 | -         | Controlled visibility state.                         |    No    |
| `onOpenChange` | `(open: boolean) => void` | -         | Callback when visibility status changes.             |    No    |

## 🎨 Design Tokens

- **Tooltip Background**: `--dyn-tooltip-bg` (Usually Neutral 900)
- **Text Color**: `--dyn-tooltip-text` (Usually Neutral 50)
- **Border Radius**: `--dyn-tooltip-radius`
- **Fade Duration**: `--dyn-duration-fast`

## ♿ Accessibility (A11y)

- **Landmarks**: Tooltips are rendered via Portal to ensure they aren't cut off by parent overflow.
- **Roles**: Uses `role="tooltip"`.
- **Relationship**: The trigger element is automatically given `aria-describedby` pointing to the tooltip's unique ID.
- **Focus**: Triggering via `focus` ensures keyboard-only users receive the same information as mouse users.

## 📝 Best Practices

- ✅ Use tooltips to explain icons that don't have text labels.
- ✅ Keep the content brief (under 5 words).
- ✅ Use `position="top"` as the primary default.
- ❌ Don't put critical information or complex forms inside a tooltip.
- ❌ Avoid putting tooltips on elements that are already highly descriptive.
- ❌ Don't use tooltips on mobile devices where "hover" doesn't exist (ensure the trigger is clickable or information is visible elsewhere).
