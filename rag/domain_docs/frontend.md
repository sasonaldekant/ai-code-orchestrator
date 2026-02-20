# Frontend Notes

## DynUI Layout Constraints

- Only use **Tailwind**, native CSS tokens inside `ui/src/dyn-ui` when overriding styles, explicitly via `var(--dyn-color...)`.
- **Form Layout**: When previewing forms in the playground (`FormStudioTab.tsx`), the form MUST respect `12-col` grid (`colSpan`). Do not hardcode `md:grid-cols-2`. Every renderer should parse `"colSpan": "half" | "third" | "quarter"` and compile to Tailwind logic (`col-span-12 md:col-span-6`, etc.). 
- **Component Linking**: We do not duplicate code from `dyn-ui-main-v01`. We use localized npm protocols (`pnpm add file:../`) inside package.json to symlink the components dynamically, ensuring one source of truth.
