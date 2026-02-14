import * as React from 'react';
import { useState } from 'react';
import { Database, Search, X, Eye } from 'lucide-react';
import { UniversalIngestionPanel } from './knowledge/UniversalIngestionPanel';
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

    const [collections, setCollections] = useState<any[]>([]);
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
        <div className="p-6 w-full space-y-8">
            <div className="flex items-center gap-3 mb-6">
                <Database className="w-6 h-6 text-primary" />
                <h1 className="text-2xl font-bold">Knowledge Base Management</h1>
            </div>

            {/* Refactored Layout: Ingestion Panel (Full Width) + Bottom Grid */}
            <div className="w-full">
                <UniversalIngestionPanel onIngestSuccess={fetchCollections} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Test Retrieval */}
                <div className="lg:col-span-2">
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

                {/* Right Column: Active Collections */}
                <div className="space-y-6">
                    <div className="bg-muted/30 border border-border rounded-lg p-6">
                        <div className="text-center text-muted-foreground/60">
                            <Database className="w-8 h-8 mx-auto mb-2 opacity-50" />
                            <p className="text-sm font-medium text-foreground mb-4">Active Collections</p>

                            {collections.length === 0 ? (
                                <p className="text-xs italic">No collections found.</p>
                            ) : (
                                <div className="space-y-2 text-left">
                                    {collections.map((col: any) => (
                                        <div key={col.name} className="flex justify-between items-center text-xs font-mono bg-background p-2 rounded border border-border/50">
                                            <span>{col.name} <span className="text-muted-foreground ml-1">({col.count})</span></span>
                                            <div className="flex gap-1">
                                                <button
                                                    onClick={() => handleViewDocuments(col.name)}
                                                    className="text-primary hover:text-primary/80 p-1"
                                                    title="View Documents"
                                                >
                                                    <Eye className="w-3 h-3" />
                                                </button>
                                                <button
                                                    onClick={() => handleDeleteCollection(col.name)}
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
                                    {collectionDocuments.map((doc: any, idx: number) => {
                                        let folderPath = doc.metadata?.full_path || doc.metadata?.file;
                                        if (!folderPath && doc.metadata?.component_info) {
                                            try {
                                                const info = JSON.parse(doc.metadata.component_info);
                                                folderPath = info.folder_path;
                                            } catch (e) { }
                                        }

                                        return (
                                            <div key={idx} className="bg-muted/30 border border-border rounded-lg p-4">
                                                <div className="flex flex-col gap-1 mb-2">
                                                    <div className="flex justify-between items-center">
                                                        <span className="text-xs font-mono text-primary">{doc.id}</span>
                                                        <span className="text-[10px] text-muted-foreground bg-secondary/50 px-2 py-0.5 rounded uppercase">
                                                            {doc.metadata?.component || doc.metadata?.type || 'Unknown'}
                                                        </span>
                                                    </div>
                                                    {folderPath && (
                                                        <div className="text-[10px] text-muted-foreground font-mono opacity-70 break-all select-all">
                                                            📍 {folderPath}
                                                        </div>
                                                    )}
                                                </div>
                                                <div className="text-sm text-foreground whitespace-pre-wrap max-h-40 overflow-y-auto font-mono text-xs">
                                                    {doc.text.substring(0, 500)}
                                                    {doc.text.length > 500 && '...'}
                                                </div>
                                                {doc.metadata && Object.keys(doc.metadata).length > 0 && (
                                                    <details className="mt-2">
                                                        <summary className="text-xs text-muted-foreground cursor-pointer hover:text-foreground transition-colors">Metadata</summary>
                                                        <pre className="text-[10px] mt-1 bg-background p-2 rounded overflow-x-auto border border-border/50">
                                                            {JSON.stringify(doc.metadata, null, 2)}
                                                        </pre>
                                                    </details>
                                                )}
                                            </div>
                                        );
                                    })}
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
