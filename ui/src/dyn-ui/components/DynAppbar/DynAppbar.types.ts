import { BaseComponentProps, AccessibilityProps, SizeProps } from '../../types';
import { ReactNode } from 'react';

export interface DynAppbarProps extends BaseComponentProps, AccessibilityProps, SizeProps {
    /**
     * Content to be placed on the left side (e.g., logo, menu button)
     */
    leftContent?: ReactNode;

    /**
     * Content to be placed on the rights side (e.g., profile, actions)
     */
    rightContent?: ReactNode;

    /**
     * Title text or element to be displayed in the center or left depending on layout
     */
    title?: ReactNode;

    /**
     * Center content
     */
    centerContent?: ReactNode;

    /**
     * Whether the appbar is sticky or fixed
     */
    position?: 'static' | 'sticky' | 'fixed';

    /**
     * Whether the appbar is in a loading state. 
     * If true, shows a progress bar at the bottom.
     */
    loading?: boolean;

    /**
     * Color variant for the appbar
     * @default 'primary'
     */
    variant?: 'primary' | 'secondary' | 'surface' | 'inverse';
}

/**
 * Default props for DynAppbar component
 */
export const DYN_APPBAR_DEFAULT_PROPS: Partial<DynAppbarProps> = {
    position: 'static',
    size: 'md',
    variant: 'primary',
};
