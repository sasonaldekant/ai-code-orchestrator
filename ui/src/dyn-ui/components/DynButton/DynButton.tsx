import React, { forwardRef, useMemo, useId } from 'react';
import type {
  FocusEventHandler,
  KeyboardEventHandler,
  MouseEventHandler,
} from 'react';
import { cn } from '../../utils/classNames';
import { DynIcon } from '../DynIcon';
import { DynLoading } from '../DynLoading';
import type {
  DynButtonDefaultProps,
  DynButtonProps,
  DynButtonRef,
  DynButtonSize,
} from './DynButton.types';
import { DYN_BUTTON_DEFAULT_PROPS } from './DynButton.types';
import styles from './DynButton.module.css';


/**
 * Normalize ARIA label values
 */
const normalizeAriaLabel = (value: string | undefined): string | undefined =>
  value?.trim() ? value.trim() : undefined;

/**
 * Generate appropriate ARIA label for icon-only buttons
 */
const generateIconAriaLabel = (icon: string | React.ReactNode): string | undefined => {
  if (typeof icon !== 'string') return undefined;
  return icon
    .replace(/[-_]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
};

type DynButtonComponentProps = DynButtonProps & DynButtonDefaultProps;

/**
 * DynButton
 *
 * Enterprise-grade button component following the DynAvatar gold standard for architecture,
 * accessibility, and composability.
 */
export const DynButton = forwardRef<DynButtonRef, DynButtonProps>(
  (
    {
      label,
      icon,
      type = DYN_BUTTON_DEFAULT_PROPS.type,
      kind = DYN_BUTTON_DEFAULT_PROPS.kind,
      size = DYN_BUTTON_DEFAULT_PROPS.size,
      color = DYN_BUTTON_DEFAULT_PROPS.color,
      loading = DYN_BUTTON_DEFAULT_PROPS.loading,
      loadingText = DYN_BUTTON_DEFAULT_PROPS.loadingText,
      danger = DYN_BUTTON_DEFAULT_PROPS.danger,
      disabled = DYN_BUTTON_DEFAULT_PROPS.disabled,
      fullWidth = DYN_BUTTON_DEFAULT_PROPS.fullWidth,
      hideOnMobile = DYN_BUTTON_DEFAULT_PROPS.hideOnMobile,
      iconOnlyOnMobile = DYN_BUTTON_DEFAULT_PROPS.iconOnlyOnMobile,
      onClick,
      onBlur,
      onKeyDown: userOnKeyDown,
      children,
      className,
      id,
      'aria-label': ariaLabel,
      'aria-describedby': ariaDescribedBy,
      'aria-labelledby': ariaLabelledBy,
      'aria-expanded': ariaExpanded,
      'aria-controls': ariaControls,
      'aria-pressed': ariaPressed,
      'data-testid': dataTestId,
      role,
      ...rest
    },
    ref
  ) => {
    // Generate stable ID using React's useId hook
    const generatedId = useId();
    const internalId = id || generatedId;

    // Memoized computations
    const trimmedLabel = useMemo(() => (typeof label === 'string' ? label.trim() : ''), [label]);
    const hasLabel = trimmedLabel.length > 0;
    const childrenCount = React.Children.count(children);
    const hasChildrenContent = childrenCount > 0;
    const isIconOnly = Boolean(icon) && !hasLabel && !hasChildrenContent;
    const isDisabled = disabled || loading;

    // Generate appropriate ARIA label for accessibility
    const iconAriaLabel = useMemo(() => generateIconAriaLabel(icon), [icon]);
    const computedAriaLabel = useMemo(
      () => normalizeAriaLabel(
        ariaLabel ?? (isIconOnly ? (trimmedLabel || iconAriaLabel || 'Button') : undefined)
      ),
      [ariaLabel, isIconOnly, trimmedLabel, iconAriaLabel]
    );

    // Normalize loading text
    const normalizedLoadingText = useMemo(() => {
      if (typeof loadingText !== 'string') return DYN_BUTTON_DEFAULT_PROPS.loadingText;
      const trimmed = loadingText.trim();
      return trimmed || DYN_BUTTON_DEFAULT_PROPS.loadingText;
    }, [loadingText]);

    // Icon size - direct mapping (size is already 'small' | 'medium' | 'large')
    const iconSizeToken = size;

    // Render icon element
    const iconElement = useMemo(() => {
      if (!icon) return null;
      if (typeof icon === 'string') {
        return <DynIcon icon={icon} aria-hidden="true" className={styles.icon} size={iconSizeToken} />;
      }
      return <span className={styles.icon} aria-hidden="true">{icon}</span>;
    }, [icon, iconSizeToken]);

    // Render children content
    const childrenContent = useMemo(() => {
      if (!hasChildrenContent) return null;
      if (typeof children === 'string') {
        const trimmedChildren = children.trim();
        if (!trimmedChildren) return null;
        return <span className={styles.label}>{trimmedChildren}</span>;
      }
      return children;
    }, [children, hasChildrenContent]);

    // Render label element (primary text)
    const labelElement = hasLabel ? (
      <span className={styles.label}>{trimmedLabel}</span>
    ) : null;

    // Generate CSS classes safely (DynAvatar pattern)
    // Map props to Full Word CSS classes as per Technical Documentation
    const SIZE_MAP: Record<DynButtonSize, string> = {
      xs: 'sizeXs',
      sm: 'sizeSm',
      md: 'sizeMd',
      lg: 'sizeLg'
    };


    const buttonClassName = cn(
      styles.root,
      styles[`kind${kind.charAt(0).toUpperCase() + kind.slice(1)}` as keyof typeof styles],
      styles[`color${color.charAt(0).toUpperCase() + color.slice(1)}` as keyof typeof styles],
      styles[SIZE_MAP[size] as keyof typeof styles],
      (danger || color === 'danger') && styles.danger,
      loading && styles.loading,
      isIconOnly && styles.iconOnly,
      fullWidth && styles.fullWidth,
      hideOnMobile && styles.hideOnMobile,
      iconOnlyOnMobile && styles.iconOnlyOnMobile,
      className
    );

    // Event handlers
    const handleClick: MouseEventHandler<HTMLButtonElement> = (event) => {
      if (isDisabled) {
        event.preventDefault();
        event.stopPropagation();
        return;
      }
      onClick?.(event);
    };

    const handleBlur: FocusEventHandler<HTMLButtonElement> = (event) => {
      onBlur?.(event);
    };

    const handleKeyDown: KeyboardEventHandler<HTMLButtonElement> = (event) => {
      if (event.key === ' ' || event.key === 'Spacebar') {
        event.preventDefault();
        if (!isDisabled) {
          event.currentTarget.click();
        }
      }
      userOnKeyDown?.(event);
    };

    return (
      <>
        <button
          ref={ref}
          id={internalId}
          type={type}
          className={buttonClassName}
          data-testid={dataTestId ?? 'dyn-button'}
          aria-label={computedAriaLabel}
          aria-describedby={ariaDescribedBy}
          aria-labelledby={ariaLabelledBy}
          aria-expanded={ariaExpanded}
          aria-controls={ariaControls}
          aria-pressed={typeof ariaPressed === 'boolean' ? ariaPressed : undefined}
          aria-busy={loading || undefined}
          aria-disabled={isDisabled || undefined}
          disabled={isDisabled}
          role={role}
          onClick={handleClick}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          {...rest}
        >
          <span className={styles.content}>
            {iconElement}
            {labelElement}
            {childrenContent}
          </span>
          {loading && (
            <DynLoading
              variant="spinner"
              aria-label={normalizedLoadingText}
              className={styles.loadingIndicator}
            />
          )}
        </button>
      </>
    );
  }
);

DynButton.displayName = 'DynButton';

export default DynButton;
