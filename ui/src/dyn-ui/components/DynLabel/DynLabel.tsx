import React, { forwardRef } from 'react';
import { cn } from '../../utils/classNames';
import type { DynLabelProps } from './DynLabel.types';
import { DYN_LABEL_DEFAULT_PROPS } from './DynLabel.types';
import styles from './DynLabel.module.css';

/**
 * DynLabel Component
 * Standardized label component for forms with requirement indicators and help text.
 */
export const DynLabel = forwardRef<HTMLLabelElement, DynLabelProps>(({
  children,
  htmlFor,
  disabled = DYN_LABEL_DEFAULT_PROPS.disabled,
  required = DYN_LABEL_DEFAULT_PROPS.required,
  optional = DYN_LABEL_DEFAULT_PROPS.optional,
  helpText,
  className,
  style,
  ...rest
}, ref) => {
  const containerClasses = cn(
    styles.container
  );

  const labelClasses = cn(
    styles.label,
    disabled && styles.disabled,
    (required || optional) && styles.withRequirement,
    className
  );


  const renderRequirementIndicator = () => {
    if (required) {
      return (
        <span className={cn(styles.requirement, styles.required)}>
          <span className={styles.asterisk} aria-hidden="true">*</span>
        </span>
      );
    }

    if (optional) {
      return (
        <span
          className={cn(styles.requirement, styles.optional)}
          data-testid="optional-indicator"
        >
          <span className={styles.optionalText}>(optional)</span>
        </span>
      );
    }

    return null;
  };

  const renderHelpText = () => {
    if (!helpText) return null;

    return (
      <span className={styles.helpText} id={htmlFor ? `${htmlFor}-help` : undefined}>
        {helpText}
      </span>
    );
  };

  const labelContent = (
    <span className={styles.text}>
      {children}
      {renderRequirementIndicator()}
    </span>
  );

  const elementProps = {
    className: labelClasses,
    ...(htmlFor && { htmlFor }),
    ...(helpText && htmlFor && { 'aria-describedby': `${htmlFor}-help` }),
    ...rest,
    ref
  };

  return (
    <div className={containerClasses} style={style} role="group">
      {htmlFor ? (
        <label {...elementProps}>
          {labelContent}
        </label>
      ) : (
        <span {...(elementProps as any)}>
          {labelContent}
        </span>
      )}
      {renderHelpText()}
    </div>
  );
});

DynLabel.displayName = 'DynLabel';

export default DynLabel;