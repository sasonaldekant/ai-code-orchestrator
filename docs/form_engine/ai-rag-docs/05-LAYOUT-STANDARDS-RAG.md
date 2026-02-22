# GUI Layout Standards for DynUI Forms (RAG Reference)

## 01. Context & Overview
This document defines the graphical user interface (GUI) layout standards for DynUI forms. It serves as a source of truth for AI agents generating or validating form layouts, ensuring consistency with industry standards (Material Design, Bootstrap, Ant Design) and DynUI design tokens.

---

## 02. Form Width Standards (Max-Width)
Forms should not span the full width of a high-resolution screen to maintain readability.

| Category | Token | Value | Use Case |
| :--- | :--- | :--- | :--- |
| **Narrow** | `dyn.form.maxWidth.narrow` | 480px | Login, password reset, very short forms (1 column). |
| **Standard** | `dyn.form.maxWidth.standard` | 720px | Core business forms, underwriting questions (2-3 columns). |
| **Wide** | `dyn.form.maxWidth.wide` | 960px | Complex enterprise forms, multi-section wizards. |
| **Full** | `dyn.form.maxWidth.full` | 100% | Forms embedded in sidebars or small containers. |

---

## 03. Grid System (12-Column Foundation)
DynUI uses a **12-column grid system** for field alignment.

### Field Positioning (colSpan)
Fields are arranged using `colSpan` properties in the JSON Schema.

| colSpan | Columns | Fields per Row | Recommended Usage |
| :--- | :--- | :--- | :--- |
| **full** | 12 | 1 | Textarea, Address, Headers, Descriptions. |
| **half** | 6 | 2 | First Name + Last Name, Email + Phone. |
| **third** | 4 | 3 | City + Zip + Country, Date + Time + User. |
| **quarter** | 3 | 4 | Short codes, Currency symbols, Numbers. |

### Spacing (Gaps)
- **Column Gap**: 16px (`dyn.grid.gap`).
- **Row Gap**: 16px (`dyn.grid.rowGap`).
- **Section Gap**: 48px (`dyn.form.section.gap`).

---

## 04. Component Sizing & Accessibility
To comply with **WCAG 2.1 AA**, all interactive components must meet minimum touch target sizes.

- **Minimum Height**: 44px (`dyn.form.field.minHeight`).
- **Label Spacing**: 4px gap between label and input.
- **Form Padding**: 32px (`dyn.form.padding.x/y`) for desktop, 16px for mobile.

---

## 05. Responsive Behavior
Layouts must adapt to screen size based on `dyn.layout.breakpoint`:

1. **Mobile (<768px)**: All fields collapse to `span 12` (full width).
2. **Tablet (768px - 991px)**: `half` spans remain, `third` and `quarter` collapse to `half` or `full`.
3. **Desktop (>992px)**: All `colSpan` values (half, third, quarter) are respected.

---

## 06. Implementation Patterns

### JSON Schema Integration
AI Agents should inject the `ui:layout` property into the field schema:

```json
{
  "id": "email_address",
  "type": "text",
  "label": "Email",
  "ui:layout": {
    "colSpan": "half",
    "row": 1
  }
}
```

### CSS Variable Mapping
```css
.form-grid {
  display: grid;
  grid-template-columns: repeat(var(--dyn-grid-columns), 1fr);
  gap: var(--dyn-grid-gap);
}

.field-half {
  grid-column: span var(--dyn-form-layout-colspan-half);
}
```

---

## 07. GAP Analysis & Status
- [x] **Form Tokens**: Implemented in `form.json`.
- [x] **Grid Extensions**: Implemented in `grid.json`.
- [x] **Documentation**: Current document (`05-LAYOUT-STANDARDS-RAG.md`).
- [ ] **Engine Support**: ValidationEngine needs update to support `colSpan` metadata.
- [ ] **React Support**: `FieldContainer` needs to apply grid classes based on tokens.
