import type {
  ButtonHTMLAttributes,
  FocusEventHandler,
  KeyboardEventHandler,
  MouseEventHandler,
  ReactNode,
} from 'react';
import type { BaseComponentProps, AccessibilityProps } from '../../types';

/**
 * Button kind/variant types following design system standards
 */
export type DynButtonKind = 'primary' | 'secondary' | 'tertiary' | 'soft' | 'outline';

/**
 * Button semantic colors
 */
export type DynButtonColor = 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info' | 'neutral';

/**
 * Button size variants using design token scale
 */
export type DynButtonSize = 'xs' | 'sm' | 'md' | 'lg';

/**
 * Props interface for DynButton component
 * Follows DynAvatar's standardized pattern with BaseComponentProps and AccessibilityProps
 */
export interface DynButtonProps
  extends BaseComponentProps,
  AccessibilityProps,
  Omit<
    ButtonHTMLAttributes<HTMLButtonElement>,
    | 'type'
    | 'onBlur'
    | 'onClick'
    | 'onKeyDown'
    | 'children'
    | 'aria-label'
    | 'aria-expanded'
    | 'aria-controls'
    | 'aria-describedby'
    | 'aria-pressed'
    | keyof BaseComponentProps
    | keyof AccessibilityProps
  > {

  /** Button text label */
  label?: string;

  /** Icon - can be string (icon name) or React node */
  icon?: string | ReactNode;

  /** HTML button type */
  type?: 'button' | 'submit' | 'reset';

  /** Loading state indicator */
  loading?: boolean;

  /** Text announced to assistive technologies while loading */
  loadingText?: string;

  /** Danger/destructive state styling (legacy, use color="danger") */
  danger?: boolean;

  /** Button semantic color */
  color?: DynButtonColor;

  /** Button kind/variant */
  kind?: DynButtonKind;

  /** Button size */
  size?: DynButtonSize;

  /** Disabled state */
  disabled?: boolean;

  /** Expand button to full width */
  fullWidth?: boolean;

  /** Hide button on viewports narrower than 768px */
  hideOnMobile?: boolean;

  /** Display as icon-only on mobile while keeping the label accessible */
  iconOnlyOnMobile?: boolean;

  /** Accessible expanded state (for dropdown buttons, etc.) */
  'aria-expanded'?: boolean;

  /** ID reference of the element controlled by the button */
  'aria-controls'?: string;

  /** Pressed/toggled state for ARIA toggle buttons */
  'aria-pressed'?: boolean;

  /** Blur event handler */
  onBlur?: FocusEventHandler<HTMLButtonElement>;

  /** Click event handler */
  onClick?: MouseEventHandler<HTMLButtonElement>;

  /** Key down handler */
  onKeyDown?: KeyboardEventHandler<HTMLButtonElement>;
}

/**
 * Ref type for DynButton component
 */
export type DynButtonRef = HTMLButtonElement;

/**
 * Default props type for DynButton
 */
export type DynButtonDefaultProps = Required<
  Pick<
    DynButtonProps,
    | 'type'
    | 'kind'
    | 'size'
    | 'color'
    | 'loading'
    | 'loadingText'
    | 'danger'
    | 'disabled'
    | 'fullWidth'
    | 'hideOnMobile'
    | 'iconOnlyOnMobile'
  >
>;

/**
 * Default props values for DynButton component
 * Provides sensible defaults for all optional props
 */
export const DYN_BUTTON_DEFAULT_PROPS: DynButtonDefaultProps = {
  type: 'button',
  kind: 'primary',
  size: 'md',
  color: 'primary',
  loading: false,
  loadingText: 'Loading…',
  danger: false,
  disabled: false,
  fullWidth: false,
  hideOnMobile: false,
  iconOnlyOnMobile: false,
} as const;