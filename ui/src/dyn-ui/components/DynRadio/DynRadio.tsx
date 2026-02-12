import React, { forwardRef, useId, createContext, useContext, useState } from 'react';
import { cn } from '../../utils/classNames';
import { DynRadioProps, DynRadioGroupProps } from './DynRadio.types';
import { useDynFieldValidation } from '../../hooks/useDynFieldValidation';
import { DynFieldContainer } from '../DynFieldContainer';
import styles from './DynRadio.module.css';
import type { ColorVariant } from '../../types';

// Context for Radio Group communication
interface RadioGroupContextType {
    name: string;
    value?: string;
    onChange: (value: string) => void;
    error?: boolean;
    color?: ColorVariant;
}

const RadioGroupContext = createContext<RadioGroupContextType | null>(null);

/**
 * DynRadioGroup Component
 * A container for a group of radio buttons with validation and label management.
 */
export const DynRadioGroup: React.FC<DynRadioGroupProps> = ({
    name: nameProp,
    value: controlledValue,
    defaultValue,
    onChange,
    label,
    description,
    helpText,
    error,
    errorMessage,
    required,
    validation,
    onValidate,
    direction = 'vertical',
    color = 'primary',
    children,
    options,
    className,
    ...props
}) => {
    const [internalValue, setInternalValue] = useState<string | undefined>(defaultValue);
    const value = controlledValue !== undefined ? controlledValue : internalValue;
    const uniqueId = useId();
    const name = nameProp || uniqueId;

    const resolvedHelpText = helpText ?? (typeof description === 'string' ? description : undefined);
    const resolvedErrorText = errorMessage;

    const { error: validationError, clearError } = useDynFieldValidation({
        value,
        required,
        validation,
        customError: resolvedErrorText,
    });

    const displayError = resolvedErrorText || validationError;
    const isError = error || !!displayError;

    const handleChange = (newValue: string) => {
        if (controlledValue === undefined) {
            setInternalValue(newValue);
        }
        onChange?.(newValue);
        clearError();
    };

    return (
        <DynFieldContainer
            label={typeof label === 'string' ? label : undefined}
            helpText={resolvedHelpText}
            errorText={displayError}
            required={required}
            className={className}
        >
            <RadioGroupContext.Provider value={{ name, value, onChange: handleChange, error: isError, color }}>
                <div
                    className={cn(styles.groupContainer)}
                    role="radiogroup"
                    aria-labelledby={label ? `${name}-label` : undefined}
                    aria-required={required}
                    aria-invalid={isError}
                    {...props}
                >
                    {label && typeof label !== 'string' && (
                        <span id={`${name}-label`} className={styles.groupLabel}>
                            {label}
                        </span>
                    )}

                    <div
                        className={cn(styles.group, {
                            [styles.horizontal]: direction === 'horizontal',
                        })}
                    >
                        {children}
                        {options &&
                            options.map((option) => (
                                <DynRadio
                                    key={String(option.value)}
                                    value={String(option.value)}
                                    label={option.label}
                                    disabled={option.disabled}
                                    color={color}
                                />
                            ))}
                    </div>
                </div>
            </RadioGroupContext.Provider>
        </DynFieldContainer>
    );
};

/**
 * DynRadio Component
 * A customizable radio button component that can be used standalone or within a DynRadioGroup.
 */
export const DynRadio = forwardRef<HTMLInputElement, DynRadioProps>(
    ({ label, description, error: errorProp, color: colorProp, className, value, checked: checkedProp, onChange, disabled, ...props }, ref) => {
        const id = useId();
        const groupContext = useContext(RadioGroupContext);

        // Determine state based on Group Context or local props
        const isChecked = groupContext ? groupContext.value === value : checkedProp;

        const name = groupContext ? groupContext.name : props.name;
        const isError = groupContext ? groupContext.error : errorProp;
        const color = groupContext?.color ?? colorProp ?? 'primary';

        const COLOR_MAP: Record<string, string | undefined> = {
            primary: styles.colorPrimary,
            secondary: styles.colorSecondary,
            success: styles.colorSuccess,
            danger: styles.colorDanger,
            warning: styles.colorWarning,
            info: styles.colorInfo,
        };

        const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
            if (disabled) return;

            const newChecked = e.target.checked;

            if (groupContext) {
                if (newChecked) {
                    groupContext.onChange(value);
                }
            } else {
                onChange?.(newChecked, value);
            }
        };

        return (
            <div className={cn(styles.container, COLOR_MAP[color], className)}>
                <label
                    htmlFor={id}
                    className={cn(styles.wrapper, {
                        [styles.wrapperDisabled]: disabled,
                        [styles.error]: isError,
                    })}
                >
                    <input
                        {...props}
                        ref={ref}
                        id={id}
                        type="radio"
                        name={name}
                        value={value}
                        checked={isChecked}
                        onChange={handleChange}
                        disabled={disabled}
                        className={styles.input}
                    />
                    <div className={styles.check}>
                        <div className={styles.dot} />
                    </div>
                    {label && <span className={styles.label}>{label}</span>}
                </label>
                {description && <div className={styles.description}>{description}</div>}
            </div>
        );
    }
);

DynRadio.displayName = 'DynRadio';
