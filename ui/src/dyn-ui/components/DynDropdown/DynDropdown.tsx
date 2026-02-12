import React, {
    forwardRef,
    useImperativeHandle,
    useRef,
    useState,
    useEffect,
    useCallback,
    useId,
} from 'react';
import { createPortal } from 'react-dom';
import { cn } from '../../utils/classNames';
import type {
    DynDropdownProps,
    DynDropdownRef,
    DynDropdownItem,
    DynDropdownPlacement
} from './DynDropdown.types';
import { DYN_DROPDOWN_DEFAULT_PROPS } from './DynDropdown.types';
import styles from './DynDropdown.module.css';

export const DynDropdown = forwardRef<DynDropdownRef, DynDropdownProps>(
    (
        {
            trigger,
            items = [],
            isOpen: isOpenProp,
            defaultOpen = false,
            onOpenChange,
            placement = DYN_DROPDOWN_DEFAULT_PROPS.placement,
            offset = DYN_DROPDOWN_DEFAULT_PROPS.offset,
            closeOnItemClick = DYN_DROPDOWN_DEFAULT_PROPS.closeOnItemClick,
            closeOnOutsideClick = DYN_DROPDOWN_DEFAULT_PROPS.closeOnOutsideClick,
            triggerType = DYN_DROPDOWN_DEFAULT_PROPS.triggerType,
            onItemClick,
            children,
            usePortal = DYN_DROPDOWN_DEFAULT_PROPS.usePortal,
            disabled = false,
            className,

            style,
            id,
            'aria-label': ariaLabel,
            'data-testid': dataTestId = 'dyn-dropdown',
            triggerWrapper = 'button',
            triggerRole,
            fullWidth = false,
        },

        ref
    ) => {
        const [internalOpen, setInternalOpen] = useState(defaultOpen);
        const isOpen = isOpenProp !== undefined ? isOpenProp : internalOpen;

        const triggerRef = useRef<HTMLButtonElement | HTMLDivElement>(null);
        const menuRef = useRef<HTMLDivElement>(null);
        const [coords, setCoords] = useState({ top: 0, left: 0 });
        const componentId = id || useId();

        const updatePosition = useCallback(() => {
            if (!triggerRef.current || !isOpen) return;

            const triggerRect = triggerRef.current.getBoundingClientRect();
            const { top, left, width, height } = triggerRect;
            let menuTop = 0;
            let menuLeft = 0;

            // Basic positioning logic based on placement
            // This is a simplified version of what floating-ui does
            switch (placement) {
                case 'bottom-start':
                    menuTop = top + height + offset;
                    menuLeft = left;
                    break;
                case 'bottom-end':
                    menuTop = top + height + offset;
                    menuLeft = left + width; // Needs adjustment based on menu width later
                    break;
                case 'top-start':
                    menuTop = top - offset; // Needs adjustment based on menu height later
                    menuLeft = left;
                    break;
                case 'top-end':
                    menuTop = top - offset;
                    menuLeft = left + width;
                    break;
                default:
                    menuTop = top + height + offset;
                    menuLeft = left;
            }

            setCoords({ top: menuTop + window.scrollY, left: menuLeft + window.scrollX });
        }, [isOpen, offset, placement]);

        const handleOpenChange = useCallback((open: boolean) => {
            setInternalOpen(open);
            onOpenChange?.(open);
        }, [onOpenChange]);

        const toggle = useCallback(() => {
            handleOpenChange(!isOpen);
        }, [handleOpenChange, isOpen]);

        useImperativeHandle(ref, () => ({
            open: () => handleOpenChange(true),
            close: () => handleOpenChange(false),
            toggle,
            getElement: () => menuRef.current,
        }), [handleOpenChange, toggle]);

        // Handle outside click
        useEffect(() => {
            if (!isOpen || !closeOnOutsideClick) return;

            const handleClickOutside = (event: MouseEvent) => {
                if (
                    triggerRef.current && !triggerRef.current.contains(event.target as Node) &&
                    menuRef.current && !menuRef.current.contains(event.target as Node)
                ) {
                    handleOpenChange(false);
                }
            };

            document.addEventListener('mousedown', handleClickOutside);
            return () => document.removeEventListener('mousedown', handleClickOutside);
        }, [isOpen, closeOnOutsideClick, handleOpenChange]);

        // Update position when open or resizing
        useEffect(() => {
            if (isOpen) {
                updatePosition();
                window.addEventListener('resize', updatePosition);
                window.addEventListener('scroll', updatePosition, true);
            }
            return () => {
                window.removeEventListener('resize', updatePosition);
                window.removeEventListener('scroll', updatePosition, true);
            };
        }, [isOpen, updatePosition]);

        const handleItemClick = (item: DynDropdownItem, e: React.MouseEvent) => {
            if (item.disabled) return;

            onItemClick?.(item, e);
            item.onClick?.(item, e);

            if (closeOnItemClick) {
                handleOpenChange(false);
            }
        };

        const renderItems = () => {
            if (children) return children;

            return items.map((item, index) => {
                if (item.type === 'divider') {
                    return <div key={`divider-${index}`} className={styles.divider} role="separator" />;
                }

                return (
                    <button
                        key={item.id}
                        type="button"
                        className={cn(styles.item, item.className, item.id === 'active' && styles.itemActive)}
                        onClick={(e) => handleItemClick(item, e)}
                        disabled={item.disabled}
                        role="menuitem"
                    >
                        {item.icon && <span className={styles.itemIcon}>{item.icon}</span>}
                        <span className={styles.itemLabel}>{item.label}</span>
                    </button>
                );
            });
        };

        const menuContent = (
            <div
                ref={menuRef}
                id={`${componentId}-menu`}
                className={cn(styles.menu, isOpen && styles.menuOpen)}
                style={{
                    top: coords.top,
                    left: coords.left,
                    position: 'absolute', // We use absolute with scrollY/X added
                    ...style
                }}
                role="menu"
                aria-label={ariaLabel}
                data-testid={`${dataTestId}-menu`}
            >
                {renderItems()}
            </div>
        );

        return (
            <div className={cn(styles.container, fullWidth && styles.containerBlock, className)} data-testid={dataTestId}>
                {triggerWrapper === 'button' ? (
                    <button
                        ref={triggerRef as React.RefObject<HTMLButtonElement>}
                        type="button"
                        className={styles.trigger}
                        onClick={!disabled && triggerType === 'click' ? toggle : undefined}
                        onMouseEnter={!disabled && triggerType === 'hover' ? () => handleOpenChange(true) : undefined}
                        aria-haspopup="true"
                        aria-expanded={isOpen}
                        aria-controls={`${componentId}-menu`}
                        aria-label={ariaLabel}
                        disabled={disabled}
                    >
                        {trigger}
                    </button>
                ) : (
                    <div
                        ref={triggerRef as React.RefObject<HTMLDivElement>}
                        className={styles.trigger}
                        onClick={!disabled && triggerType === 'click' ? toggle : undefined}
                        onMouseEnter={!disabled && triggerType === 'hover' ? () => handleOpenChange(true) : undefined}
                        role={triggerRole ?? 'button'}
                        tabIndex={triggerRole === 'presentation' || triggerRole === 'none' ? undefined : (disabled ? -1 : 0)}
                        aria-haspopup={triggerRole === 'presentation' || triggerRole === 'none' ? undefined : "true"}
                        aria-expanded={triggerRole === 'presentation' || triggerRole === 'none' ? undefined : isOpen}
                        aria-controls={triggerRole === 'presentation' || triggerRole === 'none' ? undefined : `${componentId}-menu`}
                        aria-label={ariaLabel}
                    >
                        {trigger}
                    </div>
                )}



                {isOpen && (usePortal ? createPortal(menuContent, document.body) : menuContent)}
            </div>
        );
    }
);

DynDropdown.displayName = 'DynDropdown';
