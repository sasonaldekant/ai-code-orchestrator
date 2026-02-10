# Implementation Plan - Standardize XS Button Size

## Goal Description

Align button sizing between `DynTable` and `DynGrid` by introducing a standardized `xs` size to `DynButton`.
Currently, `DynTable` uses `!important` CSS overrides to force buttons to be smaller than the minimum `sm` size, causing inconsistency when trying to replicate the look in `DynGrid`.
By standardizing `xs` size, we ensure consistent density across all components.

## User Review Required

> [!NOTE]
> This introduces a new size `'xs'` to `DynButton`. Although backward compatible, it's a new feature.

## Proposed Changes

### [DynButton]

#### [MODIFY] [DynButton.types.ts](file:///e:/PROGRAMING/AI_Projects/dyn-ui-main-v02/packages/dyn-ui-react/src/components/DynButton/DynButton.types.ts)

- Add `'xs'` to `DynButtonSize` type.

#### [MODIFY] [DynButton.module.css](file:///e:/PROGRAMING/AI_Projects/dyn-ui-main-v02/packages/dyn-ui-react/src/components/DynButton/DynButton.module.css)

- Add `.sizeXs` class:
  - `padding: var(--dyn-spacing-2xs, 0.25rem) var(--dyn-spacing-sm, 0.5rem)`
  - `font-size: var(--dyn-font-size-xs, 0.75rem)`
  - `min-height: 1.75rem` (28px)

### [DynTable]

#### [MODIFY] [DynTable.tsx](file:///e:/PROGRAMING/AI_Projects/dyn-ui-main-v02/packages/dyn-ui-react/src/components/DynTable/DynTable.tsx)

- Update `buttonSize` logic to use `'xs'` when table size is `'sm'`.

#### [MODIFY] [DynTable.module.css](file:///e:/PROGRAMING/AI_Projects/dyn-ui-main-v02/packages/dyn-ui-react/src/components/DynTable/DynTable.module.css)

- Remove the `!important` override on `.actionsContainer button`.

### [DynGrid Stories]

#### [MODIFY] [DynGrid.stories.tsx](file:///e:/PROGRAMING/AI_Projects/dyn-ui-main-v02/packages/dyn-ui-react/src/components/DynGrid/DynGrid.stories.tsx)

- Update `getColumns` helper to use `buttonSize = size === 'sm' ? 'xs' : 'sm'`.
- Remove manual style hacks if added previously.

## Verification Plan

### Manual Verification

- Run `npm run storybook`.
- Check `DynButton` -> `Sizes` story (verify `xs` size works).
- Check `DynTable` -> `Small Size` story (verify buttons look same as before, compact).
- Check `DynGrid` -> `Small Size` story (verify buttons match `DynTable`).

### [DynToolbar]

#### [MODIFY] [DynToolbar.stories.tsx](file:///e:/PROGRAMING/AI_Projects/dyn-ui-main-v02/packages/dyn-ui-react/src/components/DynToolbar/DynToolbar.stories.tsx)

- Update `CustomComponents` story:
  - Replace `#666` with `var(--dyn-semantic-text-secondary)`
  - Replace `#ccc` with `var(--dyn-semantic-border)`
  - Replace `#f0f0f0` with `var(--dyn-semantic-background-subtle)`
  - Replace `#007bff` with `var(--dyn-theme-primary)`
  - Replace `white` with `var(--dyn-semantic-text-inverse)`
  - Ensure text colors are semantic to work in both light and dark modes.

## Verification Plan

### Manual Verification

- Run `npm run storybook`.
- Check `DynToolbar` -> `Custom Components` story in Dark Mode.
- Verify "Theme:" label and "John Doe" text are visible.

### [DynPopup]

#### [MODIFY] [DynPopup.module.css](file:///e:/PROGRAMING/AI_Projects/dyn-ui-main-v02/packages/dyn-ui-react/src/components/DynPopup/DynPopup.module.css)

- Update `--dyn-popup-bg`:
  - Change `var(--dyn-semantic-surface-card)` to `var(--dyn-semantic-surface-layer1)` (or `surface-elevated` if available) to ensure proper contrast in dark mode.
- Update `--dyn-popup-item-text`:
  - Ensure it uses `var(--dyn-semantic-text)` correctly.

## Verification Plan (DynPopup)

### Manual Verification

- Run `npm run storybook`.
- Check `DynPopup` -> `Default` story in Dark Mode.
- Verify background is dark (not white) and text is visible.
