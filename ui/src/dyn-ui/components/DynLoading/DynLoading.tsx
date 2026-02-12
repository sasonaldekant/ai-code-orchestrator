/**
 * DynLoading Component
 *
 * A versatile loading component supporting spinners, skeletons, and overlays.
 *
 * Token Compliant: ✅ Full --dyn-loading-* pattern with 3-level fallback
 *
 * @component
 * @module DynLoading
 * @version 1.0.0
 */

import React, { forwardRef } from 'react';
import { cn } from '../../utils/classNames';
import {
    DynLoadingProps,
    DynLoadingRef,
    DynLoadingVariant,
    DynLoadingSize,
    DynLoadingColor,
    DYN_LOADING_VARIANTS,
    DYN_LOADING_SIZES,
    DYN_LOADING_COLORS,
    DYN_LOADING_DEFAULT_PROPS,
} from './DynLoading.types';
import styles from './DynLoading.module.css';

/**
 * DynLoading Component
 *
 * @example
 * // Basic spinner
 * <DynLoading />
 *
 * @example
 * // Skeleton loading
 * <DynLoading variant="skeleton" width="100%" height="20px" />
 *
 * @example
 * // Fullscreen overlay with blur
 * <DynLoading variant="overlay" fixed blur label="Loading application..." />
 */
export const DynLoading = forwardRef<DynLoadingRef, DynLoadingProps>(
    (props, ref) => {
        const {
            // Configuration props
            variant = DYN_LOADING_DEFAULT_PROPS.variant,
            size = DYN_LOADING_DEFAULT_PROPS.size,
            color = DYN_LOADING_DEFAULT_PROPS.color,

            // Content props
            label,
            description,

            // Overlay specific props
            blur = DYN_LOADING_DEFAULT_PROPS.blur,
            fixed = DYN_LOADING_DEFAULT_PROPS.fixed,

            // Skeleton specific props
            width,
            height,
            circle = DYN_LOADING_DEFAULT_PROPS.circle,

            // Standard props
            className,
            style,
            'aria-label': ariaLabel,
            'data-testid': dataTestId,
            ...rest
        } = props;

        // ====================================
        // PHASE 1: Validation & Normalization
        // ====================================

        const validVariant: DynLoadingVariant = DYN_LOADING_VARIANTS.includes(variant as any)
            ? variant!
            : 'spinner';

        const validSize: DynLoadingSize = DYN_LOADING_SIZES.includes(size as any)
            ? size!
            : 'md';

        const validColor: DynLoadingColor = DYN_LOADING_COLORS.includes(color as any)
            ? color!
            : 'primary';

        // ====================================
        // PHASE 2: Class Computation
        // ====================================

        const variantClass = `loading${validVariant.charAt(0).toUpperCase()}${validVariant.slice(1)}`;
        const sizeClass = `size${validSize.charAt(0).toUpperCase()}${validSize.slice(1)}`;
        const colorClass = `loading${validColor.charAt(0).toUpperCase()}${validColor.slice(1)}`;

        const rootClasses = cn(
            styles.loading,
            styles[variantClass],
            styles[sizeClass],
            styles[colorClass],
            {
                [styles.loadingBlur]: validVariant === 'overlay' && blur,
                [styles.loadingFixed]: validVariant === 'overlay' && fixed,
                [styles.loadingCircle]: validVariant === 'skeleton' && circle,
                [styles.loadingWithLabel]: !!label || !!description,
            },
            className
        );

        // ====================================
        // PHASE 3: Style Computation
        // ====================================

        const customStyle: React.CSSProperties = {
            ...style,
            ...(width ? { width } : {}),
            ...(height ? { height } : {}),
        };

        // ====================================
        // PHASE 4: Render Content
        // ====================================

        const renderIndicator = () => {
            switch (validVariant) {
                case 'skeleton':
                    return null; // Skeleton is the container itself

                case 'dots':
                    return (
                        <div className={styles.loadingDotsIndicator} aria-hidden="true">
                            <span />
                            <span />
                            <span />
                        </div>
                    );

                case 'pulse':
                    return <div className={styles.loadingPulseIndicator} aria-hidden="true" />;

                case 'spinner':
                case 'overlay':
                default:
                    return (
                        <svg
                            className={styles.loadingSpinnerIndicator}
                            viewBox="0 0 50 50"
                            aria-hidden="true"
                        >
                            <circle
                                cx="25"
                                cy="25"
                                r="20"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="5"
                            />
                        </svg>
                    );
            }
        };

        // ====================================
        // PHASE 5: Accessibility
        // ====================================

        // For skeleton, use 'none' role or aria-hidden unless meaningful
        // For others, use 'status' or 'alert' depending on context, using 'status' as safe default
        const role = validVariant === 'skeleton' ? undefined : 'status';
        const computedAriaLabel = ariaLabel || label || 'Loading';

        // ====================================
        // PHASE 6: Render
        // ====================================

        return (
            <div
                ref={ref}
                className={rootClasses}
                style={customStyle}
                role={role}
                aria-label={computedAriaLabel}
                aria-busy="true"
                data-testid={dataTestId || 'dyn-loading'}
                data-variant={validVariant}
                data-size={validSize}
                data-color={validColor}
                {...rest}
            >
                {renderIndicator()}

                {(label || description) && validVariant !== 'skeleton' && (
                    <div className={styles.loadingContent}>
                        {label && <div className={styles.loadingLabel}>{label}</div>}
                        {description && <div className={styles.loadingDescription}>{description}</div>}
                    </div>
                )}

                {/* Screen reader only text for context - only show if no visible label to avoid duplication */}
                {!label && (
                    <span className={styles.srOnly}>
                        {computedAriaLabel}
                    </span>
                )}
            </div>
        );
    }
);

DynLoading.displayName = 'DynLoading';

export default DynLoading;
