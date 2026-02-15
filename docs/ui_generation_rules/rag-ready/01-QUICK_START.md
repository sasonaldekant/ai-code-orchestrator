---
title: DynUI Quick Start
type: guide
category: foundation
version: 1.0.0
last_updated: 2026-02-13
---

# DynUI Quick Start Guide

> **Goal**: Get AI agents generating DynUI code in 5 minutes

## 🚀 Core Concepts (30 seconds)

### 1. Component Library

```tsx
import { DynButton, DynInput, DynBox } from '@dyn-ui/react';
```

**45 components organized in 5 categories:**
- Layout (7) - DynBox, DynFlex, DynContainer, DynStack, DynGrid
- Forms (10) - DynButton, DynInput, DynSelect, DynCheckbox
- Navigation (8) - DynAppbar, DynSidebar, DynMenu, DynTabs
- Display (8) - DynAvatar, DynBadge, DynToast, DynProgress
- Data (5) - DynTable, DynListView, DynChart
- Advanced (7) - DynModal, DynDialog, DynDatePicker

### 2. Design Token System

**3-Layer Architecture:**

```css
/* Layer 1: Foundation (Global) */
--dyn-color-primary: #2563eb;
--dyn-spacing-sm: 8px;

/* Layer 2: Component (Local) */
--dyn-button-bg: var(--dyn-theme-primary, #2563eb);

/* Layer 3: Theme (Context) */
@media (prefers-color-scheme: dark) {
  --dyn-color-primary: #3b82f6;
}
```

### 3. Prop Patterns

```tsx
// Size variants: sm | md | lg
<DynButton size="md" />

// Color variants: primary | success | danger | warning | info
<DynButton color="primary" />

// Common props: disabled, loading, className, style
<DynButton disabled loading />
```

## 📝 Golden Rules (2 minutes)

### Rule #1: Never Hardcode Values

```tsx
// ❌ WRONG
<div style={{ color: '#2563eb', padding: '8px' }}>

// ✅ CORRECT
<DynBox 
  style={{ 
    color: 'var(--dyn-color-primary)', 
    padding: 'var(--dyn-spacing-sm)' 
  }}
>
```

### Rule #2: Use 3-Level Token Fallback

```css
/* In component CSS modules */
:root {
  --dyn-button-bg: var(
    --dyn-button-root-backgroundColor,    /* Component override */
    var(--dyn-theme-primary, #2563eb)     /* Theme + fallback */
  );
}
```

### Rule #3: Naming Conventions

```tsx
// Props: camelCase
size="sm" color="primary"

// CSS Classes: camelCase
.root .sizeSmall .colorPrimary

// CSS Variables: kebab-case with dyn- prefix
--dyn-button-bg --dyn-spacing-sm
```

### Rule #4: Form Components = 100% Width

```tsx
// All form inputs default to width: 100%
<DynInput />      {/* width: 100% */}
<DynSelect />     {/* width: 100% */}
<DynTextArea />   {/* width: 100% */}

// Action components = auto width
<DynButton />     {/* width: auto */}
<DynBadge />      {/* width: auto */}
```

### Rule #5: Default Spacing

```tsx
// Grid gap: sm (8px)
<DynFlex gap="sm">       {/* 8px */}
<DynStack gap="sm">      {/* 8px */}

// Cell padding: xs (4px)
<DynBox padding="xs">    {/* 4px */}

// Label gap: xs (4px)
<DynLabel gap="xs">      {/* 4px */}
```

## 💻 Common Patterns (2 minutes)

### Pattern 1: Simple Form

```tsx
import { DynBox, DynInput, DynButton, DynFieldContainer } from '@dyn-ui/react';

function LoginForm() {
  return (
    <DynBox gap="md" direction="vertical">
      <DynFieldContainer label="Email" required>
        <DynInput 
          type="email" 
          placeholder="you@example.com"
          size="md"
        />
      </DynFieldContainer>
      
      <DynFieldContainer label="Password" required>
        <DynInput 
          type="password"
          size="md"
        />
      </DynFieldContainer>
      
      <DynButton 
        color="primary" 
        size="md"
        type="submit"
      >
        Sign In
      </DynButton>
    </DynBox>
  );
}
```

### Pattern 2: Card Layout

