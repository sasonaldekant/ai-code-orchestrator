import { InputHTMLAttributes, ReactNode } from 'react';
import type { BaseComponentProps, AccessibilityProps } from '../../types';
import type { DynValidationRule } from '../../hooks/useDynFieldValidation';

export type DynSwitchSize = 'sm' | 'md' | 'lg';
export type DynSwitchColor = 'primary' | 'success' | 'danger' | 'warning' | 'info';

export interface DynSwitchProps
    extends BaseComponentProps,
    AccessibilityProps,
    Omit<InputHTMLAttributes<HTMLInputElement>, 'size' | 'onChange' | keyof BaseComponentProps> {
    /**
     * The size of the switch.
     * @default 'md'
     */
    size?: DynSwitchSize;

    /**
     * The color theme of the switch when active.
     * @default 'primary'
     */
    color?: DynSwitchColor;

    /**
     * Label to display next to the switch.
     */
    label?: ReactNode;

    /**
     * Callback when the checked state changes.
     */
    onChange?: (checked: boolean) => void;

    /**
     * Helper text or error message below the switch.
     * @deprecated Use helpText instead
     */
    description?: ReactNode;

    /**
     * Help text to display below the field
     */
    helpText?: string;

    /**
     * Whether the switch is in an error state.
     */
    error?: boolean;

    /**
     * Error message text to display.
     */
    errorMessage?: string;

    /**
     * Whether the field is required
     */
    required?: boolean;

    /**
     * Validation rules
     */
    validation?: DynValidationRule | DynValidationRule[];

    /**
     * Blur handler
     */
    onBlur?: () => void;
}
