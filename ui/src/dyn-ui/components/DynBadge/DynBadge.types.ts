import type { ReactNode, MouseEvent, KeyboardEvent } from 'react';
import type { BaseComponentProps, AccessibilityProps, SizeProps } from '../../types';

/**
 * Available visual variants for the badge
 */
export type DynBadgeVariant = 'solid' | 'soft' | 'outline' | 'dot' | 'ghost';

/**
 * Array of all available badge variants
 */
export const DYN_BADGE_VARIANTS: DynBadgeVariant[] = [
  'solid',
  'soft',
  'outline',
  'dot',
  'ghost'
];

/**
 * Reference type for the badge element
 */
export type DynBadgeRef = HTMLSpanElement;

/**
 * Available semantic colors for the badge
 */
export type DynBadgeSemanticColor =
  | 'primary'
  | 'secondary'
  | 'success'
  | 'danger'
  | 'warning'
  | 'info'
  | 'neutral'
  | 'online'
  | 'offline'
  | 'away'
  | 'busy';

/**
 * Array of all available badge colors
 */
export const DYN_BADGE_COLORS: DynBadgeSemanticColor[] = [
  'primary',
  'secondary',
  'success',
  'danger',
  'warning',
  'info',
  'neutral',
  'online',
  'offline',
  'away',
  'busy'
];

/**
 * Available sizes for the badge
 */
export type DynBadgeSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

/**
 * Array of all available badge sizes
 */
export const DYN_BADGE_SIZES: DynBadgeSize[] = [
  'xs',
  'sm',
  'md',
  'lg',
  'xl'
];

/**
 * Available positions for the badge relative to parent
 */
export type DynBadgePosition = 'topRight' | 'topLeft' | 'bottomRight' | 'bottomLeft' | 'center';

/**
 * Array of all available badge positions
 */
export const DYN_BADGE_POSITIONS: DynBadgePosition[] = [
  'topRight',
  'topLeft',
  'bottomRight',
  'bottomLeft',
  'center'
];

/**
 * Props for the DynBadge component
 */
export interface DynBadgeProps extends BaseComponentProps, AccessibilityProps, SizeProps {
  /**
   * Numeric value or text label to be displayed.
   * If provided, overrides `children`.
   */
  count?: number | string;

  /**
   * Legacy prop for count, kept for backward compatibility.
   * @deprecated Use `count` instead.
   */
  value?: number | string;

  /**
   * Visual style variant of the badge.
   * @default 'solid'
   */
  variant?: DynBadgeVariant;

  /**
   * Semantic color of the badge.
   * @default 'primary'
   */
  color?: DynBadgeSemanticColor;

  /**
   * Size of the badge.
   * @default 'md'
   */
  size?: DynBadgeSize;

  /**
   * Maximum number to display before showing suffix (e.g. 99+).
   * Only applies when `count` or `value` is used.
   * @default 999
   */
  maxCount?: number;

  /**
   * Legacy prop for maxCount
   * @deprecated Use `maxCount` instead.
   */
  max?: number;

  /**
   * Optional icon to display before the text/count.
   */
  icon?: ReactNode;

  /**
   * Icon to display before content
   */
  startIcon?: ReactNode;

  /**
   * Icon to display after content
   */
  endIcon?: ReactNode;

  /**
   * Whether the badge should have an entrance animation.
   * @default false
   */
  animated?: boolean;

  /**
   * Whether the badge should have a pulsing animation.
   * @default false
   */
  pulse?: boolean;

  /**
   * Whether the badge is in a loading state. 
   * If true, shows a pulsing effect.
   */
  loading?: boolean;

  /**
   * Absolute position of the badge relative to its parent container.
   * Parent container must have `position: relative`.
   */
  position?: DynBadgePosition;

  /**
   * Content to display when count is 0 and showZero is false (or undefined).
   * Usually undefined to hide the badge, or a specific fallback content.
   */
  fallback?: ReactNode;

  /**
   * Whether to display the badge when count is 0.
   * @default false
   */
  showZero?: boolean;

  /**
   * Whether the badge is invisible but still in DOM
   */
  invisible?: boolean;

  /**
   * Accessible description for the count (e.g. "unread messages")
   */
  countDescription?: string;

  /**
   * Accessibility live region behavior
   */
  'aria-live'?: 'off' | 'assertive' | 'polite';

  /**
   * Click handler
   */
  onClick?: (e: MouseEvent<HTMLSpanElement>) => void;

  /**
   * Key down handler
   */
  onKeyDown?: (e: KeyboardEvent<HTMLSpanElement>) => void;
}

/**
 * Default props for DynBadge component
 */
export const DYN_BADGE_DEFAULT_PROPS: Partial<DynBadgeProps> = {
  maxCount: 999,
  size: 'md',
  variant: 'solid',
  color: 'primary',
  invisible: false,
  animated: false,
  pulse: false,
  showZero: false,
  'aria-live': 'polite',
  role: 'status',
};
