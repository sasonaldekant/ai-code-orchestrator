import React, { useState, useRef, useEffect, useCallback, useId } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '../../utils/classNames';
import { DynIcon } from '../DynIcon';
import { DynPopupProps } from './DynPopup.types';
import styles from './DynPopup.module.css';

/**
 * DynPopup Component
 * A lightweight popup menu for actions and navigation.
 * Standardized to 3-Layer Architecture.
 */
export const DynPopup: React.FC<DynPopupProps> = ({
    trigger,
    items = [],
    children,
    open: controlledOpen,
    defaultOpen = false,
    onOpenChange,
    placement = 'bottom-end',
    offset = 4,
    usePortal = true,
    container,
    className,
    style,
    id,
    'aria-label': ariaLabel,
}) => {
    const [internalOpen, setInternalOpen] = useState(defaultOpen);
    const isOpen = controlledOpen !== undefined ? controlledOpen : internalOpen;

    const triggerRef = useRef<HTMLDivElement>(null);
    const popupRef = useRef<HTMLDivElement>(null);
    const [coords, setCoords] = useState({ top: 0, left: 0 });

    const componentId = id || useId();

    const handleOpenChange = useCallback(
        (newOpen: boolean) => {
            if (controlledOpen === undefined) {
                setInternalOpen(newOpen);
            }
            onOpenChange?.(newOpen);
        },
        [controlledOpen, onOpenChange]
    );

    const updatePosition = useCallback(() => {
        if (!triggerRef.current || !isOpen) return;

        const triggerRect = triggerRef.current.getBoundingClientRect();
        const popupRect = popupRef.current?.getBoundingClientRect() || { width: 0, height: 0 };

        let top = 0;
        let left = 0;
        const scrollX = window.scrollX;
        const scrollY = window.scrollY;

        // Simplified positioning logic (Gold Standard approach)
        switch (placement) {
            case 'bottom-start':
                top = triggerRect.bottom + offset;
                left = triggerRect.left;
                break;
            case 'bottom-end':
                top = triggerRect.bottom + offset;
                left = triggerRect.right - popupRect.width;
                break;
            case 'top-start':
                top = triggerRect.top - popupRect.height - offset;
                left = triggerRect.left;
                break;
            case 'top-end':
                top = triggerRect.top - popupRect.height - offset;
                left = triggerRect.right - popupRect.width;
                break;
            case 'left-start':
                top = triggerRect.top;
                left = triggerRect.left - popupRect.width - offset;
                break;
            case 'right-start':
                top = triggerRect.top;
                left = triggerRect.right + offset;
                break;
            default:
                // Fallback to bottom-end
                top = triggerRect.bottom + offset;
                left = triggerRect.right - popupRect.width;
        }

        setCoords({
            top: top + scrollY,
            left: left + scrollX,
        });
    }, [isOpen, placement, offset]);

    // Handle outside click
    useEffect(() => {
        if (!isOpen) return;

        const handleClickOutside = (event: MouseEvent) => {
            const target = event.target as Node;
            if (
                triggerRef.current &&
                !triggerRef.current.contains(target) &&
                popupRef.current &&
                !popupRef.current.contains(target)
            ) {
                handleOpenChange(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [isOpen, handleOpenChange]);

    // Update position on render/resize
    useEffect(() => {
        if (isOpen) {
            updatePosition();
            // Small delay to ensure popup dimensions are ready
            const timer = setTimeout(updatePosition, 0);

            window.addEventListener('resize', updatePosition);
            window.addEventListener('scroll', updatePosition, true);

            return () => {
                clearTimeout(timer);
                window.removeEventListener('resize', updatePosition);
                window.removeEventListener('scroll', updatePosition, true);
            };
        }
    }, [isOpen, updatePosition]);

    const renderContent = () => {
        if (children) return children;

        return items.map((item) => {
            if (item.divider) {
                return <div key={item.id} className={styles.divider} role="separator" />;
            }

            return (
                <button
                    key={item.id}
                    className={cn(styles.item, {
                        [styles.itemDisabled]: item.disabled,
                        [styles.itemDanger]: item.danger,
                    })}
                    disabled={item.disabled}
                    onClick={() => {
                        item.onClick?.();
                        handleOpenChange(false);
                    }}
                    type="button"
                    role="menuitem"
                >
                    {item.icon && (
                        <span className={styles.icon}>
                            {typeof item.icon === 'string' ? <DynIcon icon={item.icon} size="sm" /> : item.icon}
                        </span>
                    )}
                    {item.label}
                </button>
            );
        });
    };

    const menu = (
        <div
            ref={popupRef}
            id={`${componentId}-menu`}
            className={cn(styles.popup, { [styles.popupOpen]: isOpen }, className)}
            style={{
                ...style,
                top: coords.top,
                left: coords.left,
            }}
            role="menu"
            aria-label={ariaLabel}
            aria-hidden={!isOpen}
        >
            {renderContent()}
        </div>
    );

    return (
        <>
            <div
                ref={triggerRef}
                className={styles.trigger}
                onClick={() => handleOpenChange(!isOpen)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        handleOpenChange(!isOpen);
                    }
                }}
                aria-haspopup="true"
                aria-expanded={isOpen}
                aria-controls={`${componentId}-menu`}
            >
                {trigger || (
                    // Default trigger: Vertical dots (Kebab) using DynIcon
                    <DynIcon icon="more-vertical" />
                )}
            </div>

            {usePortal ? createPortal(menu, container || document.body) : menu}
        </>
    );
};

DynPopup.displayName = 'DynPopup';

export default DynPopup;
