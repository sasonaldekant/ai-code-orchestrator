/**
 * DynToast Component Types
 *
 * Type definitions for toast notifications.
 * Token Compliant: ✅ Full --dyn-toast-* pattern
 *
 * @module DynToast
 * @version 1.0.0
 */

import { HTMLAttributes, ReactNode } from 'react';

/**
 * Toast types / severities
 */
export type DynToastType = 'success' | 'error' | 'warning' | 'info' | 'default';

/**
 * Toast position on screen
 */
export type DynToastPosition = 'top-left' | 'top-right' | 'top-center' | 'bottom-left' | 'bottom-right' | 'bottom-center';

/**
 * Single Toast Item Data
 */
export interface DynToastItem {
    id: string;
    type: DynToastType;
    message: ReactNode;
    description?: ReactNode;
    duration?: number; // 0 for infinite
    position?: DynToastPosition;
    onClose?: () => void;
    action?: {
        label: string;
        onClick: () => void;
    };
}

/**
 * Props for the single toast component
 */
export interface DynToastProps extends Omit<HTMLAttributes<HTMLDivElement>, 'id'> {
    toast: DynToastItem;
    onClose: (id: string) => void;
    position?: DynToastPosition;
}

/**
 * Toast Context Interface
 */
export interface DynToastContextType {
    toasts: DynToastItem[];
    addToast: (toast: Omit<DynToastItem, 'id'>) => string;
    removeToast: (id: string) => void;
    updateToast: (id: string, updates: Partial<DynToastItem>) => void;

    // Helpers
    success: (message: ReactNode, options?: Partial<DynToastItem>) => string;
    error: (message: ReactNode, options?: Partial<DynToastItem>) => string;
    warning: (message: ReactNode, options?: Partial<DynToastItem>) => string;
    info: (message: ReactNode, options?: Partial<DynToastItem>) => string;
}

/**
 * Toast Provider Props
 */
export interface DynToastProviderProps {
    children: ReactNode;
    defaultDuration?: number;
    defaultPosition?: DynToastPosition;
    maxToasts?: number;
}
