import type {
  ComponentPropsWithoutRef,
  ComponentRef,
  ElementType,
  KeyboardEventHandler,
  MouseEventHandler,
} from 'react';
import type { AccessibilityProps, BaseComponentProps } from '../../types/theme';

export type BoxDisplay =
  | 'block'
  | 'inline'
  | 'inline-block'
  | 'flex'
  | 'inline-flex'
  | 'grid'
  | 'inline-grid'
  | 'none';

export type BoxPosition = 'static' | 'relative' | 'absolute' | 'fixed' | 'sticky';
export type SpacingSize = 'none' | '0' | '2xs' | 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | 'auto';

export type BackgroundVariant =
  | 'surface'
  | 'primary'
  | 'secondary'
  | 'tertiary'
  | 'success'
  | 'success-surface'
  | 'warning'
  | 'warning-surface'
  | 'danger'
  | 'danger-surface'
  | 'info'
  | 'info-surface'
  | 'none'
  | string;
export type BorderRadius = 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'full' | string;
export type BorderVariant =
  | 'none'
  | 'default'
  | 'subtle'
  | 'strong'
  | 'danger'
  | 'danger-border'
  | 'success'
  | 'success-border'
  | 'warning'
  | 'warning-border'
  | 'info'
  | 'info-border'
  | string;

export type ColorVariant =
  | 'primary'
  | 'secondary'
  | 'tertiary'
  | 'danger'
  | 'danger-text'
  | 'success'
  | 'success-text'
  | 'warning'
  | 'warning-text'
  | 'info'
  | 'info-text'
  | string;
export type Shadow = 'none' | 'sm' | 'md' | 'lg' | string;
export type TextAlign = 'left' | 'center' | 'right' | 'justify';
export type Overflow = 'visible' | 'hidden' | 'auto' | 'scroll';

export type FlexDirection = 'row' | 'row-reverse' | 'column' | 'column-reverse';
export type FlexWrap = 'nowrap' | 'wrap' | 'wrap-reverse';
export type JustifyContent =
  | 'flex-start'
  | 'flex-end'
  | 'center'
  | 'space-between'
  | 'space-around'
  | 'space-evenly';
export type AlignItems = 'stretch' | 'flex-start' | 'flex-end' | 'center' | 'baseline';
export type AlignContent = 'stretch' | 'flex-start' | 'flex-end' | 'center' | 'space-between' | 'space-around';

export interface ResponsiveVisibilityProps {
  hideOnMobile?: boolean;
  hideOnTablet?: boolean;
  hideOnDesktop?: boolean;
  mobileOnly?: boolean;
  tabletOnly?: boolean;
  desktopOnly?: boolean;
}

type PolymorphicComponentProps<E extends ElementType, P> = P &
  Omit<ComponentPropsWithoutRef<E>, keyof P>;

export type DynColSpan =
  | 'full'
  | 'half'
  | 'third'
  | 'quarter'
  | 'auto'
  | number;

export type ResponsiveColSpan = {
  mobile?: DynColSpan;
  tablet?: DynColSpan;
  desktop?: DynColSpan;
};

export interface DynBoxOwnProps
  extends BaseComponentProps,
  AccessibilityProps,
  ResponsiveVisibilityProps {
  display?: BoxDisplay;
  position?: BoxPosition;

  // Primary spacing API
  padding?: SpacingSize;
  p?: SpacingSize; // alias for padding
  px?: SpacingSize;
  py?: SpacingSize;
  pt?: SpacingSize;
  pr?: SpacingSize;
  pb?: SpacingSize;
  pl?: SpacingSize;

  m?: SpacingSize;
  mx?: SpacingSize;
  my?: SpacingSize;
  mt?: SpacingSize;
  mr?: SpacingSize;
  mb?: SpacingSize;
  ml?: SpacingSize;

  width?: string | number;
  height?: string | number;
  minWidth?: string | number;
  minHeight?: string | number;
  maxWidth?: string | number;
  maxHeight?: string | number;

  // Color API
  background?: BackgroundVariant;
  bg?: BackgroundVariant; // alias for background
  backgroundColor?: string;
  color?: ColorVariant;

  // Border API
  border?: BorderVariant;
  borderTop?: boolean;
  borderRight?: boolean;
  borderBottom?: boolean;
  borderLeft?: boolean;
  radius?: BorderRadius;
  borderRadius?: BorderRadius; // alias for radius
  customBorderRadius?: string;

  // Effects
  shadow?: Shadow;

  textAlign?: TextAlign;

  // Overflow
  overflow?: Overflow;
  overflowX?: Overflow;
  overflowY?: Overflow;



  // Flex/Grid
  direction?: FlexDirection;
  flexDirection?: FlexDirection; // alias for direction
  wrap?: FlexWrap;
  justify?: JustifyContent;
  align?: AlignItems;
  alignContent?: AlignContent;
  gap?: SpacingSize;
  rowGap?: SpacingSize;
  columnGap?: SpacingSize;

  gridTemplateColumns?: string;
  gridTemplateRows?: string;
  gridTemplateAreas?: string;

  /**
   * Grid item column span
   */
  colSpan?: DynColSpan | ResponsiveColSpan;
  /**
   * Grid item row span
   */
  rowSpan?: number;
  /**
   * Grid item column start line
   */
  colStart?: number | string;
  /**
   * Grid item row start line
   */
  rowStart?: number | string;

  // Positioning
  top?: string | number;
  right?: string | number;
  bottom?: string | number;
  left?: string | number;
  zIndex?: number;

  interactive?: boolean;

  cssVars?: Record<string, string | number>;

  ariaLiveMessage?: string;
  ariaLivePoliteness?: 'polite' | 'assertive' | 'off';

  focusOnMount?: boolean;
}

export type DynBoxProps<E extends ElementType = 'div'> = PolymorphicComponentProps<
  E,
  DynBoxOwnProps
> & {
  as?: E;
  onClick?: MouseEventHandler<any>;
  onKeyDown?: KeyboardEventHandler<any>;
};

export type DynBoxRef<E extends ElementType = 'div'> = ComponentRef<E>;

export interface DynBoxDefaultProps {
  'data-testid': string;
}

export const DYN_BOX_DEFAULT_PROPS: DynBoxDefaultProps = {
  'data-testid': 'dyn-box',
};
