
export type DialogConfig = {
    title?: string;
    message: string;
    confirmLabel?: string;
    cancelLabel?: string;
    type?: 'confirm' | 'alert' | 'prompt';
    defaultValue?: string;
    placeholder?: string;
};

export interface DynDialogRef {
    confirm(config: DialogConfig): Promise<boolean>;
    alert(message: string, title?: string): Promise<void>;
    prompt(message: string, title?: string, defaultValue?: string): Promise<string | null>;
}

export type DialogState = DialogConfig & {
    isOpen: boolean;
    resolve?: (value: any) => void;
};
