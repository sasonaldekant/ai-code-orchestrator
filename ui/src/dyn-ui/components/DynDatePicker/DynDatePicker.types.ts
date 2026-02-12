import type { InputHTMLAttributes, FocusEventHandler } from 'react';
import type { BaseComponentProps, AccessibilityProps } from '../../types';

export type DynDatePickerSize = 'sm' | 'md' | 'lg';

// Placeholder (should import from validation hook if exported)
export interface ValidationRule {
    type: string;
    message: string;
    [key: string]: any;
}

export interface DynDatePickerProps extends BaseComponentProps, AccessibilityProps, Omit<InputHTMLAttributes<HTMLInputElement>, 'size' | 'value' | 'onChange' | 'onBlur' | 'onFocus' | keyof BaseComponentProps | keyof AccessibilityProps> {
    /** Name of the input field, used for form identification. */
    name?: string;

    /** Current date value in ISO format (YYYY-MM-DD). Use this for controlled components. */
    value?: string;

    /** Initial date value for uncontrolled components. */
    defaultValue?: string;

    /** Callback function triggered when the date changes. Returns the date in ISO format. */
    onChange?: (value: string) => void;

    /** Callback triggered when the input loses focus. */
    onBlur?: FocusEventHandler<HTMLInputElement>;

    /** Callback triggered when the input receives focus. */
    onFocus?: FocusEventHandler<HTMLInputElement>;

    /** If true, displays an "(Optional)" tag next to the label. */
    optional?: boolean;

    /** Array of validation rules to apply to the date input. */
    validation?: ValidationRule[];

    /** The visible label text for the date picker. */
    label?: string;

    /** Supplemental help text (semantic alias for helpText). */
    help?: string;

    /** Explicit error message to display (semantic alias for errorText). */
    errorMessage?: string;

    /**
     * The visual format for the date in the input field.
     * Supported tokens: dd, MM, yyyy (e.g., 'dd.MM.yyyy' or 'MM/dd/yyyy').
     * @default 'dd/MM/yyyy'
     */
    format?: string;

    /** Explanatory text displayed below the input field. */
    helpText?: string;

    /** Error text to display below the input when validation fails. */
    errorText?: string;

    /** If true, the field is marked as required with an asterisk (*). */
    required?: boolean;

    /** If true, the input and calendar interactions are disabled. */
    disabled?: boolean;

    /** If true, the date cannot be changed, although it remains focusable. */
    readonly?: boolean;

    /** 
     * The visual density of the input.
     * @default 'md'
     */
    size?: DynDatePickerSize;

    /** Earliest selectable date in ISO format (YYYY-MM-DD). */
    min?: string;

    /** Latest selectable date in ISO format (YYYY-MM-DD). */
    max?: string;

    /** Placeholder text shown when the input is empty. */
    placeholder?: string;

    /** Whether the component is rendered or hidden. */
    visible?: boolean;

    /** The day the week begins on (0 for Sunday, 1 for Monday). @default 1 */
    weekStartsOn?: 0 | 1;

    /** Label for the "Today" button in the calendar footer. @default 'Today' */
    todayText?: string;

    /** Label for the "Clear" button in the calendar footer. @default 'Clear' */
    clearText?: string;

    /** Custom array of 12 month names for localization. */
    monthNames?: string[];

    /** Custom array of 7 day names for localization, starting from Sunday. */
    weekdayNames?: string[];
}

export interface DynDatePickerRef {
    /** Focus input */
    focus: () => void;
    /** Blur input */
    blur: () => void;
    /** Clear input */
    clear: () => void;
    /** Validate input */
    validate: () => Promise<boolean>;
    /** Get value */
    getValue: () => string | undefined;
}

export const DYN_DATE_PICKER_DEFAULT_PROPS = {
    size: 'md',
    visible: true,
    weekStartsOn: 1,
    todayText: 'Today',
    clearText: 'Clear',
} as const;