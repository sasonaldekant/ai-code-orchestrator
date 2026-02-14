import { useState, useEffect } from 'react';
import { Upload, FileText, Folder, Link as LinkIcon, Type, CheckCircle, AlertCircle, RefreshCw, Info, Layers, Search, FileCode, Book, Sparkles } from 'lucide-react';
import clsx from 'clsx';
import { PathSelector } from '../admin/PathSelector';

type SourceType = 'file' | 'directory' | 'url' | 'text' | 'instructions';
type Tier = 1 | 2 | 3 | 4;

interface UniversalIngestionProps {
    onIngestSuccess?: () => void;
}

export function UniversalIngestionPanel({ onIngestSuccess }: UniversalIngestionProps) {
    // Phase 1: Source & Content
    const [sourceType, setSourceType] = useState<SourceType>('directory');
    const [path, setPath] = useState('');
    const [textContent, setTextContent] = useState('');
    const [fileFilter, setFileFilter] = useState('*.*');

    // Phase 2: Metadata
    const [tier, setTier] = useState<Tier>(3);
    const [category, setCategory] = useState('component');
    const [tags, setTags] = useState<string[]>([]);
    const [tagInput, setTagInput] = useState('');
    const [collectionName, setCollectionName] = useState('');
    const [isBridge, setIsBridge] = useState(false); // Bridge Option

    // Processing
    const [chunkSize, setChunkSize] = useState(800);
    const [chunkOverlap, setChunkOverlap] = useState(100);
    const [extractCodeBlocks, setExtractCodeBlocks] = useState(true);

    // Actions
    const [isValidating, setIsValidating] = useState(false);
    const [isIngesting, setIsIngesting] = useState(false);
    const [validationResult, setValidationResult] = useState<any>(null);
    const [ingestionResult, setIngestionResult] = useState<any>(null);

    // Auto-set defaults for Instructions type
    useEffect(() => {
        if (sourceType === 'instructions') {
            setTier(1);
            setCategory('instructions');
            setFileFilter('README.md, *.md');
            if (!tags.includes('must-follow')) setTags([...tags, 'must-follow']);
        }
    }, [sourceType]);

    // Auto-generate collection hint
    useEffect(() => {
        // Visual hint only
    }, [tier, category, collectionName]);

    const handleAddTag = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && tagInput.trim()) {
            e.preventDefault();
            if (!tags.includes(tagInput.trim())) setTags([...tags, tagInput.trim()]);
            setTagInput('');
        }
    };

    const removeTag = (tag: string) => setTags(tags.filter(t => t !== tag));

    const getPlaceholder = () => {
        switch (sourceType) {
            case 'file': return 'C:/Projects/MyApp/src/components/Button.tsx';
            case 'directory': return 'C:/Projects/MyApp/src/components';
            case 'url': return 'https://docs.framework.com/components';
            case 'text': return 'Paste content here...';
            case 'instructions': return 'C:/Projects/MyApp/docs/README.md';
            default: return '';
        }
    };

    const handleValidate = async () => {
        setIsValidating(true);
        setValidationResult(null);
        setIngestionResult(null);
        try {
            const resp = await fetch('http://localhost:8000/knowledge/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source_type: sourceType,
                    path: path,
                    file_filter: fileFilter,
                    tier: tier,
                    category: category
                })
            });
            const data = await resp.json();
            setValidationResult(data);
        } catch (error) {
            setValidationResult({ valid: false, error: 'Failed to connect to validation service' });
        } finally {
            setIsValidating(false);
        }
    };

    const handleIngest = async () => {
        setIsIngesting(true);
        setIngestionResult(null);

        const payload = {
            source_type: sourceType === 'instructions' ? 'file' : sourceType, // Map instructions back to file/dir
            path: sourceType === 'text' ? undefined : path,
            content: sourceType === 'text' ? textContent : undefined,
            file_filter: sourceType === 'directory' ? fileFilter : undefined,
            tier,
            category,
            tags: isBridge ? [...tags, 'bridge-context'] : tags,
            collection: collectionName || `tier${tier}_${category}`,
            chunk_size: chunkSize,
            chunk_overlap: chunkOverlap,
            extract_options: { code_blocks: extractCodeBlocks }
        };

        try {
            const resp = await fetch('http://localhost:8000/admin/ingest/universal', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await resp.json();

            if (resp.ok) {
                setIngestionResult({ success: true, ...data });
                if (onIngestSuccess) onIngestSuccess();
                setValidationResult(null);
            } else {
                setIngestionResult({ success: false, error: data.detail || 'Ingestion failed' });
            }
        } catch (error) {
            setIngestionResult({ success: false, error: 'Network error' });
        } finally {
            setIsIngesting(false);
        }
    };

    return (
        <div className="space-y-4">
            <div className="bg-card border border-border rounded-xl p-5 shadow-sm">
                <div className="flex items-center justify-between mb-4 border-b border-border pb-3">
                    <div className="flex items-center gap-2">
                        <Layers className="w-5 h-5 text-primary" />
                        <h2 className="text-base font-semibold">Universal Knowledge Ingestion</h2>
                    </div>
                    <div className="flex gap-1 bg-muted/30 p-1 rounded-lg">
                        {[
                            { id: 'directory', icon: Folder, label: 'Dir' },
                            { id: 'file', icon: FileCode, label: 'File' },
                            { id: 'instructions', icon: Book, label: 'Rules' },
                            { id: 'url', icon: LinkIcon, label: 'URL' },
                            { id: 'text', icon: Type, label: 'Text' },
                        ].map((type) => (
                            <button
                                key={type.id}
                                onClick={() => setSourceType(type.id as SourceType)}
                                className={clsx(
                                    "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all",
                                    sourceType === type.id
                                        ? "bg-primary text-primary-foreground shadow-sm"
                                        : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                                )}
                            >
                                <type.icon className="w-3.5 h-3.5" />
                                {type.label}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
                    {/* LEFT COLUMN: Source Input (7 cols) */}
                    <div className="md:col-span-12 lg:col-span-7 space-y-4">
                        <div className="space-y-3">
                            {sourceType === 'text' ? (
                                <textarea
                                    value={textContent}
                                    onChange={(e) => setTextContent(e.target.value)}
                                    placeholder={getPlaceholder()}
                                    className="w-full h-32 px-3 py-2 bg-background border border-border rounded-lg outline-none focus:border-primary font-mono text-xs resize-y"
                                />
                            ) : (
                                <div className="space-y-2">
                                    <PathSelector
                                        value={path}
                                        onChange={setPath}
                                        placeholder={getPlaceholder()}
                                        label={sourceType === 'directory' ? 'Target Directory' : sourceType === 'instructions' ? 'Instruction File (README.md)' : 'File Path'}
                                    />
                                    {sourceType === 'directory' && (
                                        <div className="flex items-center gap-2">
                                            <label className="text-xs font-medium text-muted-foreground whitespace-nowrap">Filter:</label>
                                            <input
                                                type="text"
                                                value={fileFilter}
                                                onChange={(e) => setFileFilter(e.target.value)}
                                                placeholder="e.g. *.ts, DOCS.md"
                                                className="flex-1 px-2 py-1 bg-background border border-border rounded text-xs font-mono focus:border-primary outline-none"
                                            />
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Bridge Option */}
                            <label className={clsx(
                                "flex items-center gap-2 p-2 border rounded-lg cursor-pointer transition-colors",
                                isBridge ? "bg-indigo-500/10 border-indigo-500/30" : "bg-transparent border-transparent hover:bg-muted/30"
                            )}>
                                <input
                                    type="checkbox"
                                    checked={isBridge}
                                    onChange={(e) => setIsBridge(e.target.checked)}
                                    className="w-4 h-4 rounded border-border text-primary focus:ring-primary"
                                />
                                <div className="flex-1">
                                    <div className="text-xs font-medium flex items-center gap-1.5">
                                        <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                                        Bridge Context
                                    </div>
                                    <div className="text-[10px] text-muted-foreground">
                                        Mark as high-priority context that bridges multiple domains.
                                    </div>
                                </div>
                            </label>
                        </div>
                    </div>

                    {/* RIGHT COLUMN: Metadata (5 cols) */}
                    <div className="md:col-span-12 lg:col-span-5 space-y-6 border-l border-border/50 lg:pl-8">
                        {/* Tier Selection - Expanded */}
                        <div className="grid grid-cols-4 gap-3">
                            {[
                                { val: 1, label: 'T1', title: 'Rules & Standards', desc: 'Must Follow', color: 'bg-blue-500/10 text-blue-500 border-blue-500/30 ring-blue-500/20' },
                                { val: 2, label: 'T2', title: 'Design System', desc: 'Tokens & Assets', color: 'bg-purple-500/10 text-purple-500 border-purple-500/30 ring-purple-500/20' },
                                { val: 3, label: 'T3', title: 'Core Components', desc: 'React Library', color: 'bg-primary/10 text-primary border-primary/30 ring-primary/20' },
                                { val: 4, label: 'T4', title: 'Backend Patterns', desc: 'API & DB Schema', color: 'bg-amber-500/10 text-amber-500 border-amber-500/30 ring-amber-500/20' },
                            ].map((t) => (
                                <button
                                    key={t.val}
                                    onClick={() => {
                                        setTier(t.val as Tier);
                                        if (t.val === 1) setCategory('architecture');
                                        if (t.val === 2) setCategory('design');
                                        if (t.val === 3) setCategory('component');
                                        if (t.val === 4) setCategory('backend');
                                    }}
                                    className={clsx(
                                        "px-2 py-4 rounded-xl border text-center transition-all duration-200 flex flex-col items-center justify-center gap-1",
                                        tier === t.val
                                            ? `${t.color} shadow-lg ring-1`
                                            : "border-border text-muted-foreground hover:bg-muted/80 hover:text-foreground hover:border-border/80"
                                    )}
                                    title={t.desc}
                                >
                                    <div className={clsx("text-lg font-bold", tier === t.val ? "scale-110" : "")}>{t.label}</div>
                                    <div className="text-[10px] uppercase font-medium tracking-wide opacity-80">{t.title}</div>
                                </button>
                            ))}
                        </div>

                        {/* Metadata Inputs */}
                        <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-1.5">
                                    <label className="text-xs uppercase font-bold text-muted-foreground tracking-wider ml-1">Category</label>
                                    <input
                                        type="text"
                                        value={category}
                                        onChange={(e) => setCategory(e.target.value)}
                                        className="w-full px-3 py-2.5 bg-background border border-border rounded-lg text-sm focus:border-primary focus:ring-1 focus:ring-primary/20 outline-none transition-all"
                                    />
                                </div>
                                <div className="space-y-1.5">
                                    <label className="text-xs uppercase font-bold text-muted-foreground tracking-wider ml-1">Collection</label>
                                    <input
                                        type="text"
                                        value={collectionName}
                                        onChange={(e) => setCollectionName(e.target.value)}
                                        placeholder={`tier${tier}_${category}`}
                                        className="w-full px-3 py-2.5 bg-background border border-border rounded-lg text-sm font-mono text-muted-foreground focus:text-foreground focus:border-primary focus:ring-1 focus:ring-primary/20 outline-none transition-all"
                                    />
                                </div>
                            </div>

                            <div className="space-y-1.5">
                                <label className="text-xs uppercase font-bold text-muted-foreground tracking-wider ml-1">Tags</label>
                                <div className="flex flex-wrap gap-2 px-3 py-2.5 bg-background border border-border rounded-lg min-h-[42px] focus-within:border-primary focus-within:ring-1 focus-within:ring-primary/20 transition-all">
                                    {tags.map(tag => (
                                        <span key={tag} className="inline-flex items-center gap-1 text-xs bg-secondary text-secondary-foreground px-2 py-1 rounded-md border border-border/50">
                                            {tag}
                                            <button onClick={() => removeTag(tag)} className="hover:text-destructive transition-colors ml-0.5">&times;</button>
                                        </span>
                                    ))}
                                    <input
                                        type="text"
                                        value={tagInput}
                                        onChange={(e) => setTagInput(e.target.value)}
                                        onKeyDown={handleAddTag}
                                        className="flex-1 bg-transparent border-none outline-none text-sm min-w-[60px] placeholder:text-muted-foreground/50"
                                        placeholder={tags.length === 0 ? "Type tag & hit Enter..." : ""}
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-3 pt-2">
                            <button
                                onClick={handleValidate}
                                disabled={isValidating || (!path && !textContent)}
                                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-secondary text-secondary-foreground rounded-lg text-sm font-semibold hover:bg-secondary/80 disabled:opacity-50 transition-all"
                            >
                                {isValidating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                                Validate
                            </button>
                            <button
                                onClick={handleIngest}
                                disabled={isIngesting || (!path && !textContent)}
                                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-primary text-primary-foreground rounded-lg text-sm font-semibold hover:bg-primary/90 disabled:opacity-50 transition-all shadow-md active:scale-[0.98]"
                            >
                                {isIngesting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                                Ingest Content
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Results Display */}
            {(validationResult || ingestionResult) && (
                <div className={clsx(
                    "border rounded-lg p-4 fade-in animate-in slide-in-from-top-2",
                    (ingestionResult?.success || validationResult?.valid) ? "bg-green-500/5 border-green-500/20" : "bg-red-500/5 border-red-500/20"
                )}>
                    {ingestionResult ? (
                        <div className="flex items-start gap-3">
                            {ingestionResult.success ? <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" /> : <AlertCircle className="w-4 h-4 text-red-500 mt-0.5" />}
                            <div>
                                <h3 className="font-semibold text-sm">{ingestionResult.success ? 'Ingestion Successful' : 'Ingestion Failed'}</h3>
                                <p className="text-xs text-muted-foreground mt-0.5">{ingestionResult.message || ingestionResult.error}</p>
                                {ingestionResult.documents_ingested > 0 && (
                                    <div className="mt-1.5 text-[10px] bg-background/50 px-2 py-1 rounded border border-border/50 inline-block">
                                        Indexed <strong>{ingestionResult.documents_ingested}</strong> documents into <code>{ingestionResult.collection}</code>
                                    </div>
                                )}
                            </div>
                        </div>
                    ) : validationResult && (
                        <div className="flex items-center justify-between gap-4">
                            <div className="flex items-center gap-2">
                                <Info className="w-4 h-4 text-blue-500" />
                                <div>
                                    <h3 className="font-semibold text-sm">Validation OK</h3>
                                    <p className="text-xs text-muted-foreground">Found {validationResult.fileCount} files (~{(validationResult.estimatedTokens / 1000).toFixed(1)}k tokens)</p>
                                </div>
                            </div>
                            <div className="text-xs text-green-600 font-medium bg-green-500/10 px-2 py-1 rounded">Ready to Ingest</div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
