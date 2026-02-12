import React, { useState, useRef, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '../../utils/classNames';
import { DynTooltipProps } from './DynTooltip.types';
import styles from './DynTooltip.module.css';

/**
 * DynTooltip Component
 * Optimized with Design Tokens & CSS Modules
 */
export const DynTooltip: React.FC<DynTooltipProps> = ({
    content,
    position = 'top',
    trigger = 'hover',
    delay = 200,
    disabled = false,
    interactive = false,
    visible: controlledVisible,
    defaultVisible = false,
    onOpenChange,
    children,
    className,
}) => {
    const [uncontrolledVisible, setUncontrolledVisible] = useState(defaultVisible);
    const isControlled = controlledVisible !== undefined;
    const isVisible = (isControlled ? controlledVisible : uncontrolledVisible) && !disabled;

    const [coords, setCoords] = useState({ top: 0, left: 0 });

    const timeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);
    const triggerRef = useRef<HTMLDivElement>(null);
    const tooltipRef = useRef<HTMLDivElement>(null);

    const setVisible = useCallback(
        (value: boolean) => {
            if (!isControlled) {
                setUncontrolledVisible(value);
            }
            onOpenChange?.(value);
        },
        [isControlled, onOpenChange]
    );

    const updatePosition = useCallback(() => {
        if (!triggerRef.current || !tooltipRef.current) return;

        const triggerRect = triggerRef.current.getBoundingClientRect();
        const tooltipRect = tooltipRef.current.getBoundingClientRect();

        let top = 0;
        let left = 0;
        const gap = 8; // distance from trigger

        switch (position) {
            case 'top':
                top = triggerRect.top - tooltipRect.height - gap;
                left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
                break;
            case 'bottom':
                top = triggerRect.bottom + gap;
                left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
                break;
            case 'left':
                top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
                left = triggerRect.left - tooltipRect.width - gap;
                break;
            case 'right':
                top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
                left = triggerRect.right + gap;
                break;
        }

        setCoords({ top, left });
    }, [position]);

    const handleOpen = () => {
        if (disabled) return;
        if (timeoutRef.current) clearTimeout(timeoutRef.current);

        timeoutRef.current = setTimeout(() => {
            setVisible(true);
            requestAnimationFrame(updatePosition);
        }, delay);
    };

    const handleClose = () => {
        if (timeoutRef.current) clearTimeout(timeoutRef.current);

        if (interactive) {
            timeoutRef.current = setTimeout(() => {
                setVisible(false);
            }, 200); // Small grace period to move mouse to tooltip
        } else {
            setVisible(false);
        }
    };

    const toggleOpen = () => {
        if (isVisible) handleClose();
        else handleOpen();
    };

    // Event handlers based on trigger type
    const handlers: Record<string, any> = {};

    if (trigger === 'hover') {
        handlers.onMouseEnter = handleOpen;
        handlers.onMouseLeave = handleClose;
        handlers.onFocus = handleOpen;
        handlers.onBlur = handleClose;
    } else if (trigger === 'click') {
        handlers.onClick = toggleOpen;
    } else if (trigger === 'focus') {
        handlers.onFocus = handleOpen;
        handlers.onBlur = handleClose;
    }

    // Recalculate position on scroll or resize when visible
    useEffect(() => {
        if (isVisible) {
            window.addEventListener('scroll', updatePosition, true);
            window.addEventListener('resize', updatePosition);
            // Initial positioning
            requestAnimationFrame(updatePosition);
        }

        return () => {
            window.removeEventListener('scroll', updatePosition, true);
            window.removeEventListener('resize', updatePosition);
        };
    }, [isVisible, updatePosition]);

    // Handle interactive tooltip (hovering the tooltip itself keeps it open)
    const tooltipHandlers =
        interactive && trigger === 'hover'
            ? {
                onMouseEnter: () => {
                    if (timeoutRef.current) clearTimeout(timeoutRef.current);
                },
                onMouseLeave: handleClose,
            }
            : {};

    return (
        <>
            <div ref={triggerRef} className={styles.tooltipContainer} {...handlers}>
                {children}
            </div>

            {isVisible &&
                createPortal(
                    <div
                        ref={tooltipRef}
                        className={cn(
                            styles.tooltip,
                            styles.tooltipVisible,
                            interactive && styles.interactive,
                            className
                        )}
                        style={{
                            top: coords.top,
                            left: coords.left,
                        }}
                        role="tooltip"
                        {...tooltipHandlers}
                    >
                        {content}
                    </div>,
                    document.body
                )}
        </>
    );
};

DynTooltip.displayName = 'DynTooltip';
