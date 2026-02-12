import React, { useState, forwardRef } from 'react';
import { cn } from '../../utils/classNames';
import { DynAccordionProps, DYN_ACCORDION_DEFAULT_PROPS } from './DynAccordion.types';
import { DynAccordionItem } from './DynAccordionItem';
import styles from './DynAccordion.module.css';

export const DynAccordion = forwardRef<HTMLDivElement, DynAccordionProps>((
    {
        items,
        multiple = DYN_ACCORDION_DEFAULT_PROPS.multiple,
        defaultExpanded = DYN_ACCORDION_DEFAULT_PROPS.defaultExpanded,
        expanded: controlledExpanded,
        onChange,
        className,
        variant = DYN_ACCORDION_DEFAULT_PROPS.variant,
        size = DYN_ACCORDION_DEFAULT_PROPS.size,
        loading = false,
        expandIcon,
        id,
        style,
        'data-testid': dataTestId,
        ...rest
    },
    ref
) => {
    const [internalExpanded, setInternalExpanded] = useState<string[]>(defaultExpanded ?? []);

    const isControlled = controlledExpanded !== undefined;
    const expandedIds = isControlled ? controlledExpanded : internalExpanded;

    const handleToggle = (id: string) => {
        let newExpanded: string[];

        if (expandedIds.includes(id)) {
            newExpanded = expandedIds.filter((itemId) => itemId !== id);
        } else {
            newExpanded = multiple ? [...expandedIds, id] : [id];
        }

        if (!isControlled) {
            setInternalExpanded(newExpanded);
        }

        onChange?.(newExpanded);
    };

    return (
        <div
            ref={ref}
            id={id}
            style={style}
            data-testid={dataTestId || 'dyn-accordion'}
            className={cn(
                styles.accordion,
                { [styles.accordionBordered]: variant === 'bordered' },
                className
            )}
            {...rest}
        >
            {items.map((item) => (
                <DynAccordionItem
                    key={item.id}
                    {...item}
                    variant={variant}
                    size={size}
                    expandIcon={expandIcon}
                    loading={loading || item.loading}
                    isExpanded={expandedIds.includes(item.id)}
                    onToggle={() => handleToggle(item.id)}
                />
            ))}
        </div>
    );
});

DynAccordion.displayName = 'DynAccordion';
