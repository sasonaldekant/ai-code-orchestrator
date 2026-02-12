import type { ReactNode } from 'react';
import type { BaseComponentProps, AccessibilityProps } from '../../types';

export type DynModalSize = 'sm' | 'md' | 'lg' | 'full';

/**
 * Ref type for DynModal component
 */
export type DynModalRef = HTMLDivElement;

export interface DynModalProps extends BaseComponentProps, AccessibilityProps {
    /** If true, the modal is displayed. */
    isOpen: boolean;

    /** Title of the modal. */
    title?: ReactNode;

    /** Callback fired when the modal requests to be closed. */
    onClose: () => void;

    /** Children to render inside the modal body. */
    children: ReactNode;

    /** Optional footer content. */
    footer?: ReactNode;

    /** Size of the modal. */
    size?: DynModalSize;

    /** If true, the modal will span the entire screen. */
    fullscreen?: boolean;

    /** If true, the modal will be vertically and horizontally centered. */
    centered?: boolean;

    /** If true, clicking on the backdrop will call onClose. */
    closeOnBackdropClick?: boolean;

    /** If true, pressing Escape will call onClose. */
    closeOnEsc?: boolean;

    /** If true, shows a close button in the header. */
    showCloseButton?: boolean;

    /** Loading state of the modal. */
    loading?: boolean;

    /** Portal container (defaults to document.body). */
    portalContainer?: HTMLElement;
}

export const DYN_MODAL_DEFAULT_PROPS = {
    size: 'md' as DynModalSize,
    fullscreen: false,
    centered: true,
    closeOnBackdropClick: true,
    closeOnEsc: true,
    showCloseButton: true,
    loading: false,
} as const;
