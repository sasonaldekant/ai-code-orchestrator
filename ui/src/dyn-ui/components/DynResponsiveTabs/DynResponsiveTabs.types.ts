import type { ReactNode, HTMLAttributes } from 'react';

/**
 * Tab item configuration
 */
export interface DynResponsiveTabItem {
  /** Tab label text */
  label: string;
  /** Tab content - can contain nested DynResponsiveTabs */
  content: ReactNode;
  /** Optional icon (string name or React element) */
  icon?: string | ReactNode;
  /** Whether tab is disabled */
  disabled?: boolean;
}

/**
 * Tab orientation types
 */
export type DynResponsiveTabsOrientation = 'horizontal' | 'vertical';

/**
 * Props interface for DynResponsiveTabs component
 */
export interface DynResponsiveTabsProps
  extends Omit<HTMLAttributes<HTMLDivElement>, 'onChange'> {
  /** Array of tab items */
  tabs: DynResponsiveTabItem[];

  /** Index of initially active tab (uncontrolled mode) */
  defaultActive?: number;

  /** Currently active tab index (controlled mode) */
  activeTab?: number;

  /** Tab orientation (horizontal or vertical) */
  orientation?: DynResponsiveTabsOrientation;

  /** Enable responsive behavior (tabs to accordion) */
  responsive?: boolean;

  /** Breakpoint in pixels for switching to accordion */
  breakpoint?: number;

  /** Allow collapsing active accordion item */
  allowCollapse?: boolean;

  /** Icon for expand state */
  expandIcon?: string | ReactNode;

  /** Icon for collapse state */
  collapseIcon?: string | ReactNode;

  /**
   * Unique identifier for this tab group (required for nested tabs)
   * Used to distinguish between parent and child tab styles
   */
  tabIdentifier?: string;

  /** Callback when active tab changes (uncontrolled mode) */
  onChange?: (index: number) => void;

  /** Callback when active tab changes (controlled mode) */
  onTabChange?: (index: number) => void;

  /** Disable animations for accessibility or performance */
  disableAnimation?: boolean;

  /** Accessible label for tab list */
  'aria-label'?: string;

  /** Custom CSS class */
  className?: string;

  /** Element ID */
  id?: string;

  /** Test ID for testing */
  'data-testid'?: string;
}

/**
 * Ref type for DynResponsiveTabs
 */
export type DynResponsiveTabsRef = HTMLButtonElement;

/**
 * Default props type for DynResponsiveTabs
 */
export type DynResponsiveTabsDefaultProps = Required<
  Pick<
    DynResponsiveTabsProps,
    | 'defaultActive'
    | 'orientation'
    | 'responsive'
    | 'breakpoint'
    | 'allowCollapse'
    | 'expandIcon'
    | 'collapseIcon'
    | 'disableAnimation'
  >
>;

/**
 * Default values for DynResponsiveTabs
 */
export const DYN_RESPONSIVE_TABS_DEFAULT_PROPS: DynResponsiveTabsDefaultProps = {
  defaultActive: 0,
  orientation: 'horizontal',
  responsive: true,
  breakpoint: 768,
  allowCollapse: false,
  expandIcon: 'chevron-down',
  collapseIcon: 'chevron-up',
  disableAnimation: false,
} as const;
