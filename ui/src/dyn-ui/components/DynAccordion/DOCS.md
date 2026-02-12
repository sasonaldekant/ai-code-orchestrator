# DynAccordion Documentation

## 📌 Overview

**Category:** Molecule
**Status:** Stable

`DynAccordion` is a vertically stacked set of interactive headings that each reveal a section of content. It follows the WAI-ARIA Accordion pattern, supporting keyboard navigation and screen readers. It supports single or multiple expansion modes and can be controlled or uncontrolled.

## 🛠 Usage

```tsx
import { DynAccordion } from '@dyn-ui/react';

function Example() {
  const items = [
    { id: '1', title: 'Section 1', content: 'Content for section 1' },
    { id: '2', title: 'Section 2', content: 'Content for section 2' },
    { id: '3', title: 'Section 3', content: 'Content for section 3' },
  ];

  return <DynAccordion items={items} />;
}
```

## ⚙️ Properties (API)

### Quick Reference

| Prop              | Type                      | Default           | Description                          | Required |
| :---------------- | :------------------------ | :---------------- | :----------------------------------- | :------: |
| `items`           | `AccordionItem[]`         | -                 | Array of accordion items             |   Yes    |
| `multiple`        | `boolean`                 | `false`           | Allow multiple items to be expanded  |    No    |
| `variant`         | `'default' \| 'bordered'` | `'default'`       | Visual style variant                 |    No    |
| `size`            | `'sm' \| 'md' \| 'lg'`    | `'md'`            | Size variant                         |    No    |
| `loading`         | `boolean`                 | `false`           | Global loading state                 |    No    |
| `expandIcon`      | `ReactNode`               | -                 | Custom expansion icon                |    No    |
| `defaultExpanded` | `string[]`                | `[]`              | Initially expanded item IDs          |    No    |
| `expanded`        | `string[]`                | -                 | Controlled expanded item IDs         |    No    |
| `onChange`        | `(ids: string[]) => void` | -                 | Callback when expanded state changes |    No    |
| `id`              | `string`                  | -                 | Unique identifier                    |    No    |
| `className`       | `string`                  | -                 | Additional CSS classes               |    No    |
| `style`           | `CSSProperties`           | -                 | Inline styles                        |    No    |
| `data-testid`     | `string`                  | `'dyn-accordion'` | Test ID for automated testing        |    No    |

### Detailed Parameter Documentation

#### `items`

**Type:** `AccordionItem[]`
**Required:** Yes

**Description:**
The data source for the accordion. Each item represents a collapsible section with a unique identifier, title, and content.

**Structure:**

```ts
interface AccordionItem {
  id: string; // Unique identifier
  title: ReactNode; // Header content
  content: ReactNode; // Body content
  disabled?: boolean; // If true, item cannot be toggled
  loading?: boolean; // If true, item shows a loading spinner
  icon?: ReactNode; // Custom icon for this specific item
}
```

**Example:**

```tsx
<DynAccordion
  items={[
    {
      id: 'section-1',
      title: 'Personal Information',
      content: <ProfileForm />,
    },
    {
      id: 'section-2',
      title: 'Preferences',
      content: <PreferencesForm />,
      disabled: true,
    },
  ]}
/>
```

#### `multiple`

**Type:** `boolean`
**Default:** `false`
**Required:** No

**Description:**
Determines expansion behavior:

- `false` (default): Only one panel can be open at a time. Opening a new panel automatically closes the previous one.
- `true`: Users can toggle multiple panels open simultaneously.

**Example:**

```tsx
// Allow users to see multiple sections at once
<DynAccordion multiple items={faqItems} />
```

#### `variant`

**Type:** `'default' | 'bordered'`
**Default:** `'default'`
**Required:** No

**Description:**
Controls the visual appearance of the accordion container.

- `default`: Clean look with no outer border; items are separated by dividers.
- `bordered`: Container has a border and rounded corners, suitable for contained layouts.

#### `size`

**Type:** `'sm' | 'md' | 'lg'`
**Default:** `'md'`
**Required:** No

