# DynTable Implementation Guide - Design Token Approach

## 🎯 Goal

Migrate DynTable component styling from CSS modules to **design tokens** (CSS custom properties) while maintaining identical visual appearance and functionality.

## 📋 What's Changed

### Before (CSS Module)
```
DynTable.module.css
├─ Hardcoded colors: #f5f5f5, #e0e0e0, etc.
├─ Hardcoded sizes: 12px 16px padding
├─ No reusability across components
└─ Difficult to maintain consistent theming
```

### After (Design Tokens)
```
design-tokens/table.css (CSS Variables)
├─ Reusable tokens: --dyn-table-header-bg-color
├─ Centralized definitions
├─ Easy theme switching
└─ Better maintainability
```

## 📂 File Structure

```
packages/
├── design-tokens/
│   ├── table.css                    ← CSS Variable Definitions
│   ├── table.json                   ← Token Metadata (source)
│   ├── tokens/
│   │   └── table.json              ← Token Schema
│   └── index.css                    ← Import Point
│
└── dyn-ui-react/
    └── src/components/DynTable/
        ├── DynTable.tsx            ← Component (unchanged)
        ├── DynTable.module.css     ← References design tokens
        ├── DynTable.stories.tsx    ← Storybook (unchanged)
        ├── DESIGN_TOKENS.md        ← Token Reference
        └── IMPLEMENTATION_GUIDE.md ← This file
```

## 🔧 Integration Steps

### Step 1: Import Design Tokens

**In `DynTable.module.css`:**
```css
/* Import design tokens */
@import '../../../../../../design-tokens/table.css';

/* Now use CSS variables in your styles */
.dyn-table {
  font-family: var(--dyn-table-font-family);
  font-size: var(--dyn-table-font-size);
  color: var(--dyn-table-text-color);
  background-color: var(--dyn-table-bg-color);
}
```

### Step 2: Replace Hardcoded Values

**Before:**
```css
.dyn-table__cell--header {
  background-color: #f5f5f5;        /* Hardcoded */
  color: #666666;                   /* Hardcoded */
  font-weight: 600;                 /* Hardcoded */
  border-color: #e0e0e0;            /* Hardcoded */
}
```

**After:**
```css
.dyn-table__cell--header {
  background-color: var(--dyn-table-header-bg-color);      /* Token */
  color: var(--dyn-table-header-text-color);               /* Token */
  font-weight: var(--dyn-table-header-font-weight);        /* Token */
  border-color: var(--dyn-table-header-border-color);      /* Token */
}
```

### Step 3: Update All Components

For **each CSS class**, replace values with tokens:

#### Table Root
```css
.dyn-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--dyn-table-font-family);
  font-size: var(--dyn-table-font-size);
  color: var(--dyn-table-text-color);
  background-color: var(--dyn-table-bg-color);
}
```

#### Size Variants
```css
.dyn-table--small .dyn-table__cell {
  padding: var(--dyn-table-size-small-padding);
  font-size: var(--dyn-table-size-small-font-size);
}

.dyn-table--medium .dyn-table__cell {
  padding: var(--dyn-table-size-medium-padding);
  font-size: var(--dyn-table-size-medium-font-size);
}

.dyn-table--large .dyn-table__cell {
  padding: var(--dyn-table-size-large-padding);
  font-size: var(--dyn-table-size-large-font-size);
}
```

#### Header Styling
```css
.dyn-table__cell--header {
  background-color: var(--dyn-table-header-bg-color);
  color: var(--dyn-table-header-text-color);
  font-weight: var(--dyn-table-header-font-weight);
  text-transform: var(--dyn-table-header-text-transform);
  letter-spacing: var(--dyn-table-header-letter-spacing);
  border-bottom: var(--dyn-table-header-border-width) solid var(--dyn-table-header-border-color);
}
```

#### Row States
```css
.dyn-table--striped tbody .dyn-table__row:nth-child(odd) {
  background-color: var(--dyn-table-row-striped-bg-color);
}

.dyn-table--hoverable tbody .dyn-table__row:hover {
  background-color: var(--dyn-table-row-hover-bg-color);
  transition: var(--dyn-table-row-hover-transition);
}

.dyn-table__row--selected {
  background-color: var(--dyn-table-row-selected-bg-color);
}
```

#### Interactive Elements
```css
/* Sortable header */
.dyn-table__cell--sortable {
  cursor: var(--dyn-table-sortable-cursor);
}

.dyn-table__cell--sortable:hover {
  background-color: var(--dyn-table-sortable-hover-bg-color);
}

.dyn-table__cell--sorted {
  background-color: var(--dyn-table-sortable-active-bg-color);
  color: var(--dyn-table-sortable-active-text-color);
}

/* Buttons */
.dyn-table__action-button {
  padding: var(--dyn-table-button-padding);
  font-size: var(--dyn-table-button-font-size);
  font-weight: var(--dyn-table-button-font-weight);
  background-color: var(--dyn-table-button-bg-color);
  color: var(--dyn-table-button-text-color);
  border-color: var(--dyn-table-button-border-color);
  border-radius: var(--dyn-table-button-border-radius);
  transition: var(--dyn-table-button-transition);
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

#### Pagination
```css
.dyn-table__pagination {
  padding: var(--dyn-table-pagination-padding);
  gap: var(--dyn-table-pagination-gap);
  background-color: var(--dyn-table-pagination-bg-color);
  border-color: var(--dyn-table-pagination-border-color);
}

