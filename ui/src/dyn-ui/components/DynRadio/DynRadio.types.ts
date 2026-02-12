import { InputHTMLAttributes, ReactNode } from 'react';
import type { BaseComponentProps, AccessibilityProps, ColorVariant } from '../../types';
import type { DynValidationRule } from '../../hooks/useDynFieldValidation';
import type { DynSelectOption } from '../DynSelect';

export interface DynRadioProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'onChange'>, BaseComponentProps {
    /**
     * Label to display next to the radio button.
     */
    label?: ReactNode;

    /**
     * Helper text or error message below the radio.
     * @deprecated Use helpText for Group, individual radio usually doesn't need helpText
     */
    description?: ReactNode;

    /**
     * Whether the radio is in an error state.
     */
    error?: boolean;

    /**
     * Color theme of the radio button
     * @default 'primary'
     */
    color?: ColorVariant;

    /**
     * Callback when the checked state changes.
     */
    onChange?: (checked: boolean, value: string) => void;

    /**
     * Value of the radio button.
     */
    value: string;
}

export interface DynRadioGroupProps extends BaseComponentProps, AccessibilityProps {
    /**
     * The name attribute for all radio buttons in the group.
     * If not provided, a unique name will be generated.
     */
    name?: string;

    /**
     * The value of the currently selected radio button.
     */
    value?: string;

    /**
     * Default selected value (uncontrolled).
     */
    defaultValue?: string;

    /**
     * Callback when the selected value changes.
     */
    onChange?: (value: string) => void;

    /**
     * Label for the group (rendered as a legend or label).
     */
    label?: ReactNode;

    /**
     * Helper text or error message for the group.
     * @deprecated Use helpText instead
     */
    description?: ReactNode;

    /**
     * Help text to display below the group
     */
    helpText?: string;

    /**
     * Whether the group is in an error state.
     */
    error?: boolean;

    /**
     * Error message string.
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
     * Callback when validation status changes
     */
    onValidate?: (isValid: boolean, errorMessage?: string) => void;

    /**
     * Direction of the radio buttons.
     * @default 'vertical'
     */
    direction?: 'vertical' | 'horizontal';

    /**
     * Color theme for all radio buttons in the group
     * @default 'primary'
     */
    color?: ColorVariant;

    /**
     * Children nodes (DynRadio components).
     */
    children?: ReactNode;

    /**
     * Options array (alternative to children)
     */
    options?: DynSelectOption[];

    /**
     * Additional class name.
     */
    className?: string;
}