**Description:**
Controls the padding and font size of the accordion headers and content.

- `sm`: Compact layout for tight spaces.
- `md`: Standard layout (default).
- `lg`: Large layout for high visibility.

#### `loading`

**Type:** `boolean`
**Default:** `false`
**Required:** No

**Description:**
When `true` on the `DynAccordion`, all items are put into a loading state (disabled with a spinner). When `true` on an `AccordionItem`, only that specific item is in a loading state.

#### `expandIcon`

**Type:** `ReactNode`
**Required:** No

**Description:**
Allows replacing the default chevron icon with a custom element.

#### `expanded` / `onChange` (Controlled Mode)

**Type:** `expanded: string[]`, `onChange: (ids: string[]) => void`
**Required:** No

**Description:**
Used for fully controlled component behavior.

- `expanded`: A list of IDs that should be currently open.
- `onChange`: Callback fired when a user tries to toggle an item. It provides the new list of IDs that _should_ be open.

**Example:**

```tsx
const [expandedIds, setExpandedIds] = useState(['info']);

return (
  <DynAccordion expanded={expandedIds} onChange={setExpandedIds} items={data} />
);
```

#### `defaultExpanded`

**Type:** `string[]`
**Default:** `[]`
**Required:** No

**Description:**
Sets the initial state for an uncontrolled accordion. Provides a list of IDs that should be open when the component first mounts.

#### `children`

**Type:** `ReactNode`
**Required:** No

**Description:**
Standard React children prop. Note that `DynAccordion` primarily uses the `items` prop for content, so `children` might not be rendered depending on implementation. It is exposed as a standard prop.

#### `id`, `className`, `style`

**Type:** `string`, `string`, `CSSProperties`
**Required:** No

**Description:**
Standard HTML attributes for customization. `className` is appended to the root container classes. `id` and `style` are applied directly to the root element.

#### `data-testid`

**Type:** `string`
**Default:** `'dyn-accordion'`
**Required:** No

**Description:**
A unique identifier for automated testing (e.g., with React Testing Library).

#### Accessibility Props (`role`, `aria-*`)

**Type:** `string`
**Required:** No

**Description:**

- `role`: Standard HTML role attribute.
- `aria-label`, `aria-labelledby`, `aria-describedby`: Standard ARIA attributes to improve screen reader accessibility.

## 🎨 Design Tokens

This component uses the following design tokens:

- **Background**:
  - `--dyn-accordion-bg` (default: `--dyn-semantic-surface`)
  - `--dyn-accordion-header-bg-hover` (default: `--dyn-semantic-surface-hover`)
- **Border**:
  - `--dyn-accordion-border` (default: `--dyn-semantic-border`)
  - `--dyn-accordion-radius` (default: `--dyn-border-radius-md`)
- **Text**:
  - `--dyn-accordion-header-color` (default: `--dyn-semantic-text`)
  - `--dyn-accordion-icon-color` (default: `--dyn-semantic-text-secondary`)
  - `--dyn-accordion-content-color` (default: `--dyn-semantic-text-secondary`)
- **Spacing**:
  - `--dyn-accordion-header-padding` (default: `--dyn-spacing-md`)
  - `--dyn-accordion-content-padding` (default: `--dyn-spacing-md`)

### Customization

```css
.my-accordion-theme {
  --dyn-accordion-header-bg-hover: var(--dyn-color-primary-light);
  --dyn-accordion-radius: 0;
}
```

## ♿ Accessibility (A11y)

- **Role**: `region` (for content panels)
- **ARIA**:
  - `aria-expanded` on headers indicates state.
  - `aria-controls` links headers to content panels.
  - `aria-labelledby` links content panels to headers.
- **Keyboard**:
  - `Enter` / `Space`: Toggles the focused header.
  - `Tab`: Navigates through headers and focusable content.

## 📝 Best Practices

- ✅ **Do** usage unique stable `id`s for items.
- ✅ **Do** use `multiple` if comparing content between sections is important.
- ❌ **Avoid** putting massive amounts of content in a single accordion item; consider lazy loading or sub-pages if content is extremely heavy.
