import type { BaseComponentProps, AccessibilityProps, SizeProps } from '../../types';
import type { ReactNode } from 'react';

export interface AccordionItem {
    id: string;
    title: ReactNode;
    content: ReactNode;
    disabled?: boolean;
    /**
     * Optional icon to display for this item (replaces default chevron)
     */
    icon?: ReactNode;
    /**
     * Whether the item is in a loading state
     */
    loading?: boolean;
}

export interface DynAccordionProps extends BaseComponentProps, AccessibilityProps, SizeProps {
    /**
     * Array of accordion items
     */
    items: AccordionItem[];

    /**
     * Whether multiple items can be expanded simultaneously
     * @default false
     */
    multiple?: boolean;

    /**
     * IDs of items that are expanded by default
     */
    defaultExpanded?: string[];

    /**
     * Controlled expanded items IDs
     */
    expanded?: string[];

    /**
     * Callback when expanded items change
     */
    onChange?: (expandedIds: string[]) => void;

    /**
     * Variant for styling
     * @default 'default'
     */
    variant?: 'default' | 'bordered';

    /**
     * Whether the entire accordion is in a loading state
     */
    loading?: boolean;

    /**
     * Optional default icon for all items
     */
    expandIcon?: ReactNode;
}

/**
 * Default props for DynAccordion component
 */
export const DYN_ACCORDION_DEFAULT_PROPS: Partial<DynAccordionProps> = {
    multiple: false,
    variant: 'default',
    defaultExpanded: [],
    size: 'md',
};

export interface DynAccordionItemProps extends AccordionItem {
    isExpanded: boolean;
    onToggle: () => void;
    variant?: 'default' | 'bordered';
    size?: DynAccordionProps['size'];
    expandIcon?: ReactNode;
}
