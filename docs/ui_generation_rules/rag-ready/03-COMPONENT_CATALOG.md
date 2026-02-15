---
title: Component Catalog
type: reference
category: components
version: 1.0.0
last_updated: 2026-02-13
---

# DynUI Component Catalog

> **Complete reference for all 45 components**
> **Import**: `import { ComponentName } from '@dyn-ui/react'`

## 📚 Component Categories

### Layout Components (7)

Foundational building blocks for page structure.

| Component | Purpose | Key Props | Size Support |
|-----------|---------|-----------|-------------|
| **DynBox** | Polymorphic container | `as`, `display`, `gap`, `padding` | - |
| **DynContainer** | Page container with max-width | `maxWidth`, `padding`, `as` | - |
| **DynFlex** | Flexbox layout | `direction`, `align`, `justify`, `gap` | - |
| **DynStack** | Vertical/horizontal stack | `direction`, `gap`, `spacing` | - |
| **DynGrid** | CSS Grid layout | `columns`, `rows`, `gap` | - |
| **DynPage** | Full page template | `header`, `sidebar`, `footer` | - |
| **ThemeSwitcher** | Theme toggle | `defaultTheme` | - |

### Form Components (10)

User input and form controls.

| Component | Purpose | Key Props | Sizes |
|-----------|---------|-----------|-------|
| **DynButton** | Action button | `color`, `variant`, `loading`, `disabled` | sm, md, lg |
| **DynInput** | Text input | `type`, `placeholder`, `error`, `disabled` | sm, md, lg |
| **DynSelect** | Dropdown select | `options`, `placeholder`, `disabled` | sm, md, lg |
| **DynCheckbox** | Checkbox control | `checked`, `color`, `disabled` | sm, md, lg |
| **DynRadio** | Radio button | `checked`, `color`, `disabled` | sm, md, lg |
| **DynSwitch** | Toggle switch | `checked`, `color`, `disabled` | sm, md, lg |
| **DynLabel** | Form label | `required`, `htmlFor` | - |
| **DynTextArea** | Multi-line text input | `rows`, `placeholder`, `disabled` | sm, md, lg |
| **DynFieldContainer** | Form field wrapper | `label`, `error`, `required`, `helperText` | - |
| **DynUpload** | File upload | `accept`, `multiple`, `maxSize` | sm, md, lg |

### Navigation Components (8)

Menu, navigation, and wayfinding.

| Component | Purpose | Key Props | Size Support |
|-----------|---------|-----------|-------------|
| **DynAppbar** | Top navigation bar | `logo`, `actions`, `sticky` | - |
| **DynSidebar** | Side navigation | `items`, `collapsed`, `position` | - |
| **DynBreadcrumb** | Breadcrumb navigation | `items`, `separator` | - |
| **DynMenu** | Dropdown menu | `items`, `trigger` | - |
| **DynToolbar** | Action toolbar | `actions`, `variant` | - |
| **DynStepper** | Step indicator | `steps`, `currentStep` | - |
| **DynTreeView** | Hierarchical tree | `data`, `expanded` | - |
| **DynTabs** | Tab navigation | `tabs`, `activeTab` | - |
| **DynResponsiveTabs** | Responsive tabs | `tabs`, `activeTab`, `breakpoint` | - |

### Display Components (8)

Visual indicators and feedback.

| Component | Purpose | Key Props | Sizes |
|-----------|---------|-----------|-------|
| **DynAvatar** | User avatar | `src`, `alt`, `badge`, `loading` | sm, md, lg, xl |
| **DynBadge** | Notification badge | `count`, `color`, `max` | sm, md, lg |
| **DynToast** | Toast notification | `message`, `type`, `duration` | - |
| **DynProgress** | Progress indicator | `value`, `max`, `variant` | sm, md, lg |
| **DynLoading** | Loading spinner | `size`, `color` | sm, md, lg |
| **DynDivider** | Visual separator | `orientation`, `variant` | - |
| **DynTooltip** | Hover tooltip | `content`, `placement` | - |
| **DynIcon** | Icon wrapper | `name`, `size`, `color` | sm, md, lg |

### Data Components (5)

Display and interact with data.

| Component | Purpose | Key Props | Size Support |
|-----------|---------|-----------|-------------|
| **DynTable** | Data table | `columns`, `data`, `sortable`, `pagination` | sm, md, lg |
| **DynListView** | List with items | `items`, `renderItem`, `expandable` | sm, md, lg |
| **DynChart** | Chart visualization | `type`, `data`, `options` | - |
| **DynGauge** | Gauge/meter | `value`, `min`, `max`, `thresholds` | sm, md, lg |
| **DynAccordion** | Collapsible sections | `items`, `multiple` | - |

### Advanced Components (7)

Complex interactions and overlays.

| Component | Purpose | Key Props | Size Support |
|-----------|---------|-----------|-------------|
| **DynDatePicker** | Date selection | `value`, `onChange`, `format`, `range` | sm, md, lg |
| **DynDropdown** | Dropdown container | `trigger`, `content`, `placement` | - |
| **DynPopup** | Popup overlay | `trigger`, `content`, `modal` | - |
| **DynDialog** | Dialog box | `open`, `title`, `actions`, `onClose` | sm, md, lg |
| **DynModal** | Modal overlay | `open`, `onClose`, `size` | sm, md, lg |

## 🔗 Related Documentation

- [Quick Start](01-QUICK_START.md) - Getting started
- [Design Tokens](02-DESIGN_TOKENS.md) - Token reference
- [Styling Guide](04-STYLING_GUIDE.md) - Styling patterns
- [Code Examples](05-CODE_EXAMPLES.md) - Complete examples
- [Individual Component Docs](components/) - Per-component details

---

**Next**: Explore [Styling Guide](04-STYLING_GUIDE.md) for customization patterns.
