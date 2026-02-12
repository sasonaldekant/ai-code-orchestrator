import type { LabelHTMLAttributes } from 'react';
import type { BaseComponentProps } from '../../types/theme';

export interface DynLabelProps extends BaseComponentProps, Omit<LabelHTMLAttributes<HTMLLabelElement>, keyof BaseComponentProps | 'htmlFor'> {
  /** Associated form element ID */
  htmlFor?: string;

  /** Disabled state */
  disabled?: boolean;

  /** Required field indicator */
  required?: boolean;

  /** Optional field indicator */
  optional?: boolean;

  /** Help text to display */
  helpText?: string;
}

export const DYN_LABEL_DEFAULT_PROPS = {
  disabled: false,
  required: false,
  optional: false,
} as const;
