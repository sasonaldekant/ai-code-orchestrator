import { InputHTMLAttributes, ReactNode, DragEvent, ChangeEvent } from 'react';

export interface DynUploadFile {
    file: File;
    id: string;
    preview?: string;
    progress?: number;
    error?: string;
}

export interface DynUploadProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'onChange'> {
    /**
     * Callback when files are selected or dropped.
     * Returns an array of File objects.
     */
    onUpload?: (files: File[]) => void;

    /**
     * Accepted file types (e.g., "image/*", ".pdf").
     */
    accept?: string;

    /**
     * Whether to allow multiple file selection.
     * @default false
     */
    multiple?: boolean;

    /**
     * Maximum file size in bytes.
     */
    maxSize?: number;

    /**
     * Custom label/text for the drop zone.
     */
    label?: ReactNode;

    /**
     * Helper text or description.
     */
    description?: ReactNode;

    /**
     * Whether the upload is disabled.
     */
    disabled?: boolean;

    /**
     * Whether to show the list of selected files.
     * @default true
     */
    showFileList?: boolean;

    /**
     * External file list for controlled mode or initial state.
     */
    fileList?: DynUploadFile[];

    /**
     * Callback when file list changes (add/remove).
     */
    onFileListChange?: (files: DynUploadFile[]) => void;

    /**
     * Class name for the container.
     */
    className?: string;

    /**
     * Whether the component is in an error state.
     */
    error?: boolean;

    /**
     * Error message text to display.
     */
    errorMessage?: string;
}
