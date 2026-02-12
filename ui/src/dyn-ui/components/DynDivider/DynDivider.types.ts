import type { ComponentPropsWithoutRef, ElementRef } from 'react';
import type { BaseComponentProps, AccessibilityProps } from '../../types/theme';

// Local type definitions (previously from ../../types)
export type DynDividerColor = 'default' | 'subtle' | 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
export type DynDividerLabelPosition = 'left' | 'center' | 'right';
export type DynDividerLineStyle = 'solid' | 'dashed' | 'dotted';
export type DynDividerThickness = 'thin' | 'medium' | 'thick';
export type LayoutDirection = 'horizontal' | 'vertical';
export type LayoutSpacing = 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export interface DynDividerProps 
  extends BaseComponentProps,
    AccessibilityProps,
    Omit<ComponentPropsWithoutRef<'div'>, keyof BaseComponentProps> {
  /** Direction of the divider */
  direction?: LayoutDirection;
  /** Thickness of the divider line */
  thickness?: DynDividerThickness;
  /** Style of the divider line */
  lineStyle?: DynDividerLineStyle;
  /** Color variant of the divider */
  color?: DynDividerColor;
  /** Label text to display */
  label?: string;
  /** Position of the label */
  labelPosition?: DynDividerLabelPosition;
  /** Spacing around the divider */
  spacing?: LayoutSpacing;
  /** Additional CSS classes */
  className?: string;
  /** Custom styles */
  style?: React.CSSProperties;
}

export type DynDividerRef = HTMLDivElement;

export interface DynDividerDefaultProps {
  direction: LayoutDirection;
  thickness: DynDividerThickness;
  lineStyle: DynDividerLineStyle;
  color: DynDividerColor;
  labelPosition: DynDividerLabelPosition;
  spacing: LayoutSpacing;
  'data-testid': string;
}

export const DYN_DIVIDER_DEFAULT_PROPS: DynDividerDefaultProps = {
  direction: 'horizontal',
  thickness: 'thin',
  lineStyle: 'solid',
  color: 'default',
  labelPosition: 'center',
  spacing: 'md',
  'data-testid': 'dyn-divider',
};