/**
 * DynLoading Component Types
 *
 * Type definitions for the loading component.
 * Supports spinner, skeleton, and overlay variants.
 * Token Compliant: ✅ Full --dyn-loading-* pattern
 *
 * @module DynLoading
 * @version 1.0.0
 */

import { HTMLAttributes } from 'react';

/**
 * Loading component variants
 */
export type DynLoadingVariant = 'spinner' | 'skeleton' | 'overlay' | 'dots' | 'pulse';

/**
 * Loading size variants
 */
export type DynLoadingSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

/**
 * Loading color variants (semantic)
 */
export type DynLoadingColor = 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'neutral' | 'white';

/**
 * Available variants as const array for validation
 */
export const DYN_LOADING_VARIANTS = ['spinner', 'skeleton', 'overlay', 'dots', 'pulse'] as const;

/**
 * Available sizes as const array for validation
 */
export const DYN_LOADING_SIZES = ['xs', 'sm', 'md', 'lg', 'xl'] as const;

/**
 * Available colors as const array for validation
 */
export const DYN_LOADING_COLORS = ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'neutral', 'white'] as const;

/**
 * DynLoading Component Props
 */
export interface DynLoadingProps extends HTMLAttributes<HTMLDivElement> {
    /**
     * Loading variant
     * @default 'spinner'
     */
    variant?: DynLoadingVariant;

    /**
     * Size variant
     * @default 'md'
     */
    size?: DynLoadingSize;

    /**
     * Color variant
     * @default 'primary'
     */
    color?: DynLoadingColor;

    /**
     * Text label to display (e.g. "Loading...")
     * Not used for skeleton variant
     */
    label?: string;

    /**
     * Helper text shown below label
     */
    description?: string;

    /**
     * For overlay variant: blur background
     * @default false
     */
    blur?: boolean;

    /**
     * For overlay variant: fix to viewport (fullscreen)
     * @default false
     */
    fixed?: boolean;

    /**
     * For skeleton variant: optional specific width
     */
    width?: string | number;

    /**
     * For skeleton variant: optional specific height
     */
    height?: string | number;

    /**
     * For skeleton variant: circle shape (e.g. for avatars)
     * @default false
     */
    circle?: boolean;

    /**
     * Custom ARIA label
     */
    'aria-label'?: string;

    /**
     * Test ID
     */
    'data-testid'?: string;
}

/**
 * Ref type for DynLoading
 */
export type DynLoadingRef = HTMLDivElement;

/**
 * Default props for DynLoading
 */
export const DYN_LOADING_DEFAULT_PROPS: Partial<DynLoadingProps> = {
    variant: 'spinner',
    size: 'md',
    color: 'primary',
    blur: false,
    fixed: false,
    circle: false,
};
