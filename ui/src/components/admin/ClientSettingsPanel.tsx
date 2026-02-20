import { useState, useEffect } from 'react';
import { DynButton } from '@dyn-ui/react';
import { Save, RefreshCw, AlertTriangle, Users, BookOpen } from 'lucide-react';
import { api } from '../../lib/api';

interface ClientSettings {
    allowed_user_models: string[];
    allowed_user_options: {
        modes: string[];
        form_studio: boolean;
        show_review_strategy: boolean;
        show_consensus_mode: boolean;
        show_retrieval_mode: boolean;
    };
    allowed_rag_tiers: number[];
}

const ALL_MODELS = [
    { id: 'gpt-5-nano', label: 'GPT-5 Nano ⚡' },
    { id: 'gpt-5-mini', label: 'GPT-5 Mini 🚀' },
    { id: 'gpt-5.2', label: 'GPT-5.2 🧠' },
    { id: 'claude-sonnet-4.5', label: 'Claude Sonnet 4.5 💡' },
    { id: 'claude-opus-4.6', label: 'Claude Opus 4.6 🔬' },
    { id: 'gemini-3-flash', label: 'Gemini 3 Flash ⚡' },
    { id: 'gemini-3-pro', label: 'Gemini 3 Pro 📖' },
    { id: 'sonar-deep-research', label: 'Sonar Deep Research 🌐' },
    { id: 'sonar', label: 'Sonar 🔍' }
];

