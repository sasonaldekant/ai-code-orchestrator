/**
 * DynToolbar TypeScript type definitions
 * Toolbar component types for action buttons and responsive layouts
 */

import type { ReactNode } from 'react';
import type { DynBadgeSemanticColor as DynBadgeColor, DynBadgeVariant } from '../DynBadge/DynBadge.types';
import type { BaseComponentProps, AccessibilityProps } from '../../types';

export type ToolbarBadge =
  | number
  | string
  | {
    count?: number;
    value?: number;
    label?: ReactNode;
    color?: DynBadgeColor;
    variant?: DynBadgeVariant;
    maxCount?: number;
    showZero?: boolean;
  };

export interface ToolbarItem {
  id: string;
  label?: string;
  icon?: string | React.ReactNode;
  type?: 'button' | 'separator' | 'dropdown' | 'search' | 'custom';
  action?: () => void;
  disabled?: boolean;
  visible?: boolean;
  items?: ToolbarItem[]; // for dropdown submenus
  component?: React.ReactNode; // for custom components
  tooltip?: string;
  badge?: ToolbarBadge;
  onChange?: (value: string) => void;
}

export interface DynToolbarProps extends BaseComponentProps, AccessibilityProps {
  /** Toolbar items to display */
  items: ToolbarItem[];

  /** Visual variant */
  variant?: 'default' | 'minimal' | 'floating';

  /** Size variant */
  size?: 'sm' | 'md' | 'lg';

  /** Position on screen */
  position?: 'top' | 'bottom' | 'fixed-top' | 'fixed-bottom';

  /** Enable responsive behavior */
  responsive?: boolean;

  /** Show overflow menu for hidden items */
  overflowMenu?: boolean;

  /** Number of items before overflow kicks in */
  overflowThreshold?: number;

  /** Show labels on toolbar items */
  showLabels?: boolean;

  /** Additional CSS classes */
  className?: string;

  /** CSS class for individual items */
  itemClassName?: string;

  /** Item click handler */
  onItemClick?: (item: ToolbarItem) => void;

  /** Overflow menu toggle handler */
  onOverflowToggle?: (isOpen: boolean) => void;

  /** Children elements for custom toolbar content */
  children?: React.ReactNode;

  /** Component ID */
  id?: string;

  /** ARIA label for toolbar */
  'aria-label'?: string;

  /** ARIA labelledby for toolbar */
  'aria-labelledby'?: string;

  /** Test ID */
  'data-testid'?: string;
}

export interface DynToolbarRef {
  openOverflow: () => void;
  closeOverflow: () => void;
  toggleOverflow: () => void;
  refreshLayout: () => void;
}

// Default configuration
export const TOOLBAR_DEFAULTS = {
  variant: 'default' as const,
  size: 'md' as const,
  position: 'top' as const,
  responsive: true,
  overflowMenu: true,
  overflowThreshold: 3,
  showLabels: true
};

// Toolbar item types
export const TOOLBAR_ITEM_TYPES = {
  BUTTON: 'button',
  SEPARATOR: 'separator',
  DROPDOWN: 'dropdown',
  SEARCH: 'search',
  CUSTOM: 'custom'
} as const;