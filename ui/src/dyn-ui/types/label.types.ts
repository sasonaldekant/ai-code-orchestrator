import type { BaseComponentProps } from './theme';

export interface DynLabelProps extends BaseComponentProps {
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

  /** Additional HTML attributes */
  [key: string]: any;
}
