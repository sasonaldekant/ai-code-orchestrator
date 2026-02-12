/**
 * DynProgress Component
 *
 * A flexible, accessible progress bar component for displaying
 * progress indicators, loading states, and completion percentages.
 *
 * Token Compliant: ✅ Full --dyn-progress-* pattern with 3-level fallback
 *
 * @component
 * @module DynProgress
 * @version 1.0.0
 */

import React, { forwardRef, useMemo } from 'react';
import { cn } from '../../utils/classNames';
import {
    DynProgressProps,
    DynProgressRef,
    DynProgressStatus,
    DynProgressSize,
    DYN_PROGRESS_STATUSES,
    DYN_PROGRESS_SIZES,
    DYN_PROGRESS_DEFAULT_PROPS,
} from './DynProgress.types';
import styles from './DynProgress.module.css';

/**
 * DynProgress Component
 *
 * Displays a progress bar with optional label and percentage.
 * Supports indeterminate mode for unknown progress duration.
 *
 * @example
 * // Basic usage
 * <DynProgress value={50} />
 *
 * @example
 * // With label and percentage
 * <DynProgress value={75} label="Uploading..." showPercentage />
 *
 * @example
 * // Indeterminate loading
 * <DynProgress indeterminate />
 *
 * @example
 * // Success status
 * <DynProgress value={100} status="success" />
 */
export const DynProgress = forwardRef<DynProgressRef, DynProgressProps>(
    (props, ref) => {
        const {
            // Value props
            value = DYN_PROGRESS_DEFAULT_PROPS.value,
            max = DYN_PROGRESS_DEFAULT_PROPS.max,
            min = DYN_PROGRESS_DEFAULT_PROPS.min,

            // Display props
            status = DYN_PROGRESS_DEFAULT_PROPS.status,
            size = DYN_PROGRESS_DEFAULT_PROPS.size,
            label,
            showPercentage = DYN_PROGRESS_DEFAULT_PROPS.showPercentage,
            formatValue,

            // Animation props
            indeterminate = DYN_PROGRESS_DEFAULT_PROPS.indeterminate,
            striped = DYN_PROGRESS_DEFAULT_PROPS.striped,
            animated = DYN_PROGRESS_DEFAULT_PROPS.animated,

            // Styling props
            height,
            className,
            style,

            // Accessibility props
            'aria-label': ariaLabel,
            'data-testid': dataTestId,

            ...rest
        } = props;

        // ====================================
        // PHASE 1: Input Validation
        // ====================================

        const validStatus: DynProgressStatus = DYN_PROGRESS_STATUSES.includes(status as any)
            ? status!
            : 'default';

        const validSize: DynProgressSize = DYN_PROGRESS_SIZES.includes(size as any)
            ? size!
            : 'md';

        // ====================================
        // PHASE 2: Value Computation
        // ====================================

        /**
         * Calculate percentage with bounds checking
         */
        const { percentage, clampedValue } = useMemo(() => {
            if (indeterminate) {
                return { percentage: 0, clampedValue: 0 };
            }

            const range = (max ?? 100) - (min ?? 0);
            if (range <= 0) {
                return { percentage: 0, clampedValue: min ?? 0 };
            }

            const clamped = Math.max(min ?? 0, Math.min(max ?? 100, value ?? 0));
            const pct = ((clamped - (min ?? 0)) / range) * 100;

            return {
                percentage: Math.round(pct * 100) / 100,
                clampedValue: clamped,
            };
        }, [value, min, max, indeterminate]);

        /**
         * Format display value
         */
        const displayValue = useMemo(() => {
            if (indeterminate) return null;
            if (formatValue) return formatValue(clampedValue, percentage);
            return `${Math.round(percentage)}%`;
        }, [indeterminate, formatValue, clampedValue, percentage]);

        // ====================================
        // PHASE 3: Class Computation
        // ====================================

        const statusClass = `progress${validStatus.charAt(0).toUpperCase()}${validStatus.slice(1)}`;
        const sizeClass = `progress${validSize.charAt(0).toUpperCase()}${validSize.slice(1)}`;

        const progressClasses = cn(
            styles.progress,
            styles[statusClass],
            styles[sizeClass],
            {
                [styles.progressIndeterminate]: indeterminate,
                [styles.progressStriped]: striped,
                [styles.progressAnimated]: animated || indeterminate,
                [styles.progressWithLabel]: !!label || showPercentage,
            },
            className
        );

        const barClasses = cn(
            styles.progressBar,
            {
                [styles.progressBarIndeterminate]: indeterminate,
                [styles.progressBarStriped]: striped,
                [styles.progressBarAnimated]: animated,
            }
        );

        // ====================================
        // PHASE 4: Style Computation
        // ====================================

        const progressStyle: React.CSSProperties = {
            ...style,
            ...(height ? { '--dyn-progress-height': `${height}px` } as React.CSSProperties : {}),
        };

        const barStyle: React.CSSProperties = indeterminate
            ? {}
            : { width: `${percentage}%` };

        // ====================================
        // PHASE 5: Accessibility
        // ====================================

        const computedAriaLabel = ariaLabel || label || `Progress: ${Math.round(percentage)}%`;

        // ====================================
        // PHASE 6: Render
        // ====================================

        return (
            <div
                ref={ref}
                className={progressClasses}
                style={progressStyle}
                role="progressbar"
                aria-valuenow={indeterminate ? undefined : clampedValue}
                aria-valuemin={min}
                aria-valuemax={max}
                aria-label={computedAriaLabel}
                aria-busy={indeterminate}
                data-testid={dataTestId || 'dyn-progress'}
                data-status={validStatus}
                data-size={validSize}
                data-indeterminate={indeterminate || undefined}
                {...rest}
            >
                {/* Header with label and percentage */}
                {(label || showPercentage) && (
                    <div className={styles.progressHeader}>
                        {label && <span className={styles.progressLabel}>{label}</span>}
                        {showPercentage && !indeterminate && (
                            <span className={styles.progressValue}>{displayValue}</span>
                        )}
                    </div>
                )}

                {/* Progress track and bar */}
                <div className={styles.progressTrack}>
                    <div className={barClasses} style={barStyle}>
                        {/* Screen reader text for progress */}
                        <span className={styles.srOnly}>
                            {indeterminate ? 'Loading...' : `${Math.round(percentage)}% complete`}
                        </span>
                    </div>
                </div>
            </div>
        );
    }
);

DynProgress.displayName = 'DynProgress';

export default DynProgress;
