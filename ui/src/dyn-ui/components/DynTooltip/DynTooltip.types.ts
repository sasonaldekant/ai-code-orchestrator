import type { ReactNode, ReactElement } from 'react';
import type { BaseComponentProps } from '../../types';

export type TooltipPosition = 'top' | 'bottom' | 'left' | 'right';
export type TooltipTrigger = 'hover' | 'click' | 'focus' | 'manual';

export interface DynTooltipProps extends BaseComponentProps {
    /**
     * The content to display inside the tooltip
     */
    content: string | ReactNode;

    /**
     * Preferred position of the tooltip
     * @default 'top'
     */
    position?: TooltipPosition;

    /**
     * Tooltip trigger mode
     * @default 'hover'
     */
    trigger?: TooltipTrigger;

    /**
     * Delay in milliseconds before showing the tooltip
     * @default 200
     */
    delay?: number;

    /**
     * Whether the tooltip is disabled
     */
    disabled?: boolean;

    /**
     * Whether the tooltip content is interactive (allows pointer events)
     */
    interactive?: boolean;

    /**
     * Controlled visibility state (used with trigger='manual')
     */
    visible?: boolean;

    /**
     * Default visibility for uncontrolled state
     */
    defaultVisible?: boolean;

    /**
     * Callback when visibility changes
     */
    onOpenChange?: (open: boolean) => void;

    /**
     * The element that triggers the tooltip
     */
    children: ReactElement;

    /**
     * Optional class name for the tooltip container
     */
    className?: string;
}
