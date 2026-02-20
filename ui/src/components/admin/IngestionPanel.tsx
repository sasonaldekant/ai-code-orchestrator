import { useState } from 'react';
import { Database, FolderOpen, CheckCircle, AlertCircle, Loader2, Upload, Info, Zap } from 'lucide-react';
import clsx from 'clsx';
import { PathSelector } from './PathSelector';

type IngestionType = 'database' | 'component_library' | 'project_codebase' | 'database_content' | 'instruction_docs' | 'specialization_rules' | 'custom';
type IngestionTier = 1 | 2 | 3 | 4;
type ContentMode = 'json' | 'sql';

interface ValidationResult {
    valid: boolean;
    errors: string[];
    warnings: string[];
    info: {
        path_exists?: boolean;
        cs_files_found?: number;
        component_files_found?: number;
        source_files_found?: number;
        file_types?: Record<string, number>;
        estimated_entities?: number;
        estimated_documents?: number;
        estimated_tokens?: number;
        estimated_cost_usd?: number;
    };
}

export function IngestionPanel() {
    const [type, setType] = useState<IngestionType>('custom');
    const [tier, setTier] = useState<IngestionTier>(3);
    const [category, setCategory] = useState('component');
    const [path, setPath] = useState('');
    const [modelsDir, setModelsDir] = useState('');
    const [collection, setCollection] = useState('');
    const [chunkSize, setChunkSize] = useState(800);
    const [chunkOverlap, setChunkOverlap] = useState(120);

    // Phase 13: Content Ingestion State
    const [contentMode, setContentMode] = useState<ContentMode>('json');
    const [tableName, setTableName] = useState('');
    const [connectionString, setConnectionString] = useState('');
    const [sqlQuery, setSqlQuery] = useState('SELECT * FROM {table_name}');

    const [isValidating, setIsValidating] = useState(false);
    const [isIngesting, setIsIngesting] = useState(false);
    const [validation, setValidation] = useState<ValidationResult | null>(null);
    const [result, setResult] = useState<any>(null);

    const handleValidate = async () => {
        setIsValidating(true);
        setValidation(null);
        setResult(null);

        try {
            const resp = await fetch('http://localhost:8000/admin/ingest/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type,
                    path,
                    tier,
                    category,
                    models_dir: modelsDir || undefined,
                    collection: collection || undefined,
                    chunk_size: chunkSize,
                    chunk_overlap: chunkOverlap,
                }),
            });
            const data = await resp.json();
            setValidation(data);
        } catch (e) {
            setValidation({
                valid: false,
                errors: ['Failed to connect to backend'],
                warnings: [],
                info: {},
            });
        } finally {
            setIsValidating(false);
        }
    };

    const handleIngest = async () => {
        setIsIngesting(true);
        setResult(null);

        try {
            // Phase 13 Logic
            let endpoint = 'http://localhost:8000/admin/ingest/execute';
            let body: any = {
                type,
                path,
                tier,
                category,
                models_dir: modelsDir || undefined,
                collection: collection || undefined,
                chunk_size: chunkSize,
                chunk_overlap: chunkOverlap,
            };

            if (type === 'database_content') {
                endpoint = 'http://localhost:8000/admin/ingest/content';
                body = {
                    mode: contentMode,
                    table_name: tableName,
                    collection_name: collection || 'database_content',
                    file_path: contentMode === 'json' ? path : undefined,
                    connection_string: contentMode === 'sql' ? connectionString : undefined,
                    query: contentMode === 'sql' ? sqlQuery : undefined
                };
            }

            const resp = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            const data = await resp.json();
            if (resp.ok) {
                setResult({ success: true, ...data });
            } else {
                setResult({ success: false, error: data.detail });
            }
        } catch (e) {
            setResult({ success: false, error: 'Network error' });
        } finally {
            setIsIngesting(false);
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold">RAG Knowledge Ingestion</h2>
                <p className="text-muted-foreground mt-1">
                    Import domain knowledge into the vector database for context-aware code generation.
                </p>
            </div>

            {/* Main Form */}
            <div className="bg-card border border-border rounded-xl p-6 space-y-5">
                {/* Tier Selection */}
                <div>
                    <label className="block text-sm font-medium mb-3">Knowledge Tier</label>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        {[
                            { val: 1, label: 'T1: Rules', color: 'border-blue-500 bg-blue-500/10 text-blue-500', desc: 'Architecture & Rules' },
                            { val: 2, label: 'T2: Tokens', color: 'border-purple-500 bg-purple-500/10 text-purple-500', desc: 'Design Tokens' },
                            { val: 3, label: 'T3: Components', color: 'border-primary bg-primary/10 text-primary', desc: 'Code & Components' },
                            { val: 4, label: 'T4: Backend', color: 'border-amber-500 bg-amber-500/10 text-amber-500', desc: 'DTOs & Patterns' },
                        ].map((t) => (
                            <button
                                key={t.val}
                                onClick={() => {
                                    setTier(t.val as IngestionTier);
                                    if (t.val === 1) setCategory('architecture');
                                    if (t.val === 2) setCategory('design');
                                    if (t.val === 3) setCategory('component');
                                    if (t.val === 4) setCategory('backend');
                                    setType('project_codebase'); // Generic codebase ingestion logic
                                }}
                                className={clsx(
                                    "flex flex-col items-center justify-center p-3 rounded-lg border transition-all text-center",
                                    tier === t.val ? t.color : "border-border hover:border-border/80"
                                )}
                            >
                                <span className="font-bold text-sm">{t.label}</span>
                                <span className="text-[10px] opacity-70 mt-1">{t.desc}</span>
                            </button>
                        ))}
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium mb-2">Category Name</label>
                        <input
                            type="text"
                            value={category}
                            onChange={(e) => setCategory(e.target.value)}
                            placeholder="e.g. component, dto, rules"
                            className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:border-primary text-sm"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-2">Parsing Logic (Optional)</label>
                        <select
                            value={type}
                            onChange={(e) => setType(e.target.value as IngestionType)}
                            className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:border-primary text-sm"
                        >
                            <option value="custom">Generic Auto-Detect</option>
                            <option value="project_codebase">Source Code Explorer</option>
                            <option value="database">C# DbContext (T4 spec)</option>
                            <option value="component_library">React Library (T3 spec)</option>
                            <option value="instruction_docs">Text/MD Docs (T1 spec)</option>
                        </select>
                    </div>
                </div>

                {/* Phase 13: Content Ingestion Inputs */}
                {type === 'database_content' && (
                    <div className="p-4 bg-amber-500/5 border border-amber-500/10 rounded-lg space-y-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">Source Mode</label>
                            <div className="flex gap-4">
                                <label className="flex items-center gap-2 cursor-pointer">
                                    <input type="radio" checked={contentMode === 'json'} onChange={() => setContentMode('json')} />
                                    <span>JSON File</span>
                                </label>
                                <label className="flex items-center gap-2 cursor-pointer">
                                    <input type="radio" checked={contentMode === 'sql'} onChange={() => setContentMode('sql')} />
                                    <span>Direct SQL Connection</span>
                                </label>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">Target Table Name</label>
                            <input
                                type="text"
                                value={tableName}
                                onChange={(e) => setTableName(e.target.value)}
                                placeholder="e.g. Products"
                                className="w-full px-4 py-2.5 bg-background border border-border rounded-lg focus:border-primary text-sm"
                            />
                        </div>

                        {contentMode === 'sql' && (
                            <>
                                <div>
                                    <label className="block text-sm font-medium mb-2">Connection String</label>
                                    <input
                                        type="text"
                                        value={connectionString}
                                        onChange={(e) => setConnectionString(e.target.value)}
                                        placeholder="Driver={ODBC Driver 17 for SQL Server};Server=...;"
                                        className="w-full px-4 py-2.5 bg-background border border-border rounded-lg focus:border-primary text-sm font-mono"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-2">Query</label>
                                    <input
                                        type="text"
                                        value={sqlQuery}
                                        onChange={(e) => setSqlQuery(e.target.value)}
                                        className="w-full px-4 py-2.5 bg-background border border-border rounded-lg focus:border-primary text-sm font-mono"
                                    />
                                    <p className="text-xs text-muted-foreground mt-1">Use {`{table_name}`} placeholder if needed.</p>
                                </div>
                            </>
                        )}
                    </div>
                )}

                {/* Path Input */}
                <PathSelector
                    label={
                        type === 'database' ? 'DbContext Path' :
                            type === 'component_library' ? 'Components Directory' :
                                type === 'database_content' && contentMode === 'json' ? 'JSON File Path' :
                                    type === 'project_codebase' ? 'Project Root Path' : 'Path'
                    }
                    value={path}
                    onChange={setPath}
                    disabled={type === 'database_content' && contentMode === 'sql'}
                    placeholder={
                        type === 'database' ? 'E:\\Project\\Backend\\Data' :
                            type === 'component_library' ? 'E:\\Project\\Frontend\\src\\components' :
                                type === 'database_content' ? 'E:\\exports\\products.json' :
                                    'E:\\Project\\MyExistingApp'
                    }
                />

                {/* Models Dir (Database only) */}
                {type === 'database' && (
                    <PathSelector
                        label="Models Directory (optional)"
                        value={modelsDir}
                        onChange={setModelsDir}
                        placeholder="Same as path if empty"
                    />
                )}

                {/* Collection Name */}
                <div>
                    <label className="block text-sm font-medium mb-2">
                        Collection Name <span className="text-muted-foreground">(optional)</span>
                    </label>
                    <input
                        type="text"
                        value={collection}
                        onChange={(e) => setCollection(e.target.value)}
                        placeholder={type === 'database' ? 'database_schema' : 'component_library'}
                        className="w-full px-4 py-2.5 bg-background border border-border rounded-lg focus:border-primary focus:ring-1 focus:ring-primary/20 text-sm"
                    />
                </div>

                {/* Chunk Settings */}
                <div className="pt-4 border-t border-border">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                            Chunk Settings
                        </h3>
                        <div className="flex items-center gap-2 bg-emerald-500/10 text-emerald-500 px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider border border-emerald-500/20">
                            <Zap className="w-3 h-3" />
                            Auto-Chunking Active (v3.1)
                        </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">Chunk Size (chars)</label>
                            <input
                                type="number"
                                value={chunkSize}
                                onChange={(e) => setChunkSize(Number(e.target.value))}
                                className="w-full px-4 py-2.5 bg-background border border-border rounded-lg focus:border-primary text-sm"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">Overlap (chars)</label>
                            <input
                                type="number"
                                value={chunkOverlap}
                                onChange={(e) => setChunkOverlap(Number(e.target.value))}
                                className="w-full px-4 py-2.5 bg-background border border-border rounded-lg focus:border-primary text-sm"
                            />
                        </div>
                    </div>
                </div>
                旋
                {/* Action Buttons */}
                <div className="flex gap-3 pt-4">
                    <button
                        onClick={handleValidate}
                        disabled={!path || isValidating || type === 'database_content'}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-secondary text-secondary-foreground rounded-lg font-medium hover:bg-secondary/80 disabled:opacity-50 transition-all"
                    >
                        {isValidating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Info className="w-4 h-4" />}
                        Validate
                    </button>
                    <button
                        onClick={handleIngest}
                        disabled={type !== 'database_content' && (!validation?.valid || isIngesting)}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 disabled:opacity-50 transition-all"
                    >
                        {isIngesting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                        Ingest Knowledge
                    </button>
                </div>
            </div>

            {/* Validation Result */}
            {validation && (
                <div className={clsx(
                    "border rounded-xl p-5",
                    validation.valid
                        ? "bg-green-500/5 border-green-500/20"
                        : "bg-red-500/5 border-red-500/20"
                )}>
                    <div className="flex items-center gap-2 mb-3">
                        {validation.valid ? (
                            <CheckCircle className="w-5 h-5 text-green-500" />
                        ) : (
                            <AlertCircle className="w-5 h-5 text-red-500" />
                        )}
                        <h3 className="font-semibold">
                            {validation.valid ? 'Validation Passed' : 'Validation Failed'}
                        </h3>
                    </div>

                    {validation.errors.length > 0 && (
                        <ul className="text-sm text-red-400 space-y-1 mb-3">
                            {validation.errors.map((e, i) => <li key={i}>• {e}</li>)}
                        </ul>
                    )}

                    {validation.warnings.length > 0 && (
                        <ul className="text-sm text-amber-400 space-y-1 mb-3">
                            {validation.warnings.map((w, i) => <li key={i}>⚠ {w}</li>)}
                        </ul>
                    )}

                    {validation.valid && validation.info && (
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                            <div className="bg-card/50 rounded-lg p-3 text-center">
                                <div className="text-2xl font-bold text-primary">
                                    {validation.info.cs_files_found || validation.info.component_files_found || validation.info.source_files_found || 0}
                                </div>
                                <div className="text-xs text-muted-foreground">Files Found</div>
                            </div>
                            <div className="bg-card/50 rounded-lg p-3 text-center">
                                <div className="text-2xl font-bold text-primary">
                                    {validation.info.estimated_documents || 0}
                                </div>
                                <div className="text-xs text-muted-foreground">Est. Documents</div>
                            </div>
                            <div className="bg-card/50 rounded-lg p-3 text-center">
                                <div className="text-2xl font-bold text-primary">
                                    {((validation.info.estimated_tokens || 0) / 1000).toFixed(1)}K
                                </div>
                                <div className="text-xs text-muted-foreground">Est. Tokens</div>
                            </div>
                            <div className="bg-card/50 rounded-lg p-3 text-center">
                                <div className="text-2xl font-bold text-green-400">
                                    ${validation.info.estimated_cost_usd || '0.00'}
                                </div>
                                <div className="text-xs text-muted-foreground">Est. Cost</div>
                            </div>
                        </div>
                    )}

                    {/* Optimization Recommendations */}
                    {validation.valid && (validation.warnings.length > 0 || chunkSize > 1000 || chunkOverlap > 150) && (
                        <div className="mt-4 bg-amber-500/5 border border-amber-500/20 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Zap className="w-4 h-4 text-amber-500" />
                                <h4 className="text-sm font-semibold text-amber-500">Optimization Advisor (Phase 10)</h4>
                            </div>
                            <ul className="text-sm text-zinc-300 space-y-1">
                                {validation.warnings.map((w, i) => (
                                    <li key={i} className="flex gap-2">
                                        <span className="text-amber-500">•</span>
                                        <span>{w}</span>
                                    </li>
                                ))}
                                {chunkSize > 1000 && (
                                    <li className="flex gap-2">
                                        <span className="text-amber-500">•</span>
                                        <span>Consider reducing chunk size to 800 for better retrieval accuracy.</span>
                                    </li>
                                )}
                                {chunkOverlap > 150 && (
                                    <li className="flex gap-2">
                                        <span className="text-amber-500">•</span>
                                        <span>Consider reducing overlap to 100-120 for ~10% token savings.</span>
                                    </li>
                                )}
                            </ul>
                        </div>
                    )}
                </div>
            )}

            {/* Ingestion Result */}
            {result && (
                <div className={clsx(
                    "border rounded-xl p-5",
                    result.success
                        ? "bg-green-500/5 border-green-500/20"
                        : "bg-red-500/5 border-red-500/20"
                )}>
                    <div className="flex items-center gap-2">
                        {result.success ? (
                            <CheckCircle className="w-5 h-5 text-green-500" />
                        ) : (
                            <AlertCircle className="w-5 h-5 text-red-500" />
                        )}
                        <h3 className="font-semibold text-white">
                            {result.success ? 'Ingestion Complete!' : 'Ingestion Failed'}
                        </h3>
                    </div>
                    {result.success ? (
                        <div className="mt-3 space-y-2">
                            <p className="text-sm text-zinc-300">
                                Successfully indexed <strong>{result.documents_ingested}</strong> documents
                                into <code className="bg-zinc-800 px-1.5 py-0.5 rounded text-primary">{result.collection}</code>
                            </p>
                            {result.validation?.duplicates_skipped > 0 && (
                                <div className="flex items-center gap-2 text-xs text-amber-400 bg-amber-400/10 w-fit px-2 py-1 rounded">
                                    <Zap className="w-3 h-3" />
                                    <span>P3 Similarity Engine: Skipped {result.validation.duplicates_skipped} duplicate chunks</span>
                                </div>
                            )}
                        </div>
                    ) : (
                        <p className="text-sm text-red-400 mt-2">{result.error}</p>
                    )}
                </div>
            )}
        </div>
    );
}
