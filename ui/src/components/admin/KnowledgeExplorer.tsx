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

    // Browsing state
    const [documents, setDocuments] = useState<any[]>([]);
    const [docOffset, setDocOffset] = useState(0);
    const [isLoadDocs, setIsLoadDocs] = useState(false);
    const [expandedDoc, setExpandedDoc] = useState<string | null>(null);

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
        setDocuments([]);
        setDocOffset(0);
        setExpandedDoc(null);
        try {
            const resp = await fetch(`http://localhost:8000/admin/collections/${name}/stats`);
            if (!resp.ok) throw new Error('Failed to load stats');
            const data = await resp.json();
            setStats(data.stats);
        } catch (e) {
            console.error('Failed to load stats', e);
        }
    };

    const loadDocuments = async (offset = 0) => {
        if (!selectedCollection) return;
        setIsLoadDocs(true);
        try {
            const resp = await fetch(`http://localhost:8000/admin/collections/${selectedCollection}/documents?limit=10&offset=${offset}`);
            if (!resp.ok) throw new Error('Failed to load documents');
            const data = await resp.json();
            if (offset === 0) {
                setDocuments(data.documents);
            } else {
                setDocuments(prev => [...prev, ...data.documents]);
            }
            setDocOffset(offset);
        } catch (e) {
            console.error('Failed to load documents', e);
        } finally {
            setIsLoadDocs(false);
        }
    };

    const deleteDocument = async (docId: string) => {
        if (!selectedCollection || !confirm('Delete this document chunk?')) return;
        try {
            const resp = await fetch(`http://localhost:8000/admin/collections/${selectedCollection}/documents/${docId}`, {
                method: 'DELETE'
            });
            if (resp.ok) {
                setDocuments(prev => prev.filter(d => d.id !== docId));
                if (stats) setStats({ ...stats, count: stats.count - 1 });
            }
        } catch (e) {
            console.error('Delete failed', e);
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
                setDocuments([]);
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
                body: JSON.stringify({ query: queryText, top_k: 5, collection: selectedCollection }),
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
        <div className="space-y-6 pb-20">
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
                <div className="grid md:grid-cols-2 gap-6 items-start">
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
                                            <button
                                                onClick={() => loadDocuments(0)}
                                                className="flex flex-col items-center justify-center bg-primary/10 border border-primary/20 rounded-lg p-3 hover:bg-primary/20 transition-colors"
                                            >
                                                <Search className="w-5 h-5 text-primary mb-1" />
                                                <div className="text-xs font-medium">Browse Files</div>
                                            </button>
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
                                                    <div key={i} className="bg-background border border-border rounded-lg p-3 text-xs">
                                                        <div className="flex justify-between mb-1 text-muted-foreground">
                                                            <span className="font-mono">
                                                                Score: {typeof r.score === 'number' ? r.score.toFixed(3) : 'N/A'}
                                                            </span>
                                                            {r.metadata?.source && <span>{r.metadata.source}</span>}
                                                        </div>
                                                        <p className="text-foreground line-clamp-3">
                                                            {r.text || r.document?.text}
                                                        </p>
                                                    </div>
                                                ))
                                            )}
                                        </div>
                                    )}
                                </div>

                                {/* Document Browser */}
                                {documents.length > 0 && (
                                    <div className="bg-card border border-border rounded-xl p-5 space-y-3">
                                        <div className="flex items-center justify-between">
                                            <h4 className="text-sm font-semibold">Document Browser</h4>
                                            <span className="text-xs text-muted-foreground">Showing {documents.length} of {stats?.count}</span>
                                        </div>
                                        <div className="space-y-2 max-h-96 overflow-y-auto">
                                            {documents.map((doc) => (
                                                <div key={doc.id} className="bg-background border border-border rounded-lg overflow-hidden transition-all">
                                                    <div
                                                        onClick={() => setExpandedDoc(expandedDoc === doc.id ? null : doc.id)}
                                                        className="p-3 text-xs flex items-center justify-between cursor-pointer hover:bg-muted/30"
                                                    >
                                                        <div className="flex-1 truncate mr-4">
                                                            <span className="font-mono text-primary mr-2 opacity-50">[{doc.id.split('_').pop()}]</span>
                                                            <span className="text-foreground">{doc.metadata?.file || doc.id}</span>
                                                        </div>
                                                        <div className="flex items-center gap-2">
                                                            <button
                                                                onClick={(e) => { e.stopPropagation(); deleteDocument(doc.id); }}
                                                                className="p-1 hover:text-red-500 rounded transition-colors"
                                                            >
                                                                <Trash2 className="w-3.5 h-3.5" />
                                                            </button>
                                                        </div>
                                                    </div>
                                                    {expandedDoc === doc.id && (
                                                        <div className="p-3 bg-muted/20 border-t border-border space-y-3">
                                                            <div className="text-[11px] font-mono text-muted-foreground bg-black/20 p-2 rounded max-h-60 overflow-y-auto whitespace-pre-wrap">
                                                                {doc.text}
                                                            </div>
                                                            <div className="flex flex-wrap gap-2">
                                                                {Object.entries(doc.metadata || {}).map(([k, v]) => (
                                                                    <div key={k} className="text-[10px] bg-secondary px-1.5 py-0.5 rounded">
                                                                        <span className="opacity-60">{k}:</span> {String(v)}
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                        {stats && documents.length < stats.count && (
                                            <button
                                                onClick={() => loadDocuments(docOffset + 10)}
                                                disabled={isLoadDocs}
                                                className="w-full py-2 text-xs text-primary hover:bg-primary/5 rounded-lg border border-dashed border-primary/30 transition-all font-medium"
                                            >
                                                {isLoadDocs ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Load More Documents'}
                                            </button>
                                        )}
                                    </div>
                                )}
                            </>
                        ) : (
                            <div className="bg-card border border-dashed border-border rounded-xl p-8 text-center h-full flex items-center justify-center min-h-[300px]">
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
