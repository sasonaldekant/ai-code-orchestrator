import { useState, useEffect } from 'react';

import { DynButton, DynInput } from '@dyn-ui/react';
import { Save, RefreshCw, AlertTriangle, Sliders } from 'lucide-react';
import { api } from '../../lib/api';

interface GlobalConfig {
    temperature: number;
    max_retries: number;
    max_feedback_iterations: number;
    deep_search: boolean;
    per_task_budget?: number;
    per_hour_budget?: number;
    per_day_budget?: number;
}

export function GlobalSettingsPanel() {
    console.log('Rendering GlobalSettingsPanel'); // Debug log

    const [config, setConfig] = useState<GlobalConfig>({
        temperature: 0.0,
        max_retries: 3,
        max_feedback_iterations: 3,
        deep_search: false,
        per_task_budget: 0.25,
        per_hour_budget: 1.0,
        per_day_budget: 2.0
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
            console.log('Fetching settings...');
            const data = await api.get('/config/settings');
            console.log('Settings fetched:', data);

            // Merge global_config with limits from the separate key if available
            let mergedConfig = { ...data.global_config };

            if (data.limits && data.limits.global) {
                mergedConfig = { ...mergedConfig, ...data.limits.global };
            }

            if (mergedConfig) {
                setConfig(mergedConfig);
            }
        } catch (error) {
            console.error('Failed to load settings:', error);
            setMessage({ type: 'error', text: 'Failed to load settings' });
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        setMessage(null);
        try {
            console.log('Saving settings:', config);

            // The API expects global_config within the request body. 
            // It uses this to update both limits.yaml (global section) and others.
            await api.post('/config/settings', {
                global_config: config,
                // We also explicitly send limits if the backend needs it structured that way,
                // but based on config_routes.py:138, it reads global_config to update limits['global'].
            });
            setMessage({ type: 'success', text: 'Settings saved successfully' });
        } catch (error) {
            console.error('Failed to save settings:', error);
            setMessage({ type: 'error', text: 'Failed to save settings' });
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight">Global Settings</h2>
                    <p className="text-muted-foreground">Configure orchestrator behavior and default parameters.</p>
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
                        onClick={handleSave}
                        disabled={saving}
                        icon={<Save className="w-4 h-4 mr-2" />}
                        label="Save Changes"
                    />
                </div>
            </div>

            {message && (
                <div className={`p-4 rounded-lg flex items-center gap-2 ${message.type === 'success' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                    {message.type === 'error' && <AlertTriangle className="w-4 h-4" />}
                    {message.text}
                </div>
            )}

            <div className="grid gap-6 md:grid-cols-2">
                <div className="bg-card border border-border rounded-xl p-6 space-y-5">
                    <div className="flex items-center gap-2 font-semibold text-lg">
                        <Sliders className="w-5 h-5 text-primary" />
                        Core Parameters
                    </div>
                    <div className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Global Temperature ({config.temperature})</label>
                            <input
                                type="range"
                                min="0"
                                max="1"
                                step="0.1"
                                value={config.temperature}
                                onChange={(e) => setConfig({ ...config, temperature: parseFloat(e.target.value) })}
                                className="w-full"
                            />
                            <p className="text-xs text-muted-foreground">Controls randomness: 0.0 is deterministic, 1.0 is creative.</p>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Deep Search Default</label>
                            <div className="flex items-center gap-2">
                                <input
                                    type="checkbox"
                                    checked={config.deep_search}
                                    onChange={(e) => setConfig({ ...config, deep_search: e.target.checked })}
                                    className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
                                />
                                <span className="text-sm">Enable Agentic Retrieval by default</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="bg-card border border-border rounded-xl p-6 space-y-5">
                    <div className="flex items-center gap-2 font-semibold text-lg">
                        <RefreshCw className="w-5 h-5 text-primary" />
                        Resilience & Feedback
                    </div>
                    <div className="space-y-4">
                        <DynInput
                            label="Max Retries"
                            type="number"
                            value={config.max_retries.toString()}
                            onChange={(val) => setConfig({ ...config, max_retries: Number(val) || 0 })}
                            min={0}
                            max={10}
                        />
                        <p className="text-xs text-muted-foreground -mt-3">Number of retry attempts per failed phase.</p>

                        <DynInput
                            label="Max Feedback Iterations"
                            type="number"
                            value={config.max_feedback_iterations.toString()}
                            onChange={(val) => setConfig({ ...config, max_feedback_iterations: Number(val) || 0 })}
                            min={0}
                            max={10}
                        />
                        <p className="text-xs text-muted-foreground -mt-3">Maximum self-correction loops for quality improvement.</p>
                    </div>
                </div>

                <div className="bg-card border border-border rounded-xl p-6 space-y-5 md:col-span-2">
                    <div className="flex items-center gap-2 font-semibold text-lg">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                        Budget Limits (USD)
                    </div>
                    <div className="grid md:grid-cols-3 gap-6">
                        <div className="space-y-2">
                            <DynInput
                                label="Per Task Limit"
                                type="number"
                                value={config.per_task_budget?.toString() || "0.25"}
                                onChange={(val) => setConfig({ ...config, per_task_budget: Number(val) || 0 })}
                                min={0}
                                step={0.01}
                            />
                            <p className="text-xs text-muted-foreground">Max cost for a single orchestration request.</p>
                        </div>
                        <div className="space-y-2">
                            <DynInput
                                label="Hourly Limit"
                                type="number"
                                value={config.per_hour_budget?.toString() || "1.0"}
                                onChange={(val) => setConfig({ ...config, per_hour_budget: Number(val) || 0 })}
                                min={0}
                                step={0.1}
                            />
                            <p className="text-xs text-muted-foreground">Max cumulative cost per rolling hour.</p>
                        </div>
                        <div className="space-y-2">
                            <DynInput
                                label="Daily Limit"
                                type="number"
                                value={config.per_day_budget?.toString() || "2.0"}
                                onChange={(val) => setConfig({ ...config, per_day_budget: Number(val) || 0 })}
                                min={0}
                                step={0.5}
                            />
                            <p className="text-xs text-muted-foreground">Hard stop limit per day.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
