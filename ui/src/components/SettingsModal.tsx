import React, { useState, useEffect } from 'react';
import { X, Save, Lock, Bot, Sliders } from 'lucide-react';
import clsx from 'clsx';

interface SettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
    const [activeTab, setActiveTab] = useState<'models' | 'api_keys' | 'limits'>('models');
    const [isLoading, setIsLoading] = useState(false);
    const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

    // Config State
    const [models, setModels] = useState<any>({});
    const [limits, setLimits] = useState<any>({});
    const [apiKeys, setApiKeys] = useState<any>({});

    // Fetch settings on open
    useEffect(() => {
        if (isOpen) {
            setIsLoading(true);
            fetch('http://localhost:8000/config/settings')
                .then(res => res.json())
                .then(data => {
                    setModels(data.models);
                    setLimits(data.limits);
                    setApiKeys(data.api_keys);
                })
                .catch(err => console.error("Failed to load settings", err))
                .finally(() => setIsLoading(false));
        }
    }, [isOpen]);

    const handleSave = async () => {
        setIsLoading(true);
        try {
            const resp = await fetch('http://localhost:8000/config/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    models: models,
                    limits: limits,
                    api_keys: apiKeys
                })
            });
            if (resp.ok) {
                setHasUnsavedChanges(false);
                alert("Settings saved successfully!");
                onClose();
            } else {
                alert("Failed to save settings.");
            }
        } catch (e) {
            console.error(e);
            alert("Error connecting to API.");
        } finally {
            setIsLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
            <div className="w-[800px] h-[600px] bg-card border border-border rounded-xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                {/* Header */}
                <div className="h-14 border-b border-border flex items-center justify-between px-6 bg-muted/20">
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <Sliders className="w-5 h-5" />
                        System Configuration
                    </h2>
                    <button onClick={onClose} className="p-2 hover:bg-muted rounded-full transition-colors">
                        <X className="w-5 h-5 text-muted-foreground" />
                    </button>
                </div>

                {/* Body */}
                <div className="flex-1 flex overflow-hidden">
                    {/* Sidebar */}
                    <div className="w-48 border-r border-border bg-muted/10 p-4 space-y-1">
                        <SidebarItem active={activeTab === 'models'} onClick={() => setActiveTab('models')} icon={<Bot className="w-4 h-4" />}>Models & Roles</SidebarItem>
                        <SidebarItem active={activeTab === 'api_keys'} onClick={() => setActiveTab('api_keys')} icon={<Lock className="w-4 h-4" />}>API Keys</SidebarItem>
                        <SidebarItem active={activeTab === 'limits'} onClick={() => setActiveTab('limits')} icon={<Sliders className="w-4 h-4" />}>System Limits</SidebarItem>
                    </div>

                    {/* Content */}
                    <div className="flex-1 p-6 overflow-y-auto bg-card">
                        {isLoading && !models ? (
                            <div className="flex items-center justify-center h-full">Loading...</div>
                        ) : (
                            <>
                                {activeTab === 'models' && <ModelsPanel config={models} onChange={(newConfig) => { setModels(newConfig); setHasUnsavedChanges(true); }} />}
                                {activeTab === 'api_keys' && <ApiKeysPanel keys={apiKeys} onChange={(newKeys) => { setApiKeys(newKeys); setHasUnsavedChanges(true); }} />}
                                {activeTab === 'limits' && <LimitsPanel config={limits} onChange={(newLimits) => { setLimits(newLimits); setHasUnsavedChanges(true); }} />}
                            </>
                        )}
                    </div>
                </div>

                {/* Footer */}
                <div className="h-16 border-t border-border flex items-center justify-end px-6 bg-muted/20 gap-3">
                    <button onClick={onClose} className="px-4 py-2 text-sm font-medium hover:bg-muted rounded-lg transition-colors">Cancel</button>
                    <button
                        onClick={handleSave}
                        disabled={isLoading || !hasUnsavedChanges}
                        className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all shadow-sm"
                    >
                        {isLoading ? <span className="animate-spin w-4 h-4 border-2 border-white/50 border-t-white rounded-full" /> : <Save className="w-4 h-4" />}
                        Save Changes
                    </button>
                </div>
            </div>
        </div>
    );
}

function SidebarItem({ active, onClick, icon, children }: any) {
    return (
        <button
            onClick={onClick}
            className={clsx(
                "w-full flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-lg transition-all",
                active ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-muted hover:text-foreground"
            )}
        >
            {icon}
            {children}
        </button>
    )
}

