/**
 * DynProgress Component Types
 *
 * Type definitions for the progress bar component.
 * Token Compliant: ✅ Full --dyn-progress-* pattern
 *
 * @module DynProgress
 * @version 1.0.0
 */

import { HTMLAttributes } from 'react';

/**
 * Progress status variants
 */
export type DynProgressStatus = 'default' | 'success' | 'error' | 'warning' | 'info';

/**
 * Progress size variants
 */
export type DynProgressSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

/**
 * Progress variant types
 */
export type DynProgressVariant = 'linear' | 'circular';

/**
 * Available status values as const array for validation
 */
export const DYN_PROGRESS_STATUSES = ['default', 'success', 'error', 'warning', 'info'] as const;

/**
 * Available size values as const array for validation
 */
export const DYN_PROGRESS_SIZES = ['xs', 'sm', 'md', 'lg', 'xl'] as const;

/**
 * DynProgress Component Props
 */
export interface DynProgressProps extends Omit<HTMLAttributes<HTMLDivElement>, 'color'> {
  /**
   * Current progress value (0-100 by default)
   */
  value?: number;

  /**
   * Maximum value (default: 100)
   */
  max?: number;

  /**
   * Minimum value (default: 0)
   */
  min?: number;

  /**
   * Progress status for color theming
   * @default 'default'
   */
  status?: DynProgressStatus;

  /**
   * Size variant
   * @default 'md'
   */
  size?: DynProgressSize;

  /**
   * Display text label
   */
  label?: string;

  /**
   * Show percentage value
   * @default false
   */
  showPercentage?: boolean;

  /**
   * Custom format function for displayed value
   */
  formatValue?: (value: number, percentage: number) => string;

  /**
   * Enable indeterminate (loading) animation
   * @default false
   */
  indeterminate?: boolean;

  /**
   * Enable striped animation
   * @default false
   */
  striped?: boolean;

  /**
   * Animate stripes
   * @default false
   */
  animated?: boolean;

  /**
   * Custom height in pixels (overrides size)
   */
  height?: number;

  /**
   * ARIA label for accessibility
   */
  'aria-label'?: string;

  /**
   * Additional CSS class
   */
  className?: string;

  /**
   * Test ID for testing
   */
  'data-testid'?: string;
}

/**
 * Ref type for DynProgress
 */
export type DynProgressRef = HTMLDivElement;

/**
 * Default props for DynProgress
 */
export const DYN_PROGRESS_DEFAULT_PROPS: Partial<DynProgressProps> = {
  value: 0,
  max: 100,
  min: 0,
  status: 'default',
  size: 'md',
  showPercentage: false,
  indeterminate: false,
  striped: false,
  animated: false,
};
