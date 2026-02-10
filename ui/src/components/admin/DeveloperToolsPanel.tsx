import React, { useState } from 'react';
import { FileText, Shield, Code, Play, CheckCircle, AlertTriangle, AlertOctagon, Info } from 'lucide-react';
import clsx from 'clsx';

type ToolTab = 'doc-gen' | 'code-review';

export function DeveloperToolsPanel() {
    const [activeTab, setActiveTab] = useState<ToolTab>('doc-gen');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);

    // Doc Gen State
    const [docType, setDocType] = useState<'openapi' | 'readme'>('openapi');
    const [code, setCode] = useState('');
    const [projectName, setProjectName] = useState('');
    const [projectDesc, setProjectDesc] = useState('');

    // Review State
    const [reviewContext, setReviewContext] = useState('');

    const handleDocGen = async () => {
        setLoading(true);
        setResult(null);
        try {
            const res = await fetch('http://localhost:8000/admin/tools/doc-gen', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    code,
                    type: docType,
                    project_name: projectName,
                    description: projectDesc,
                    features: ["Feature 1", "Feature 2"] // Hardcoded for simplified UI demo
                })
            });
            const data = await res.json();
            setResult(data);
        } catch (e) {
            console.error(e);
            alert("Error generating docs");
        } finally {
            setLoading(false);
        }
    };

    const handleCodeReview = async () => {
        setLoading(true);
        setResult(null);
        try {
            const res = await fetch('http://localhost:8000/admin/tools/code-review', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    code,
                    context: reviewContext
                })
            });
            const data = await res.json();
            setResult(data);
        } catch (e) {
            console.error(e);
            alert("Error reviewing code");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <header>
                <h2 className="text-2xl font-bold tracking-tight text-foreground">Developer Tools</h2>
                <p className="text-muted-foreground">Access specialist agents for documentation and code analysis.</p>
            </header>

            {/* Tabs */}
            <div className="flex gap-2 border-b border-border pb-1">
                <button
                    onClick={() => { setActiveTab('doc-gen'); setResult(null); }}
                    className={clsx(
                        "flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-t-lg transition-colors",
                        activeTab === 'doc-gen'
                            ? "bg-card border-x border-t border-border text-primary"
                            : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                    )}
                >
                    <FileText className="w-4 h-4" />
                    Documentation Generator
                </button>
                <button
                    onClick={() => { setActiveTab('code-review'); setResult(null); }}
                    className={clsx(
                        "flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-t-lg transition-colors",
                        activeTab === 'code-review'
                            ? "bg-card border-x border-t border-border text-primary"
                            : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                    )}
                >
                    <Shield className="w-4 h-4" />
                    Code Reviewer V2
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Input Column */}
                <div className="space-y-4">
                    <div className="p-4 bg-card rounded-lg border border-border space-y-4">
                        {activeTab === 'doc-gen' ? (
                            <>
                                <div>
                                    <label className="block text-sm font-medium mb-2">Generation Type</label>
                                    <div className="flex gap-4">
                                        <label className="flex items-center gap-2">
                                            <input
                                                type="radio"
                                                checked={docType === 'openapi'}
                                                onChange={() => setDocType('openapi')}
                                            />
                                            OpenAPI Spec (YAML)
                                        </label>
                                        <label className="flex items-center gap-2">
                                            <input
                                                type="radio"
                                                checked={docType === 'readme'}
                                                onChange={() => setDocType('readme')}
                                            />
                                            README.md
                                        </label>
                                    </div>
                                </div>

                                {docType === 'readme' && (
                                    <>
                                        <div>
                                            <label className="block text-sm font-medium mb-1">Project Name</label>
                                            <input
                                                className="w-full bg-input border border-border rounded p-2"
                                                value={projectName}
                                                onChange={(e) => setProjectName(e.target.value)}
                                                placeholder="e.g., MyAwesomeApp"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium mb-1">Description</label>
                                            <input
                                                className="w-full bg-input border border-border rounded p-2"
                                                value={projectDesc}
                                                onChange={(e) => setProjectDesc(e.target.value)}
                                                placeholder="Short description..."
                                            />
                                        </div>
                                    </>
                                )}

                                <div>
                                    <label className="block text-sm font-medium mb-1">
                                        {docType === 'openapi' ? 'API Code to Analyze' : 'Additional Context'}
                                    </label>
                                    <textarea
                                        className="w-full h-64 bg-input border border-border rounded p-2 font-mono text-sm"
                                        value={code}
                                        onChange={(e) => setCode(e.target.value)}
                                        placeholder={docType === 'openapi' ? "Paste your FastAPI/Flask code here..." : "Paste code snippets or context..."}
                                    />
                                </div>

                                <button
                                    onClick={handleDocGen}
                                    disabled={loading}
                                    className="w-full flex items-center justify-center gap-2 bg-primary text-primary-foreground py-2 rounded-lg hover:bg-primary/90 disabled:opacity-50"
                                >
                                    {loading ? 'Generating...' : <><Play className="w-4 h-4" /> Generate Documentation</>}
                                </button>
                            </>
                        ) : (
                            <>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Code to Review</label>
                                    <textarea
                                        className="w-full h-80 bg-input border border-border rounded p-2 font-mono text-sm"
                                        value={code}
                                        onChange={(e) => setCode(e.target.value)}
                                        placeholder="Paste Python/JS/C# code here..."
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Context</label>
                                    <input
                                        className="w-full bg-input border border-border rounded p-2"
                                        value={reviewContext}
                                        onChange={(e) => setReviewContext(e.target.value)}
                                        placeholder="e.g. Authentication module, high security requirement"
                                    />
                                </div>
                                <button
                                    onClick={handleCodeReview}
                                    disabled={loading}
                                    className="w-full flex items-center justify-center gap-2 bg-primary text-primary-foreground py-2 rounded-lg hover:bg-primary/90 disabled:opacity-50"
                                >
                                    {loading ? 'Reviewing...' : <><Shield className="w-4 h-4" /> Run Security Review</>}
                                </button>
                            </>
                        )}
                    </div>
                </div>

                {/* Output Column */}
                <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Results</h3>
                    {result ? (
                        <div className="bg-card border border-border rounded-lg p-4 overflow-auto max-h-[600px]">
                            {activeTab === 'doc-gen' ? (
                                <div>
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="text-xs font-mono bg-muted px-2 py-1 rounded uppercase">{result.format}</span>
                                        <button className="text-xs text-primary hover:underline">Copy</button>
                                    </div>
                                    <pre className="font-mono text-sm text-foreground/80 whitespace-pre-wrap">
                                        {result.content}
                                    </pre>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    <div className="flex items-center justify-between pb-4 border-b border-border">
                                        <div>
                                            <div className="text-3xl font-bold">{Math.round(result.score * 100)}/100</div>
                                            <div className="text-sm text-muted-foreground">Quality Score</div>
                                        </div>
                                        {result.passed ? (
                                            <div className="flex items-center gap-2 text-green-500 bg-green-500/10 px-3 py-1 rounded-full">
                                                <CheckCircle className="w-5 h-5" /> PASSED
                                            </div>
                                        ) : (
                                            <div className="flex items-center gap-2 text-red-500 bg-red-500/10 px-3 py-1 rounded-full">
                                                <AlertTriangle className="w-5 h-5" /> FAILED
                                            </div>
                                        )}
                                    </div>

                                    <p className="text-foreground">{result.summary}</p>

                                    <div className="space-y-2">
                                        <h4 className="font-medium text-sm text-muted-foreground uppercase">Issues Detected</h4>
                                        {result.issues.length === 0 && (
                                            <div className="text-sm text-muted-foreground italic">No issues found. Great job!</div>
                                        )}
                                        {result.issues.map((issue: any, idx: number) => (
                                            <div key={idx} className="p-3 bg-muted/50 rounded-lg border-l-4 border-l-primary flex gap-3">
                                                <div className={clsx(
                                                    "mt-0.5",
                                                    issue.severity === 'high' ? "text-red-500" :
                                                        issue.severity === 'medium' ? "text-yellow-500" : "text-blue-500"
                                                )}>
                                                    {issue.severity === 'high' ? <AlertOctagon className="w-4 h-4" /> :
                                                        <Info className="w-4 h-4" />}
                                                </div>
                                                <div>
                                                    <div className="font-medium text-sm flex gap-2 items-center">
                                                        <span className="uppercase text-xs font-bold opacity-70">{issue.type}</span>
                                                        <span>{issue.message}</span>
                                                    </div>
                                                    <div className="text-xs text-muted-foreground mt-1">Line {issue.line}: {issue.suggestion}</div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="h-64 flex items-center justify-center border border-dashed border-border rounded-lg text-muted-foreground">
                            {loading ? 'Processing...' : 'Run a tool to see results here.'}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
