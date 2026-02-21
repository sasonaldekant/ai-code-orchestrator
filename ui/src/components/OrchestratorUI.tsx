import * as React from 'react';
import { useState } from 'react';
import type { Milestone, Task } from '../lib/types';
import { useLogStream } from '../hooks/useLogStream';
import { Send, SquareCode, Activity, Settings, Search, Sparkles, Globe, Wrench, X, ImageIcon, SlidersHorizontal, Check, Square, Layers, Zap, Brain, Bot } from 'lucide-react';
import clsx from 'clsx';
import { ThinkingBlock } from './ThinkingBlock';
import { KnowledgeTab } from './KnowledgeTab';
import { AdvancedOptions } from './AdvancedOptions';
import { AgentRegistry } from './AgentRegistry';
import { FormStudioTab } from './FormStudioTab';
import { api } from '../lib/api';

interface OrchestratorUIProps {
    onOpenSettings?: () => void;
}

export function OrchestratorUI({ onOpenSettings }: OrchestratorUIProps) {
    const { logs, isConnected, plan, clearLogs } = useLogStream();
    const [prompt, setPrompt] = useState("");
    const [activePrompt, setActivePrompt] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const scrollRef = React.useRef<HTMLDivElement>(null);
    const [activeTab, setActiveTab] = useState<'stream' | 'graph' | 'knowledge' | 'agents' | 'forms'>('stream');

    // Phase 4: Client Settings
    const [clientSettings, setClientSettings] = useState<any>(null);
    const [activeMode, setActiveMode] = useState<'fast' | 'thinking' | 'agentic'>('agentic');

    React.useEffect(() => {
        api.get('/config/client-settings').then(data => {
            setClientSettings(data);
            if (data?.modes?.length > 0 && !data.modes.includes(activeMode)) {
                setActiveMode(data.modes[0]);
            }
        }).catch(err => console.error("Failed to load client settings", err));
    }, []);

    const [showOptions, setShowOptions] = useState(false);
    const [retrievalStrategy, setRetrievalStrategy] = useState<'local' | 'hybrid' | 'external'>('local');

    const [selectedImage, setSelectedImage] = useState<string | null>(null);

    const [selectedModel, setSelectedModel] = useState<string>('gpt-5.2');
    const [consensusMode, setConsensusMode] = useState(false);
    const [reviewStrategy, setReviewStrategy] = useState<'basic' | 'strict'>('basic');

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

    const handleStop = async (e: React.MouseEvent) => {
        e.preventDefault();
        try {
            await api.post('/stop', {});
            setIsLoading(false);
            // Add a system message to logs indicating cancellation
            // clearLogs(); // Optional: keep logs or clear them? Usually users want to see partial results.
        } catch (e) {
            console.error("Failed to stop", e);
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
                    const visionResp = await api.post('/vision/analyze', {
                        image: selectedImage,
                        prompt: "Analyze this image in the context of software development. If it's a UI mockup, describe the components and layout. If it's an error, identify the issue."
                    });
                    if (visionResp.ok) {
                        const visionData = await visionResp.json();
                        if (visionData.success && visionData.analysis) {
                            finalPrompt += `\n\n[Vision Analysis Context]:\n${visionData.analysis}`;
                        }
                    }
                } catch (err) {
                    console.error("Vision analysis failed", err);
                    // Continue without visual context.
                }
            }

            setActivePrompt(finalPrompt); // Persist prompt for display

            const response = await api.post('/orchestrate', {
                request: finalPrompt,
                mode: activeMode,
                image: selectedImage,
                retrieval_strategy: retrievalStrategy,
                consensus_mode: consensusMode,
                review_strategy: reviewStrategy,
                model: selectedModel
            });
            if (!response.ok) throw new Error("Failed to start");

            // Success: only then clear input
            setPrompt("");
            setSelectedImage(null);
        } catch (e) {
            console.error(e);
            alert("Error starting request. Check console.");
            setIsLoading(false); // Reset loading state on error
        }
        // Finally block removed because we want isLoading to stay true until stream finishes or stop is clicked
        // Actually, explicit stream handling usually sets isLoading=false when stream ends.
        // But here we rely on the stream events? No, handleSubmit uses await fetch, but orchestrate returns stream?
        // Wait, app.py /orchestrate returns JSON result after await. It is NOT streaming the RESPONSE body directly.
        // It streams via SSE /stream/logs separately.
        // So await fetch() will wait until the entire execution is done!
        // That means we DO need to setIsLoading(false) at the end.

        setIsLoading(false);
    };

    // Auto-scroll to bottom of logs
    React.useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    return (
        <div className="flex h-full w-full bg-background text-foreground overflow-hidden font-sans">
            {/* SIDEBAR - REFACTORED */}
            <aside className="w-80 border-r border-border bg-card/30 flex flex-col hidden md:flex shrink-0">
                <div className="p-4 border-b border-border flex items-center gap-2 h-14">
                    <Activity className="w-5 h-5 text-primary" />
                    <h1 className="font-semibold text-lg tracking-tight">Nexus <span className="text-xs text-muted-foreground ml-1 font-normal">v3.1</span></h1>
                </div>

                <div className="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar">
                    {/* PRIMARY NAVIGATION */}
                    <nav className="space-y-1">
                        <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 px-2">Menu</div>
                        {[
                            { id: 'stream', label: 'Chat & Plan', icon: Sparkles },
                            { id: 'graph', label: 'Knowledge Graph', icon: Activity },
                            { id: 'knowledge', label: 'Manage Knowledge', icon: Layers },
                            { id: 'agents', label: 'Agent Registry', icon: Globe },
                            ...(clientSettings?.form_studio_enabled !== false ? [{ id: 'forms', label: 'Form Studio', icon: SquareCode }] : [])
                        ].map((item) => (
                            <button
                                key={item.id}
                                onClick={() => setActiveTab(item.id as any)}
                                className={clsx(
                                    "w-full flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200",
                                    activeTab === item.id
                                        ? "bg-primary/10 text-primary shadow-sm"
                                        : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                                )}
                            >
                                <item.icon className={clsx("w-4 h-4", activeTab === item.id ? "text-primary" : "text-muted-foreground")} />
                                {item.label}
                            </button>
                        ))}
                    </nav>

                    <div className="h-px bg-border/50 my-2" />

                    {/* Execution Plan (Conditionally Shown if Active) */}
                    <div className={clsx("transition-opacity duration-300", !plan ? "opacity-40 hover:opacity-100" : "opacity-100")}>
                        <h2 className="text-xs uppercase font-bold text-muted-foreground mb-3 flex items-center justify-between px-2">
                            Execution Plan
                            {plan && <span className="text-primary font-mono bg-primary/10 px-1.5 rounded text-[10px]">{plan.milestones.length}</span>}
                        </h2>

                        {plan ? (
                            <div className="space-y-3">
                                {plan.milestones.map((milestone: Milestone, i: number) => (
                                    <div key={i} className="bg-card border border-border rounded-md p-3 text-sm shadow-sm">
                                        <div className="flex justify-between items-center mb-1">
                                            <span className="font-semibold text-xs">{milestone.id}</span>
                                            <span className={clsx(
                                                "text-[10px] uppercase font-bold px-1.5 py-0.5 rounded",
                                                milestone.status === 'completed' ? "bg-green-500/10 text-green-500" :
                                                    milestone.status === 'running' ? "bg-blue-500/10 text-blue-500 animate-pulse" :
                                                        "bg-secondary text-muted-foreground"
                                            )}>{milestone.status}</span>
                                        </div>
                                        <div className="space-y-1 pl-1 border-l-2 border-border/50 ml-1 mt-2">
                                            {milestone.tasks.map((task: Task, j: number) => (
                                                <div key={j} className="text-xs text-muted-foreground flex items-center gap-2 truncate">
                                                    <div className={clsx("w-1.5 h-1.5 rounded-full shrink-0",
                                                        task.status === 'completed' ? "bg-primary" :
                                                            task.status === 'running' ? "bg-amber-400" : "bg-card-foreground/20"
                                                    )} />
                                                    <span className="truncate">{task.description}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-xs text-muted-foreground italic p-4 text-center border border-dashed border-border rounded-lg bg-muted/20">
                                No active plan
                            </div>
                        )}
                    </div>
                </div>

                {/* Settings at Bottom */}
                <div className="p-4 border-t border-border mt-auto">
                    <button
                        onClick={onOpenSettings}
                        className="w-full flex items-center justify-between p-3 rounded-lg text-muted-foreground hover:bg-muted/50 hover:text-foreground transition-colors group"
                    >
                        <Settings className="w-4 h-4" />
                        Settings
                    </button>
                    <div className="flex items-center gap-2 mt-4 justify-center">
                        <div className={clsx("w-2 h-2 rounded-full transition-colors", isConnected ? "bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]" : "bg-red-500")} />
                        <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-widest">{isConnected ? "System Online" : "Offline"}</span>
                    </div>
                    {clientSettings?.daily_spend && (
                        <div className="mt-3 px-3 py-2 bg-muted/20 border border-border/50 rounded-lg text-center">
                            <div className="text-[10px] text-muted-foreground uppercase font-bold mb-1">Daily Spend</div>
                            <div className="text-sm font-mono text-foreground font-medium">
                                ${clientSettings.daily_spend.today_usd?.toFixed(2)} / ${clientSettings.daily_spend.limit_usd?.toFixed(2)}
                            </div>
                        </div>
                    )}
                </div>
            </aside>

            <main className="flex-1 flex flex-col relative bg-background/50 backdrop-blur-sm h-full overflow-hidden">
                {/* Header removed - blended into main area or sidebar */}

                {/* Scrollable Content - Full Width Container enables scrollbar at edge */}
                <div className="flex-1 overflow-y-auto w-full custom-scrollbar" ref={scrollRef}>
                    <div className="p-4 md:p-8 w-full max-w-[1600px] mx-auto space-y-6">
                        {activeTab === 'knowledge' ? (
                            <KnowledgeTab />
                        ) : activeTab === 'agents' ? (
                            <AgentRegistry />
                        ) : activeTab === 'forms' ? (
                            <FormStudioTab />
                        ) : activeTab === 'graph' ? (
                            <div className="flex items-center justify-center h-full text-muted-foreground italic min-h-[50vh]">
                                Knowledge Graph Visualization Coming Soon...
                            </div>
                        ) : (
                            <>
                                {logs.length === 0 && (
                                    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-4 opacity-40">
                                        <SquareCode className="w-16 h-16 text-muted-foreground" />
                                        <h3 className="text-xl font-semibold">Ready to Orchestrate</h3>
                                        <p className="max-w-md text-sm text-muted-foreground">
                                            Enter a feature request below. The system will plan, architect, and implement it using generic RAG and specialized agents.
                                        </p>
                                    </div>
                                )}

                                {/* Result Display Section */}
                                {(activePrompt || (() => {
                                    // Efficiently find the last info event without reversing the whole array
                                    let lastInfoEvent = null;
                                    for (let i = logs.length - 1; i >= 0; i--) {
                                        if (logs[i].type === 'info') {
                                            lastInfoEvent = logs[i];
                                            break;
                                        }
                                    }
                                    return lastInfoEvent && lastInfoEvent.content;
                                })()) && (
                                        <div className="space-y-4 animate-in fade-in zoom-in duration-500 pb-20">
                                            {/* User Request Card */}
                                            {activePrompt && (
                                                <div className="bg-card/50 border border-border rounded-xl p-4 shadow-sm backdrop-blur-sm">
                                                    <div className="flex items-center gap-2 mb-2 text-muted-foreground">
                                                        <div className="p-1.5 bg-muted rounded-md">
                                                            <Activity className="w-4 h-4" />
                                                        </div>
                                                        <h3 className="font-semibold text-sm uppercase tracking-wider">User Request</h3>
                                                    </div>
                                                    <div className="text-foreground/80 font-medium text-sm md:text-base pl-1">
                                                        {activePrompt}
                                                    </div>
                                                </div>
                                            )}

                                            {/* Final Answer Card */}
                                            {(() => {
                                                let lastInfoEvent = null;
                                                for (let i = logs.length - 1; i >= 0; i--) {
                                                    if (logs[i].type === 'info') {
                                                        lastInfoEvent = logs[i];
                                                        break;
                                                    }
                                                }

                                                if (lastInfoEvent && lastInfoEvent.content) {
                                                    const content = lastInfoEvent.content;
                                                    const isString = typeof content === 'string';
                                                    const displayContent = isString
                                                        ? content.replace(/^###\s+/gm, '') // Remove markdown headers for cleaner look if desired, or keep specific ones
                                                        : JSON.stringify(content, null, 2);

                                                    return (
                                                        <div className="bg-gradient-to-br from-indigo-500/5 to-purple-500/5 border border-indigo-500/20 rounded-xl p-6 shadow-xl shadow-indigo-500/5">
                                                            <div className="flex items-center gap-3 mb-4 border-b border-indigo-500/10 pb-3">
                                                                <div className="p-2 bg-indigo-500/10 text-indigo-400 rounded-lg shadow-sm">
                                                                    <Sparkles className="w-5 h-5" />
                                                                </div>
                                                                <div>
                                                                    <h3 className="font-bold text-base text-foreground">Final Answer</h3>
                                                                    {lastInfoEvent.timestamp && <span className="text-[10px] text-muted-foreground opacity-70">Generated at {new Date(lastInfoEvent.timestamp).toLocaleTimeString()}</span>}
                                                                </div>
                                                                <span className="ml-auto px-2 py-0.5 bg-indigo-500/10 text-indigo-400 text-[10px] font-bold uppercase tracking-widest rounded border border-indigo-500/20">
                                                                    Compleated
                                                                </span>
                                                            </div>

                                                            <div className="text-foreground/90 leading-relaxed font-sans prose prose-invert max-w-none whitespace-pre-wrap text-sm md:text-base">
                                                                {displayContent}
                                                            </div>
                                                        </div>
                                                    );
                                                }
                                                return null;
                                            })()}
                                        </div>
                                    )}

                                {/* Render logs grouped or sequenced */}
                                {logs.length > 0 && (
                                    <div className="mt-8 pb-10">
                                        <ThinkingBlock logs={logs} title="Full Execution Process" />
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                </div>

                {/* Input Area (Only visible in Stream/Chat mode) */}
                {activeTab === 'stream' && (
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
                                {/* Options Dropdown */}
                                <div className="relative mr-2">
                                    <button
                                        type="button"
                                        onClick={() => setShowOptions(!showOptions)}
                                        className={clsx(
                                            "p-2 rounded-full transition-all border",
                                            showOptions
                                                ? "bg-primary/20 text-primary border-primary/50 shadow-[0_0_15px_rgba(var(--primary),0.3)]"
                                                : "bg-background/50 text-muted-foreground border-border hover:bg-muted hover:text-foreground"
                                        )}
                                        title="Execution Options"
                                    >
                                        <SlidersHorizontal className="w-5 h-5" />
                                    </button>

                                    {showOptions && (
                                        <div className="absolute bottom-full mb-2 right-0 w-56 bg-card border border-border rounded-xl shadow-xl backdrop-blur-md p-2 space-y-1 z-50">
                                            <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                                                Execution Mode
                                            </div>

                                            {clientSettings?.modes?.includes('fast') && (
                                                <button
                                                    type="button"
                                                    onClick={() => setActiveMode('fast')}
                                                    className={clsx(
                                                        "w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors",
                                                        activeMode === 'fast' ? "bg-primary/20 text-primary" : "hover:bg-muted text-foreground"
                                                    )}
                                                >
                                                    <Zap className="w-4 h-4 mr-2" />
                                                    Fast
                                                    {activeMode === 'fast' && <Check className="w-4 h-4 ml-auto" />}
                                                </button>
                                            )}

                                            {clientSettings?.modes?.includes('thinking') && (
                                                <button
                                                    type="button"
                                                    onClick={() => setActiveMode('thinking')}
                                                    className={clsx(
                                                        "w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors",
                                                        activeMode === 'thinking' ? "bg-primary/20 text-primary" : "hover:bg-muted text-foreground"
                                                    )}
                                                >
                                                    <Brain className="w-4 h-4 mr-2" />
                                                    Thinking
                                                    {activeMode === 'thinking' && <Check className="w-4 h-4 ml-auto" />}
                                                </button>
                                            )}

                                            {clientSettings?.modes?.includes('agentic') && (
                                                <button
                                                    type="button"
                                                    onClick={() => setActiveMode('agentic')}
                                                    className={clsx(
                                                        "w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors",
                                                        activeMode === 'agentic' ? "bg-indigo-500/20 text-indigo-400" : "hover:bg-muted text-foreground"
                                                    )}
                                                >
                                                    <Bot className="w-4 h-4 mr-2" />
                                                    Agentic
                                                    {activeMode === 'agentic' && <Check className="w-4 h-4 ml-auto" />}
                                                </button>
                                            )}

                                            <div className="h-px bg-border my-1" />

                                            <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                                                Model Choice
                                            </div>
                                            <div className="px-2 pb-2">
                                                <select
                                                    value={selectedModel}
                                                    onChange={(e) => setSelectedModel(e.target.value)}
                                                    className="w-full bg-background/50 border border-border rounded-lg text-xs p-1.5 focus:outline-none focus:ring-1 focus:ring-primary/50"
                                                >
                                                    {clientSettings?.models ? clientSettings.models.map((m: any) => (
                                                        <option key={m.id} value={m.id}>{m.label}</option>
                                                    )) : (
                                                        <>
                                                            <option value="gpt-5.2">GPT-5.2 (Recommended)</option>
                                                            <option value="gpt-5-mini">GPT-5 Mini</option>
                                                        </>
                                                    )}
                                                </select>
                                                {clientSettings?.models && (
                                                    <div className="text-[10px] text-muted-foreground mt-1 px-1">
                                                        {clientSettings.models.find((m: any) => m.id === selectedModel)?.traits}
                                                    </div>
                                                )}
                                            </div>

                                            <div className="h-px bg-border my-1" />
                                        </div>
                                    )}
                                </div>

                                {activeMode === 'thinking' && (
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
                                    </div>
                                )}

                                <textarea
                                    value={prompt}
                                    onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setPrompt(e.target.value)}
                                    onKeyDown={(e: React.KeyboardEvent<HTMLTextAreaElement>) => {
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
                                    type={isLoading ? "button" : "submit"}
                                    onClick={isLoading ? handleStop : undefined}
                                    disabled={!isLoading && !prompt.trim()}
                                    className={clsx(
                                        "p-2 rounded-lg transition-all shadow-md active:scale-95",
                                        isLoading
                                            ? "bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                            : "bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
                                    )}
                                >
                                    {isLoading ? (
                                        <Square className="w-5 h-5 fill-current" />
                                    ) : (
                                        <Send className="w-5 h-5" />
                                    )}
                                </button>
                            </div >

                            <AdvancedOptions
                                consensus={consensusMode}
                                setConsensus={setConsensusMode}
                                reviewStrategy={reviewStrategy}
                                setReviewStrategy={setReviewStrategy}
                                showReviewStrategy={clientSettings?.advanced_options?.review_strategy}
                                showConsensusMode={clientSettings?.advanced_options?.consensus_mode}
                            />

                            <div className="mt-2 ml-2 text-[10px] text-muted-foreground opacity-60">
                                Press <kbd className="font-mono bg-muted/50 px-1 rounded mx-0.5 border border-border">Enter</kbd> to send, <kbd className="font-mono bg-muted/50 px-1 rounded mx-0.5 border border-border">Shift+Enter</kbd> for new line
                            </div>
                        </form >
                    </div >
                )}
            </main >
        </div >
    );
}
