# Implementation Plan - Integrate DynUI Components

## Goal
Integrate `dyn-ui` components into `ai-code-orchestrator` by copying the source code and design tokens locally, as the package is not yet published to npm.

## User Review Required
> [!IMPORTANT]
> This approach involves copying the source code of `dyn-ui-react` and `design-tokens` into `ai-code-orchestrator/ui/src/dyn-ui`. This decouples it from the original repo but allows for easy modification ("oživljavanje"). Any upstream updates to `dyn-ui` will need to be manually synchronized.

## Proposed Changes

### 1. Copy Source Files
- Copy `dyn-ui-main-v01/packages/dyn-ui-react/src` to `ai-code-orchestrator/ui/src/dyn-ui`.
- Copy relevant parts of `dyn-ui-main-v01/packages/design-tokens` to `ai-code-orchestrator/ui/src/dyn-design-tokens`.

### 2. Configure Dependencies
- Install required peer dependencies in `ai-code-orchestrator/ui`:
  - `classnames` (already seems present or needed)
  - `lucide-react` (already present)
  - `framer-motion` (already present)

### 3. Configure Vite Aliases
- specific valid alias in `vite.config.ts`:
  - `@dyn-ui/react` -> `./src/dyn-ui`
  - `@dyn-ui/design-tokens` -> `./src/dyn-design-tokens` (or specific CSS file path)

### 4. Integrate Styles
- Copy `dyn-ui-main-v01/packages/design-tokens/styles` to `ai-code-orchestrator/ui/src/dyn-design-tokens`.
- Import `ai-code-orchestrator/ui/src/dyn-design-tokens/index.css` in `main.tsx`.

## Verification Plan

### Automated Tests
- None planned for this integration task specifically, as it's a structural change.

### Manual Verification
- Add a temporary `DynButton` to `App.tsx`:
```tsx
import { DynButton } from '@dyn-ui/react';

// In App component:
<DynButton label="Test Button" kind="primary" />
```
- Verify the button renders with correct styles and no console errors.
- Verify `vite` build succeeds.
