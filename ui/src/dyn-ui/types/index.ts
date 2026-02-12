/**
 * Type exports for DYN UI React
 * Centralized type definitions and re-exports.
 */

// Base component props - standardized across all components
export type {
  BaseComponentProps,
  VariantProps,
  SizeProps,
  ComponentSize,
  AccessibilityProps
} from './theme';

// Theme types
export type { ThemeName, ThemeConfig, ThemeContextValue, ColorVariant, Size } from './theme';

// Display Components types
export type {
  DynAvatarProps,
  DynAvatarRef,
  DynAvatarSize,
  DynAvatarShape,
  DynAvatarStatus,
} from '../components/DynAvatar/DynAvatar.types';
export {
  DYN_AVATAR_STATUS_LABELS,
} from '../components/DynAvatar/DynAvatar.types';

export type {
  DynBadgeProps,
  DynBadgeSize,
  DynBadgeVariant,
  DynBadgeSemanticColor,
} from '../components/DynBadge/DynBadge.types';
export {
  DYN_BADGE_COLORS,
  DYN_BADGE_SIZES,
  DYN_BADGE_VARIANTS,
} from '../components/DynBadge/DynBadge.types';

export type {
  DynButtonProps,
  DynButtonRef,
  DynButtonSize,
  DynButtonKind,
} from '../components/DynButton/DynButton.types';
export {
  DYN_BUTTON_DEFAULT_PROPS,
} from '../components/DynButton/DynButton.types';

export type { DynIconProps, IconDictionary, ProcessedIcon } from './icon.types';

export type {
  DynLabelProps,
} from '../components/DynLabel/DynLabel.types';
export {
  DYN_LABEL_DEFAULT_PROPS,
} from '../components/DynLabel/DynLabel.types';

// Form Components types
export type {
  DynFieldContainerProps,
} from '../components/DynFieldContainer/DynFieldContainer.types';

export type {
  ValidationRule,
  DynFieldRef,
  DynFieldBase,
} from './field.types';

export type {
  DynInputProps,
  DynInputRef,
  DynInputSize,
  DynInputType,
} from '../components/DynInput/DynInput.types';
export {
  DYN_INPUT_DEFAULT_PROPS,
} from '../components/DynInput/DynInput.types';

export type {
  DynTextAreaProps,
  DynTextAreaRef,
  DynTextAreaResize,
} from '../components/DynTextArea/DynTextArea.types';
export {
  DYN_TEXT_AREA_DEFAULT_PROPS,
} from '../components/DynTextArea/DynTextArea.types';

export type {
  DynSelectProps,
  DynSelectRef,
  DynSelectOption,
  DynSelectSize,
} from '../components/DynSelect/DynSelect.types';
export {
  DYN_SELECT_DEFAULT_PROPS,
} from '../components/DynSelect/DynSelect.types';

export type {
  DynDatePickerProps,
  DynDatePickerRef,
  DynDatePickerSize,
} from '../components/DynDatePicker/DynDatePicker.types';
export {
  DYN_DATE_PICKER_DEFAULT_PROPS,
} from '../components/DynDatePicker/DynDatePicker.types';

export type {
  DynCheckboxProps,
  DynCheckboxRef,
  DynCheckboxSize,
} from '../components/DynCheckbox/DynCheckbox.types';
export {
  DYN_CHECKBOX_DEFAULT_PROPS,
} from '../components/DynCheckbox/DynCheckbox.types';

// Layout Components types
export type {
  DynContainerProps,
  DynContainerOwnProps,
  DynContainerBackground,
  DynPageProps,
  DynPageBreadcrumb,
  DynPageAction,
  LayoutSize,
  LayoutSpacing,
  LayoutDirection,
  LayoutAlignment,
  LayoutJustify
} from './layout.types';

export type {
  DynFlexProps,
  DynFlexDirection,
  DynFlexAlign,
  DynFlexJustify,
  DynFlexWrap,
  DynFlexGap,
} from '../components/DynFlex/DynFlex.types';

export type {
  DynStackProps,
  DynStackDirection,
} from '../components/DynStack/DynStack.types';

export type {
  DynDropdownProps,
  DynDropdownRef,
  DynDropdownItem,
  DynDropdownPlacement,
} from '../components/DynDropdown/DynDropdown.types';

export type {
  DynModalProps,
  DynModalSize,
} from '../components/DynModal/DynModal.types';
export {
  DYN_MODAL_DEFAULT_PROPS,
} from '../components/DynModal/DynModal.types';

export type {
  DynGridProps,
  DynGridColumn,
  DynGridPagination,
  DynGridSelectable,
  DynGridSortDirection,
} from '../components/DynGrid/DynGrid.types';
export { DYN_GRID_DEFAULT_PROPS } from '../components/DynGrid/DynGrid.types';
