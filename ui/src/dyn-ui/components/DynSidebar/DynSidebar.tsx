import React, { forwardRef } from 'react';
import { cn } from '../../utils/classNames';
import styles from './DynSidebar.module.css';
import type { DynSidebarProps, DynSidebarItem } from './DynSidebar.types';
import { DynIcon } from '../DynIcon';

/**
 * DynSidebar Component
 * A robust navigation sidebar with support for collapse/expand and mobile responsiveness.
 */
export const DynSidebar = forwardRef<HTMLElement, DynSidebarProps>(
    (
        {
            items = [],
            footerItems = [],
            header,
            collapsed = false,
            onCollapseChange,
            activeId,
            open = false,
            onOpenChange,
            onItemClick,
            className,
            style,
            ...rest
        },
        ref
    ) => {
        const renderItem = (item: DynSidebarItem) => {
            const isActive = activeId === item.id;
            return (
                <button
                    key={item.id}
                    type="button"
                    className={cn(styles.item, isActive && styles.itemActive)}
                    onClick={() => {
                        item.onClick?.();
                        onItemClick?.(item);
                    }}
                    disabled={item.disabled}
                    title={collapsed ? item.label : undefined}
                    aria-label={item.label}
                >
                    {item.icon && (
                        <div className={styles.icon}>
                            {typeof item.icon === 'string' ? (
                                <DynIcon icon={item.icon} size="md" />
                            ) : (
                                item.icon
                            )}
                        </div>
                    )}
                    {!collapsed && <span className={styles.label}>{item.label}</span>}
                </button>
            );
        };

        return (
            <aside
                ref={ref}
                className={cn(
                    styles.container,
                    collapsed && styles.collapsed,
                    open && styles.open,
                    className
                )}
                style={style}
                {...rest}
            >
                {header && <div className={styles.header}>{header}</div>}

                <nav className={styles.content}>
                    {items.map(renderItem)}
                </nav>

                {(footerItems.length > 0) && (
                    <div className={styles.footer}>
                        {footerItems.map(renderItem)}
                    </div>
                )}
            </aside>
        );
    }
);

DynSidebar.displayName = 'DynSidebar';

export default DynSidebar;
