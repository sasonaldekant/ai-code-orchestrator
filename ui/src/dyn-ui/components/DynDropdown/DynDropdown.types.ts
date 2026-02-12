import type { ReactNode, MouseEvent } from 'react';
import type { BaseComponentProps, AccessibilityProps } from '../../types';

export type DynDropdownPlacement =
    | 'bottom-start'
    | 'bottom-end'
    | 'top-start'
    | 'top-end'
    | 'left-start'
    | 'right-start';

export type DynDropdownTriggerType = 'click' | 'hover';

export interface DynDropdownItem {
    /** Unique identifier for the item */
    id: string;
    /** Primary text to display */
    label?: ReactNode;
    /** Optional icon to display before label */
    icon?: ReactNode;
    /** Whether the item is disabled */
    disabled?: boolean;
    /** Item type */
    type?: 'item' | 'divider';
    /** Custom data associated with item */
    data?: any;
    /** Custom class for the item */
    className?: string;
    /** Click handler for this specific item */
    onClick?: (item: DynDropdownItem, e: MouseEvent) => void;
}

export interface DynDropdownProps extends BaseComponentProps, AccessibilityProps {
    /** The element that triggers the dropdown */
    trigger: ReactNode;

    /** Array of menu items */
    items?: DynDropdownItem[];

    /** Controlled open state */
    isOpen?: boolean;

    /** Uncontrolled default open state */
    defaultOpen?: boolean;

    /** Callback when open state changes */
    onOpenChange?: (open: boolean) => void;

    /** Placement of the dropdown relative to trigger */
    placement?: DynDropdownPlacement;

    /** Gap between trigger and dropdown in pixels */
    offset?: number;

    /** Whether to close the dropdown when an item is clicked */
    closeOnItemClick?: boolean;

    /** Whether to close the dropdown when clicking outside */
    closeOnOutsideClick?: boolean;

    /** How the dropdown is triggered */
    triggerType?: DynDropdownTriggerType;

    /** Callback when an item is clicked */
    onItemClick?: (item: DynDropdownItem, e: MouseEvent) => void;

    /** Custom content if items are not used */
    children?: ReactNode;

    /** Whether to render in a portal (default: true) */
    usePortal?: boolean;

    /** Disabled state */
    disabled?: boolean;

    /**
     * DOM element to wrap the trigger with.
     * Use 'div' if the trigger contains interactive elements like inputs.
     * Default: 'button'
     */
    triggerWrapper?: 'button' | 'div';

    /**
     * Optional ARIA role for the trigger wrapper.
     * Defaults to 'button' when triggerWrapper is 'div'.
     * Set to 'presentation' or 'none' if the trigger contains interactive elements.
     */
    triggerRole?: string;

    /**
     * Whether the dropdown container should take up the full width of its parent.
     * Useful for form fields like DatePicker.
     */
    fullWidth?: boolean;
}


export interface DynDropdownRef {
    /** Programmatically open the dropdown */
    open: () => void;
    /** Programmatically close the dropdown */
    close: () => void;
    /** Toggle the dropdown state */
    toggle: () => void;
    /** Get the dropdown element */
    getElement: () => HTMLDivElement | null;
}

export const DYN_DROPDOWN_DEFAULT_PROPS = {
    placement: 'bottom-start',
    offset: 8,
    closeOnItemClick: true,
    closeOnOutsideClick: true,
    triggerType: 'click',
    usePortal: true,
} as const;