export function ClientSettingsPanel() {
    const [settings, setSettings] = useState<ClientSettings>({
        allowed_user_models: ['gpt-5-mini', 'gpt-5.2'],
        allowed_user_options: {
            modes: ['fast', 'thinking', 'agentic'],
            form_studio: true,
            show_review_strategy: false,
            show_consensus_mode: false,
            show_retrieval_mode: false
        },
        allowed_rag_tiers: [3, 4]
    });

    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    useEffect(() => {
        loadSettings();
    }, []);

    const loadSettings = async () => {
        setLoading(true);
        try {
            const data = await api.get('/config/settings');
            const limits = data.limits || {};
            setSettings({
                allowed_user_models: limits.allowed_user_models || ['gpt-5-mini', 'gpt-5.2'],
                allowed_user_options: limits.allowed_user_options || {
                    modes: ['fast', 'thinking', 'agentic'],
                    form_studio: true,
                    show_review_strategy: false,
                    show_consensus_mode: false,
                    show_retrieval_mode: false
                },
                allowed_rag_tiers: limits.allowed_rag_tiers || [3, 4]
            });
        } catch (error) {
            setMessage({ type: 'error', text: 'Failed to load settings' });
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = async () => {
        setSaving(true);
        setMessage(null);
        try {
            // /config/approve is basically /config/settings post that writes to limits
            const payload = {
                limits: {
                    allowed_user_models: settings.allowed_user_models,
                    allowed_user_options: settings.allowed_user_options,
                    allowed_rag_tiers: settings.allowed_rag_tiers
                }
            };
            await api.post('/config/approve', payload);
            setMessage({ type: 'success', text: 'Settings approved and saved to config!' });
        } catch (error) {
            setMessage({ type: 'error', text: 'Failed to approve settings' });
        } finally {
            setSaving(false);
        }
    };

    const toggleModel = (id: string) => {
        setSettings(prev => ({
            ...prev,
            allowed_user_models: prev.allowed_user_models.includes(id)
                ? prev.allowed_user_models.filter(m => m !== id)
                : [...prev.allowed_user_models, id]
        }));
    };

    const toggleMode = (mode: string) => {
        setSettings(prev => ({
            ...prev,
            allowed_user_options: {
                ...prev.allowed_user_options,
                modes: prev.allowed_user_options.modes.includes(mode)
                    ? prev.allowed_user_options.modes.filter(m => m !== mode)
                    : [...prev.allowed_user_options.modes, mode]
            }
        }));
    };

    const toggleTier = (tier: number) => {
        setSettings(prev => ({
            ...prev,
            allowed_rag_tiers: prev.allowed_rag_tiers.includes(tier)
                ? prev.allowed_rag_tiers.filter(t => t !== tier)
                : [...prev.allowed_rag_tiers, tier]
        }));
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight">Client Configurations</h2>
                    <p className="text-muted-foreground">Manage what is allowed in the Playground and VS Code Extension.</p>
                </div>
                <div className="flex gap-2">
                    <DynButton
                        kind="secondary"
                        size="sm"
                        onClick={loadSettings}
                        disabled={loading}
                        icon={<RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />}
                        label="Refresh"
                    />
                    <DynButton
                        kind="primary"
                        size="sm"
                        onClick={handleApprove}
                        disabled={saving}
                        icon={<Save className="w-4 h-4 mr-2" />}
                        label="Final Approve"
                    />
                </div>
            </div>

            {message && (
                <div className={`p-4 rounded-lg flex items-center gap-2 ${message.type === 'success' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                    {message.type === 'error' && <AlertTriangle className="w-4 h-4" />}
                    {message.text}
                </div>
            )}

            <div className="bg-card border border-border rounded-xl p-6 space-y-5">
                <div className="flex items-center gap-2 font-semibold text-lg">
                    <Users className="w-5 h-5 text-primary" />
                    Allowed Models (Whitelist)
                </div>
                <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                    {ALL_MODELS.map(model => (
                        <label key={model.id} className="flex items-center gap-3 p-3 rounded-lg border border-border bg-background cursor-pointer hover:border-primary/50 transition-colors">
                            <input
                                type="checkbox"
                                className="w-4 h-4 rounded appearance-none border border-input focus:ring-primary checked:bg-primary checked:border-primary"
                                checked={settings.allowed_user_models.includes(model.id)}
                                onChange={() => toggleModel(model.id)}
                            />
                            <span className="text-sm font-medium">{model.label}</span>
                        </label>
                    ))}
                </div>
            </div>

            <div className="bg-card border border-border rounded-xl p-6 space-y-5">
                <div className="flex items-center gap-2 font-semibold text-lg">
                    <AlertTriangle className="w-5 h-5 text-primary" />
                    Allowed User Options
                </div>

                <div className="space-y-4">
                    <h3 className="font-medium text-sm text-muted-foreground">Operating Modes</h3>
                    <div className="flex gap-4">
                        {['fast', 'thinking', 'agentic'].map(mode => (
                            <label key={mode} className="flex items-center gap-2">
                                <input
                                    type="checkbox"
                                    className="w-4 h-4"
                                    checked={settings.allowed_user_options.modes.includes(mode)}
                                    onChange={() => toggleMode(mode)}
                                />
                                <span className="text-sm capitalize">{mode}</span>
                            </label>
                        ))}
                    </div>

                    <h3 className="font-medium text-sm text-muted-foreground mt-4">Features</h3>
                    <div className="grid grid-cols-2 gap-4">
                        <label className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                className="w-4 h-4"
                                checked={settings.allowed_user_options.form_studio}
                                onChange={(e) => setSettings(s => ({ ...s, allowed_user_options: { ...s.allowed_user_options, form_studio: e.target.checked } }))}
                            />
                            <span className="text-sm">Enable Form Studio Tab</span>
                        </label>
                        <label className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                className="w-4 h-4"
                                checked={settings.allowed_user_options.show_review_strategy}
                                onChange={(e) => setSettings(s => ({ ...s, allowed_user_options: { ...s.allowed_user_options, show_review_strategy: e.target.checked } }))}
                            />
                            <span className="text-sm">Show Review Strategy Option</span>
                        </label>
                        <label className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                className="w-4 h-4"
                                checked={settings.allowed_user_options.show_consensus_mode}
                                onChange={(e) => setSettings(s => ({ ...s, allowed_user_options: { ...s.allowed_user_options, show_consensus_mode: e.target.checked } }))}
                            />
                            <span className="text-sm">Show Consensus Mode Option</span>
                        </label>
                    </div>
                </div>
            </div>

            <div className="bg-card border border-border rounded-xl p-6 space-y-5">
                <div className="flex items-center gap-2 font-semibold text-lg">
                    <BookOpen className="w-5 h-5 text-primary" />
                    Client RAG Access (Extension Knowledge Tab)
                </div>
                <p className="text-sm text-muted-foreground -mt-3">Select which RAG tiers users can view and edit directly from the client. Tiers 1-2 (Governance/Styling) should typically be admin-only.</p>
                <div className="flex gap-6">
                    {[1, 2, 3, 4].map(tier => (
                        <label key={tier} className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                className="w-4 h-4"
                                checked={settings.allowed_rag_tiers.includes(tier)}
                                onChange={() => toggleTier(tier)}
                            />
                            <span className="text-sm font-medium">Tier {tier}</span>
                        </label>
                    ))}
                </div>
            </div>
        </div>
    );
}
