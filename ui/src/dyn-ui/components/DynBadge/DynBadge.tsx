/**
 * DynBadge Component
 * 
 * A flexible, accessible badge component for displaying counts, status indicators,
 * and notifications. Supports multiple variants (solid, soft, outline, dot),
 * sizes, colors, and positions.
 * 
 * Token Compliant: ✅ Full --dyn-badge-* pattern with 3-level fallback
 * 
 * @component
 * @module DynBadge
 * @version 1.0.0
 */

import React, { forwardRef, useMemo, useCallback } from 'react';
import { cn } from '../../utils/classNames';

import type {
  DynBadgeProps,
  DynBadgeRef,
  DynBadgeVariant,
  DynBadgeSemanticColor,
} from './DynBadge.types';
import {
  DYN_BADGE_COLORS,
  DYN_BADGE_SIZES,
  DYN_BADGE_VARIANTS,
  DYN_BADGE_DEFAULT_PROPS,
} from './DynBadge.types';
import styles from './DynBadge.module.css';

/**
 * DynBadge Component
 * 
 * Fully accessible badge component with rich customization options.
 * Used throughout the system for counters, status indicators, and notifications.
 * 
 * ✅ Full accessibility support:
 * - Semantic HTML (span, with proper role)
 * - ARIA attributes (aria-label, aria-live for dynamic updates)
 * - Screen reader friendly text content
 * - Keyboard accessible when interactive
 * - Color contrast WCAG AA compliant
 * 
 * ✅ Token Compliant (Design System):
 * - All colors use --dyn-badge-* tokens
 * - 3-level fallback pattern for all tokens
 * - Dark mode support (@media prefers-color-scheme: dark)
 * - High contrast support (@media prefers-contrast: more)
 * - Reduced motion support (@media prefers-reduced-motion: reduce)
 * 
 * ✅ Variants:
 * - solid: Filled background (default)
 * - soft: Light background with darker text
 * - outline: Bordered with transparent background
 * - dot: Small circular indicator
 * 
 * ✅ Used in:
 * - DynAvatar: Status indicator (dot variant, positioned topRight/bottomRight)
 * - DynNotification: Badge counter
 * - DynAlert: Status indicator
 * - DynTag: Count badges
 * 
 * @component
 * @param {DynBadgeProps} props - Component props
 * @param {React.ReactNode} [props.children] - Content to display in badge
 * @param {string} [props.className] - Additional CSS classes
 * @param {number | string} [props.count] - Counter value (replaces children if provided)
 * @param {number} [props.maxCount=99] - Maximum count value (shows 99+ when exceeded)
 * @param {string} [props.size="md"] - Badge size: xs, sm, md, lg, xl
 * @param {DynBadgeVariant} [props.variant="solid"] - Style variant: solid, soft, outline, dot
 * @param {DynBadgeSemanticColor} [props.color="primary"] - Color: primary, secondary, success, danger, warning, info, neutral
 * @param {string} [props.position] - Position for overlay badges: topRight, topLeft, bottomRight, bottomLeft, center
 * @param {boolean} [props.invisible=false] - Hide badge while keeping DOM accessible
 * @param {React.SVGProps<SVGSVGElement>} [props.icon] - Optional icon element
 * @param {boolean} [props.animated=false] - Enable entrance animation
 * @param {boolean} [props.pulse=false] - Enable pulsing animation for attention
 * @param {string} [props.id] - HTML id attribute
 * @param {string} [props.aria-label] - ARIA label for badge content
 * @param {string} [props.aria-live="polite"] - ARIA live region setting
 * @param {string} [props.role="status"] - ARIA role
 * @param {string} [props.data-testid] - Test ID for testing
 * @param {React.ReactNode} [props.fallback] - Fallback content if no children/count
 * @param {HTMLSpanElement} ref - Forwarded ref
 * @returns {JSX.Element} Badge component
 */
