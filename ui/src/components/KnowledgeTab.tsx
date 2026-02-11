import * as React from 'react';
import { useState } from 'react';
import { Upload, Database, FileCode, CheckCircle, AlertCircle, RefreshCw, Search, X, Eye } from 'lucide-react';
import clsx from 'clsx';

interface SearchResult {
    score: number;
    text: string;
    metadata?: {
        source?: string;
        [key: string]: any;
    };
}

export function KnowledgeTab() {
    const [ingestType, setIngestType] = useState<'database' | 'component_library'>('component_library');
    const [path, setPath] = useState('');
    const [collectionName, setCollectionName] = useState('');
    const [isIngesting, setIsIngesting] = useState(false);
    const [status, setStatus] = useState<{ type: 'success' | 'error', message: string } | null>(null);
    const [collections, setCollections] = useState<string[]>([]);
    const [testQuery, setTestQuery] = useState('');
    const [testResults, setTestResults] = useState<SearchResult[]>([]);
    const [isTesting, setIsTesting] = useState(false);
    const [selectedCollection, setSelectedCollection] = useState<string | null>(null);
    const [collectionDocuments, setCollectionDocuments] = useState<any[]>([]);

    const fetchCollections = () => {
        fetch('http://localhost:8000/knowledge/collections')
            .then(res => res.json())
            .then(data => setCollections(data.collections || []))
            .catch(err => console.error("Failed to fetch collections", err));
    };

    React.useEffect(() => {
        fetchCollections();
    }, []);

    const handleIngest = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!path) return;

        setIsIngesting(true);
        setStatus(null);

        try {
            const resp = await fetch('http://localhost:8000/knowledge/ingest', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: ingestType,
                    path: path,
                    collection: collectionName || undefined
                })
            });

            const data = await resp.json();

            if (resp.ok) {
                setStatus({ type: 'success', message: `Successfully ingested ${data.documents_ingested} documents into '${data.collection}'` });
                setPath('');
                setCollectionName('');
                fetchCollections();
            } else {
                setStatus({ type: 'error', message: data.detail || 'Ingestion failed' });
            }
        } catch (err) {
            setStatus({ type: 'error', message: 'Failed to connect to API' });
        } finally {
            setIsIngesting(false);
        }
    };

    const handleTestQuery = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!testQuery) return;
        setIsTesting(true);

        try {
            const resp = await fetch('http://localhost:8000/knowledge/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: testQuery,
                    top_k: 3
                })
            });
            const data = await resp.json();
            if (data.results) {
                setTestResults(data.results);
            }
        } catch (error) {
            console.error(error);
        } finally {
            setIsTesting(false);
        }
    };

    const handleDeleteCollection = async (name: string) => {
        if (!confirm(`Are you sure you want to delete collection '${name}'?`)) return;
        try {
            await fetch(`http://localhost:8000/knowledge/collections/${name}`, { method: 'DELETE' });
            fetchCollections();
            if (selectedCollection === name) {
                setSelectedCollection(null);
                setCollectionDocuments([]);
            }
        } catch (error) {
            console.error(error);
        }
    };

    const handleViewDocuments = async (name: string) => {
        try {
            const resp = await fetch(`http://localhost:8000/knowledge/collections/${name}/documents`);
            const data = await resp.json();
            setSelectedCollection(name);
            setCollectionDocuments(data.documents || []);
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <div className="p-6 max-w-5xl mx-auto space-y-8">
            <div className="flex items-center gap-3 mb-6">
                <Database className="w-6 h-6 text-primary" />
                <h1 className="text-2xl font-bold">Knowledge Base Management</h1>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Ingestion */}
                <div className="lg:col-span-2 space-y-8">
                    <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <Upload className="w-5 h-5 text-muted-foreground" />
                            Ingest New Knowledge
                        </h2>

                        <form onSubmit={handleIngest} className="space-y-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Source Type</label>
                                <div className="flex gap-2 p-1 bg-muted/50 rounded-lg">
                                    <button
                                        type="button"
                                        onClick={() => setIngestType('database')}
                                        className={clsx(
                                            "flex-1 py-2 px-3 rounded-md text-sm font-medium transition-all flex items-center justify-center gap-2",
                                            ingestType === 'database' ? "bg-background shadow-sm text-primary" : "text-muted-foreground hover:text-foreground"
                                        )}
                                    >
                                        <Database className="w-4 h-4" />
                                        Database Schema
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => setIngestType('component_library')}
                                        className={clsx(
                                            "flex-1 py-2 px-3 rounded-md text-sm font-medium transition-all flex items-center justify-center gap-2",
                                            ingestType === 'component_library' ? "bg-background shadow-sm text-primary" : "text-muted-foreground hover:text-foreground"
                                        )}
                                    >
                                        <FileCode className="w-4 h-4" />
                                        Component Library
                                    </button>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium">Source Path (Absolute)</label>
                                <input
                                    type="text"
                                    value={path}
                                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPath(e.target.value)}
                                    placeholder={ingestType === 'database' ? "e.g., C:/projects/myapp/backend" : "e.g., C:/projects/myapp/src/components"}
                                    className="w-full px-3 py-2 bg-background border border-border rounded-md focus:ring-1 focus:ring-primary outline-none"
                                    required
                                />
                                <p className="text-xs text-muted-foreground">
                                    Enter the <strong>absolute path</strong> to the directory on your local machine.
                                    The backend will read files directly from this location.
                                </p>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium">Collection Name (Optional)</label>
                                <input
                                    type="text"
                                    value={collectionName}
                                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCollectionName(e.target.value)}
                                    placeholder="Auto-generated if empty"
                                    className="w-full px-3 py-2 bg-background border border-border rounded-md focus:ring-1 focus:ring-primary outline-none"
                                />
                            </div>

                            {status && (
                                <div className={clsx(
                                    "p-3 rounded-md text-sm flex items-start gap-2",
                                    status.type === 'success' ? "bg-green-500/10 text-green-600" : "bg-red-500/10 text-red-600"
                                )}>
                                    {status.type === 'success' ? <CheckCircle className="w-4 h-4 mt-0.5" /> : <AlertCircle className="w-4 h-4 mt-0.5" />}
                                    {status.message}
                                </div>
                            )}

                            <button
                                type="submit"
                                disabled={isIngesting || !path}
                                className="w-full py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium flex items-center justify-center gap-2"
                            >
                                {isIngesting ? (
                                    <>
                                        <RefreshCw className="w-4 h-4 animate-spin" />
                                        Ingesting...
                                    </>
                                ) : (
                                    "Start Ingestion"
                                )}
                            </button>
                        </form>
                    </div>

                    {/* Test Retrieval Section */}
                    <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <Search className="w-5 h-5 text-muted-foreground" />
                            Test Retrieval
                        </h2>
                        <form onSubmit={handleTestQuery} className="flex gap-2">
                            <input
                                type="text"
                                value={testQuery}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTestQuery(e.target.value)}
                                placeholder="Search query..."
                                className="flex-1 px-3 py-2 bg-background border border-border rounded-md outline-none focus:ring-1 focus:ring-primary"
                            />
                            <button type="submit" disabled={isTesting} className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80">
                                {isTesting ? "..." : "Search"}
                            </button>
                        </form>

                        {testResults.length > 0 && (
                            <div className="mt-4 space-y-3">
                                {testResults.map((res: SearchResult, i: number) => (
                                    <div key={i} className="p-3 bg-muted/30 rounded-md border border-border text-sm">
                                        <div className="font-semibold text-xs text-primary mb-1 uppercase tracking-wider">
                                            Score: {(res.score * 100).toFixed(1)}%
                                        </div>
                                        <p className="line-clamp-3 text-muted-foreground">{res.text}</p>
                                        {res.metadata?.source && (
                                            <div className="mt-2 text-[10px] text-muted-foreground/60 font-mono">
                                                {res.metadata.source}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Right Column: Status / Info Panel */}
                <div className="space-y-6">
                    <div className="bg-card border border-border rounded-lg p-6 shadow-sm">
                        <h2 className="text-lg font-semibold mb-4">Ingestion Guide</h2>
                        <ul className="space-y-3 text-sm text-muted-foreground">
                            <li className="flex gap-2">
                                <span className="bg-primary/10 text-primary w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold shrink-0">1</span>
                                <div>
                                    <strong className="text-foreground">Database Schema:</strong> Point to your backend directory containing Entity Framework or ORM models.
                                </div>
                            </li>
                            <li className="flex gap-2">
                                <span className="bg-primary/10 text-primary w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold shrink-0">2</span>
                                <div>
                                    <strong className="text-foreground">Component Library:</strong> Point to your React/Frontend folder.
                                </div>
                            </li>
                            <li className="flex gap-2">
                                <span className="bg-primary/10 text-primary w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold shrink-0">3</span>
                                <div>
                                    <strong className="text-foreground">Vector Store:</strong> Data is stored key-value in ChromaDB.
                                </div>
                            </li>
                        </ul>
                    </div>

                    <div className="bg-muted/30 border border-border rounded-lg p-6">
                        <div className="text-center text-muted-foreground/60">
                            <Database className="w-8 h-8 mx-auto mb-2 opacity-50" />
                            <p className="text-sm font-medium text-foreground mb-4">Active Collections</p>

                            {collections.length === 0 ? (
                                <p className="text-xs italic">No collections found.</p>
                            ) : (
                                <div className="space-y-2 text-left">
                                    {collections.map((col: string) => (
                                        <div key={col} className="flex justify-between items-center text-xs font-mono bg-background p-2 rounded border border-border/50">
                                            <span>{col}</span>
                                            <div className="flex gap-1">
                                                <button
                                                    onClick={() => handleViewDocuments(col)}
                                                    className="text-primary hover:text-primary/80 p-1"
                                                    title="View Documents"
                                                >
                                                    <Eye className="w-3 h-3" />
                                                </button>
                                                <button
                                                    onClick={() => handleDeleteCollection(col)}
                                                    className="text-destructive hover:text-red-600 p-1"
                                                    title="Delete Collection"
                                                >
                                                    <X className="w-3 h-3" />
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Documents Viewer Modal */}
            {selectedCollection && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-card border border-border rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden flex flex-col">
                        <div className="p-4 border-b border-border flex justify-between items-center">
                            <h2 className="text-lg font-semibold">Documents in '{selectedCollection}'</h2>
                            <button
                                onClick={() => {
                                    setSelectedCollection(null);
                                    setCollectionDocuments([]);
                                }}
                                className="text-muted-foreground hover:text-foreground"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="p-4 overflow-y-auto flex-1">
                            {collectionDocuments.length === 0 ? (
                                <p className="text-muted-foreground text-center">No documents found.</p>
                            ) : (
                                <div className="space-y-4">
                                    {collectionDocuments.map((doc: any, idx: number) => (
                                        <div key={idx} className="bg-muted/30 border border-border rounded-lg p-4">
                                            <div className="flex justify-between items-start mb-2">
                                                <span className="text-xs font-mono text-primary">{doc.id}</span>
                                                <span className="text-xs text-muted-foreground">
                                                    {doc.metadata?.component || doc.metadata?.type || 'Unknown'}
                                                </span>
                                            </div>
                                            <div className="text-sm text-foreground whitespace-pre-wrap max-h-40 overflow-y-auto">
                                                {doc.text.substring(0, 500)}
                                                {doc.text.length > 500 && '...'}
                                            </div>
                                            {doc.metadata && Object.keys(doc.metadata).length > 0 && (
                                                <details className="mt-2">
                                                    <summary className="text-xs text-muted-foreground cursor-pointer">Metadata</summary>
                                                    <pre className="text-xs mt-1 bg-background p-2 rounded overflow-x-auto">
                                                        {JSON.stringify(doc.metadata, null, 2)}
                                                    </pre>
                                                </details>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                        <div className="p-4 border-t border-border text-sm text-muted-foreground">
                            Total: {collectionDocuments.length} documents
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
