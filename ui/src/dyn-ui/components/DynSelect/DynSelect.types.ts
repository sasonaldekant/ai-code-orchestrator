import type { ReactNode } from 'react';
import type { BaseComponentProps, AccessibilityProps } from '../../types';
import type { DynValidationRule } from '../../hooks/useDynFieldValidation';

export interface DynSelectOption<T = string | number> {
  value: T;
  label: string;
  disabled?: boolean;
  icon?: ReactNode;
  group?: string;
  description?: string;
}

export type DynSelectSize = 'sm' | 'md' | 'lg';

export interface DynSelectProps<T = string | number> extends BaseComponentProps, AccessibilityProps {
  /** Input name */
  name?: string;

  /** Current value */
  value?: T | T[];

  /** Default value for uncontrolled usage */
  defaultValue?: T | T[];

  /** Callback on value change */
  onChange?: (value: T | T[]) => void;

  /** Options to display */
  options?: DynSelectOption<T>[];

  /** Groups for categorized options */
  groups?: string[];

  /** Placeholder text */
  placeholder?: string;

  /** Label for the select field */
  label?: string;

  /** Alias for helpText for backward compatibility */
  help?: string;

  /** Alias for errorText for backward compatibility */
  errorMessage?: string;

  /** Optional/Helper text */
  helpText?: string;

  /** Validation error message */
  errorText?: string;

  /** Whether the field is required */
  required?: boolean;

  /** Whether the field is disabled */
  disabled?: boolean;

  /** Whether the field is readonly */
  readOnly?: boolean;

  /** Size variant */
  size?: DynSelectSize;

  /** Support for multiple selection */
  multiple?: boolean;

  /** Searchable mode */
  searchable?: boolean;

  /** Clear button visibility */
  clearable?: boolean;

  /** Custom filter function for search */
  filterOption?: (option: DynSelectOption<T>, searchText: string) => boolean;

  /** Add search placeholder */
  searchPlaceholder?: string;

  /** Max height of the dropdown menu */
  maxMenuHeight?: number | string;

  /** Loading state */
  loading?: boolean;

  /** Empty results message */
  noOptionsMessage?: ReactNode;

  /** Visibility */
  visible?: boolean;

  /** Whether the select should take up the full width of its container */
  fullWidth?: boolean;

  /** Validation rules (consistent with DynInput) */
  validation?: DynValidationRule | DynValidationRule[];

  /** Whether to validate on blur */
  validateOnBlur?: boolean;

  /** Whether to validate on change */
  validateOnChange?: boolean;

  /** Callback when validation status changes */
  onValidate?: (isValid: boolean, errorMessage?: string) => void;
}

export interface DynSelectRef<T = string | number> {
  /** Focus the input */
  focus: () => void;
  /** Blur the input */
  blur: () => void;
  /** Clear the selection */
  clear: () => void;
  /** Open the dropdown */
  open: () => void;
  /** Close the dropdown */
  close: () => void;
  /** Get current value */
  getValue: () => T | T[] | undefined;
  /** Validate the selection and return result */
  validate: () => Promise<boolean>;
  /** Clear any validation errors */
  clearError: () => void;
}

export const DYN_SELECT_DEFAULT_PROPS = {
  size: 'md',
  multiple: false,
  searchable: false,
  clearable: false,
  visible: true,
  noOptionsMessage: 'No options found',
} as const;
