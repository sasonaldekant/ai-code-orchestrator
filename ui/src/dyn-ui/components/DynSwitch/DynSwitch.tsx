import React, { forwardRef, useId } from 'react';
import { cn } from '../../utils/classNames';
import { DynSwitchProps } from './DynSwitch.types';
import { useDynFieldValidation } from '../../hooks/useDynFieldValidation';
import { DynFieldContainer } from '../DynFieldContainer';
import styles from './DynSwitch.module.css';

export const DynSwitch = forwardRef<HTMLInputElement, DynSwitchProps>(
    (
        {
            size = 'md',
            color = 'primary',
            label,
            description,
            helpText,
            error,
            errorMessage,
            className,
            style,
            disabled,
            onChange,
            onBlur,
            required,
            validation,
            id,
            checked: controlledChecked,
            defaultChecked,
            ...props
        },
        ref
    ) => {
        const uniqueId = useId();
        const switchId = id || uniqueId;
        const labelId = `${switchId}-label`;

        const [internalChecked, setInternalChecked] = React.useState<boolean>(!!(controlledChecked ?? defaultChecked));

        React.useEffect(() => {
            if (controlledChecked !== undefined) {
                setInternalChecked(controlledChecked);
            }
        }, [controlledChecked]);

        const resolvedHelpText = helpText ?? (typeof description === 'string' ? description : undefined);
        const resolvedErrorText = errorMessage;

        const { error: validationError, validate, clearError } = useDynFieldValidation({
            value: internalChecked ? 'checked' : '',
            required,
            validation,
            customError: resolvedErrorText,
        });

        const displayError = resolvedErrorText || validationError;
        const isError = error || !!displayError;

        const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
            if (disabled) return;
            const newChecked = e.target.checked;

            if (controlledChecked === undefined) {
                setInternalChecked(newChecked);
            }

            onChange?.(newChecked);
            clearError();
        };

        const handleBlur = () => {
            validate();
            onBlur?.();
        };

        return (
            <DynFieldContainer
                helpText={resolvedHelpText}
                errorText={displayError}
                className={className}
                required={required}
            >
                <div
                    className={cn(
                        styles.root,
                        styles.container,
                        styles[`size${size.charAt(0).toUpperCase() + size.slice(1)}`],
                        styles[`color${color.charAt(0).toUpperCase()}${color.slice(1)}`],
                        {
                            [styles.error]: isError,
                        }
                    )}
                    style={style}
                >
                    <label
                        htmlFor={switchId}
                        className={cn(styles.wrapper, {
                            [styles.wrapperDisabled]: disabled,
                        })}
                    >
                        <input
                            {...props}
                            id={switchId}
                            ref={ref}
                            type="checkbox"
                            className={styles.input}
                            disabled={disabled}
                            checked={internalChecked}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            role="switch"
                            aria-checked={internalChecked}
                            aria-labelledby={label ? labelId : undefined}
                            aria-required={required}
                            aria-invalid={!!isError}
                        />
                        <span className={styles.track} aria-hidden="true">
                            <span className={styles.thumb} />
                        </span>
                        {label && (
                            <span id={labelId} className={styles.label}>
                                {label}
                            </span>
                        )}
                    </label>
                </div>
            </DynFieldContainer>
        );
    }
);

DynSwitch.displayName = 'DynSwitch';

export default DynSwitch;
