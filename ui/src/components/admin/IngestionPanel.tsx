import React, { useState } from 'react';
import { Database, FolderOpen, CheckCircle, AlertCircle, Loader2, Upload, Info, Zap } from 'lucide-react';
import clsx from 'clsx';
import { PathSelector } from './PathSelector';

type IngestionType = 'database' | 'component_library' | 'project_codebase';

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
    const [type, setType] = useState<IngestionType>('database');
    const [path, setPath] = useState('');
    const [modelsDir, setModelsDir] = useState('');
    const [collection, setCollection] = useState('');
    const [chunkSize, setChunkSize] = useState(800);
    const [chunkOverlap, setChunkOverlap] = useState(120);

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
            const resp = await fetch('http://localhost:8000/admin/ingest/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type,
                    path,
                    models_dir: modelsDir || undefined,
                    collection: collection || undefined,
                    chunk_size: chunkSize,
                    chunk_overlap: chunkOverlap,
                }),
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
                {/* Type Selection */}
                <div>
                    <label className="block text-sm font-medium mb-2">Ingestion Type</label>
                    <div className="grid grid-cols-3 gap-3">
                        <button
                            onClick={() => setType('database')}
                            className={clsx(
                                "flex items-center justify-center gap-2 p-3 rounded-lg border transition-all",
                                type === 'database'
                                    ? "border-primary bg-primary/10 text-primary"
                                    : "border-border hover:border-primary/50"
                            )}
                        >
                            <Database className="w-5 h-5" />
                            <span className="font-medium">Database Schema</span>
                        </button>
                        <button
                            onClick={() => setType('component_library')}
                            className={clsx(
                                "flex items-center justify-center gap-2 p-3 rounded-lg border transition-all",
                                type === 'component_library'
                                    ? "border-primary bg-primary/10 text-primary"
                                    : "border-border hover:border-primary/50"
                            )}
                        >
                            <FolderOpen className="w-5 h-5" />
                            <span className="font-medium">Component Library</span>
                        </button>
                        <button
                            onClick={() => setType('project_codebase')}
                            className={clsx(
                                "flex items-center justify-center gap-2 p-3 rounded-lg border transition-all",
                                type === 'project_codebase'
                                    ? "border-emerald-500 bg-emerald-500/10 text-emerald-500"
                                    : "border-border hover:border-emerald-500/50"
                            )}
                        >
                            <Upload className="w-5 h-5" />
                            <span className="font-medium">Project Codebase</span>
                        </button>
                    </div>
                </div>

                {/* Path Input */}
                <PathSelector
                    label={
                        type === 'database' ? 'DbContext Path' :
                            type === 'component_library' ? 'Components Directory' :
                                'Project Root Path'
                    }
                    value={path}
                    onChange={setPath}
                    placeholder={
                        type === 'database' ? 'E:\\Project\\Backend\\Data' :
                            type === 'component_library' ? 'E:\\Project\\Frontend\\src\\components' :
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
                    <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-4">
                        Chunk Settings
                    </h3>
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

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4">
                    <button
                        onClick={handleValidate}
                        disabled={!path || isValidating}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-secondary text-secondary-foreground rounded-lg font-medium hover:bg-secondary/80 disabled:opacity-50 transition-all"
                    >
                        {isValidating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Info className="w-4 h-4" />}
                        Validate
                    </button>
                    <button
                        onClick={handleIngest}
                        disabled={!validation?.valid || isIngesting}
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
                    {validation.valid && (
                        <div className="mt-4 bg-amber-500/5 border border-amber-500/20 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Zap className="w-4 h-4 text-amber-500" />
                                <h4 className="text-sm font-semibold text-amber-500">Optimization Recommendations</h4>
                            </div>
                            <ul className="text-sm text-muted-foreground space-y-1">
                                {chunkSize === 800 && (
                                    <li>✓ Current chunk size (800) is optimal for most use cases</li>
                                )}
                                {chunkSize > 1000 && (
                                    <li>⚠ Consider reducing chunk size to 800 for better retrieval accuracy</li>
                                )}
                                {chunkOverlap > 150 && (
                                    <li>⚠ Consider reducing overlap to 100-120 for ~10% token savings</li>
                                )}
                                {chunkOverlap < 100 && (
                                    <li>⚠ Overlap below 100 may cause context loss between chunks</li>
                                )}
                                {(validation.info.cs_files_found || 0) > 50 && (
                                    <li>💡 Large codebase detected: consider filtering generated files (*.g.cs)</li>
                                )}
                                {(validation.info.estimated_tokens || 0) > 50000 && (
                                    <li>💡 High token count: consider splitting into multiple collections</li>
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
                        <h3 className="font-semibold">
                            {result.success ? 'Ingestion Complete!' : 'Ingestion Failed'}
                        </h3>
                    </div>
                    {result.success ? (
                        <p className="text-sm text-muted-foreground mt-2">
                            Successfully ingested <strong>{result.documents_ingested}</strong> documents
                            into collection <code className="bg-muted px-1 rounded">{result.collection}</code>
                        </p>
                    ) : (
                        <p className="text-sm text-red-400 mt-2">{result.error}</p>
                    )}
                </div>
            )}
        </div>
    );
}