function ApiKeysPanel({ keys, onChange }: { keys: any, onChange: (v: any) => void }) {
    const handleChange = (key: string, val: string) => {
        onChange({ ...keys, [key]: val });
    };

    return (
        <div className="space-y-6 max-w-lg">
            <div>
                <h3 className="text-lg font-medium mb-1">API Credentials</h3>
                <p className="text-sm text-muted-foreground">Manage access keys for external LLM providers. Keys are stored locally in `.env`.</p>
            </div>

            <div className="space-y-4">
                <ApiKeyInput label="OpenAI API Key" value={keys?.OPENAI_API_KEY || ''} onChange={(v) => handleChange('OPENAI_API_KEY', v)} />
                <ApiKeyInput label="Anthropic API Key" value={keys?.ANTHROPIC_API_KEY || ''} onChange={(v) => handleChange('ANTHROPIC_API_KEY', v)} />
                <ApiKeyInput label="Google AI Key" value={keys?.GOOGLE_API_KEY || ''} onChange={(v) => handleChange('GOOGLE_API_KEY', v)} />
            </div>
        </div>
    );
}

function LimitsPanel({ config, onChange }: { config: any, onChange: (v: any) => void }) {
    // Helper to deeply update nested state
    const updateNested = (path: string[], value: any) => {
        const newConfig = JSON.parse(JSON.stringify(config || {}));
        let current = newConfig;
        for (let i = 0; i < path.length - 1; i++) {
            if (!current[path[i]]) current[path[i]] = {};
            current = current[path[i]];
        }
        current[path[path.length - 1]] = value;
        onChange(newConfig);
    };

    if (!config) return <div>Loading limits...</div>;

    return (
        <div className="space-y-8">
            <div>
                <h3 className="text-lg font-medium mb-1">Token Budgets</h3>
                <p className="text-sm text-muted-foreground mb-4">Set safety limits for token usage per request.</p>
                <div className="grid grid-cols-2 gap-4">
                    <TokenInput
                        label="Max Input Tokens"
                        value={config.budgets?.max_input_tokens}
                        onChange={(v) => updateNested(['budgets', 'max_input_tokens'], parseInt(v))}
                    />
                    <TokenInput
                        label="Max Output Tokens"
                        value={config.budgets?.max_output_tokens}
                        onChange={(v) => updateNested(['budgets', 'max_output_tokens'], parseInt(v))}
                    />
                </div>
            </div>

            <div className="border-t border-border/50 pt-6">
                <h3 className="text-lg font-medium mb-1">RAG Retrieval Settings</h3>
                <p className="text-sm text-muted-foreground mb-4">Configure how the system processes and retrieves knowledge.</p>
                <div className="grid grid-cols-2 gap-4">
                    <TokenInput
                        label="Top K Results"
                        value={config.retrieval?.top_k}
                        onChange={(v) => updateNested(['retrieval', 'top_k'], parseInt(v))}
                    />
                    <TokenInput
                        label="Chunk Size (Chars)"
                        value={config.retrieval?.chunk_chars}
                        onChange={(v) => updateNested(['retrieval', 'chunk_chars'], parseInt(v))}
                    />
                    <TokenInput
                        label="Chunk Overlap"
                        value={config.retrieval?.chunk_overlap}
                        onChange={(v) => updateNested(['retrieval', 'chunk_overlap'], parseInt(v))}
                    />
                </div>
            </div>

            <div className="border-t border-border/50 pt-6">
                <h3 className="text-lg font-medium mb-1">Concurrency</h3>
                <p className="text-sm text-muted-foreground mb-4">Control parallel execution limits.</p>
                <div className="grid grid-cols-2 gap-4">
                    <TokenInput
                        label="Max Workers"
                        value={config.concurrency?.max_workers}
                        onChange={(v) => updateNested(['concurrency', 'max_workers'], parseInt(v))}
                    />
                </div>
            </div>
        </div>
    );
}

function ApiKeyInput({ label, value, onChange }: any) {
    return (
        <div className="space-y-1.5">
            <label className="text-sm font-medium">{label}</label>
            <div className="relative">
                <input
                    type="password"
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder="sk-..."
                    className="w-full px-3 py-2 bg-background border border-border rounded-md focus:ring-1 focus:ring-primary outline-none font-mono text-sm"
                />
            </div>
        </div>
    );
}