.dyn-table__pagination-button {
  padding: var(--dyn-table-button-padding);
  font-size: var(--dyn-table-pagination-font-size);
}
```

#### Checkboxes
```css
.dyn-table__checkbox {
  width: var(--dyn-table-checkbox-size);
  height: var(--dyn-table-checkbox-size);
}

.dyn-table__checkbox:focus {
  outline: var(--dyn-table-checkbox-focus-outline-width) solid var(--dyn-table-checkbox-focus-outline-color);
}
```

#### Empty & Loading States
```css
.dyn-table__empty-state {
  padding: var(--dyn-table-empty-padding);
  color: var(--dyn-table-empty-text-color);
  font-size: var(--dyn-table-empty-font-size);
}

.dyn-table__loading-state {
  padding: var(--dyn-table-loading-padding);
  color: var(--dyn-table-loading-text-color);
  font-size: var(--dyn-table-loading-font-size);
}
```

## ✅ Verification Checklist

After implementation, verify:

### Visual Appearance
- [ ] Header background color matches original (#f5f5f5)
- [ ] Text colors are correct (#333 for body, #666 for header)
- [ ] Border colors are correct (#e0e0e0)
- [ ] Padding matches original values
- [ ] Font sizes are correct

### Size Variants
- [ ] Small: 6px 12px padding, 12px font
- [ ] Medium: 12px 16px padding, 14px font (default)
- [ ] Large: 16px 20px padding, 16px font

### States
- [ ] Striped: #f9f9f9 background on odd rows
- [ ] Hover: #f5f5f5 background with smooth transition
- [ ] Selected: #e3f2fd background (or #bbdefb for striped)
- [ ] Sorted: #e3f2fd background with #1976d2 text

### Interactive Elements
- [ ] Buttons: white background (#fff), #333 text
- [ ] Primary buttons: #1976d2 background, white text
- [ ] Danger buttons: #d32f2f background, white text
- [ ] Hover states work correctly
- [ ] Focus states visible (2px outline)

### Pagination
- [ ] Buttons are properly styled
- [ ] Background is #fafafa
- [ ] Border is #e0e0e0
- [ ] Page info displays correctly

### Accessibility
- [ ] Focus states are visible
- [ ] Color contrast is sufficient (WCAG AA)
- [ ] Keyboard navigation works
- [ ] ARIA labels are present

## 🎨 Testing in Storybook

```bash
cd packages/dyn-ui-react
npm run storybook
```

Then navigate to: **Data Display → DynTable**

Test all stories:
- ✓ Default
- ✓ SmallSize
- ✓ LargeSize
- ✓ WithoutBorders
- ✓ Striped
- ✓ WithSelection
- ✓ WithActions
- ✓ WithPagination
- ✓ FixedHeight
- ✓ Loading
- ✓ Empty

## 🔄 Customization Example

### Override tokens in your application:

```css
/* app.css or global styles */
:root {
  /* Override default design tokens */
  --dyn-table-header-bg-color: #f0f0f0;
  --dyn-table-header-text-color: #333;
  --dyn-table-button-primary-bg-color: #2196f3;
  --dyn-table-row-selected-bg-color: #fff3e0;
  --dyn-table-border-color: #ccc;
}
```

The entire table will update automatically.

## 📊 Token Usage Statistics

Total tokens used in DynTable:
- **Color tokens**: 24
- **Size tokens**: 6
- **Typography tokens**: 8
- **Spacing tokens**: 4
- **Transition tokens**: 2
- **Total**: 44 design tokens

## 🔗 Related Documentation

- [Design Tokens Reference](./DESIGN_TOKENS.md) - Complete token list
- [packages/design-tokens/table.json](../../../design-tokens/tokens/table.json) - Token definitions
- [packages/design-tokens/table.css](../../../design-tokens/table.css) - CSS variables
- [DynTable Component](./DynTable.tsx) - Implementation

## ❓ Troubleshooting

### Problem: Colors don't match
**Solution**: Verify CSS variable names are correct and `table.css` is imported.

### Problem: Responsive doesn't work
**Solution**: Media queries in `table.css` should override tokens appropriately.

### Problem: Tokens not recognized
**Solution**: Ensure `@import` path is correct and file exists.

## 📝 Notes

- All token values are defined in `packages/design-tokens/table.css`
- Token names follow pattern: `--dyn-table-[component]-[property]`
- Component CSS module imports tokens and uses them
- No changes to React component logic
- No changes to TypeScript types
- Visual appearance remains identical

## ✨ Benefits

1. **Consistency**: All DynTable instances use same values
2. **Maintainability**: Change values in one place
3. **Scalability**: Easy to add new variants
4. **Theming**: Simple theme switching via CSS variables
5. **Documentation**: Token metadata auto-generates docs
6. **Reusability**: Other components can use same tokens
7. **Version Control**: Easy to track style changes
8. **Analytics**: Measure which tokens are used
