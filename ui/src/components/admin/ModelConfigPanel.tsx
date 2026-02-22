import { useState, useEffect } from 'react';
import { Bot, Save, RefreshCw, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import clsx from 'clsx';

interface PhaseConfig {
    model: string;
    provider: string;
    temperature: number;
    max_tokens: number;
    reasoning?: string;
    consensus_mode?: boolean;
    producer_reviewer_loop?: boolean;
    max_iterations?: number;
}

interface ModelConfig {
    version: string;
    default?: {
        model: string;
        temperature: number;
        max_tokens: number;
    };
    routing: {
        phase?: Record<string, PhaseConfig>;
        phases?: Record<string, PhaseConfig>;
    };
    cost_management?: {
        budget_alert_threshold: number;
        max_cascade_depth: number;
        prefer_cached: boolean;
    };
    caching?: {
        enabled: boolean;
        tier_1_rules?: { ttl_seconds: number };
        tier_2_tokens?: { ttl_seconds: number };
        tier_3_catalog?: { ttl_seconds: number };
    };
}

const AVAILABLE_MODELS = [
    { value: 'gpt-5-nano', label: 'GPT-5 Nano', provider: 'openai' },
    { value: 'gpt-5-mini', label: 'GPT-5 Mini', provider: 'openai' },
    { value: 'gpt-5.2', label: 'GPT-5.2 (Recommended)', provider: 'openai' },
    { value: 'claude-sonnet-4.5', label: 'Claude Sonnet 4.5', provider: 'anthropic' },
    { value: 'claude-opus-4.6', label: 'Claude Opus 4.6', provider: 'anthropic' },
    { value: 'gemini-3.5-flash', label: 'Gemini 3.5 Flash (New)', provider: 'google' },
    { value: 'gemini-3.5-pro', label: 'Gemini 3.5 Pro (New)', provider: 'google' },
    { value: 'gemini-3-flash', label: 'Gemini 3 Flash', provider: 'google' },
    { value: 'gemini-3-pro', label: 'Gemini 3 Pro', provider: 'google' },
    { value: 'gemini-2.0-flash', label: 'Gemini 2.0 Flash', provider: 'google' },
    { value: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro', provider: 'google' },
    { value: 'sonar', label: 'Sonar', provider: 'perplexity' },
    { value: 'sonar-deep-research', label: 'Sonar Deep Research', provider: 'perplexity' },
];

const PHASES = ['gate', 'analyst', 'architect', 'implementer_frontend', 'implementer_backend', 'tester', 'reviewer', 'self_healer', 'research', 'monitor', 'fact_checker'];

export function ModelConfigPanel() {
    const [config, setConfig] = useState<ModelConfig | null>(null);
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
            const resp = await fetch('http://localhost:8000/admin/config/model_mapping_v2');
            if (!resp.ok) throw new Error('Failed to load config');
            const data = await resp.json();
            setConfig(data.data);
        } catch (e) {
            setError('Failed to load model configuration');
        } finally {
            setIsLoading(false);
        }
    };

    const saveConfig = async () => {
        if (!config) return;
        setIsSaving(true);
        setSaveResult(null);
        try {
            const resp = await fetch('http://localhost:8000/admin/config/model_mapping_v2', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: config }),
            });
            if (!resp.ok) throw new Error('Failed to save');
            setSaveResult({ success: true, message: 'Configuration saved successfully' });
        } catch (e) {
            setSaveResult({ success: false, message: 'Failed to save configuration' });
        } finally {
            setIsSaving(false);
        }
    };

    const updatePhaseConfig = (phase: string, field: keyof PhaseConfig, value: any) => {
        if (!config) return;
        const routing = config.routing;
        const phaseKey = routing.phases ? 'phases' : 'phase';
        const currentPhases = (routing as any)[phaseKey] || {};

        setConfig({
            ...config,
            routing: {
                ...routing,
                [phaseKey]: {
                    ...currentPhases,
                    [phase]: {
                        ...(currentPhases[phase] || {}),
                        [field]: value,
                    },
                },
            },
        });
        setSaveResult(null);
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
                    <h2 className="text-2xl font-bold">Model Configuration</h2>
                    <p className="text-muted-foreground mt-1">
                        Configure LLM models for each orchestration phase.
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

            {/* Default Settings */}
            <div className="bg-card border border-border rounded-xl p-5">
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-4">
                    Default Settings
                </h3>
                <div className="grid grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium mb-2">Default Model</label>
                        <select
                            value={config?.default?.model || ''}
                            onChange={(e) => setConfig(c => c ? {
                                ...c,
                                default: {
                                    model: e.target.value,
                                    temperature: c.default?.temperature || 0,
                                    max_tokens: c.default?.max_tokens || 4000
                                }
                            } : c)}
                            className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm"
                        >
                            {AVAILABLE_MODELS.map(m => (
                                <option key={m.value} value={m.value}>{m.label}</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-2">Temperature</label>
                        <input
                            type="number"
                            step="0.1"
                            min="0"
                            max="1"
                            value={config?.default?.temperature || 0}
                            onChange={(e) => setConfig(c => c ? {
                                ...c,
                                default: {
                                    model: c.default?.model || '',
                                    temperature: parseFloat(e.target.value),
                                    max_tokens: c.default?.max_tokens || 4000
                                }
                            } : c)}
                            className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-2">Max Tokens</label>
                        <input
                            type="number"
                            value={config?.default?.max_tokens || 4000}
                            onChange={(e) => setConfig(c => c ? {
                                ...c,
                                default: {
                                    model: c.default?.model || '',
                                    temperature: c.default?.temperature || 0,
                                    max_tokens: parseInt(e.target.value)
                                }
                            } : c)}
                            className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm"
                        />
                    </div>
                </div>
            </div>

            {/* Cost Management */}
            <div className="bg-card border border-border rounded-xl p-5">
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-4">
                    Cost Management & Optimization
                </h3>
                <div className="grid grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium mb-2">Budget Alert Threshold (0.0-1.0)</label>
                        <input
                            type="number"
                            step="0.05"
                            min="0"
                            max="1"
                            value={config?.cost_management?.budget_alert_threshold || 0}
                            onChange={(e) => setConfig(c => c ? {
                                ...c,
                                cost_management: {
                                    budget_alert_threshold: parseFloat(e.target.value),
                                    max_cascade_depth: c.cost_management?.max_cascade_depth || 2,
                                    prefer_cached: c.cost_management?.prefer_cached ?? true
                                }
                            } : c)}
                            className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-2">Max Cascade Depth</label>
                        <input
                            type="number"
                            min="1"
                            max="5"
                            value={config?.cost_management?.max_cascade_depth || 2}
                            onChange={(e) => setConfig(c => c ? {
                                ...c,
                                cost_management: {
                                    budget_alert_threshold: c.cost_management?.budget_alert_threshold || 0.8,
                                    max_cascade_depth: parseInt(e.target.value),
                                    prefer_cached: c.cost_management?.prefer_cached ?? true
                                }
                            } : c)}
                            className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm"
                        />
                    </div>
                    <div className="flex items-end pb-2">
                        <label className="flex items-center gap-3 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={config?.cost_management?.prefer_cached ?? true}
                                onChange={(e) => setConfig(c => c ? {
                                    ...c,
                                    cost_management: {
                                        budget_alert_threshold: c.cost_management?.budget_alert_threshold || 0.8,
                                        max_cascade_depth: c.cost_management?.max_cascade_depth || 2,
                                        prefer_cached: e.target.checked
                                    }
                                } : c)}
                                className="w-4 h-4 rounded border-border accent-primary"
                            />
                            <div>
                                <span className="text-sm font-medium">Prefer Cached Results</span>
                                <p className="text-xs text-muted-foreground">Reuse deterministic LLM outputs</p>
                            </div>
                        </label>
                    </div>
                </div>
            </div>

            {/* Caching Settings */}
            <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                        Caching (Domain & Token)
                    </h3>
                    <label className="flex items-center gap-2 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={config?.caching?.enabled ?? true}
                            onChange={(e) => setConfig(c => c ? {
                                ...c,
                                caching: { ...(c.caching || { enabled: true }), enabled: e.target.checked }
                            } : c)}
                            className="w-4 h-4 rounded border-border accent-primary"
                        />
                        <span className="text-sm font-medium">Enable Cache</span>
                    </label>
                </div>

                <div className="grid grid-cols-3 gap-4">
                    <div>
                        <label className="block text-xs font-medium text-muted-foreground mb-1">Tier 1 (Rules) TTL (s)</label>
                        <input
                            type="number"
                            value={config?.caching?.tier_1_rules?.ttl_seconds || 3600}
                            onChange={(e) => setConfig(c => c ? {
                                ...c,
                                caching: {
                                    ...(c.caching || { enabled: true }),
                                    tier_1_rules: { ttl_seconds: parseInt(e.target.value) }
                                }
                            } : c)}
                            className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm"
                        />
                    </div>
                    <div>
                        <label className="block text-xs font-medium text-muted-foreground mb-1">Tier 2 (Tokens) TTL (s)</label>
                        <input
                            type="number"
                            value={config?.caching?.tier_2_tokens?.ttl_seconds || 3600}
                            onChange={(e) => setConfig(c => c ? {
                                ...c,
                                caching: {
                                    ...(c.caching || { enabled: true }),
                                    tier_2_tokens: { ttl_seconds: parseInt(e.target.value) }
                                }
                            } : c)}
                            className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm"
                        />
                    </div>
                    <div>
                        <label className="block text-xs font-medium text-muted-foreground mb-1">Tier 3 (Catalog) TTL (s)</label>
                        <input
                            type="number"
                            value={config?.caching?.tier_3_catalog?.ttl_seconds || 1800}
                            onChange={(e) => setConfig(c => c ? {
                                ...c,
                                caching: {
                                    ...(c.caching || { enabled: true }),
                                    tier_3_catalog: { ttl_seconds: parseInt(e.target.value) }
                                }
                            } : c)}
                            className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm"
                        />
                    </div>
                </div>
            </div>

            {/* Phase Configurations */}
            <div className="space-y-4">
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                    Phase-Specific Models
                </h3>

                {PHASES.map(phase => {
                    const phaseConfig = config?.routing?.phases?.[phase] || config?.routing?.phase?.[phase];
                    if (!phaseConfig) return null;

                    const isArchitect = phase === 'architect';
                    const isConsensusMode = isArchitect && (phaseConfig as any).consensus_mode;

                    return (
                        <div key={phase} className="bg-card border border-border rounded-xl p-5">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-2">
                                    <Bot className="w-5 h-5 text-primary" />
                                    <h4 className="font-semibold capitalize">{phase}</h4>
                                    {isArchitect && (
                                        <span className={clsx(
                                            "text-xs px-2 py-0.5 rounded-full",
                                            isConsensusMode
                                                ? "bg-purple-500/20 text-purple-400"
                                                : "bg-muted text-muted-foreground"
                                        )}>
                                            {isConsensusMode ? 'Consensus' : 'Single'}
                                        </span>
                                    )}
                                </div>
                                {phaseConfig.reasoning && (
                                    <span className="text-xs text-muted-foreground italic max-w-md truncate">
                                        {phaseConfig.reasoning}
                                    </span>
                                )}
                            </div>

                            {/* Architect Consensus Mode Toggle */}
                            {isArchitect && (
                                <div className="mb-4 p-3 bg-muted/30 rounded-lg">
                                    <label className="flex items-center gap-3 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            checked={isConsensusMode}
                                            onChange={(e) => updatePhaseConfig(phase, 'consensus_mode' as any, e.target.checked)}
                                            className="w-4 h-4 rounded border-border accent-purple-500"
                                        />
                                        <div>
                                            <span className="font-medium">Consensus Mode</span>
                                            <p className="text-xs text-muted-foreground">
                                                Use multiple models and synthesize their outputs
                                            </p>
                                        </div>
                                    </label>

                                    {/* Consensus Model Weights */}
                                    {isConsensusMode && (
                                        <div className="mt-4 grid grid-cols-3 gap-3">
                                            <div className="bg-background rounded-lg p-3">
                                                <label className="block text-xs font-medium text-muted-foreground mb-1">Primary Model</label>
                                                <select
                                                    defaultValue="claude-3-5-sonnet"
                                                    className="w-full px-2 py-1.5 bg-background border border-border rounded text-sm mb-2"
                                                >
                                                    {AVAILABLE_MODELS.map(m => (
                                                        <option key={m.value} value={m.value}>{m.label}</option>
                                                    ))}
                                                </select>
                                                <label className="block text-xs text-muted-foreground">Weight: 0.5</label>
                                            </div>
                                            <div className="bg-background rounded-lg p-3">
                                                <label className="block text-xs font-medium text-muted-foreground mb-1">Secondary Model</label>
                                                <select
                                                    defaultValue="gpt-4o"
                                                    className="w-full px-2 py-1.5 bg-background border border-border rounded text-sm mb-2"
                                                >
                                                    {AVAILABLE_MODELS.map(m => (
                                                        <option key={m.value} value={m.value}>{m.label}</option>
                                                    ))}
                                                </select>
                                                <label className="block text-xs text-muted-foreground">Weight: 0.3</label>
                                            </div>
                                            <div className="bg-background rounded-lg p-3">
                                                <label className="block text-xs font-medium text-muted-foreground mb-1">Tertiary Model</label>
                                                <select
                                                    defaultValue="gemini-2.5-pro"
                                                    className="w-full px-2 py-1.5 bg-background border border-border rounded text-sm mb-2"
                                                >
                                                    {AVAILABLE_MODELS.map(m => (
                                                        <option key={m.value} value={m.value}>{m.label}</option>
                                                    ))}
                                                </select>
                                                <label className="block text-xs text-muted-foreground">Weight: 0.2</label>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <div>
                                    <label className="block text-xs font-medium text-muted-foreground mb-1">
                                        {isConsensusMode ? 'Synthesis Model' : 'Model'}
                                    </label>
                                    <select
                                        value={phaseConfig.model || ''}
                                        onChange={(e) => {
                                            const model = AVAILABLE_MODELS.find(m => m.value === e.target.value);
                                            updatePhaseConfig(phase, 'model', e.target.value);
                                            if (model) updatePhaseConfig(phase, 'provider', model.provider);
                                        }}
                                        className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm"
                                    >
                                        {AVAILABLE_MODELS.map(m => (
                                            <option key={m.value} value={m.value}>{m.label}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-xs font-medium text-muted-foreground mb-1">Temperature</label>
                                    <input
                                        type="number"
                                        step="0.1"
                                        min="0"
                                        max="1"
                                        value={phaseConfig.temperature || 0}
                                        onChange={(e) => updatePhaseConfig(phase, 'temperature', parseFloat(e.target.value))}
                                        className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-medium text-muted-foreground mb-1">Max Tokens</label>
                                    <input
                                        type="number"
                                        value={phaseConfig.max_tokens || 4000}
                                        onChange={(e) => updatePhaseConfig(phase, 'max_tokens', parseInt(e.target.value))}
                                        className="w-full px-3 py-2 bg-background border border-border rounded-lg text-sm"
                                    />
                                </div>
                                <div className="flex items-end gap-4">
                                    {phase === 'reviewer' && (
                                        <label className="flex items-center gap-2 text-sm cursor-pointer">
                                            <input
                                                type="checkbox"
                                                checked={phaseConfig.producer_reviewer_loop || false}
                                                onChange={(e) => updatePhaseConfig(phase, 'producer_reviewer_loop', e.target.checked)}
                                                className="w-4 h-4 rounded border-border"
                                            />
                                            Review Loop
                                        </label>
                                    )}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

