/**
 * DynMenu TypeScript type definitions
 * Navigation component types for hierarchical menu system
 * 
 * SIMPLIFIED VERSION - Removed non-implemented props:
 * - collapsed, collapsedIcon, filter, shortLogo, logo, literals, 
 * - automaticToggle, onCollapse, onMenuClick
 * 
 * These were defined but not implemented in the actual component.
 * Focus on what's actually working: items, orientation, onAction
 */

import type { ReactNode } from 'react';
import type { BaseComponentProps, AccessibilityProps } from '../../types/theme';

export interface MenuBadge {
  /** Badge numeric indicator */
  count?: number;

  /** @deprecated Legacy alias for `count` */
  value?: number;

  /** Optional text label rendered inside the badge */
  label?: ReactNode;

  /** Visual color token */
  color?: string;

  /** Variant styling */
  variant?: string;

  /** Maximum count before `max+` is shown */
  maxCount?: number;

  /** Display when the count is zero */
  showZero?: boolean;
}

export interface MenuItem {
  label?: string;
  icon?: string | React.ReactNode;
  shortLabel?: string;
  link?: string;
  action?: string | (() => void);
  badge?: MenuBadge;
  subItems?: MenuItem[];
  children?: MenuItem[]; // alias for subItems for compatibility
  disabled?: boolean;
  visible?: boolean;
  type?: 'divider' | 'item';
}

// Alias for backward compatibility
export type DynMenuItem = MenuItem;

export type MenuOrientation = 'horizontal' | 'vertical';

/**
 * DynMenu component props
 * Simple, focused props for horizontal/vertical navigation menus
 */
export interface DynMenuProps extends BaseComponentProps, AccessibilityProps {
  /** Menu items array - REQUIRED */
  items: MenuItem[];
  
  /** Legacy menu items prop (alias for items) */
  menus?: MenuItem[];
  
  /** Menu orientation - horizontal or vertical */
  orientation?: MenuOrientation;
  
  /** Generic action handler - called when menu item is clicked */
  onAction?: (item: MenuItem | string) => void;
  
  /** Menu ID for ARIA */
  id?: string;
  
  /** ARIA label for menu */
  'aria-label'?: string;
  
  /** ARIA labelledby for menu */
  'aria-labelledby'?: string;
  
  /** ARIA describedby for menu */
  'aria-describedby'?: string;
  
  /** Test ID */
  'data-testid'?: string;
  
  /** Additional CSS classes */
  className?: string;
}

export interface DynMenuRef {
  collapse: () => void;
  expand: () => void;
  toggle: () => void;
}
