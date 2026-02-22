import React, { useState, useCallback, useRef } from 'react';
import { api, API_BASE_URL } from '../lib/api';
import clsx from 'clsx';
import {
    Upload, Eye, Code2, LayoutGrid, Columns, ListOrdered,
    CheckCircle2, XCircle, AlertTriangle, FileJson, Loader2,
    Download, Sparkles, ChevronRight, Eye as EyeIcon,
    GitBranch, ShieldCheck, Database, Zap, ChevronDown, ChevronUp,
    MessageSquare, StopCircle
} from 'lucide-react';
import { FormChatPanel } from './FormChatPanel';
import './form-studio-preview.css';

// ─── Types ──────────────────────────────────────────────────────────────────

interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
    updatedSchema?: any;
    schemaDiff?: { changes: any[]; explanation: string };
    ragSources?: string[];
    timestamp: Date;
    streaming?: boolean;
}

interface PreviewField {
    id: string;
    label: string;
    type: string;
    layout?: { span?: 'full' | 'half' | 'third' | 'quarter' | string };
    required?: boolean;
    placeholder?: string;
    helperText?: string;
    options?: { value: string; label: string }[];
    minLength?: number;
    maxLength?: number;
    min?: number;
    max?: number;
}

interface PreviewSection {
    title: string;
    fields: PreviewField[];
    showWhen?: any;
}

interface LogicSummary {
    visibilityRules: { target: string; targetTitle?: string; showWhen: { field: string; operator: string; value: any } }[];
    crossValidations: { rule: string; errorMessage: string; errorTarget: string }[];
    lookupDefinitions: { name: string; endpoint: string; method: string; cache: boolean; cacheTTL?: number }[];
    lookupFields: { fieldId: string; label: string; lookupRef: string; dependsOn?: string }[];
    customValidators: { fieldId: string; label: string; rule: string; errorMessage: string }[];
    hasLogic: boolean;
}

interface PreviewConfig {
    formConfig: { sections: PreviewSection[] };
    dummyValues: Record<string, any>;
    fieldMeta: Record<string, { originalType: string; visibility?: any; lookupRef?: string }>;
    layout: string;
    complexity: string;
    warnings: string[];
    metadata: { title: string; description: string; fieldCount: number };
    actions: { component: string; props: { label: string; color: string; type: string } }[];
    logicSummary?: LogicSummary;
}

// ─── Logic Inspector Panel ──────────────────────────────────────────────────

