/**
 * DynToast Context & Provider
 *
 * Manages the state of toast notifications and renders them via React Portal.
 */

import React, { createContext, useContext, useState, useCallback, useRef, ReactNode } from 'react';
import { createPortal } from 'react-dom';
import { DynToast } from './DynToast';
import {
    DynToastContextType,
    DynToastItem,
    DynToastProviderProps,
    DynToastPosition
} from './DynToast.types';
import styles from './DynToast.module.css';

// Context
const ToastContext = createContext<DynToastContextType | undefined>(undefined);

// Hook
export const useToast = () => {
    const context = useContext(ToastContext);
    if (!context) {
        throw new Error('useToast must be used within a DynToastProvider');
    }
    return context;
};

// Provider
export const DynToastProvider: React.FC<DynToastProviderProps> = ({
    children,
    defaultDuration = 5000,
    defaultPosition = 'top-right',
    maxToasts = 5,
}) => {
    const [toasts, setToasts] = useState<DynToastItem[]>([]);
    const portalRef = useRef<HTMLElement | null>(null);

    // Initialize portal container
    if (!portalRef.current && typeof document !== 'undefined') {
        let el = document.getElementById('dyn-toast-portal');
        if (!el) {
            el = document.createElement('div');
            el.id = 'dyn-toast-portal';
            document.body.appendChild(el);
        }
        portalRef.current = el;
    }

    const removeToast = useCallback((id: string) => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
    }, []);

    const addToast = useCallback((toast: Omit<DynToastItem, 'id'>) => {
        const id = Math.random().toString(36).substr(2, 9);
        const newToast: DynToastItem = {
            id,
            duration: defaultDuration,
            position: defaultPosition,
            ...toast,
        };

        setToasts((prev) => {
            // Filter by position to manage maxToasts per position effectively, 
            // or global maxToasts. Here implemented as global maxToasts.
            // If we want maxToasts per position, logic would be more complex.
            // Simple LIFO/FIFO logic:
            const filtered = prev.length >= maxToasts ? prev.slice(1) : prev;
            return [...filtered, newToast];
        });

        return id;
    }, [defaultDuration, defaultPosition, maxToasts]);

    const updateToast = useCallback((id: string, updates: Partial<DynToastItem>) => {
        setToasts((prev) => prev.map((t) => (t.id === id ? { ...t, ...updates } : t)));
    }, []);

    // Helpers
    const helpers = {
        success: (message: ReactNode, options?: Partial<DynToastItem>) =>
            addToast({ type: 'success', message, ...options }),
        error: (message: ReactNode, options?: Partial<DynToastItem>) =>
            addToast({ type: 'error', message, ...options }),
        warning: (message: ReactNode, options?: Partial<DynToastItem>) =>
            addToast({ type: 'warning', message, ...options }),
        info: (message: ReactNode, options?: Partial<DynToastItem>) =>
            addToast({ type: 'info', message, ...options }),
    };

    // Group toasts by position for rendering
    const toastsByPosition = toasts.reduce((acc, toast) => {
        const pos = toast.position || defaultPosition;
        if (!acc[pos]) acc[pos] = [];
        acc[pos].push(toast);
        return acc;
    }, {} as Record<DynToastPosition, DynToastItem[]>);

    return (
        <ToastContext.Provider value={{ toasts, addToast, removeToast, updateToast, ...helpers }}>
            {children}
            {portalRef.current && createPortal(
                <>
                    {Object.entries(toastsByPosition).map(([pos, positionToasts]) => (
                        <div key={pos} className={`${styles.toastContainer} ${styles[camelCasePosition(pos)]}`}>
                            {positionToasts.map((toast) => (
                                <DynToast
                                    key={toast.id}
                                    toast={toast}
                                    onClose={removeToast}
                                    position={pos as DynToastPosition}
                                />
                            ))}
                        </div>
                    ))}
                </>,
                portalRef.current
            )}
        </ToastContext.Provider>
    );
};

// Helper to convert top-right to toastTopRight for CSS modules
function camelCasePosition(pos: string) {
    return 'toastContainer' + pos.split('-').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join('');
}
