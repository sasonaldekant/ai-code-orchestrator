---
title: DynUI Documentation Index
type: navigation
category: root
version: 1.0.0
last_updated: 2026-02-13
---

# DynUI Documentation Index

> **Purpose**: Master index for RAG-optimized DynUI documentation
> **Audience**: AI Agents, Code Generators, Developers
> **Status**: Production Ready

## 📚 Quick Navigation

### Essential Reading (Start Here)

1. **[Quick Start Guide](01-QUICK_START.md)** - Get started in 5 minutes
2. **[Design Token System](02-DESIGN_TOKENS.md)** - Complete token reference
3. **[Component Catalog](03-COMPONENT_CATALOG.md)** - All 45 components
4. **[Styling Guide](04-STYLING_GUIDE.md)** - How to style components
5. **[Code Examples](05-CODE_EXAMPLES.md)** - Real-world patterns

### Component Reference

Detailed documentation for each component:

#### Layout Components (7)
- [DynBox](components/DynBox.md) - Polymorphic container
- [DynContainer](components/DynContainer.md) - Page container
- [DynFlex](components/DynFlex.md) - Flex layout
- [DynStack](components/DynStack.md) - Vertical/horizontal stack
- [DynGrid](components/DynGrid.md) - CSS Grid layout
- [DynPage](components/DynPage.md) - Full page template
- [ThemeSwitcher](components/ThemeSwitcher.md) - Theme toggle

#### Form Components (10)
- [DynButton](components/DynButton.md)
- [DynInput](components/DynInput.md)
- [DynSelect](components/DynSelect.md)
- [DynCheckbox](components/DynCheckbox.md)
- [DynRadio](components/DynRadio.md)
- [DynSwitch](components/DynSwitch.md)
- [DynLabel](components/DynLabel.md)
- [DynTextArea](components/DynTextArea.md)
- [DynFieldContainer](components/DynFieldContainer.md)
- [DynUpload](components/DynUpload.md)

#### Navigation Components (8)
- [DynAppbar](components/DynAppbar.md)
- [DynSidebar](components/DynSidebar.md)
- [DynBreadcrumb](components/DynBreadcrumb.md)
- [DynMenu](components/DynMenu.md)
- [DynToolbar](components/DynToolbar.md)
- [DynStepper](components/DynStepper.md)
- [DynTreeView](components/DynTreeView.md)
- [DynTabs](components/DynTabs.md)
- [DynResponsiveTabs](components/DynResponsiveTabs.md)

#### Display Components (8)
- [DynAvatar](components/DynAvatar.md)
- [DynBadge](components/DynBadge.md)
- [DynToast](components/DynToast.md)
- [DynProgress](components/DynProgress.md)
- [DynLoading](components/DynLoading.md)
- [DynDivider](components/DynDivider.md)
- [DynTooltip](components/DynTooltip.md)
- [DynIcon](components/DynIcon.md)

#### Data Components (5)
- [DynTable](components/DynTable.md)
- [DynListView](components/DynListView.md)
- [DynChart](components/DynChart.md)
- [DynGauge](components/DynGauge.md)
- [DynAccordion](components/DynAccordion.md)

#### Advanced Components (7)
- [DynDatePicker](components/DynDatePicker.md)
- [DynDropdown](components/DynDropdown.md)
- [DynPopup](components/DynPopup.md)
- [DynDialog](components/DynDialog.md)
- [DynModal](components/DynModal.md)

## 🎯 Document Types

### By Purpose

| Type | Files | Purpose |
|------|-------|----------|
| **Foundation** | 01, 02 | Core concepts, tokens |
| **Reference** | 03, 04 | Component API, styling |
| **Examples** | 05 | Implementation patterns |
| **Component Docs** | components/* | Per-component details |

### By Audience

| Audience | Start With | Then Read |
|----------|-----------|------------|
| **AI Code Generators** | 01, 02, 05 | Component-specific docs |
| **Human Developers** | 01, 04, 05 | 02, 03 |
| **Design Systems** | 02, 04 | Component docs |

## 📊 Document Statistics

- **Total Components**: 45
- **Foundation Tokens**: 80+
- **Code Examples**: 50+
- **Documented Props**: 300+

## 🔗 External References

- **Source Code**: `packages/dyn-ui-react/src/components/`
- **Design Tokens**: `packages/design-tokens/styles/`
- **Storybook**: Run `npm run storybook`

## 📝 Version Info

- **Documentation Version**: 1.0.0
- **Component Library**: @dyn-ui/react v2.1
- **Last Updated**: February 13, 2026
- **Status**: Production

## 💡 Usage Tips for AI Agents

1. **Always start with** `01-QUICK_START.md` for context
2. **Reference tokens from** `02-DESIGN_TOKENS.md` (never hardcode)
3. **Check examples in** `05-CODE_EXAMPLES.md` for patterns
4. **Component-specific details** in `components/[ComponentName].md`
5. **Follow 3-layer token fallback** pattern everywhere

## 🚫 What's NOT in These Docs

- Historical data / changelogs
- Audit logs / implementation details
- Internal development workflows
- Legacy patterns / deprecated APIs

**Focus**: Current state, actionable information, clear examples.

---

**Next Steps**: Read [01-QUICK_START.md](01-QUICK_START.md)