```tsx
import { DynBox, DynAvatar, DynBadge, DynButton } from '@dyn-ui/react';

function UserCard({ user }) {
  return (
    <DynBox 
      padding="md" 
      gap="sm"
      style={{ 
        border: '1px solid var(--dyn-color-border)',
        borderRadius: 'var(--dyn-border-radius-md)'
      }}
    >
      <DynBox display="flex" align="center" gap="sm">
        <DynAvatar 
          src={user.avatar} 
          size="md"
          badge={{ count: user.notifications }}
        />
        
        <DynBox direction="vertical" gap="xs">
          <span>{user.name}</span>
          <DynBadge color="success" size="sm">
            {user.status}
          </DynBadge>
        </DynBox>
      </DynBox>
      
      <DynButton size="sm" variant="outline">
        View Profile
      </DynButton>
    </DynBox>
  );
}
```

### Pattern 3: Responsive Grid

```tsx
import { DynGrid, DynBox } from '@dyn-ui/react';

function Dashboard() {
  return (
    <DynGrid 
      columns={{ mobile: 1, tablet: 2, desktop: 3 }}
      gap="md"
    >
      <DynBox>Widget 1</DynBox>
      <DynBox>Widget 2</DynBox>
      <DynBox>Widget 3</DynBox>
    </DynGrid>
  );
}
```

### Pattern 4: Data Table

```tsx
import { DynTable } from '@dyn-ui/react';

function UsersTable({ users }) {
  return (
    <DynTable
      columns={[
        { key: 'name', label: 'Name', sortable: true },
        { key: 'email', label: 'Email' },
        { key: 'role', label: 'Role' }
      ]}
      data={users}
      size="md"
      striped
      hoverable
    />
  );
}
```

## 🎯 Size Scale Reference

| Size | Button Height | Input Height | Spacing |
|------|---------------|--------------|----------|
| `sm` | 32px | 32px | 8px |
| `md` | 40px | 40px | 16px |
| `lg` | 48px | 48px | 24px |

## 🎨 Color Variants

| Variant | Use Case | Components |
|---------|----------|------------|
| `primary` | Main actions | DynButton, DynCheckbox, DynRadio |
| `success` | Positive actions | All form controls |
| `danger` | Destructive actions | All form controls |
| `warning` | Caution states | All form controls |
| `info` | Informational | All form controls |

## ✨ Complete Example

```tsx
import {
  DynBox,
  DynFlex,
  DynInput,
  DynSelect,
  DynCheckbox,
  DynButton,
  DynFieldContainer
} from '@dyn-ui/react';

function RegistrationForm() {
  return (
    <DynBox 
      as="form"
      gap="md"
      style={{
        maxWidth: '400px',
        padding: 'var(--dyn-spacing-lg)'
      }}
    >
      <h2>Create Account</h2>
      
      {/* Name Fields */}
      <DynFlex gap="sm">
        <DynFieldContainer label="First Name" required>
          <DynInput size="md" />
        </DynFieldContainer>
        
        <DynFieldContainer label="Last Name" required>
          <DynInput size="md" />
        </DynFieldContainer>
      </DynFlex>
      
      {/* Email */}
      <DynFieldContainer label="Email" required>
        <DynInput type="email" size="md" />
      </DynFieldContainer>
      
      {/* Role */}
      <DynFieldContainer label="Role">
        <DynSelect 
          size="md"
          options={[
            { value: 'dev', label: 'Developer' },
            { value: 'designer', label: 'Designer' }
          ]}
        />
      </DynFieldContainer>
      
      {/* Terms */}
      <DynCheckbox color="primary">
        I agree to the terms and conditions
      </DynCheckbox>
      
      {/* Actions */}
      <DynFlex gap="sm" justify="end">
        <DynButton variant="outline" size="md">
          Cancel
        </DynButton>
        <DynButton color="primary" size="md" type="submit">
          Create Account
        </DynButton>
      </DynFlex>
    </DynBox>
  );
}
```

## 🔗 Next Steps

1. **Deep dive into tokens**: [02-DESIGN_TOKENS.md](02-DESIGN_TOKENS.md)
2. **Browse components**: [03-COMPONENT_CATALOG.md](03-COMPONENT_CATALOG.md)
3. **Learn styling**: [04-STYLING_GUIDE.md](04-STYLING_GUIDE.md)
4. **See more examples**: [05-CODE_EXAMPLES.md](05-CODE_EXAMPLES.md)

## ❓ Quick FAQ

**Q: Can I use inline styles?**
A: Yes, but use CSS variables: `style={{ color: 'var(--dyn-color-primary)' }}`

**Q: What about custom themes?**
A: Override Layer 1 tokens in `:root` or use `data-theme` attribute

**Q: How to handle dark mode?**
A: Automatic via `@media (prefers-color-scheme: dark)` overrides

**Q: TypeScript support?**
A: Full TypeScript support with `.types.ts` files for all components

---

**You're ready to generate DynUI code!** 🎉
