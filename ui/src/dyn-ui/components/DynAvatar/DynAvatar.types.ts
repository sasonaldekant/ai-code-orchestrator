import { type ImgHTMLAttributes, type ReactNode } from 'react';
import type { BaseComponentProps, AccessibilityProps, SizeProps } from '../../types';
import type { DynBadgeProps } from '../DynBadge/DynBadge.types';

// Direct type definitions - no external dependencies
export type DynAvatarSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';
export type DynAvatarShape = 'circle' | 'square' | 'rounded';
export type DynAvatarStatus = 'online' | 'offline' | 'away' | 'busy';

/**
 * Token-based avatar size map that mirrors CSS module sizing
 */
export const AVATAR_SIZES = {
  xs: '1.5rem',
  sm: '2rem',
  md: '2.5rem',
  lg: '3rem',
  xl: '4rem',
} as const satisfies Record<DynAvatarSize, string>;

/**
 * Badge configuration for avatar badge overlay
 * Accepts either a React node or full DynBadge props for customization
 */
export type DynAvatarBadgeConfig =
  | ReactNode
  | (Omit<DynBadgeProps, 'position'> & {
    /** Badge content (number, text, or icon) */
    content?: ReactNode;
  });

/**
 * Props interface for DynAvatar component
 * Clean TypeScript implementation without external namespace dependencies
 */
export interface DynAvatarProps extends
  Omit<BaseComponentProps, 'children'>,
  AccessibilityProps,
  SizeProps,
  Omit<React.HTMLAttributes<HTMLDivElement>, keyof BaseComponentProps | keyof AccessibilityProps | 'onClick' | 'children'> {

  /** Image source URL */
  src?: string;

  /** Alt text for image (required for accessibility) */
  alt: string;

  /** Avatar size using design token scale */
  size?: DynAvatarSize;

  /** Avatar shape variant */
  shape?: DynAvatarShape;

  /** Manual initials override */
  initials?: string;

  /** Status indicator */
  status?: DynAvatarStatus;

  /**
   * Badge overlay configuration
   * 
   * Can be used for:
   * - Notification counts
   * - Status indicators
   * - Icons or custom content
   * 
   * @example
   * // Simple count badge
   * <DynAvatar badge={5} />
   * 
   * @example
   * // Custom badge with DynBadge props
   * <DynAvatar badge={{ content: "3", color: "danger", variant: "solid" }} />
   * 
   * @example
   * // Custom React node
   * <DynAvatar badge={<CustomIcon />} />
   */
  badge?: DynAvatarBadgeConfig;

  /** Loading state */
  loading?: boolean;

  /** Error state */
  error?: boolean;

  /** Click handler for interactive avatars */
  onClick?: (event: React.MouseEvent<HTMLDivElement>) => void;

  /** Custom fallback content */
  fallback?: ReactNode;

  /** Children content */
  children?: ReactNode;

  /** Image loading strategy */
  imageLoading?: 'eager' | 'lazy';

  /** Custom image properties */
  imageProps?: Omit<ImgHTMLAttributes<HTMLImageElement>, 'src' | 'alt' | 'loading'> & {
    'data-testid'?: string;
  };

  /**
   * Maximum time (ms) to wait for image to load before falling back
   * If the image doesn't load within this time, it will be treated as an error
   * and the fallback content will be shown.
   * 
   * @default 10000 (10 seconds)
   * @example
   * // Quick timeout for critical UI
   * <DynAvatar loadTimeout={3000} />
   */
  loadTimeout?: number;

  /**
   * Callback when the image fails to load or times out
   * Useful for logging, analytics, or showing custom error states
   * 
   * @example
   * <DynAvatar 
   *   src="/avatar.jpg"
   *   onError={(e) => console.log('Avatar failed:', e)}
   * />
   */
  onImageError?: (event: React.SyntheticEvent<HTMLImageElement> | { type: 'timeout' }) => void;

  /**
   * Text announced to screen readers when avatar fails to load
   * @default 'Avatar failed to load'
   */
  errorMessage?: string;

  /**
   * Text announced to screen readers when avatar is loading
   * @default 'Loading avatar'
   */
  loadingLabel?: string;
}

/**
 * Default props for DynAvatar component
 */
export const DYN_AVATAR_DEFAULT_PROPS: Partial<DynAvatarProps> = {
  size: 'md',
  shape: 'circle',
  loading: false,
  error: false,
  imageLoading: 'eager',
  loadTimeout: 10000,
  errorMessage: 'Avatar failed to load',
  loadingLabel: 'Loading avatar',
};

/**
 * Ref type for DynAvatar component
 */
export type DynAvatarRef = HTMLDivElement;

/**
 * Status accessibility labels
 */
export const DYN_AVATAR_STATUS_LABELS: Record<DynAvatarStatus, string> = {
  online: 'Online',
  offline: 'Offline',
  away: 'Away',
  busy: 'Busy',
} as const;