function ModelsPanel({ config, onChange }: { config: any, onChange: (v: any) => void }) {
    // Helper to deeply update nested state
    const updateNested = (path: string[], value: any) => {
        const newConfig = JSON.parse(JSON.stringify(config));
        let current = newConfig;
        for (let i = 0; i < path.length - 1; i++) {
            current = current[path[i]];
        }
        current[path[path.length - 1]] = value;
        onChange(newConfig);
    };

    if (!config || !config.routing) return <div>Loading config structure...</div>;

    return (
        <div className="space-y-8">
            <div>
                <h3 className="text-lg font-medium mb-1">Default Model</h3>
                <div className="grid grid-cols-2 gap-4 mt-4">
                    <div className="space-y-1.5">
                        <label className="text-sm text-muted-foreground">Global Default</label>
                        <select
                            value={config.default?.model}
                            onChange={(e) => updateNested(['default', 'model'], e.target.value)}
                            className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm outline-none"
                        >
                            <option value="gpt-4o">GPT-4o</option>
                            <option value="gpt-4o-mini">GPT-4o Mini</option>
                            <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
                            <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                        </select>
                    </div>
                </div>
            </div>

            <div className="border-t border-border/50 pt-6">
                <h3 className="text-lg font-medium mb-4">Phase-Specific Models</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Analyst */}
                    <div className="p-4 rounded-lg border border-border bg-muted/5 space-y-3">
                        <div className="flex items-center gap-2 mb-2">
                            <div className="w-2 h-2 rounded-full bg-blue-500" />
                            <h4 className="font-medium text-sm">Analyst Agent</h4>
                        </div>
                        <ModelSelector
                            label="Model"
                            value={config.routing?.phase?.analyst?.model}
                            onChange={(v) => updateNested(['routing', 'phase', 'analyst', 'model'], v)}
                        />
                        <TokenInput
                            value={config.routing?.phase?.analyst?.max_tokens}
                            onChange={(v) => updateNested(['routing', 'phase', 'analyst', 'max_tokens'], parseInt(v))}
                        />
                    </div>

                    {/* Architect */}
                    <div className="p-4 rounded-lg border border-border bg-muted/5 space-y-3">
                        <div className="flex items-center gap-2 mb-2">
                            <div className="w-2 h-2 rounded-full bg-purple-500" />
                            <h4 className="font-medium text-sm">Architect Agent</h4>
                        </div>
                        <ModelSelector
                            label="Model"
                            value={config.routing?.phase?.architect?.model}
                            onChange={(v) => updateNested(['routing', 'phase', 'architect', 'model'], v)}
                        />
                        <div className="flex items-center justify-between pt-1">
                            <span className="text-xs font-medium text-muted-foreground">Consensus Mode</span>
                            <input
                                type="checkbox"
                                checked={config.routing?.phase?.architect?.consensus_mode || false}
                                onChange={(e) => updateNested(['routing', 'phase', 'architect', 'consensus_mode'], e.target.checked)}
                                className="accent-primary"
                            />
                        </div>
                    </div>

                    {/* Implementer */}
                    <div className="p-4 rounded-lg border border-border bg-muted/5 space-y-3">
                        <div className="flex items-center gap-2 mb-2">
                            <div className="w-2 h-2 rounded-full bg-amber-500" />
                            <h4 className="font-medium text-sm">Implementation Agent</h4>
                        </div>
                        <ModelSelector
                            label="Model"
                            value={config.routing?.phase?.implementation?.model}
                            onChange={(v) => updateNested(['routing', 'phase', 'implementation', 'model'], v)}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}

function ModelSelector({ label, value, onChange }: any) {
    return (
        <div className="space-y-1">
            <label className="text-xs text-muted-foreground">{label}</label>
            <select
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="w-full px-2 py-1.5 bg-background border border-border rounded text-sm outline-none focus:ring-1 focus:ring-primary"
            >
                <option value="gpt-4o">GPT-4o (OpenAI)</option>
                <option value="gpt-4o-mini">GPT-4o Mini (OpenAI)</option>
                <option value="claude-3-5-sonnet">Claude 3.5 Sonnet (Anthropic)</option>
                <option value="gemini-1.5-pro">Gemini 1.5 Pro (Google)</option>
                <option value="gemini-2.5-pro">Gemini 2.5 Pro (Google)</option>
            </select>
        </div>
    )
}

function TokenInput({ label, value, onChange }: any) {
    return (
        <div className="space-y-1">
            <label className="text-xs text-muted-foreground">{label || "Max Tokens"}</label>
            <input
                type="number"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="w-full px-2 py-1.5 bg-background border border-border rounded text-sm outline-none focus:ring-1 focus:ring-primary"
            />
        </div>
    )
}