function LogicInspector({ logic }: { logic: LogicSummary }) {
    const [expanded, setExpanded] = useState(true);

    const hasAnything = logic.visibilityRules.length > 0
        || logic.crossValidations.length > 0
        || logic.lookupDefinitions.length > 0
        || logic.customValidators.length > 0;

    if (!hasAnything) return null;

    return (
        <div className="rounded-xl border border-border/60 bg-card/30 overflow-hidden">
            <button
                onClick={() => setExpanded(e => !e)}
                className="w-full flex items-center justify-between px-4 py-3 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted/30 transition-all"
            >
                <div className="flex items-center gap-2">
                    <Zap className="w-4 h-4 text-yellow-400" />
                    <span className="text-yellow-400/90">Logika &amp; Validacije</span>
                    <span className="text-xs text-muted-foreground/60 font-normal">
                        — nisu vidljive u Preview-u, biće implementirane pri generisanju
                    </span>
                </div>
                {expanded
                    ? <ChevronUp className="w-3.5 h-3.5" />
                    : <ChevronDown className="w-3.5 h-3.5" />}
            </button>

            {expanded && (
                <div className="px-4 pb-4 space-y-4 border-t border-border/40">

                    {/* Conditional Visibility */}
                    {logic.visibilityRules.length > 0 && (
                        <div className="pt-3">
                            <div className="flex items-center gap-1.5 mb-2">
                                <GitBranch className="w-3.5 h-3.5 text-blue-400" />
                                <span className="text-xs font-semibold text-blue-400">Uslovna Vidljivost ({logic.visibilityRules.length})</span>
                            </div>
                            <div className="space-y-1.5">
                                {logic.visibilityRules.map((r, i) => (
                                    <div key={i} className="text-xs rounded-lg bg-blue-500/8 border border-blue-500/15 px-3 py-2 flex items-start gap-2">
                                        <span className="font-mono text-blue-300/80 shrink-0">⊙ {r.targetTitle || r.target}</span>
                                        <span className="text-muted-foreground">
                                            prikaži kad <code className="text-blue-300 bg-blue-900/20 px-1 rounded">{r.showWhen?.field}</code>
                                            {' '}{r.showWhen?.operator}{' '}
                                            <code className="text-green-300 bg-green-900/20 px-1 rounded">{String(r.showWhen?.value)}</code>
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Cross-field Validations */}
                    {logic.crossValidations.length > 0 && (
                        <div>
                            <div className="flex items-center gap-1.5 mb-2">
                                <ShieldCheck className="w-3.5 h-3.5 text-orange-400" />
                                <span className="text-xs font-semibold text-orange-400">Međuzavisne Validacije ({logic.crossValidations.length})</span>
                            </div>
                            <div className="space-y-1.5">
                                {logic.crossValidations.map((v, i) => (
                                    <div key={i} className="text-xs rounded-lg bg-orange-500/8 border border-orange-500/15 px-3 py-2">
                                        <div className="font-mono text-orange-300/90 mb-0.5">{v.rule}</div>
                                        <div className="text-muted-foreground/70">{v.errorMessage}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Custom Validators */}
                    {logic.customValidators.length > 0 && (
                        <div>
                            <div className="flex items-center gap-1.5 mb-2">
                                <ShieldCheck className="w-3.5 h-3.5 text-purple-400" />
                                <span className="text-xs font-semibold text-purple-400">Prilagođeni Validator-i ({logic.customValidators.length})</span>
                            </div>
                            <div className="space-y-1.5">
                                {logic.customValidators.map((v, i) => (
                                    <div key={i} className="text-xs rounded-lg bg-purple-500/8 border border-purple-500/15 px-3 py-2">
                                        <span className="font-mono text-purple-300/90">{v.label}</span>
                                        <span className="text-muted-foreground/70 ml-2">→ {v.rule}</span>
                                        <div className="text-muted-foreground/50 mt-0.5">{v.errorMessage}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Lookup Definitions */}
                    {logic.lookupDefinitions.length > 0 && (
                        <div>
                            <div className="flex items-center gap-1.5 mb-2">
                                <Database className="w-3.5 h-3.5 text-teal-400" />
                                <span className="text-xs font-semibold text-teal-400">Dinamički Lookup-ovi ({logic.lookupDefinitions.length})</span>
                            </div>
                            <div className="space-y-1.5">
                                {logic.lookupDefinitions.map((l, i) => {
                                    const dep = logic.lookupFields.find(f => f.lookupRef === l.name && f.dependsOn);
                                    return (
                                        <div key={i} className="text-xs rounded-lg bg-teal-500/8 border border-teal-500/15 px-3 py-2 flex items-center justify-between">
                                            <div>
                                                <span className="font-mono text-teal-300/90">{l.name}</span>
                                                <span className="text-muted-foreground/60 ml-2">{l.method} {l.endpoint}</span>
                                                {dep && <span className="text-yellow-400/70 ml-2">↳ depends on: {dep.dependsOn}</span>}
                                            </div>
                                            {l.cache && (
                                                <span className="text-[10px] bg-teal-500/15 text-teal-400 px-1.5 py-0.5 rounded">
                                                    cache {l.cacheTTL ? `${l.cacheTTL}s` : ''}
                                                </span>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

// ─── Default Template ───────────────────────────────────────────────────────

const DEFAULT_TEMPLATE = JSON.stringify({
    metadata: { title: "Example Form", version: "1.0", description: "A sample registration form" },
    form: {
        fields: [
            { id: "firstName", type: "text", label: "First Name", required: true, placeholder: "Enter first name" },
            { id: "lastName", type: "text", label: "Last Name", required: true },
            { id: "email", type: "email", label: "Email Address", required: true },
            { id: "department", type: "select", label: "Department", options: ["Engineering", "HR", "Sales", "Marketing"] },
            { id: "startDate", type: "date", label: "Start Date" },
            { id: "bio", type: "textarea", label: "Short Bio" }
        ],
        actions: [{ type: "submit", label: "Register", variant: "primary" }]
    }
}, null, 2);

// ─── Field Renderer (Token-Based) ───────────────────────────────────────────

function PreviewFieldRenderer({ field, value }: { field: PreviewField; value: any }) {
    switch (field.type) {
        case 'dropdown':
            return (
                <select className="fs-preview-input fs-preview-select" defaultValue={value || ''}>
                    <option value="" disabled>Select...</option>
                    {(field.options || []).map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                </select>
            );
        case 'radio':
            return (
                <div className="fs-preview-radio-group">
                    {(field.options || []).map(opt => (
                        <label key={opt.value} className="fs-preview-radio-wrap">
                            <input
                                type="radio"
                                name={field.id}
                                value={opt.value}
                                defaultChecked={value === opt.value}
                                className="fs-preview-radio"
                            />
                            <span className="fs-preview-radio-label">{opt.label}</span>
                        </label>
                    ))}
                </div>
            );
        case 'checkbox':
            return (
                <label className="fs-preview-checkbox-wrap">
                    <input type="checkbox" defaultChecked={!!value} className="fs-preview-checkbox" />
                    <span className="fs-preview-checkbox-label">{field.label}</span>
                </label>
            );
        case 'number':
            return <input type="number" className="fs-preview-input" defaultValue={value} min={field.min} max={field.max} placeholder={field.placeholder} />;
        case 'date':
            return <input type="date" className="fs-preview-input fs-preview-date" defaultValue={value} />;
        case 'email':
            return <input type="email" className="fs-preview-input" defaultValue={value} placeholder={field.placeholder || 'email@example.com'} />;
        case 'tel':
            return <input type="tel" className="fs-preview-input" defaultValue={value} placeholder={field.placeholder || '+381...'} />;
        case 'textarea':
            return <textarea className="fs-preview-input fs-preview-textarea" defaultValue={value} placeholder={field.placeholder} rows={3} />;
        default:
            return <input type="text" className="fs-preview-input" defaultValue={value} placeholder={field.placeholder} />;
    }
}

// ─── Live Preview Component (Token-Based) ───────────────────────────────────

function FormPreview({ preview }: { preview: PreviewConfig }) {
    return (
        <div className="fs-preview bg-card border border-border rounded-xl overflow-hidden shadow-lg">
            {/* Form Header */}
            <div className="fs-preview-header">
                <h3 className="fs-preview-title">{preview.metadata.title}</h3>
                {preview.metadata.description && (
                    <p className="fs-preview-description">{preview.metadata.description}</p>
                )}
                <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                    <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium">
                        {preview.layout}
                    </span>
                    <span>{preview.metadata.fieldCount} fields</span>
                    <span className={clsx(
                        "px-2 py-0.5 rounded-full font-medium",
                        preview.complexity === 'low' && "bg-green-500/10 text-green-500",
                        preview.complexity === 'medium' && "bg-yellow-500/10 text-yellow-500",
                        preview.complexity === 'high' && "bg-red-500/10 text-red-500",
                    )}>
                        {preview.complexity} complexity
                    </span>
                </div>
            </div>

            {/* Form Body */}
            <div className="fs-preview-body">
                {preview.formConfig.sections.map((section, si) => (
                    <div key={si} className="fs-preview-section">
                        {section.title !== 'General' && section.title !== 'Default' && (
                            <h4 className="fs-preview-section-title">
                                {section.title}
                            </h4>
                        )}
                        <div className="fs-preview-grid">
                            {section.fields.map(field => {
                                const meta = preview.fieldMeta[field.id];
                                const isCheckbox = field.type === 'checkbox';

                                // colSpan → grid column span
                                const span = field.layout?.span || 'full';
                                const colSpanStyle: React.CSSProperties = {};
                                if (span === 'full') colSpanStyle.gridColumn = 'span 12';
                                else if (span === 'half') colSpanStyle.gridColumn = 'span 6';
                                else if (span === 'third') colSpanStyle.gridColumn = 'span 4';
                                else if (span === 'quarter') colSpanStyle.gridColumn = 'span 3';
                                else colSpanStyle.gridColumn = 'span 12';

                                return (
                                    <div
                                        key={field.id}
                                        className="fs-preview-field"
                                        style={colSpanStyle}
                                    >
                                        {!isCheckbox && (
                                            <label className="fs-preview-label">
                                                {field.label}
                                                {field.required && <span className="fs-preview-required">*</span>}
                                            </label>
                                        )}
                                        <PreviewFieldRenderer field={field} value={preview.dummyValues[field.id]} />
                                        {field.helperText && (
                                            <p className="fs-preview-help">{field.helperText}</p>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                ))}

                {/* Actions */}
                <div className="fs-preview-actions">
                    {preview.actions.map((action, ai) => (
                        <button
                            key={ai}
                            className={clsx(
                                "fs-preview-btn",
                                action.props.color === 'primary' || action.props.type === 'submit'
                                    ? "fs-preview-btn-primary"
                                    : "fs-preview-btn-secondary"
                            )}
                        >
                            {action.props.label}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}

// ─── Main Form Studio Tab ───────────────────────────────────────────────────

export function FormStudioTab() {
    const [jsonInput, setJsonInput] = useState(DEFAULT_TEMPLATE);
    const [preview, setPreview] = useState<PreviewConfig | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [layoutOverride, setLayoutOverride] = useState<string | null>(null);
    const [activeView, setActiveView] = useState<'split' | 'preview' | 'editor' | 'chat'>('split');
    const [generating, setGenerating] = useState(false);
    const [generateResult, setGenerateResult] = useState<any>(null);
    const [enrichedInstructions, setEnrichedInstructions] = useState<string | null>(null);
    const [showEnrichedInstructions, setShowEnrichedInstructions] = useState(false);
    const [autoRefreshed, setAutoRefreshed] = useState(false);
    const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const generateAbortRef = useRef<AbortController | null>(null);

    // ─── Preview generation ─────────────────────────────────────────────

    const generatePreview = useCallback(async (jsonStr?: string) => {
        const input = jsonStr || jsonInput;
        setLoading(true);
        setError(null);

        try {
            const parsed = JSON.parse(input);
            const response = await api.post('/forms/preview', {
                schema_data: parsed,
                layout_override: layoutOverride
            });
            setPreview(response);
        } catch (err: any) {
            if (err instanceof SyntaxError) {
                setError('Invalid JSON. Please check your input.');
            } else {
                setError(err.message || 'Preview generation failed.');
            }
        } finally {
            setLoading(false);
        }
    }, [jsonInput, layoutOverride]);

    // ─── File upload handler ────────────────────────────────────────────

    const handleFileUpload = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        const text = await file.text();
        setJsonInput(text);
        generatePreview(text);
    }, [generatePreview]);

    const handleGenerate = useCallback(async () => {
        setGenerating(true);
        setGenerateResult(null);
        const controller = new AbortController();
        generateAbortRef.current = controller;
        try {
            const parsed = JSON.parse(jsonInput);
            const projectName = (parsed.metadata?.title || 'form')
                .toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');

            const result = await api.post('/forms/generate', {
                schema_data: parsed,
                project_name: projectName,
                layout_override: layoutOverride,
                enriched_instructions: enrichedInstructions
            }, { signal: controller.signal });
            // Attach project name for download link
            setGenerateResult({ ...result, projectName });
        } catch (err: any) {
            if (err.name === 'AbortError') {
                setError('Generisanje prekinuto.');
            } else {
                setError(err.message || 'Generation failed.');
            }
        } finally {
            setGenerating(false);
            generateAbortRef.current = null;
        }
    }, [jsonInput, layoutOverride, enrichedInstructions]);

    const handleStopGeneration = useCallback(async () => {
        // 1. Abort the frontend fetch
        if (generateAbortRef.current) {
            generateAbortRef.current.abort();
        }
        // 2. Call backend /stop to cancel server-side task
        try {
            await api.post('/stop', {});
        } catch (_) {
            // Ignore — stop is best-effort
        }
    }, []);

    // ─── Layout ─────────────────────────────────────────────────────────

    const layouts = [
        { id: null, label: 'Auto', icon: Sparkles },
        { id: 'standard', label: 'Standard', icon: LayoutGrid },
        { id: 'tabs', label: 'Tabs', icon: Columns },
        { id: 'stepper', label: 'Stepper', icon: ListOrdered },
    ];

    // ─── Chat integration ────────────────────────────────────────────

    const handleChatSchemaUpdate = useCallback((newSchema: any) => {
        setJsonInput(JSON.stringify(newSchema, null, 2));
        generatePreview(JSON.stringify(newSchema, null, 2));
        setAutoRefreshed(true);
        setTimeout(() => setAutoRefreshed(false), 3000);
    }, [generatePreview]);

    const handleEnrichedGenerate = useCallback((prompt: string) => {
        setEnrichedInstructions(prompt);
    }, []);

    return (
        <div className="space-y-4">
            {/* Toolbar */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <h2 className="text-lg font-semibold">Form Studio</h2>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium">Preview</span>
                </div>

                <div className="flex items-center gap-2">
                    {/* Layout Switcher */}
                    <div className="flex bg-muted/50 rounded-lg p-0.5">
                        {layouts.map(l => (
                            <button
                                key={l.id || 'auto'}
                                onClick={() => { setLayoutOverride(l.id); if (preview) generatePreview(); }}
                                className={clsx(
                                    "flex items-center gap-1.5 px-2.5 py-1.5 text-xs rounded-md transition-all",
                                    layoutOverride === l.id
                                        ? "bg-background shadow text-foreground font-medium"
                                        : "text-muted-foreground hover:text-foreground"
                                )}
                            >
                                <l.icon className="w-3.5 h-3.5" />
                                {l.label}
                            </button>
                        ))}
                    </div>

                    {/* View Toggle */}
                    <div className="flex bg-muted/50 rounded-lg p-0.5 ml-2">
                        {[
                            { id: 'split' as const, label: 'Split' },
                            { id: 'editor' as const, label: 'Editor' },
                            { id: 'preview' as const, label: 'Preview' },
                            { id: 'chat' as const, label: 'AI Chat', icon: MessageSquare },
                        ].map(v => (
                            <button
                                key={v.id}
                                onClick={() => setActiveView(v.id)}
                                className={clsx(
                                    "flex items-center gap-1 px-2.5 py-1.5 text-xs rounded-md transition-all",
                                    activeView === v.id
                                        ? "bg-background shadow text-foreground font-medium"
                                        : "text-muted-foreground hover:text-foreground"
                                )}
                            >
                                {'icon' in v && v.icon && <v.icon className="w-3 h-3" />}
                                {v.label}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Error / Warning Display */}
            {error && (
                <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 text-red-400 text-sm">
                    <XCircle className="w-4 h-4 flex-shrink-0" />
                    {error}
                    <button onClick={() => setError(null)} className="ml-auto text-xs hover:text-red-300">Dismiss</button>
                </div>
            )}

            {/* Generation Success */}
            {generateResult && (
                <div className="flex items-center gap-4 p-4 rounded-lg bg-green-500/10 text-green-400 border border-green-500/20">
                    <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
                    <div className="flex-1">
                        <p className="font-medium">{generateResult.message}</p>
                        <p className="text-xs text-green-400/70 mt-0.5 max-w-lg truncate" title={generateResult.project_path}>
                            Output: {generateResult.project_path}
                        </p>
                    </div>
                    {generateResult.projectName && (
                        <button
                            onClick={() => window.open(`${API_BASE_URL}/forms/download/${generateResult.projectName}`, '_blank')}
                            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-all border border-green-500/30 whitespace-nowrap"
                        >
                            <Download className="w-3.5 h-3.5" />
                            Download ZIP
                        </button>
                    )}
                </div>
            )}

            {/* Main Content */}
            <div className={clsx(
                "gap-4",
                activeView === 'split' && "grid grid-cols-1 lg:grid-cols-3",
                activeView === 'editor' && "grid grid-cols-1",
                activeView === 'preview' && "grid grid-cols-1",
                activeView === 'chat' && "grid grid-cols-1 lg:grid-cols-2",
            )}>
                {/* JSON Editor */}
                {(activeView !== 'preview' && activeView !== 'chat') && (
                    <div className="space-y-3">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                                <Code2 className="w-4 h-4" />
                                JSON Schema Editor
                            </div>
                            <div className="flex gap-2">
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept=".json"
                                    onChange={handleFileUpload}
                                    className="hidden"
                                />
                                <button
                                    onClick={() => fileInputRef.current?.click()}
                                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg bg-muted/50 text-muted-foreground hover:text-foreground hover:bg-muted transition-all"
                                >
                                    <Upload className="w-3.5 h-3.5" />
                                    Upload JSON
                                </button>
                                <button
                                    onClick={() => generatePreview()}
                                    disabled={loading}
                                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-all disabled:opacity-50"
                                >
                                    {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Eye className="w-3.5 h-3.5" />}
                                    Preview
                                </button>
                            </div>
                        </div>
                        <textarea
                            value={jsonInput}
                            onChange={e => setJsonInput(e.target.value)}
                            className="w-full h-[60vh] p-4 font-mono text-xs bg-[#0d1117] text-[#c9d1d9] border border-border rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-primary/30"
                            spellCheck={false}
                        />

                        {/* Logic Inspector — shown below editor when preview is ready */}
                        {preview?.logicSummary && (
                            <LogicInspector logic={preview.logicSummary} />
                        )}
                    </div>
                )}

                {/* Preview Panel */}
                {activeView !== 'editor' && (
                    <div className="space-y-3">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                                <Eye className="w-4 h-4" />
                                Live Preview
                            </div>
                            {preview && (
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={handleGenerate}
                                        disabled={generating}
                                        className="flex items-center gap-1.5 px-4 py-2 text-xs rounded-lg bg-green-600 text-white hover:bg-green-500 font-medium transition-all disabled:opacity-50 shadow-sm"
                                    >
                                        {generating ? (
                                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                                        ) : (
                                            <CheckCircle2 className="w-3.5 h-3.5" />
                                        )}
                                        {generating ? 'Generisanje...' : 'Approve & Generate Project'}
                                    </button>
                                    {generating && (
                                        <button
                                            onClick={handleStopGeneration}
                                            className="flex items-center gap-1.5 px-3 py-2 text-xs rounded-lg bg-red-600 text-white hover:bg-red-500 font-medium transition-all shadow-sm"
                                            title="Prekini generisanje"
                                        >
                                            <StopCircle className="w-3.5 h-3.5" />
                                            Stop
                                        </button>
                                    )}
                                </div>
                            )}
                        </div>

                        {preview ? (
                            <FormPreview preview={preview} />
                        ) : (
                            <div className="flex flex-col items-center justify-center h-[60vh] border-2 border-dashed border-border/50 rounded-xl text-center">
                                <FileJson className="w-12 h-12 text-muted-foreground/30 mb-4" />
                                <h3 className="text-sm font-medium text-muted-foreground mb-1">No Preview Yet</h3>
                                <p className="text-xs text-muted-foreground/70 max-w-xs">
                                    Edit the JSON schema and click "Preview" to see a live rendering with real DynUI components.
                                </p>
                                <button
                                    onClick={() => generatePreview()}
                                    className="mt-4 flex items-center gap-1.5 px-4 py-2 text-xs rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-all"
                                >
                                    <ChevronRight className="w-3.5 h-3.5" />
                                    Generate Preview
                                </button>
                            </div>
                        )}
                    </div>
                )}

                {/* AI Chat Panel */}
                {(activeView === 'split' || activeView === 'chat') && (
                    <FormChatPanel
                        currentSchema={(() => { try { return JSON.parse(jsonInput); } catch { return {}; } })()}
                        previewState={{
                            layout: preview?.layout,
                            complexity: preview?.complexity,
                            fieldCount: preview?.metadata?.fieldCount,
                            inferredSections: preview?.formConfig?.sections,
                        }}
                        messages={chatMessages}
                        setMessages={setChatMessages}
                        onSchemaUpdate={handleChatSchemaUpdate}
                        onEnrichedGenerate={handleEnrichedGenerate}
                    />
                )}
            </div>

            {/* Enriched Prompt Indicator */}
            {enrichedInstructions && (
                <div className="space-y-2">
                    <div className="flex items-center gap-2 p-3 rounded-lg bg-purple-500/10 text-purple-400 text-sm border border-purple-500/20 shadow-lg shadow-purple-500/5">
                        <Sparkles className="w-4 h-4 shrink-0" />
                        <span className="flex-1 font-medium italic">Obogaćeni prompt spreman — biće prosleđen orkestratoru pri generisanju.</span>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => setShowEnrichedInstructions(!showEnrichedInstructions)}
                                className="flex items-center gap-1 px-2 py-1 rounded bg-purple-500/20 hover:bg-purple-500/30 transition-all text-xs"
                            >
                                {showEnrichedInstructions ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                                {showEnrichedInstructions ? 'Sakrij instrukcije' : 'Prikaži instrukcije'}
                            </button>
                            <button
                                onClick={() => { setEnrichedInstructions(null); setShowEnrichedInstructions(false); }}
                                className="p-1 px-2 text-xs hover:text-purple-300 hover:bg-purple-500/10 rounded transition-all"
                            >Obriši</button>
                        </div>
                    </div>

                    {showEnrichedInstructions && (
                        <div className="p-4 rounded-xl bg-[#0d1117] border border-purple-500/30 text-[#c9d1d9] font-mono text-xs whitespace-pre-wrap max-h-[40vh] overflow-y-auto custom-scrollbar animate-in slide-in-from-top-2 duration-300">
                            {enrichedInstructions}
                        </div>
                    )}
                </div>
            )}

            {/* AI Auto-refresh Toast */}
            {autoRefreshed && (
                <div className="fixed bottom-6 right-6 flex items-center gap-2 p-3 rounded-lg bg-green-600 text-white shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-300 z-50">
                    <Zap className="w-4 h-4" />
                    <span className="text-xs font-semibold">Preview osvežen (AI promene primenjene)</span>
                </div>
            )}
        </div>
    );
}
