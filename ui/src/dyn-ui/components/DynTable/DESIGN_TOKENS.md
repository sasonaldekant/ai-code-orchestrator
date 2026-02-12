# DynTable Design Tokens Integration

## 📋 Overview

DynTable component uses **design tokens** (CSS custom properties) for styling. All colors, sizes, spacing, and other style values are defined as reusable tokens in `packages/design-tokens/table.css`.

## 🎯 Design Token Approach

Instead of hardcoded values, the component uses CSS variables for:
- **Colors**: Primary, secondary, interactive states
- **Typography**: Font families, sizes, weights
- **Spacing**: Padding, gaps, margins
- **Effects**: Transitions, shadows, borders

## 📂 File Structure

```
packages/
├── design-tokens/
│   ├── table.css           ← CSS variables and styles
│   ├── table.json          ← Token definitions (source)
│   ├── tokens/
│   │   └── table.json      ← Token metadata
│   └── index.css           ← Import point
└── dyn-ui-react/
    └── src/components/DynTable/
        ├── DynTable.tsx
        ├── DynTable.module.css  ← Imports design tokens CSS
        ├── DynTable.stories.tsx
        └── DESIGN_TOKENS.md     ← This file
```

## 🔧 How to Use Design Tokens

### 1. Import Design Tokens CSS

**In DynTable.module.css:**
```css
@import '../../../../../../design-tokens/table.css';

.dyn-table {
  /* Now you can use CSS variables */
  font-family: var(--dyn-table-font-family);
  font-size: var(--dyn-table-font-size);
  color: var(--dyn-table-text-color);
  background-color: var(--dyn-table-bg-color);
}
```

### 2. Available Tokens

#### Root Variables
```css
--dyn-table-font-family
--dyn-table-font-size
--dyn-table-bg-color
--dyn-table-text-color
```

#### Size Variants
```css
/* Small */
--dyn-table-size-small-padding
--dyn-table-size-small-font-size

/* Medium (default) */
--dyn-table-size-medium-padding
--dyn-table-size-medium-font-size

/* Large */
--dyn-table-size-large-padding
--dyn-table-size-large-font-size
```

#### Header Styling
```css
--dyn-table-header-bg-color
--dyn-table-header-text-color
--dyn-table-header-font-weight
--dyn-table-header-border-color
--dyn-table-header-border-width
--dyn-table-header-text-transform
--dyn-table-header-letter-spacing
```

#### Row States
```css
--dyn-table-row-striped-bg-color
--dyn-table-row-hover-bg-color
--dyn-table-row-hover-transition
--dyn-table-row-selected-bg-color
--dyn-table-row-selected-striped-bg-color
```

#### Interactive Elements
```css
/* Sortable */
--dyn-table-sortable-cursor
--dyn-table-sortable-hover-bg-color
--dyn-table-sortable-active-bg-color
--dyn-table-sortable-active-text-color

/* Buttons */
--dyn-table-button-padding
--dyn-table-button-font-size
--dyn-table-button-font-weight
--dyn-table-button-bg-color
--dyn-table-button-text-color
--dyn-table-button-border-color
--dyn-table-button-border-radius
--dyn-table-button-transition

/* Primary Button */
--dyn-table-button-primary-bg-color
--dyn-table-button-primary-text-color
--dyn-table-button-primary-hover-bg-color

/* Danger Button */
--dyn-table-button-danger-bg-color
--dyn-table-button-danger-text-color
--dyn-table-button-danger-hover-bg-color
```

#### Pagination
```css
--dyn-table-pagination-padding
--dyn-table-pagination-gap
--dyn-table-pagination-bg-color
--dyn-table-pagination-border-color
--dyn-table-pagination-font-size
```

#### Other States
```css
/* Checkbox */
--dyn-table-checkbox-size
--dyn-table-checkbox-focus-outline-color
--dyn-table-checkbox-focus-outline-width

/* Empty State */
--dyn-table-empty-padding
--dyn-table-empty-text-color
--dyn-table-empty-font-size

/* Loading State */
--dyn-table-loading-padding
--dyn-table-loading-text-color
--dyn-table-loading-font-size
```

## 🎨 Customization

### Change Token Values

To customize table appearance globally, override CSS variables in your application:

```css
:root {
  /* Override default token values */
  --dyn-table-header-bg-color: #f0f0f0;        /* Lighter header */
  --dyn-table-button-primary-bg-color: #2196f3;  /* Different primary */
  --dyn-table-row-hover-bg-color: #efefef;    /* Different hover */
}
```

