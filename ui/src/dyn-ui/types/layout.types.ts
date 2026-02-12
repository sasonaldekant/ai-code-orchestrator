/**
 * Layout Components Type Definitions
 * Part of DYN UI Layout Components Group - SCOPE 7
 */

import type { CSSProperties, HTMLAttributes, ReactNode } from 'react';
import type { BaseComponentProps } from './theme';

// Common layout types
export type LayoutSize = 'sm' | 'md' | 'lg';
export type LayoutSpacing = 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl';
export type LayoutDirection = 'horizontal' | 'vertical';
export type LayoutAlignment = 'start' | 'center' | 'end' | 'stretch';
export type LayoutJustify = 'start' | 'center' | 'end' | 'between' | 'around' | 'evenly';

// DynContainer Props
export type DynContainerBackground = 'none' | 'surface' | 'card';

export interface DynContainerOwnProps {
  children?: ReactNode;
  title?: string;
  subtitle?: string;
  direction?: LayoutDirection;
  align?: LayoutAlignment;
  justify?: LayoutJustify;
  spacing?: LayoutSpacing;
  size?: LayoutSize;
  bordered?: boolean;
  shadow?: boolean;
  background?: DynContainerBackground;
  height?: number | string;
  maxWidth?: number | string;
  noBorder?: boolean;
  noPadding?: boolean;
  style?: CSSProperties;
}

export type DynContainerProps = BaseComponentProps &
  DynContainerOwnProps &
  Omit<
    HTMLAttributes<HTMLDivElement>,
    keyof BaseComponentProps | keyof DynContainerOwnProps
  >;

export type DynDividerLabelPosition = 'left' | 'center' | 'right';
export type DynDividerThickness = 'thin' | 'medium' | 'thick';
export type DynDividerLineStyle = 'solid' | 'dashed' | 'dotted';
export type DynDividerColor = 'default' | 'primary' | 'secondary' | 'muted';

export interface DynDividerOwnProps {
  /** Optional label rendered between the divider lines */
  label?: string;
  /** Placement for the optional label */
  labelPosition?: DynDividerLabelPosition;
  /** Orientation of the divider */
  direction?: LayoutDirection;
  /** Line thickness */
  thickness?: DynDividerThickness;
  /** Line visual style */
  lineStyle?: DynDividerLineStyle;
  /** Color variant */
  color?: DynDividerColor;
  /** External spacing around the divider */
  spacing?: LayoutSpacing;
  /** Optional custom content rendered instead of the label */
  children?: ReactNode;
}

export type DynDividerProps = BaseComponentProps &
  DynDividerOwnProps &
  Omit<
    HTMLAttributes<HTMLDivElement>,
    keyof BaseComponentProps | keyof DynDividerOwnProps | 'color'
  >;

// DynGrid Props
export interface DynGridColumn {
  key: string;
  title: string;
  width?: string | number;
  minWidth?: string | number;
  sortable?: boolean;
  filterable?: boolean;
  resizable?: boolean;
  render?: (value: any, record: any, index: number) => ReactNode;
  align?: 'left' | 'center' | 'right';
  fixed?: 'left' | 'right';
  hidden?: boolean;
}

// DynPage Props
export interface DynPageBreadcrumb {
  title: string;
  href?: string;
  onClick?: () => void;
}

export interface DynPageAction {
  key: string;
  title: string;
  icon?: string;
  type?: 'primary' | 'secondary' | 'danger';
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
}

export interface DynPageProps {
  title: string;
  subtitle?: string;
  breadcrumbs?: DynPageBreadcrumb[];
  actions?: DynPageAction[];
  children: ReactNode;
  loading?: boolean;
  error?: string | ReactNode;
  size?: LayoutSize;
  padding?: LayoutSpacing;
  background?: 'none' | 'surface' | 'page';
  className?: string;
  id?: string;
  'data-testid'?: string;
}