export const DynBadge = forwardRef<DynBadgeRef, DynBadgeProps>(
  (
    {
      // Content props
      children,
      count,
      maxCount = DYN_BADGE_DEFAULT_PROPS.maxCount,
      fallback = null,

      // Style props
      size = DYN_BADGE_DEFAULT_PROPS.size,
      variant = DYN_BADGE_DEFAULT_PROPS.variant,
      color = DYN_BADGE_DEFAULT_PROPS.color,
      position,

      // Interaction props
      invisible = DYN_BADGE_DEFAULT_PROPS.invisible,
      icon,
      startIcon,
      endIcon,
      animated = DYN_BADGE_DEFAULT_PROPS.animated,
      pulse = DYN_BADGE_DEFAULT_PROPS.pulse,
      loading = false,
      showZero = DYN_BADGE_DEFAULT_PROPS.showZero,
      onKeyDown,

      // Accessibility props
      id,
      'aria-label': ariaLabel,
      'aria-live': ariaLive = DYN_BADGE_DEFAULT_PROPS['aria-live'],
      role = DYN_BADGE_DEFAULT_PROPS.role,
      countDescription,

      // HTML props
      className,
      'data-testid': dataTestId,

      // Legacy prop support
      value,
      onClick,
      ...rest
    },
    ref
  ) => {

    // ====================================
    // PHASE 0: State & Initial Identifiers
    // ====================================

    /**
     * Generate unique implementation ID if none provided
     * Stable across re-renders via useState
     */
    const generatedId = React.useId();
    const internalId = id || generatedId;

    // ====================================
    // PHASE 1: Input Validation & Fallback
    // ====================================

    /**
     * Handle legacy 'value' prop for backward compatibility
     * Newer code should use 'count' prop instead
     */
    const normalizedCount = count ?? value;

    /**
     * Validate variant is supported
     * Falls back to 'solid' if invalid variant provided
     */
    const validVariant: DynBadgeVariant = variant && DYN_BADGE_VARIANTS.includes(variant) ? variant : 'solid';

    /**
     * Validate color is supported
     * Falls back to 'primary' if invalid color provided
     */
    const validColor: DynBadgeSemanticColor = color && DYN_BADGE_COLORS.includes(color) ? color : 'primary';

    /**
     * Validate size is supported
     * Falls back to 'md' if invalid size provided
     */
    const validSize = size && DYN_BADGE_SIZES.includes(size) ? size : 'md';

    // ====================================
    // PHASE 2: Content Computation
    // ====================================

    /**
     * Determine if component should act as a wrapper
     * We act as a wrapper if children are provided AND there's badge-specific content or explicit positioning
     */
    const isWrapper = useMemo(() => {
      // If no children, definitely not a wrapper
      if (!children) return false;

      // If count/value is provided, children must be the wrapped element
      if (normalizedCount !== undefined) return true;

      // If it's a dot variant with children, it's a wrapper context
      if (validVariant === 'dot') return true;

      // If children is an object (React element), we assume it's a target container
      // If it is a string/number, we treat it as the badge's own label (standalone mode)
      return typeof children === 'object';
    }, [children, normalizedCount, validVariant]);

    /**
     * Compute final badge content with memoization for performance
     * Priority: count > children (if not wrapping) > icon > fallback
     */
    const displayContent = useMemo(() => {
      // Show count if provided
      if (normalizedCount !== undefined) {
        // Don't show if count is 0 and showZero is false
        if (normalizedCount === 0 && !showZero) {
          return null;
        }

        if (typeof normalizedCount === 'number' && maxCount !== undefined && normalizedCount > maxCount) {
          return `${maxCount}+`;
        }
        return String(normalizedCount);
      }

      // Show children as content ONLY if we are not in wrapper mode
      if (children && !isWrapper) {
        return children;
      }

      // Show icon if provided and no text
      if (icon) {
        return icon;
      }

      // Fallback to fallback prop or empty
      return fallback;
    }, [normalizedCount, maxCount, children, isWrapper, icon, fallback, showZero]);

    /**
     * Determine if badge itself (the bubble) should be visible
     */
    const isBadgeVisible = !invisible && (displayContent !== null || validVariant === 'dot');

    // ====================================
    // PHASE 3: Accessibility Attributes
    // ====================================

    /**
     * Generate appropriate ARIA label if not provided
     * Describes badge content and purpose for screen readers
     */
    const computedAriaLabel = useMemo(() => {
      if (ariaLabel) return ariaLabel;

      // Build context-aware label
      let label = '';

      // Add status/role context
      if (validColor === 'danger') label += 'Alert: ';
      if (validColor === 'success') label += 'Success: ';
      if (validColor === 'warning') label += 'Warning: ';
      if (validColor === 'info') label += 'Information: ';

      // Add content
      if (normalizedCount !== undefined) {
        const description = countDescription || (normalizedCount === 1 ? 'item' : 'items');
        label += `${displayContent} ${description}`;
      } else if (typeof displayContent === 'string') {
        label += displayContent;
      }

      return label || undefined;
    }, [ariaLabel, validColor, displayContent, normalizedCount, countDescription]);

    // ====================================
    // PHASE 4: Class Computation
    // ====================================

    /**
     * Determine if a custom color (hex/rgb) is provided
     */
    const isCustomColor = useMemo(() => {
      if (!color) return false;
      return !DYN_BADGE_COLORS.includes(color as any);
    }, [color]);

    /**
     * Compute inline styles for custom colors
     */
    const inlineStyles = useMemo<React.CSSProperties>(() => {
      const styles: any = {};
      if (isCustomColor) {
        styles['--dyn-badge-bg'] = color;
        styles['--dyn-badge-color'] = '#ffffff'; // Default to white text for custom badges
        styles['--dyn-badge-border'] = color;
      }
      return styles;
    }, [isCustomColor, color]);

    /**
     * Compute root element classes
     * Combines module styles with variant, color, size, and custom classes
     */
    const badgeClasses = useMemo(() => {
      // Convert variant/color/size to camelCase class names
      const variantClass = `badge${validVariant.charAt(0).toUpperCase()}${validVariant.slice(1)}`;
      const colorClass = `badge${validColor.charAt(0).toUpperCase()}${validColor.slice(1)}`;
      const sizeClass = `size${validSize.charAt(0).toUpperCase()}${validSize.slice(1)}`;

      // Default position to topRight if wrapping but no position specified
      const finalPosition = position || (isWrapper ? 'topRight' : null);
      const positionClass = finalPosition ? `badge${finalPosition.charAt(0).toUpperCase()}${finalPosition.slice(1)}` : null;

      return cn(
        styles.badge,

        // Variant styles (camelCase)
        styles[variantClass],

        // Color styles (camelCase)
        styles[colorClass],

        // Size styles (camelCase)
        styles[sizeClass],

        // Position styles (camelCase)
        positionClass && styles[positionClass],
        (finalPosition || positionClass) && styles.badgePositioned,

        // State classes (camelCase)
        {
          [styles.badgeInvisible]: invisible,
          [styles.badgeAnimated]: animated,
          [styles.badgePulse]: pulse || loading,
          [styles.badgeClickable]: !!onClick,
          [styles.badgeCircle]: typeof displayContent === 'string' && displayContent.length === 1,
        },

        // Custom classes
        !isWrapper && className
      );
    }, [validVariant, validColor, validSize, position, isWrapper, invisible, animated, pulse, loading, onClick, className, displayContent]);

    // ====================================
    // PHASE 5: Event Handlers
    // ====================================

    const handleClick = useCallback(
      (e: React.MouseEvent<HTMLSpanElement>) => {
        e.stopPropagation();
        onClick?.(e);
      },
      [onClick]
    );

    const handleKeyDown = useCallback(
      (e: React.KeyboardEvent<HTMLSpanElement>) => {
        if (onClick && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          handleClick(e as any);
        }
        onKeyDown?.(e);
      },
      [onClick, handleClick, onKeyDown]
    );

    // ====================================
    // PHASE 6: Render
    // ====================================

    // The actual badge bubble element
    const badgeElement = isBadgeVisible || invisible ? (
      <span
        ref={isWrapper ? undefined : ref}
        id={isWrapper ? undefined : internalId}
        className={badgeClasses}
        role={onClick ? 'button' : (role || 'status')}
        tabIndex={onClick ? 0 : undefined}
        aria-label={computedAriaLabel}
        aria-live={ariaLive}
        aria-busy={loading}
        aria-hidden={invisible ? 'true' : undefined}
        data-testid={dataTestId || 'dyn-badge'}
        data-variant={validVariant}
        data-color={validColor}
        data-size={validSize}
        data-position={position}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        key={animated ? `${internalId}-${normalizedCount ?? 'no-count'}` : undefined}
        style={{ ...inlineStyles, ...(!isWrapper ? rest.style : {}) } as React.CSSProperties}
        {...(!isWrapper ? rest : {})}
      >
        <span className={styles.badgeContent}>
          {validVariant === 'dot' && (
            <span className={styles.badgeDotIndicator} aria-hidden="true" />
          )}

          {displayContent && (
            <>
              {(startIcon || (icon && !startIcon)) && (
                <span className={styles.badgeIcon} aria-hidden="true">
                  {startIcon || icon}
                </span>
              )}

              {typeof displayContent === 'string' ? (
                <span className={styles.badgeText}>{displayContent}</span>
              ) : (
                displayContent
              )}

              {endIcon && (
                <span className={styles.badgeIcon} aria-hidden="true">
                  {endIcon}
                </span>
              )}
            </>
          )}
        </span>
      </span>
    ) : null;

    // If we are in wrapper mode, return the children wrapped with the badge
    if (isWrapper) {
      return (
        <span
          ref={ref}
          id={internalId}
          className={cn(styles.wrapper, className)}
          style={rest.style}
          {...rest}
        >
          {children}
          {badgeElement}
        </span>
      );
    }

    // Otherwise just return the badge element
    return badgeElement;
  }
);

DynBadge.displayName = 'DynBadge';

/**
 * Export the component for use in other modules
 */
export default DynBadge;