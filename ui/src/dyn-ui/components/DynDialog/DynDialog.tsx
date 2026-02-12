import React, { useState, useRef, useImperativeHandle, forwardRef, useCallback } from 'react';
import { DynModal } from '../DynModal';
import { DynButton } from '../DynButton';
import { DynInput } from '../DynInput';
import { DialogConfig, DialogState, DynDialogRef } from './DynDialog.types';
import styles from './DynDialog.module.css';

const defaultState: DialogState = {
    isOpen: false,
    message: '',
    type: 'confirm',
};

export const DynDialog = forwardRef<DynDialogRef, {}>((_, ref) => {
    const [state, setState] = useState<DialogState>(defaultState);
    const [inputValue, setInputValue] = useState('');
    const resolveRef = useRef<((value: any) => void) | null>(null);

    const close = useCallback(() => {
        setState((prev) => ({ ...prev, isOpen: false }));
        setInputValue('');
    }, []);

    const handleConfirm = useCallback(() => {
        if (state.type === 'prompt') {
            resolveRef.current?.(inputValue);
        } else {
            resolveRef.current?.(true);
        }
        close();
    }, [state.type, inputValue, close]);

    const handleCancel = useCallback(() => {
        if (state.type === 'prompt') {
            resolveRef.current?.(null);
        } else {
            resolveRef.current?.(false);
        }
        close();
    }, [state.type, close]);

    useImperativeHandle(ref, () => ({
        confirm: (config: DialogConfig) => {
            return new Promise<boolean>((resolve) => {
                resolveRef.current = resolve;
                setState({ ...config, type: 'confirm', isOpen: true });
            });
        },
        alert: (message: string, title?: string) => {
            return new Promise<void>((resolve) => {
                resolveRef.current = resolve;
                setState({ message, title, type: 'alert', isOpen: true });
            });
        },
        prompt: (message: string, title?: string, defaultValue: string = '') => {
            return new Promise<string | null>((resolve) => {
                resolveRef.current = resolve;
                setInputValue(defaultValue);
                setState({
                    message,
                    title,
                    defaultValue,
                    type: 'prompt',
                    isOpen: true
                });
            });
        },
    }));

    const isAlert = state.type === 'alert';
    const isPrompt = state.type === 'prompt';

    return (
        <DynModal
            isOpen={state.isOpen}
            onClose={handleCancel}
            title={state.title}
            size="sm"
        >
            <div className={styles.content}>
                <p className={styles.message}>{state.message}</p>

                {isPrompt && (
                    <div className={styles.inputContainer}>
                        <DynInput
                            value={inputValue}
                            onChange={(value) => setInputValue(String(value))}
                            placeholder={state.placeholder}
                            autoFocus
                            className={styles.input}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter') handleConfirm();
                                if (e.key === 'Escape') handleCancel();
                            }}
                        />
                    </div>
                )}

                <div className={styles.actions}>
                    {!isAlert && (
                        <DynButton kind="secondary" onClick={handleCancel}>
                            {state.cancelLabel || 'Cancel'}
                        </DynButton>
                    )}
                    <DynButton kind="primary" onClick={handleConfirm}>
                        {state.confirmLabel || 'OK'}
                    </DynButton>
                </div>
            </div>
        </DynModal>
    );
});

DynDialog.displayName = 'DynDialog';
