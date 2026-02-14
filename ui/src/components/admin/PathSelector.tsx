import { useState, useEffect, useRef } from 'react';
import { FolderOpen, ChevronRight, Folder, File, Loader2, X, Home, ArrowUp } from 'lucide-react';
import clsx from 'clsx';

interface PathSelectorProps {
    value: string;
    onChange: (path: string) => void;
    placeholder?: string;
    label?: string;
    filterExtensions?: string;
    disabled?: boolean;
}

interface FileItem {
    name: string;
    path: string;
    is_dir: boolean;
    size?: number;
    extension?: string;
}

export function PathSelector({ value, onChange, placeholder, label, filterExtensions, disabled }: PathSelectorProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [currentPath, setCurrentPath] = useState('.');
    const [items, setItems] = useState<FileItem[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const modalRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (isOpen) {
            loadDirectory(currentPath);
        }
    }, [isOpen, currentPath]);

    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        }
        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [isOpen]);

    const loadDirectory = async (path: string) => {
        setIsLoading(true);
        setError(null);
        try {
            const url = new URL('http://localhost:8000/admin/browse');
            url.searchParams.set('path', path);
            if (filterExtensions) {
                url.searchParams.set('filter_ext', filterExtensions);
            }

            const resp = await fetch(url.toString());
            if (!resp.ok) throw new Error('Failed to load');
            const data = await resp.json();
            setItems(data.items || []);
            setCurrentPath(data.path);
        } catch (e) {
            setError(`Failed to load directory: ${path}`);
            setItems([]);
        } finally {
            setIsLoading(false);
        }
    };

    const navigateUp = () => {
        const parts = currentPath.split('\\').filter(Boolean);
        if (parts.length > 1) {
            parts.pop();
            setCurrentPath(parts.join('\\'));
        }
    };

    const selectItem = (item: FileItem) => {
        if (item.is_dir) {
            setCurrentPath(item.path);
        } else {
            onChange(item.path);
            setIsOpen(false);
        }
    };

    const selectCurrentFolder = () => {
        onChange(currentPath);
        setIsOpen(false);
    };

    return (
        <div className="relative">
            {label && <label className="block text-sm font-medium mb-2">{label}</label>}
            <div className="flex gap-2">
                <input
                    type="text"
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder={placeholder}
                    disabled={disabled}
                    className="flex-1 px-4 py-2.5 bg-background border border-border rounded-lg focus:border-primary focus:ring-1 focus:ring-primary/20 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                />
                <button
                    type="button"
                    onClick={() => setIsOpen(true)}
                    disabled={disabled}
                    className="px-3 py-2.5 bg-secondary hover:bg-secondary/80 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <FolderOpen className="w-5 h-5" />
                </button>
            </div>

            {/* Browse Modal */}
            {isOpen && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div
                        ref={modalRef}
                        className="bg-card border border-border rounded-xl w-[600px] max-h-[500px] flex flex-col shadow-2xl"
                    >
                        {/* Header */}
                        <div className="p-4 border-b border-border flex items-center justify-between">
                            <h3 className="font-semibold">Browse Folders</h3>
                            <button onClick={() => setIsOpen(false)} className="p-1 hover:bg-muted rounded">
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Path Bar */}
                        <div className="px-4 py-2 border-b border-border flex items-center gap-2 bg-muted/30">
                            <button
                                onClick={() => setCurrentPath('C:\\')}
                                className="p-1.5 hover:bg-muted rounded"
                                title="Go to root"
                            >
                                <Home className="w-4 h-4" />
                            </button>
                            <button
                                onClick={navigateUp}
                                className="p-1.5 hover:bg-muted rounded"
                                title="Go up"
                            >
                                <ArrowUp className="w-4 h-4" />
                            </button>
                            <div className="flex-1 text-sm font-mono text-muted-foreground truncate">
                                {currentPath}
                            </div>
                        </div>

                        {/* File List */}
                        <div className="flex-1 overflow-y-auto p-2 min-h-[200px]">
                            {isLoading ? (
                                <div className="flex items-center justify-center h-32">
                                    <Loader2 className="w-6 h-6 animate-spin text-primary" />
                                </div>
                            ) : error ? (
                                <div className="text-center text-red-400 p-4">{error}</div>
                            ) : items.length === 0 ? (
                                <div className="text-center text-muted-foreground p-4">Empty folder</div>
                            ) : (
                                <div className="space-y-0.5">
                                    {items.map((item) => (
                                        <button
                                            key={item.path}
                                            onClick={() => selectItem(item)}
                                            onDoubleClick={() => {
                                                if (item.is_dir) {
                                                    onChange(item.path);
                                                    setIsOpen(false);
                                                }
                                            }}
                                            className={clsx(
                                                "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-left transition-colors",
                                                "hover:bg-primary/10"
                                            )}
                                        >
                                            {item.is_dir ? (
                                                <Folder className="w-4 h-4 text-amber-500" />
                                            ) : (
                                                <File className="w-4 h-4 text-muted-foreground" />
                                            )}
                                            <span className="flex-1 truncate">{item.name}</span>
                                            {item.is_dir && (
                                                <ChevronRight className="w-4 h-4 text-muted-foreground" />
                                            )}
                                            {!item.is_dir && item.size && (
                                                <span className="text-xs text-muted-foreground">
                                                    {(item.size / 1024).toFixed(1)} KB
                                                </span>
                                            )}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Footer */}
                        <div className="p-4 border-t border-border flex justify-between">
                            <button
                                onClick={() => setIsOpen(false)}
                                className="px-4 py-2 text-sm text-muted-foreground hover:text-foreground"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={selectCurrentFolder}
                                className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90"
                            >
                                Select This Folder
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
