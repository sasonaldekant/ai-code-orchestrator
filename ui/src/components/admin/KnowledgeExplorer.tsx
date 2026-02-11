import { useState, useEffect } from 'react';
import { BookOpen, Trash2, RefreshCw, Loader2, Search, Database, AlertCircle, CheckCircle } from 'lucide-react';
import clsx from 'clsx';

interface Collection {
    name: string;
    count: number;
    metadata: Record<string, any>;
}

interface CollectionStats {
    count: number;
    metadata?: Record<string, any>;
}

export function KnowledgeExplorer() {
    const [collections, setCollections] = useState<Collection[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedCollection, setSelectedCollection] = useState<string | null>(null);
    const [stats, setStats] = useState<CollectionStats | null>(null);
    const [isDeleting, setIsDeleting] = useState<string | null>(null);
    const [deleteResult, setDeleteResult] = useState<{ success: boolean; message: string } | null>(null);

    // Query state
    const [queryText, setQueryText] = useState('');
    const [queryResults, setQueryResults] = useState<any[] | null>(null);
    const [isQuerying, setIsQuerying] = useState(false);

    useEffect(() => {
        loadCollections();
    }, []);

    const loadCollections = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const resp = await fetch('http://localhost:8000/admin/collections');
            if (!resp.ok) throw new Error('Failed to load');
            const data = await resp.json();
            setCollections(data.collections || []);
        } catch (e) {
            setError('Failed to load collections. Is ChromaDB running?');
        } finally {
            setIsLoading(false);
        }
    };

    const loadStats = async (name: string) => {
        setSelectedCollection(name);
        setStats(null);
        setQueryResults(null);
        try {
            const resp = await fetch(`http://localhost:8000/admin/collections/${name}/stats`);
            if (!resp.ok) throw new Error('Failed to load stats');
            const data = await resp.json();
            setStats(data.stats);
        } catch (e) {
            console.error('Failed to load stats', e);
        }
    };

    const deleteCollection = async (name: string) => {
        if (!confirm(`Are you sure you want to delete collection "${name}"? This cannot be undone.`)) {
            return;
        }

        setIsDeleting(name);
        setDeleteResult(null);
        try {
            const resp = await fetch(`http://localhost:8000/admin/collections/${name}`, {
                method: 'DELETE',
            });
            if (!resp.ok) throw new Error('Failed to delete');
            setDeleteResult({ success: true, message: `Collection "${name}" deleted` });
            setCollections(c => c.filter(col => col.name !== name));
            if (selectedCollection === name) {
                setSelectedCollection(null);
                setStats(null);
            }
        } catch (e) {
            setDeleteResult({ success: false, message: 'Failed to delete collection' });
        } finally {
            setIsDeleting(null);
        }
    };

    const runQuery = async () => {
        if (!queryText.trim() || !selectedCollection) return;
        setIsQuerying(true);
        setQueryResults(null);
        try {
            const resp = await fetch('http://localhost:8000/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: queryText, top_k: 5 }),
            });
            if (!resp.ok) throw new Error('Query failed');
            const data = await resp.json();
            setQueryResults(data.results || []);
        } catch (e) {
            setQueryResults([]);
        } finally {
            setIsQuerying(false);
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
                <button onClick={loadCollections} className="mt-4 px-4 py-2 bg-red-500/20 rounded-lg text-sm">
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">Knowledge Base Explorer</h2>
                    <p className="text-muted-foreground mt-1">
                        View, query, and manage RAG vector collections.
                    </p>
                </div>
                <button
                    onClick={loadCollections}
                    className="flex items-center gap-2 px-3 py-2 bg-secondary rounded-lg text-sm hover:bg-secondary/80"
                >
                    <RefreshCw className="w-4 h-4" />
                    Refresh
                </button>
            </div>

            {/* Delete Result */}
            {deleteResult && (
                <div className={clsx(
                    "flex items-center gap-2 p-3 rounded-lg text-sm",
                    deleteResult.success ? "bg-green-500/10 text-green-400" : "bg-red-500/10 text-red-400"
                )}>
                    {deleteResult.success ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                    {deleteResult.message}
                </div>
            )}

            {collections.length === 0 ? (
                <div className="bg-card border border-dashed border-border rounded-xl p-8 text-center">
                    <Database className="w-12 h-12 mx-auto text-muted-foreground/40" />
                    <h3 className="text-lg font-semibold mt-4">No Collections Found</h3>
                    <p className="text-muted-foreground mt-2">
                        Use the Ingestion panel to add knowledge to the RAG system.
                    </p>
                </div>
            ) : (
                <div className="grid md:grid-cols-2 gap-6">
                    {/* Collection List */}
                    <div className="space-y-3">
                        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                            Collections ({collections.length})
                        </h3>
                        {collections.map(col => (
                            <div
                                key={col.name}
                                onClick={() => loadStats(col.name)}
                                className={clsx(
                                    "bg-card border rounded-xl p-4 cursor-pointer transition-all hover:border-primary/50",
                                    selectedCollection === col.name ? "border-primary ring-1 ring-primary/20" : "border-border"
                                )}
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <BookOpen className="w-5 h-5 text-primary" />
                                        <div>
                                            <h4 className="font-semibold">{col.name}</h4>
                                            <p className="text-xs text-muted-foreground">
                                                {col.count} documents
                                            </p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            deleteCollection(col.name);
                                        }}
                                        disabled={isDeleting === col.name}
                                        className="p-2 text-muted-foreground hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-colors disabled:opacity-50"
                                    >
                                        {isDeleting === col.name ? (
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                        ) : (
                                            <Trash2 className="w-4 h-4" />
                                        )}
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Selected Collection Details */}
                    <div className="space-y-4">
                        {selectedCollection ? (
                            <>
                                <div className="bg-card border border-border rounded-xl p-5">
                                    <h3 className="font-semibold mb-3">Collection: {selectedCollection}</h3>
                                    {stats ? (
                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="bg-background rounded-lg p-3 text-center">
                                                <div className="text-2xl font-bold text-primary">{stats.count}</div>
                                                <div className="text-xs text-muted-foreground">Documents</div>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="flex items-center justify-center h-20">
                                            <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
                                        </div>
                                    )}
                                </div>

                                {/* Query Test */}
                                <div className="bg-card border border-border rounded-xl p-5">
                                    <h4 className="text-sm font-semibold mb-3">Test Query</h4>
                                    <div className="flex gap-2">
                                        <input
                                            type="text"
                                            value={queryText}
                                            onChange={(e) => setQueryText(e.target.value)}
                                            onKeyDown={(e) => e.key === 'Enter' && runQuery()}
                                            placeholder="Search documents..."
                                            className="flex-1 px-3 py-2 bg-background border border-border rounded-lg text-sm"
                                        />
                                        <button
                                            onClick={runQuery}
                                            disabled={isQuerying || !queryText.trim()}
                                            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg disabled:opacity-50"
                                        >
                                            {isQuerying ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                                        </button>
                                    </div>

                                    {queryResults !== null && (
                                        <div className="mt-4 space-y-2 max-h-60 overflow-y-auto">
                                            {queryResults.length === 0 ? (
                                                <p className="text-sm text-muted-foreground italic">No results found</p>
                                            ) : (
                                                queryResults.map((r, i) => (
                                                    <div key={i} className="bg-background rounded-lg p-3 text-xs">
                                                        <div className="flex justify-between mb-1">
                                                            <span className="font-mono text-muted-foreground">
                                                                Score: {typeof r.score === 'number' ? r.score.toFixed(3) : 'N/A'}
                                                            </span>
                                                        </div>
                                                        <p className="text-foreground line-clamp-3">
                                                            {r.document?.text || r.text || JSON.stringify(r)}
                                                        </p>
                                                    </div>
                                                ))
                                            )}
                                        </div>
                                    )}
                                </div>
                            </>
                        ) : (
                            <div className="bg-card border border-dashed border-border rounded-xl p-8 text-center h-full flex items-center justify-center">
                                <div>
                                    <Search className="w-8 h-8 mx-auto text-muted-foreground/40" />
                                    <p className="text-muted-foreground mt-2">Select a collection to view details</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
