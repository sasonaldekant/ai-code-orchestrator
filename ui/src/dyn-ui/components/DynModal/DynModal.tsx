import React, { forwardRef, useEffect, useCallback, useId, useRef, useImperativeHandle } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '../../utils/classNames';
import { DynIcon } from '../DynIcon';
import type { DynModalProps, DynModalRef, DynModalSize } from './DynModal.types';
import { DYN_MODAL_DEFAULT_PROPS } from './DynModal.types';
import styles from './DynModal.module.css';

/**
 * DynModal Component
 * A customizable modal component with overlay, header, body, and footer sections.
 */
export const DynModal = forwardRef<DynModalRef, DynModalProps>((
    {
        isOpen,
        onClose,
        title,
        children,
        footer,
        size = DYN_MODAL_DEFAULT_PROPS.size,
        fullscreen = DYN_MODAL_DEFAULT_PROPS.fullscreen,
        centered = DYN_MODAL_DEFAULT_PROPS.centered,
        closeOnBackdropClick = DYN_MODAL_DEFAULT_PROPS.closeOnBackdropClick,
        closeOnEsc = DYN_MODAL_DEFAULT_PROPS.closeOnEsc,
        showCloseButton = DYN_MODAL_DEFAULT_PROPS.showCloseButton,
        loading = DYN_MODAL_DEFAULT_PROPS.loading,
        className,
        style,
        portalContainer = typeof document !== 'undefined' ? document.body : undefined,
        'aria-label': ariaLabel,
        'aria-labelledby': ariaLabelledBy,
        'aria-describedby': ariaDescribedBy,
        id: idProp,
        ...rest
    },
    ref
) => {
    const generatedId = useId();
    const modalId = idProp || generatedId;
    const titleId = `${modalId}-title`;
    const bodyId = `${modalId}-body`;
    const modalRef = useRef<HTMLDivElement>(null);

    // Forward ref to the modal container
    useImperativeHandle(ref, () => modalRef.current!, []);

    const previousFocus = useRef<HTMLElement | null>(null);

    useEffect(() => {
        if (isOpen) {
            previousFocus.current = document.activeElement as HTMLElement;

            // Focus the modal content for accessibility
            requestAnimationFrame(() => {
                modalRef.current?.focus();
            });

            document.body.style.overflow = 'hidden';

            const handleKeyDown = (event: KeyboardEvent) => {
                if (!isOpen) return;

                // Handle Escape
                if (closeOnEsc && event.key === 'Escape') {
                    event.preventDefault();
                    onClose();
                    return;
                }

                // Handle Focus Trap (Tab)
                if (event.key === 'Tab' && modalRef.current) {
                    const focusables = modalRef.current.querySelectorAll<HTMLElement>(
                        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                    );

                    if (focusables.length === 0) return;

                    const first = focusables[0];
                    const last = focusables[focusables.length - 1];

                    if (event.shiftKey) {
                        if (document.activeElement === first) {
                            last.focus();
                            event.preventDefault();
                        }
                    } else {
                        if (document.activeElement === last) {
                            first.focus();
                            event.preventDefault();
                        }
                    }
                }
            };

            document.addEventListener('keydown', handleKeyDown);

            return () => {
                document.removeEventListener('keydown', handleKeyDown);
                document.body.style.overflow = '';
                // Restore focus
                if (previousFocus.current) {
                    previousFocus.current.focus();
                }
            };
        }
        return undefined;
    }, [isOpen, closeOnEsc, onClose]);

    const handleBackdropClick = (event: React.MouseEvent) => {
        if (closeOnBackdropClick && event.target === event.currentTarget) {
            onClose();
        }
    };

    if (!isOpen || !portalContainer) return null;

    // Map props to Full Word CSS classes as per Technical Documentation
    const SIZE_MAP: Record<DynModalSize, string> = {
        sm: 'sizeSm',
        md: 'sizeMd',
        lg: 'sizeLg',
        full: 'modalFullscreen' // Assuming 'full' maps to fullscreen variant or similar behavior handled by className
    };

    const modalClasses = cn(
        styles.modalContainer,
        styles[SIZE_MAP[size] || 'sizeMd'],
        fullscreen && styles.modalFullscreen,
        loading && styles.modalLoading,
        className
    );

    return createPortal(
        <div
            className={cn(styles.modalOverlay, styles.open)}
            onClick={handleBackdropClick}
            role="presentation"
        >
            <div
                ref={modalRef}
                id={modalId}
                className={modalClasses}
                style={style}
                tabIndex={-1}
                role="dialog"
                aria-modal="true"
                aria-labelledby={title ? titleId : ariaLabelledBy}
                aria-describedby={ariaDescribedBy || bodyId}
                aria-label={ariaLabel}
                {...rest}
            >
                {(title || showCloseButton) && (
                    <header className={styles.modalHeader}>
                        {title && (
                            <h2 id={titleId} className={styles.modalTitle}>
                                {title}
                            </h2>
                        )}
                        {showCloseButton && (
                            <button
                                type="button"
                                className={styles.modalClose}
                                onClick={onClose}
                                aria-label="Close modal"
                            >
                                <DynIcon icon="close" size="md" />

                            </button>
                        )}
                    </header>
                )}

                <main id={bodyId} className={styles.modalBody}>
                    {children}
                </main>

                {footer && (
                    <footer className={styles.modalFooter}>
                        {footer}
                    </footer>
                )}
            </div>
        </div>,
        portalContainer
    );
});

DynModal.displayName = 'DynModal';

export default DynModal;
