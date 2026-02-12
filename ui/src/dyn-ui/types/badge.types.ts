export type {
  DynBadgeProps,
  DynBadgeRef,
  DynBadgeVariant,
  DynBadgeSemanticColor,
  DynBadgeSemanticColor as DynBadgeColor, // Alias
  DynBadgeSize,
  DynBadgePosition,
} from '../components/DynBadge/DynBadge.types';

export {
  DYN_BADGE_VARIANTS,
  DYN_BADGE_COLORS,
  DYN_BADGE_SIZES,
  DYN_BADGE_POSITIONS,
} from '../components/DynBadge/DynBadge.types';

// AccessibilityProps is declared in the common types; re-export under badge namespace
export type { AccessibilityProps as DynBadgeAccessibilityProps } from './index';
