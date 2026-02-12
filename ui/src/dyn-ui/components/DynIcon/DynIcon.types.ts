import type { HTMLAttributes, ReactNode } from 'react';

export type DynIconTone = 'success' | 'warning' | 'danger' | 'info';
export type DynIconSizeToken = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export interface DynIconProps extends Omit<HTMLAttributes<HTMLSpanElement>, 'color'> {
  /** Icon identifier - string (dictionary key, class names) or React node */
  icon?: string | ReactNode;

  /** Icon size token or explicit dimension */
  size?: DynIconSizeToken | number | string;

  /** Semantic tone helper that maps to predefined colors */
  tone?: DynIconTone;

  /** Custom color override */
  color?: string;

  /** Custom stroke width for registry icons */
  strokeWidth?: number | string;

  /** Mirror/flip the icon */
  mirror?: 'horizontal' | 'vertical' | 'both';

  /** Whether the icon should spin */
  spin?: boolean;

  /** Disabled state prevents interaction */
  disabled?: boolean;

  /** Icon content fallback */
  children?: ReactNode;

  /** Test identifier for automated testing */
  'data-testid'?: string;
}

export interface DynIconDefaultProps {
  size: DynIconSizeToken;
  spin: boolean;
  disabled: boolean;
}

export const DYN_ICON_DEFAULT_PROPS: DynIconDefaultProps = {
  size: 'md',
  spin: false,
  disabled: false,
} as const;

export type IconDictionary = Record<string, string>;

export interface ProcessedIcon {
  baseClass: string;
  iconClass: string;
}
