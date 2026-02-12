import React, { createContext, useContext, useRef, ReactNode, useCallback } from 'react';
import { DynDialog } from './DynDialog';
import { DynDialogRef, DialogConfig } from './DynDialog.types';

interface DynDialogContextType {
    confirm: (config: DialogConfig) => Promise<boolean>;
    alert: (message: string, title?: string) => Promise<void>;
    prompt: (message: string, title?: string, defaultValue?: string) => Promise<string | null>;
}

const DynDialogContext = createContext<DynDialogContextType | undefined>(undefined);

export const DynDialogProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const dialogRef = useRef<DynDialogRef>(null);

    const confirm = useCallback((config: DialogConfig) => {
        if (dialogRef.current) {
            return dialogRef.current.confirm(config);
        }
        return Promise.resolve(false);
    }, []);

    const alert = useCallback((message: string, title?: string) => {
        if (dialogRef.current) {
            return dialogRef.current.alert(message, title);
        }
        return Promise.resolve();
    }, []);

    const prompt = useCallback((message: string, title?: string, defaultValue?: string) => {
        if (dialogRef.current) {
            return dialogRef.current.prompt(message, title, defaultValue);
        }
        return Promise.resolve(null);
    }, []);

    return (
        <DynDialogContext.Provider value={{ confirm, alert, prompt }}>
            {children}
            <DynDialog ref={dialogRef} />
        </DynDialogContext.Provider>
    );
};

export const useDialog = (): DynDialogContextType => {
    const context = useContext(DynDialogContext);
    if (!context) {
        throw new Error('useDialog must be used within a DynDialogProvider');
    }
    return context;
};
