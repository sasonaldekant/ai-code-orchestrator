import React, { useState, useEffect } from 'react';
import { DollarSign, Save, RefreshCw, Loader2, CheckCircle, AlertCircle, Zap } from 'lucide-react';
import clsx from 'clsx';

interface LimitsConfig {
    budgets: {
        max_input_tokens: number;
        max_output_tokens: number;
    };
    retrieval: {
        top_k: number;
        chunk_chars: number;
        chunk_overlap: number;
    };
    concurrency: {
        max_workers: number;
    };
}

export function BudgetPanel() {
    const [config, setConfig] = useState<LimitsConfig | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [saveResult, setSaveResult] = useState<{ success: boolean; message: string } | null>(null);

    useEffect(() => {
        loadConfig();
    }, []);

    const loadConfig = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const resp = await fetch('http://localhost:8000/admin/config/limits');
            if (!resp.ok) throw new Error('Failed to load');
            const data = await resp.json();
            setConfig(data.data);
        } catch (e) {
            setError('Failed to load limits configuration');
        } finally {
            setIsLoading(false);
        }
    };

    const saveConfig = async () => {
        if (!config) return;
        setIsSaving(true);
        setSaveResult(null);
        try {
            const resp = await fetch('http://localhost:8000/admin/config/limits', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: config }),
            });
            if (!resp.ok) throw new Error('Failed to save');
            setSaveResult({ success: true, message: 'Limits saved successfully' });
        } catch (e) {
            setSaveResult({ success: false, message: 'Failed to save limits' });
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6 text-center">
                <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-2" />
                <p className="text-red-400">{error}</p>
                <button onClick={loadConfig} className="mt-4 px-4 py-2 bg-red-500/20 rounded-lg text-sm">
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">Budgets & Limits</h2>
                    <p className="text-muted-foreground mt-1">
                        Configure token limits, retrieval settings, and concurrency.
                    </p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={loadConfig}
                        className="flex items-center gap-2 px-3 py-2 bg-secondary rounded-lg text-sm hover:bg-secondary/80"
                    >
                        <RefreshCw className="w-4 h-4" />
                        Reload
                    </button>
                    <button
                        onClick={saveConfig}
                        disabled={isSaving}
                        className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm hover:bg-primary/90 disabled:opacity-50"
                    >
                        {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                        Save Changes
                    </button>
                </div>
            </div>

            {/* Save Result */}
            {saveResult && (
                <div className={clsx(
                    "flex items-center gap-2 p-3 rounded-lg text-sm",
                    saveResult.success ? "bg-green-500/10 text-green-400" : "bg-red-500/10 text-red-400"
                )}>
                    {saveResult.success ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                    {saveResult.message}
                </div>
            )}

            {/* Token Budgets */}
            <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center gap-2 mb-4">
                    <DollarSign className="w-5 h-5 text-green-500" />
                    <h3 className="text-sm font-semibold uppercase tracking-wide">Token Budgets</h3>
                </div>
                <div className="grid grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium mb-2">Max Input Tokens</label>
                        <input
                            type="number"
                            value={config?.budgets?.max_input_tokens || 6000}
                            onChange={(e) => setConfig(c => c ? {
                                ...c,
                                budgets: { ...c.budgets, max_input_tokens: parseInt(e.target.value) }
                            } : c)}
                            className="w-full px-4 py-2.5 bg-background border border-border rounded-lg text-sm"
                        />
                        <p className="text-xs text-muted-foreground mt-1">Maximum tokens for context/prompt</p>
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-2">Max Output Tokens</label>
                        <input
                            type="number"
                            value={config?.budgets?.max_output_tokens || 1000}
                            onChange={(e) => setConfig(c => c ? {
                                ...c,
                                budgets: { ...c.budgets, max_output_tokens: parseInt(e.target.value) }
                            } : c)}
                            className="w-full px-4 py-2.5 bg-background border border-border rounded-lg text-sm"
                        />
                        <p className="text-xs text-muted-foreground mt-1">Maximum tokens for LLM response</p>
                    </div>
                </div>
            </div>

            {/* Retrieval Settings */}
            <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center gap-2 mb-4">
                    <Zap className="w-5 h-5 text-amber-500" />
                    <h3 className="text-sm font-semibold uppercase tracking-wide">Retrieval Settings</h3>
                </div>
                <div className="grid grid-cols-3 gap-6">
                    <div>
                        <label className="block text-sm font-medium mb-2">Top-K Results</label>
                        <input
                            type="number"
                            min="1"
                            max="20"
                            value={config?.retrieval?.top_k || 4}
                            onChange={(e) => setConfig(c => c ? {
                                ...c,
                                retrieval: { ...c.retrieval, top_k: parseInt(e.target.value) }
                            } : c)}
                            className="w-full px-4 py-2.5 bg-background border border-border rounded-lg text-sm"
                        />
                        <p className="text-xs text-muted-foreground mt-1">Number of documents to retrieve</p>
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-2">Chunk Size (chars)</label>
                        <input
                            type="number"
                            value={config?.retrieval?.chunk_chars || 800}
                            onChange={(e) => setConfig(c => c ? {
                                ...c,
                                retrieval: { ...c.retrieval, chunk_chars: parseInt(e.target.value) }
                            } : c)}
                            className="w-full px-4 py-2.5 bg-background border border-border rounded-lg text-sm"
                        />
                        <p className="text-xs text-muted-foreground mt-1">Characters per document chunk</p>
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-2">Chunk Overlap (chars)</label>
                        <input
                            type="number"
                            value={config?.retrieval?.chunk_overlap || 120}
                            onChange={(e) => setConfig(c => c ? {
                                ...c,
                                retrieval: { ...c.retrieval, chunk_overlap: parseInt(e.target.value) }
                            } : c)}
                            className="w-full px-4 py-2.5 bg-background border border-border rounded-lg text-sm"
                        />
                        <p className="text-xs text-muted-foreground mt-1">Overlap between chunks</p>
                    </div>
                </div>
            </div>

            {/* Concurrency */}
            <div className="bg-card border border-border rounded-xl p-5">
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-4">
                    Concurrency
                </h3>
                <div className="max-w-xs">
                    <label className="block text-sm font-medium mb-2">Max Workers</label>
                    <input
                        type="number"
                        min="1"
                        max="8"
                        value={config?.concurrency?.max_workers || 2}
                        onChange={(e) => setConfig(c => c ? {
                            ...c,
                            concurrency: { ...c.concurrency, max_workers: parseInt(e.target.value) }
                        } : c)}
                        className="w-full px-4 py-2.5 bg-background border border-border rounded-lg text-sm"
                    />
                    <p className="text-xs text-muted-foreground mt-1">Parallel task execution limit</p>
                </div>
            </div>

            {/* Cost Budgets - Read-only info since from different config */}
            <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center gap-2 mb-4">
                    <DollarSign className="w-5 h-5 text-emerald-500" />
                    <h3 className="text-sm font-semibold uppercase tracking-wide">Cost Budgets</h3>
                    <span className="text-xs bg-muted px-2 py-0.5 rounded-full">from model_mapping_v2.yaml</span>
                </div>
                <div className="grid grid-cols-3 gap-6">
                    <div className="bg-background rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-emerald-400">$0.50</div>
                        <div className="text-xs text-muted-foreground mt-1">Per Task Budget</div>
                    </div>
                    <div className="bg-background rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-emerald-400">$40.00</div>
                        <div className="text-xs text-muted-foreground mt-1">Per Day Budget</div>
                    </div>
                    <div className="bg-background rounded-lg p-4 text-center">
                        <div className="text-2xl font-bold text-emerald-400">$800.00</div>
                        <div className="text-xs text-muted-foreground mt-1">Per Month Budget</div>
                    </div>
                </div>
                <p className="text-xs text-muted-foreground mt-4 italic">
                    Edit cost budgets in Model Config → cost_management section
                </p>
            </div>
        </div>
    );
}
