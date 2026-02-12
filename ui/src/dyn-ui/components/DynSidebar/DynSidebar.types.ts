import type { BaseComponentProps } from '../../types';

export interface DynSidebarItem {
    id: string;
    label: string;
    icon?: string | React.ReactNode;
    onClick?: () => void;
    disabled?: boolean;
}

export interface DynSidebarProps extends BaseComponentProps {
    /** Items to display in the main content area */
    items?: DynSidebarItem[];
    /** Items to display in the footer area */
    footerItems?: DynSidebarItem[];
    /** Header content */
    header?: React.ReactNode;
    /** Whether the sidebar is collapsed */
    collapsed?: boolean;
    /** Callback when collapse state changes */
    onCollapseChange?: (collapsed: boolean) => void;
    /** Currently active item ID */
    activeId?: string;
    /** Whether the sidebar is open on mobile */
    open?: boolean;
    /** Callback when open state changes on mobile */
    onOpenChange?: (open: boolean) => void;
    /** Callback when an item is clicked */
    onItemClick?: (item: DynSidebarItem) => void;
}