### Theme-Based Tokens

Create different themes by overriding tokens:

```css
/* Light theme (default) */
:root {
  --dyn-table-bg-color: #ffffff;
  --dyn-table-text-color: #333333;
  --dyn-table-header-bg-color: #f5f5f5;
}

/* Dark theme */
@media (prefers-color-scheme: dark) {
  :root {
    --dyn-table-bg-color: #1e1e1e;
    --dyn-table-text-color: #ffffff;
    --dyn-table-header-bg-color: #2d2d2d;
  }
}
```

## 📝 CSS Module Implementation

**DynTable.module.css:**
```css
@import '../../../../../../design-tokens/table.css';

/* Table Root */
.dyn-table {
  font-family: var(--dyn-table-font-family);
  font-size: var(--dyn-table-font-size);
  color: var(--dyn-table-text-color);
  background-color: var(--dyn-table-bg-color);
}

/* Header */
.dyn-table__cell--header {
  background-color: var(--dyn-table-header-bg-color);
  color: var(--dyn-table-header-text-color);
  font-weight: var(--dyn-table-header-font-weight);
  border-bottom: var(--dyn-table-header-border-width) solid var(--dyn-table-header-border-color);
}

/* Buttons */
.dyn-table__action-button {
  padding: var(--dyn-table-button-padding);
  background-color: var(--dyn-table-button-bg-color);
  color: var(--dyn-table-button-text-color);
  border: 1px solid var(--dyn-table-button-border-color);
}

.dyn-table__action-button.primary {
  background-color: var(--dyn-table-button-primary-bg-color);
  color: var(--dyn-table-button-primary-text-color);
}

.dyn-table__action-button.danger {
  background-color: var(--dyn-table-button-danger-bg-color);
  color: var(--dyn-table-button-danger-text-color);
}
```

## 🔄 Token JSON Structure

**packages/design-tokens/tokens/table.json:**

Tokens are defined as JSON for programmatic access and tool generation:

```json
{
  "dyn": {
    "table": {
      "root": {
        "fontSize": {
          "value": "14px",
          "description": "Default font size for table cells"
        }
      },
      "header": {
        "backgroundColor": {
          "value": "#f5f5f5",
          "description": "Header cell background color"
        }
      }
    }
  }
}
```

This allows:
- **Documentation generation**: Auto-generate token reference
- **Tool integration**: Design tools can import tokens
- **Version control**: Track token changes
- **Analytics**: Measure token usage

## 🛠️ Build & Generation

Tokens are processed via Style Dictionary:

```bash
# In packages/design-tokens/
npm run build
```

This generates:
- `table.css` - CSS variable definitions
- Other format outputs (SCSS, JSON, etc.)

## 📊 Token Categories

### By Type
| Category | Tokens | Use Case |
|----------|--------|----------|
| **Colors** | `*-color` | Backgrounds, text, borders |
| **Spacing** | `*-padding`, `*-gap` | Padding, margins, gaps |
| **Typography** | `*-font-*` | Font family, size, weight |
| **Interactive** | `*-hover-*`, `*-focus-*` | State changes, effects |

### By Component
| Component | Tokens | Example |
|-----------|--------|----------|
| **Header** | `header-*` | `--dyn-table-header-bg-color` |
| **Button** | `button-*` | `--dyn-table-button-padding` |
| **Row** | `row-*` | `--dyn-table-row-selected-bg-color` |
| **Pagination** | `pagination-*` | `--dyn-table-pagination-gap` |

## ✅ Best Practices

1. **Always use tokens** - Never hardcode values
2. **Name consistently** - Follow `--dyn-table-[component]-[property]` pattern
3. **Document tokens** - Add descriptions in JSON
4. **Group logically** - Related tokens together
5. **Version control** - Track token changes in git
6. **Test variations** - Verify all size/color variants work

## 🔗 Related Files

- [`packages/design-tokens/table.json`](../../../design-tokens/tokens/table.json) - Token definitions
- [`packages/design-tokens/table.css`](../../../design-tokens/table.css) - CSS variables
- [`packages/dyn-ui-react/src/components/DynTable/DynTable.module.css`](./DynTable.module.css) - Component styles
- [`packages/dyn-ui-react/src/components/DynTable/DynTable.tsx`](./DynTable.tsx) - Component implementation

## 📚 Additional Resources

- [Design Tokens Documentation](../../../design-tokens/README.md)
- [Style Dictionary Documentation](https://amzn.github.io/style-dictionary/)
- [CSS Custom Properties Reference](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)
