import React, { useRef, useState, useCallback, useId, useEffect } from 'react';
import { cn } from '../../utils/classNames';
import { DynUploadProps, DynUploadFile } from './DynUpload.types';
import { DynIcon } from '../DynIcon';
import styles from './DynUpload.module.css';

/**
 * DynUpload Component
 * Standardized with Design Tokens & CSS Modules
 */
export const DynUpload: React.FC<DynUploadProps> = ({
    onUpload,
    accept,
    multiple = false,
    maxSize,
    label = 'Click to upload or drag and drop',
    description = 'SVG, PNG, JPG or GIF (max. 800x400px)',
    disabled = false,
    showFileList = true,
    fileList: controlledFileList,
    onFileListChange,
    className,
    error,
    errorMessage,
    ...props
}) => {
    const inputRef = useRef<HTMLInputElement>(null);
    const [isDragActive, setIsDragActive] = useState(false);
    const [internalFileList, setInternalFileList] = useState<DynUploadFile[]>([]);
    const id = useId();

    const fileList = controlledFileList || internalFileList;

    useEffect(() => {
        // Cleanup object URLs to avoid memory leaks
        return () => {
            if (typeof URL !== 'undefined' && URL.revokeObjectURL) {
                fileList.forEach(file => {
                    if (file.preview) {
                        URL.revokeObjectURL(file.preview);
                    }
                });
            }
        };
    }, [fileList]);

    const handleFiles = useCallback((files: FileList | null) => {
        if (!files) return;

        const newFiles: DynUploadFile[] = Array.from(files)
            .filter(file => {
                if (maxSize && file.size > maxSize) {
                    alert(`File ${file.name} is too large. Max size is ${maxSize} bytes.`);
                    return false;
                }
                return true;
            })
            .map(file => ({
                file,
                id: Math.random().toString(36).substr(2, 9),
                preview: file.type.startsWith('image/') && typeof URL !== 'undefined' && URL.createObjectURL
                    ? URL.createObjectURL(file)
                    : undefined,
            }));

        if (newFiles.length === 0) return;

        const updatedList = multiple ? [...fileList, ...newFiles] : newFiles;

        if (controlledFileList === undefined) {
            setInternalFileList(updatedList);
        }

        onFileListChange?.(updatedList);
        onUpload?.(newFiles.map(f => f.file));
    }, [maxSize, multiple, fileList, controlledFileList, onFileListChange, onUpload]);

    const handleDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setIsDragActive(true);
        } else if (e.type === 'dragleave') {
            setIsDragActive(false);
        }
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragActive(false);
        if (!disabled && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFiles(e.dataTransfer.files);
        }
    }, [disabled, handleFiles]);

    const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        handleFiles(e.target.files);
        // Reset input value to allow selecting the same file again
        if (inputRef.current) inputRef.current.value = '';
    }, [handleFiles]);

    const handleRemove = useCallback((fileId: string) => {
        const updatedList = fileList.filter(f => f.id !== fileId);

        if (controlledFileList === undefined) {
            setInternalFileList(updatedList);
        }
        onFileListChange?.(updatedList);
    }, [fileList, controlledFileList, onFileListChange]);

    const formatSize = (bytes: number) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    return (
        <div className={cn(styles.container, className)}>
            <div
                className={cn(styles.dropZone, {
                    [styles.dropZoneActive]: isDragActive,
                    [styles.dropZoneDisabled]: disabled,
                    [styles.dropZoneError]: error || !!errorMessage,
                })}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => !disabled && inputRef.current?.click()}
                role="button"
                tabIndex={disabled ? -1 : 0}
                onKeyDown={(e) => {
                    if (!disabled && (e.key === 'Enter' || e.key === ' ')) {
                        e.preventDefault();
                        inputRef.current?.click();
                    }
                }}
            >
                <input
                    {...props}
                    ref={inputRef}
                    id={id}
                    type="file"
                    className={styles.input}
                    onChange={handleChange}
                    accept={accept}
                    multiple={multiple}
                    disabled={disabled}
                    aria-hidden="true"
                />

                <div className={styles.icon}>
                    <DynIcon icon="upload-cloud" size="xl" />
                </div>

                <div className={styles.label}>{label}</div>
                {errorMessage && <div className={styles.errorMessage}>{errorMessage}</div>}
                {!errorMessage && description && <div className={styles.description}>{description}</div>}
            </div>

            {showFileList && fileList.length > 0 && (
                <div className={styles.fileList}>
                    {fileList.map((file) => (
                        <div key={file.id} className={styles.fileItem}>
                            {file.preview ? (
                                <img src={file.preview} alt="Preview" className={styles.fileItemPreview} />
                            ) : (
                                <div className={styles.fileItemIcon}>
                                    <DynIcon icon="file-text" size="lg" />
                                </div>
                            )}
                            <div className={styles.fileItemInfo}>
                                <div className={styles.fileName} title={file.file.name}>{file.file.name}</div>
                                <div className={styles.fileSize}>{formatSize(file.file.size)}</div>
                            </div>
                            {!disabled && (
                                <button
                                    type="button"
                                    className={styles.removeButton}
                                    onClick={() => handleRemove(file.id)}
                                    aria-label={`Remove ${file.file.name}`}
                                >
                                    <DynIcon icon="x" size="sm" />
                                </button>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

DynUpload.displayName = 'DynUpload';
