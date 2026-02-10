import React, { useState } from 'react';
import type { LogEvent, ImplementationPlan } from '../lib/types';
import { useLogStream } from '../hooks/useLogStream';
import { Send, Upload, SquareCode, Activity, Play, Settings, Search, Sparkles, Globe, Wrench, X, ImageIcon } from 'lucide-react';
import clsx from 'clsx';
import { ThinkingBlock } from './ThinkingBlock';

interface OrchestratorUIProps {
    onOpenSettings?: () => void;
}

export function OrchestratorUI({ onOpenSettings }: OrchestratorUIProps) {
    const { logs, isConnected, plan, clearLogs } = useLogStream();
    const [prompt, setPrompt] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const scrollRef = React.useRef<HTMLDivElement>(null);
    const [activeTab, setActiveTab] = useState<'stream' | 'board' | 'graph'>('stream');

    // Phase 15: Deep Search State
    const [deepSearch, setDeepSearch] = useState(false);
    const [retrievalStrategy, setRetrievalStrategy] = useState<'local' | 'hybrid' | 'external'>('local');
    // Phase 16: Auto-Fix
    const [autoFix, setAutoFix] = useState(false);
    // Phase 16: Vision
    const [selectedImage, setSelectedImage] = useState<string | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setSelectedImage(reader.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!prompt.trim()) return;

        setIsLoading(true);
        clearLogs(); // Clear for new run

        try {
            let finalPrompt = prompt;

            // [Phase 16] Vision Analysis (if image present)
            if (selectedImage) {
                try {
                    const visionResp = await fetch('http://localhost:8000/vision/analyze', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            image: selectedImage,
                            prompt: "Analyze this image in the context of software development. If it's a UI mockup, describe the components and layout. If it's an error, identify the issue."
                        })
                    });

                    if (visionResp.ok) {
                        const visionData = await visionResp.json();
                        if (visionData.success && visionData.analysis) {
                            finalPrompt += `

[Vision Analysis Context]:
${visionData.analysis}`;
                        }
                    }
                } catch (err) {
                    console.error("Vision analysis failed", err);
                    // Continue without visual context.
                }
            }

            const resp = await fetch('http://localhost:8000/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    request: finalPrompt,
                    deep_search: deepSearch,
                    retrieval_strategy: retrievalStrategy,
                    auto_fix: autoFix
                })
            });

            if (!resp.ok) throw new Error('Failed to start');
        } catch (e) {
            console.error(e);
            alert('Error starting request. Check console.');
        } finally {
            setIsLoading(false);
            setPrompt('');
            setSelectedImage(null);
        }
    };

        // Auto-scroll to bottom of logs
        React.useEffect(() => {
            if (scrollRef.current) {
                scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
            }
        }, [logs]);

        return (
            <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans">
                {/* SIDEBAR */}
                <aside className="w-80 border-r border-border bg-card/30 flex flex-col hidden md:flex">
                    <div className="p-4 border-b border-border flex items-center gap-2">
                        <Activity className="w-5 h-5 text-primary" />
                        <h1 className="font-semibold text-lg tracking-tight">Nexus <span className="text-xs text-muted-foreground ml-1 font-normal">v3.0</span></h1>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4 space-y-6">
                        {/* Plan Status */}
                        <div>
                            <h2 className="text-xs uppercase font-bold text-muted-foreground mb-3 flex items-center justify-between">
                                Execution Plan
                                {plan && <span className="text-primary font-mono bg-primary/10 px-1.5 rounded">{plan.milestones.length}</span>}
                            </h2>

                            {plan ? (
                                <div className="space-y-3">
                                    {plan.milestones.map((milestone, i) => (
                                        <div key={i} className="bg-card border border-border rounded-md p-3 text-sm">
                                            <div className="flex justify-between items-center mb-1">
                                                <span className="font-semibold">{milestone.id}</span>
                                                <span className={clsx(
                                                    "text-[10px] uppercase font-bold px-1.5 py-0.5 rounded",
                                                    milestone.status === 'completed' ? "bg-green-500/10 text-green-500" :
                                                        milestone.status === 'running' ? "bg-blue-500/10 text-blue-500 animate-pulse" :
                                                            "bg-secondary text-muted-foreground"
                                                )}>{milestone.status}</span>
                                            </div>
                                            <div className="space-y-1 pl-1 border-l-2 border-border/50 ml-1 mt-2">
                                                {milestone.tasks.map((task, j) => (
                                                    <div key={j} className="text-xs text-muted-foreground flex items-center gap-2 truncate">
                                                        <div className={clsx("w-1.5 h-1.5 rounded-full",
                                                            task.status === 'completed' ? "bg-primary" :
                                                                task.status === 'running' ? "bg-amber-400" : "bg-card-foreground/20"
                                                        )} />
                                                        {task.description}
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-sm text-muted-foreground/60 italic p-4 text-center border border-dashed border-border rounded-lg">
                                    No active plan. waiting for task...
                                </div>
                            )}
                        </div>

                        {/* Metrics Component (Placeholder) */}
                        <div className="border-t border-border pt-4">
                            <div className="flex justify-between text-xs mb-1">
                                <span className="text-muted-foreground">Session Cost</span>
                                <span className="font-mono text-foreground">$0.00</span>
                            </div>
                            <div className="flex justify-between text-xs">
                                <span className="text-muted-foreground">Tokens</span>
                                <span className="font-mono text-foreground">0</span>
                            </div>
                        </div>
                    </div>

                    {/* Settings Button */}
                    {onOpenSettings && (
                        <div className="p-4 border-t border-border">
                            <button
                                onClick={onOpenSettings}
                                className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors"
                            >
                                <Settings className="w-4 h-4" />
                                Admin Settings
                            </button>
                        </div>
                    )}
                </aside>

                {/* MAIN CONTENT */}
                <main className="flex-1 flex flex-col relative bg-background/50 backdrop-blur-sm">
                    {/* Header/Tabs */}
                    <header className="h-14 border-b border-border flex items-center px-4 justify-between bg-card/20">
                        <div className="flex items-center space-x-1 bg-muted/30 p-1 rounded-lg">
                            <button
                                onClick={() => setActiveTab('stream')}
                                className={clsx("px-3 py-1 text-sm font-medium rounded-md transition-all", activeTab === 'stream' ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground")}
                            >Thought Stream</button>
                            <button
                                onClick={() => setActiveTab('graph')}
                                className={clsx("px-3 py-1 text-sm font-medium rounded-md transition-all", activeTab === 'graph' ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground")}
                            >Knowledge Graph</button>
                        </div>

                        <div className="flex items-center gap-2">
                            <span className={clsx("w-2 h-2 rounded-full transition-colors", isConnected ? "bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]" : "bg-red-500")} />
                            <span className="text-xs font-medium text-muted-foreground uppercase">{isConnected ? "Connected" : "Disconnected"}</span>
                        </div>
                    </header>

                    {/* Scrollable Content */}
                    <div className="flex-1 overflow-y-auto p-4 md:p-8 max-w-4xl mx-auto w-full space-y-6 custom-scrollbar" ref={scrollRef}>
                        {logs.length === 0 && (
                            <div className="flex flex-col items-center justify-center h-full text-center space-y-4 opacity-40 mt-20">
                                <SquareCode className="w-16 h-16 text-muted-foreground" />
                                <h3 className="text-xl font-semibold">Ready to Orchestrate</h3>
                                <p className="max-w-md text-sm text-muted-foreground">
                                    Enter a feature request below. The system will plan, architect, and implement it using generic RAG and specialized agents.
                                </p>
                            </div>
                        )}

                        {/* Render logs grouped or sequenced */}
                        {/* Simple approach: Group consecutive logs into a Thinking Block */}

                        {/* For Demo v1, just show one massive growing thinking block for the current run */}
                        {logs.length > 0 && <ThinkingBlock logs={logs} title="Complete Execution Log" />}
                    </div>

                    {/* Input Area */}
                    <div className="p-4 border-t border-border bg-card/40 backdrop-blur-md">
                        {/* Image Preview */}
                        {selectedImage && (
                            <div className="max-w-3xl mx-auto mb-2 relative inline-block">
                                <div className="relative group/img">
                                    <img src={selectedImage} alt="Upload Preview" className="h-20 rounded-lg border border-border shadow-sm object-cover" />
                                    <button
                                        onClick={() => setSelectedImage(null)}
                                        className="absolute -top-2 -right-2 bg-destructive text-destructive-foreground rounded-full p-0.5 shadow-md hover:bg-destructive/90 transition-colors"
                                    >
                                        <X className="w-3 h-3" />
                                    </button>
                                </div>
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative group">
                            <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-accent/10 rounded-xl blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                            <div className="relative flex items-end gap-2 bg-background border border-border focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/20 rounded-xl p-2 shadow-lg transition-all">
                                <label htmlFor="file-upload" className={clsx("p-2 rounded-lg cursor-pointer transition-colors", selectedImage ? "text-primary bg-primary/10" : "text-muted-foreground hover:text-foreground hover:bg-muted")}>
                                    <ImageIcon className="w-5 h-5" />
                                    <input id="file-upload" type="file" accept="image/*" className="hidden" onChange={handleFileChange} />
                                </label>

                                {/* Deep Search Toolbar */}
                                <div className="flex items-center gap-2 mr-2">
                                    <button
                                        type="button"
                                        onClick={() => setDeepSearch(!deepSearch)}
                                        className={clsx(
                                            "p-1.5 rounded-md transition-all flex items-center gap-1.5 border",
                                            deepSearch
                                                ? "bg-blue-500/10 border-blue-500/50 text-blue-400"
                                                : "bg-muted/30 border-transparent text-muted-foreground hover:text-foreground"
                                        )}
                                        title="Toggle Deep Search (Investigator Agent)"
                                    >
                                        <Search className="w-4 h-4" />
                                        <span className="text-xs font-medium">Deep Search</span>
                                    </button>

                                    {deepSearch && (
                                        <div className="flex items-center gap-1 bg-muted/30 p-0.5 rounded-md border border-border">
                                            <button
                                                type="button"
                                                onClick={() => setRetrievalStrategy('local')}
                                                className={clsx(
                                                    "px-2 py-0.5 text-[10px] rounded transition-colors",
                                                    retrievalStrategy === 'local' ? "bg-background shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"
                                                )}
                                            >Local</button>
                                            <button
                                                type="button"
                                                onClick={() => setRetrievalStrategy('hybrid')}
                                                className={clsx(
                                                    "px-2 py-0.5 text-[10px] rounded transition-colors flex items-center gap-1",
                                                    retrievalStrategy === 'hybrid' ? "bg-background shadow-sm text-blue-400" : "text-muted-foreground hover:text-foreground"
                                                )}
                                                title="Use External AI to plan investigation"
                                            >
                                                <Sparkles className="w-3 h-3" />
                                                Hybrid
                                            </button>
                                            <button
                                                type="button"
                                                onClick={() => setRetrievalStrategy('external')}
                                                className={clsx(
                                                    "px-2 py-0.5 text-[10px] rounded transition-colors flex items-center gap-1",
                                                    retrievalStrategy === 'external' ? "bg-background shadow-sm text-purple-400" : "text-muted-foreground hover:text-foreground"
                                                )}
                                                title="Full External Delegation (High Cost)"
                                            >
                                                <Globe className="w-3 h-3" />
                                                Pro
                                            </button>
                                        </div>
                                    )}
                                </div>

                                {/* Auto-Fix Toggle */}
                                <button
                                    type="button"
                                    onClick={() => setAutoFix(!autoFix)}
                                    className={clsx(
                                        "p-1.5 rounded-md transition-all flex items-center gap-1.5 border mr-2",
                                        autoFix
                                            ? "bg-amber-500/10 border-amber-500/50 text-amber-500"
                                            : "bg-muted/30 border-transparent text-muted-foreground hover:text-foreground"
                                    )}
                                    title="Enable Autonomous Self-Healing (Auto-Fixer)"
                                >
                                    <Wrench className="w-4 h-4" />
                                    <span className="text-xs font-medium">Auto-Fix</span>
                                </button>

                                <textarea
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter' && !e.shiftKey) {
                                            e.preventDefault();
                                            if (!isLoading) handleSubmit(e);
                                        }
                                    }}
                                    placeholder="Describe a feature (e.g., 'Add a dark mode toggle to the navbar')..."
                                    className="flex-1 bg-transparent border-none focus:ring-0 text-sm py-3 min-h-[44px] max-h-[200px] resize-none placeholder:text-muted-foreground/50"
                                    rows={1}
                                />

                                <button
                                    type="submit"
                                    disabled={isLoading || !prompt.trim()}
                                    className="p-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md active:scale-95"
                                >
                                    {isLoading ? (
                                        <div className="w-5 h-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                                    ) : (
                                        <Send className="w-5 h-5" />
                                    )}
                                </button>
                            </div>

                            <div className="mt-2 ml-2 text-[10px] text-muted-foreground opacity-60">
                                Press <kbd className="font-mono bg-muted/50 px-1 rounded mx-0.5 border border-border">Enter</kbd> to send, <kbd className="font-mono bg-muted/50 px-1 rounded mx-0.5 border border-border">Shift+Enter</kbd> for new line
                            </div>
                        </form>
                    </div>
                </main>
            </div>
        );
    }
