import { useState, useEffect } from 'react';
import { Lock, Save, Loader2, CheckCircle, AlertCircle, Eye, EyeOff } from 'lucide-react';
import clsx from 'clsx';

interface ApiKeys {
    OPENAI_API_KEY: string;
    ANTHROPIC_API_KEY: string;
    GOOGLE_API_KEY: string;
    PERPLEXITY_API_KEY: string;
}

export function ApiKeysPanel() {
    const [keys, setKeys] = useState<ApiKeys>({
        OPENAI_API_KEY: '',
        ANTHROPIC_API_KEY: '',
        GOOGLE_API_KEY: '',
        PERPLEXITY_API_KEY: '',
    });
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [saveResult, setSaveResult] = useState<{ success: boolean; message: string } | null>(null);
    const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});

    useEffect(() => {
        loadKeys();
    }, []);

    const loadKeys = async () => {
        setIsLoading(true);
        try {
            const resp = await fetch('http://localhost:8000/config/settings');
            if (resp.ok) {
                const data = await resp.json();
                setKeys(data.api_keys || {});
            }
        } catch (e) {
            console.error("Failed to load keys", e);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSave = async () => {
        setIsSaving(true);
        setSaveResult(null);
        try {
            const resp = await fetch('http://localhost:8000/config/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    models: {}, // Sending empty models since we only want to update keys here
                    api_keys: keys
                })
            });
            if (resp.ok) {
                setSaveResult({ success: true, message: 'API keys updated successfully. Restart may be required.' });
            } else {
                throw new Error('Failed to save');
            }
        } catch (e) {
            setSaveResult({ success: false, message: 'Failed to update API keys' });
        } finally {
            setIsSaving(false);
        }
    };

    const toggleShow = (key: string) => {
        setShowKeys(prev => ({ ...prev, [key]: !prev[key] }));
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold">API Credentials</h2>
                    <p className="text-muted-foreground mt-1">
                        Securely manage your API keys for external LLM providers.
                    </p>
                </div>
                <button
                    onClick={handleSave}
                    disabled={isSaving}
                    className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm hover:bg-primary/90 disabled:opacity-50 transition-all shadow-sm"
                >
                    {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                    Save Keys
                </button>
            </div>

            {saveResult && (
                <div className={clsx(
                    "flex items-center gap-2 p-3 rounded-lg text-sm",
                    saveResult.success ? "bg-green-500/10 text-green-400 border border-green-500/20" : "bg-red-500/10 text-red-400 border border-red-500/20"
                )}>
                    {saveResult.success ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                    {saveResult.message}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <ApiKeyField
                    label="OpenAI API Key"
                    value={keys.OPENAI_API_KEY}
                    onChange={(v: string) => setKeys({ ...keys, OPENAI_API_KEY: v })}
                    show={showKeys['OPENAI_API_KEY']}
                    onToggle={() => toggleShow('OPENAI_API_KEY')}
                />
                <ApiKeyField
                    label="Anthropic API Key"
                    value={keys.ANTHROPIC_API_KEY}
                    onChange={(v: string) => setKeys({ ...keys, ANTHROPIC_API_KEY: v })}
                    show={showKeys['ANTHROPIC_API_KEY']}
                    onToggle={() => toggleShow('ANTHROPIC_API_KEY')}
                />
                <ApiKeyField
                    label="Google Gemini Key"
                    value={keys.GOOGLE_API_KEY}
                    onChange={(v: string) => setKeys({ ...keys, GOOGLE_API_KEY: v })}
                    show={showKeys['GOOGLE_API_KEY']}
                    onToggle={() => toggleShow('GOOGLE_API_KEY')}
                />
                <ApiKeyField
                    label="Perplexity API Key"
                    value={keys.PERPLEXITY_API_KEY}
                    onChange={(v: string) => setKeys({ ...keys, PERPLEXITY_API_KEY: v })}
                    show={showKeys['PERPLEXITY_API_KEY']}
                    onToggle={() => toggleShow('PERPLEXITY_API_KEY')}
                />
            </div>

            <div className="bg-amber-500/5 border border-amber-500/20 rounded-xl p-4 flex gap-3">
                <AlertCircle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                <div className="text-sm text-amber-200/80">
                    <p className="font-semibold text-amber-500 uppercase text-[10px] tracking-widest mb-1">Security Note</p>
                    Keys are stored in your local <code className="bg-black/30 px-1 rounded">.env</code> file.
                    They are never sent to external servers other than the configured LLM providers.
                    Values showing as <code className="bg-black/30 px-1 rounded">****</code> are existing keys that won't be overwritten unless you change them.
                </div>
            </div>
        </div>
    );
}

function ApiKeyField({ label, value, onChange, show, onToggle }: any) {
    return (
        <div className="bg-card border border-border rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between">
                <label className="text-sm font-semibold">{label}</label>
                <div className="flex items-center gap-1 text-[10px] uppercase font-bold text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                    <Lock className="w-2.5 h-2.5" /> Secure
                </div>
            </div>
            <div className="relative group">
                <input
                    type={show ? "text" : "password"}
                    value={value || ''}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder="sk-..."
                    className="w-full px-4 py-2 bg-background border border-border rounded-lg focus:border-primary focus:ring-1 focus:ring-primary/20 outline-none font-mono text-xs transition-all"
                />
                <button
                    onClick={onToggle}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                    {show ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
            </div>
        </div>
    );
}
