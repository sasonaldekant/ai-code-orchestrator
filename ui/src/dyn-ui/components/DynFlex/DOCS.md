# DynFlex Documentation

## 📌 Overview

**Category:** Layout  
**Status:** Stable

A flexbox layout component providing wrapper with prop-based configuration for direction, alignment, and gap.

## 🛠 Usage

```tsx
import { DynFlex } from '@dyn-ui/react';

<DynFlex direction="row" justify="space-between" align="center" gap="md">
  <div>Left</div>
  <div>Right</div>
</DynFlex>;
```

## ⚙️ Properties (API)

| Prop        | Type                                                                | Default     | Description                   |
| ----------- | ------------------------------------------------------------------- | ----------- | ----------------------------- |
| `direction` | `'row' \| 'column' \| 'row-reverse' \| 'column-reverse'`            | `'row'`     | Flex direction.               |
| `justify`   | `'start' \| 'center' \| 'end' \| 'between' \| 'around' \| 'evenly'` | `'start'`   | Justify content.              |
| `align`     | `'start' \| 'center' \| 'end' \| 'stretch'`                         | `'stretch'` | Align items.                  |
| `wrap`      | `'wrap' \| 'nowrap' \| 'wrap-reverse'`                              | `'nowrap'`  | Flex wrap.                    |
| `gap`       | `'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl'`                              | -           | Gap between items.            |
| `padding`   | `'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl'`                              | -           | Internal padding.             |
| `inline`    | `boolean`                                                           | `false`     | Use inline-flex.              |
| `as`        | `ElementType`                                                       | `'div'`     | Polymorphic tag (e.g. `main`) |
| `className` | `string`                                                            | -           | Custom classes.               |
| `style`     | `CSSProperties`                                                     | -           | Custom styles/overrides.      |
| `id`        | `string`                                                            | -           | Unique ID.                    |

## 📝 Best Practices

- ✅ Use for simple layouts
- ✅ Use `gap` instead of margins
- ❌ For grid layouts, use DynGrid
