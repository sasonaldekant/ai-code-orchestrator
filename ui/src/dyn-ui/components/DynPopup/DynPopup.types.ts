import { ReactNode, CSSProperties } from 'react';

export type DynPopupPlacement =
    | 'top-start' | 'top-end' | 'bottom-start' | 'bottom-end'
    | 'left-start' | 'left-end' | 'right-start' | 'right-end';

export interface DynPopupItem {
    id: string;
    label: string;
    icon?: ReactNode;
    disabled?: boolean;
    danger?: boolean;
    onClick?: () => void;
    divider?: boolean;
}

export interface DynPopupProps {
    /**
     * The element that triggers the popup.
     * If not provided, a default "More" icon button will be used.
     */
    trigger?: ReactNode;

    /**
     * List of action items to display in the popup menu.
     */
    items?: DynPopupItem[];

    /**
     * Custom content to render inside the popup.
     * If provided, `items` prop is ignored.
     */
    children?: ReactNode;

    /**
     * Whether the popup is open (controlled).
     */
    open?: boolean;

    /**
     * Initial open state (uncontrolled).
     */
    defaultOpen?: boolean;

    /**
     * Callback when open state changes.
     */
    onOpenChange?: (open: boolean) => void;

    /**
     * Preferred placement of the popup relative to the trigger.
     * @default 'bottom-end'
     */
    placement?: DynPopupPlacement;

    /**
     * Distance in pixels from the sidebar/trigger.
     * @default 4
     */
    offset?: number;

    /**
     * Whether to display the popup using a React Portal.
     * @default true
     */
    usePortal?: boolean;

    /**
     * Optional container to portal the popup into.
     * Defaults to document.body, but can be set for scoped styling.
     */
    container?: HTMLElement | null;

    /**
     * Additional class name for the popup container.
     */
    className?: string;

    /**
     * Inline styles for the popup container.
     */
    style?: CSSProperties;

    /**
     * ID for accessibility.
     */
    id?: string;

    /**
     * Aria label for the popup menu.
     */
    'aria-label'?: string;
}
