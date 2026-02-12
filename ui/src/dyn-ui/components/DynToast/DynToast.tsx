/**
 * DynToast Component
 *
 * Individual toast notification component.
 * Features customizable content, icons, generic actions, and animations.
 *
 * Token Compliant: ✅ Full --dyn-toast-* pattern
 */

import React, { useEffect } from 'react';
import { cn } from '../../utils/classNames';
import { DynIcon } from '../DynIcon';
import { DynButton } from '../DynButton';
import { DynToastProps } from './DynToast.types';
import styles from './DynToast.module.css';

const DEFAULT_ICONS = {
    success: 'ok',
    error: 'warning', // Warning icon is a triangle with !, suitable for error too
    warning: 'warning',
    info: 'info',
    default: 'notifications',
};

export const DynToast: React.FC<DynToastProps> = ({
    toast,
    onClose,
    position = 'top-right',
    className,
    ...rest
}) => {
    const { id, type, message, description, duration, action } = toast;

    // Auto-close logic handled by effect
    useEffect(() => {
        if (duration !== 0 && duration !== Infinity) {
            const timer = setTimeout(() => {
                onClose(id);
            }, duration || 5000); // Default 5s
            return () => clearTimeout(timer);
        }
    }, [id, duration, onClose]);

    const typeClass = `toast${type.charAt(0).toUpperCase()}${type.slice(1)}`;
    const positionClass = `toast${position.replace(/-([a-z])/g, (g) => g[1].toUpperCase()).replace(/^([a-z])/, (c) => c.toUpperCase())}`;
    // e.g. top-right -> ToastTopRight (fix later in CSS, for now just use data attr or standard class)

    // We actually put position on the container, not the toast itself usually.
    // But here we might want animation direction.

    return (
        <div
            className={cn(styles.toast, styles[typeClass], className)}
            role="alert"
            data-position={position}
            data-type={type}
            {...rest}
        >
            <div className={styles.toastIcon}>
                <DynIcon icon={DEFAULT_ICONS[type]} />
            </div>

            <div className={styles.toastContent}>
                <div className={styles.toastMessage}>{message}</div>
                {description && <div className={styles.toastDescription}>{description}</div>}
            </div>

            <div className={styles.toastActions}>
                {action && (
                    <DynButton
                        size="sm"
                        kind="tertiary"
                        className={styles.toastActionButton}
                        onClick={(e) => {
                            e.stopPropagation();
                            action.onClick();
                        }}
                        label={action.label}
                    />
                )}

                <button
                    className={styles.toastCloseButton}
                    onClick={(e) => {
                        e.stopPropagation();
                        onClose(id);
                    }}
                    aria-label="Close notification"
                >
                    <DynIcon icon="close" size="sm" />
                </button>
            </div>

            {/* Progress bar for auto-dismiss could be added here */}
        </div>
    );
};

export default DynToast;
