import type { BaseComponentProps, ColorVariant } from '../../types';
import type { DynFieldRef, ValidationRule } from '../../types/field.types';

export type DynCheckboxSize = 'sm' | 'md' | 'lg';

export interface DynCheckboxProps extends BaseComponentProps {
  /** Field name */
  name?: string;
  /** Label displayed next to the checkbox */
  label?: string;
  /** Helper text displayed below the field */
  helpText?: string;
  /** 
   * @deprecated Use helpText instead
   */
  help?: string;
  /** Disables user interaction */
  disabled?: boolean;
  /** Prevents value changes while keeping the field focusable */
  readonly?: boolean;
  /** Marks the field as required */
  required?: boolean;
  /** Shows the optional indicator */
  optional?: boolean;
  /** Controls visibility of the field */
  visible?: boolean;
  /** Controlled checked state */
  checked?: boolean;
  /** Shows the indeterminate state */
  indeterminate?: boolean;
  /** Custom validation error message */
  errorMessage?: string;
  /** Validation rules */
  validation?: ValidationRule[];
  /** Size variant */
  size?: DynCheckboxSize;
  /** 
   * Color theme of the checkbox when active
   * @default 'primary'
   */
  color?: ColorVariant;
  /** Change handler */
  onChange?: (checked: boolean) => void;
  /** Blur handler */
  onBlur?: () => void;
  /** Focus handler */
  onFocus?: () => void;
}

export type DynCheckboxRef = DynFieldRef;

export interface DynCheckboxDefaultProps
  extends Required<
    Pick<
      DynCheckboxProps,
      | 'disabled'
      | 'readonly'
      | 'required'
      | 'optional'
      | 'visible'
      | 'checked'
      | 'indeterminate'
      | 'size'
      | 'color'
    >
  > {
  'data-testid': string;
}

export const DYN_CHECKBOX_DEFAULT_PROPS: DynCheckboxDefaultProps = {
  disabled: false,
  readonly: false,
  required: false,
  optional: false,
  visible: true,
  checked: false,
  indeterminate: false,
  size: 'md',
  color: 'primary',
  'data-testid': 'dyn-checkbox',
};
