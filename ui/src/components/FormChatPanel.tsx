import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { api } from '../lib/api';
import clsx from 'clsx';
import {
    MessageSquare, Send, Loader2, Bot, User, BookOpen,
    Sparkles, ArrowRight, CheckCircle2, XCircle, FileJson,
    Layout, ShieldCheck, Wand2, Columns, Plus, Trash2,
    Eye, EyeOff, GitCompare, StopCircle, Zap
} from 'lucide-react';

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

interface SchemaChange {
    field: string;
    property: string;
    from: string;
    to: string;
}

interface FormChatPanelProps {
    currentSchema: any;
    previewState: {
        layout?: string;
        complexity?: string;
        fieldCount?: number;
        inferredSections?: any[];
    };
    messages: ChatMessage[];
    setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
    onSchemaUpdate: (newSchema: any) => void;
    onEnrichedGenerate: (enrichedPrompt: string) => void;
}

// ─── Schema Diff Utility ────────────────────────────────────────────────────

function computeSchemaDiff(oldSchema: any, newSchema: any): SchemaChange[] {
    const changes: SchemaChange[] = [];
    if (!oldSchema || !newSchema) return changes;

    const oldFields = flattenFields(oldSchema);
    const newFields = flattenFields(newSchema);

    // Detect changed fields
    for (const [id, newField] of Object.entries(newFields)) {
        const oldField = oldFields[id] as any;
        const nf = newField as any;
        if (!oldField) {
            changes.push({ field: id, property: 'field', from: '(none)', to: 'added' });
            continue;
        }
        // Compare key properties
        for (const prop of ['type', 'label', 'required', 'layout.colSpan', 'layout.span', 'placeholder', 'helperText']) {
            const oldVal = getNestedProp(oldField, prop);
            const newVal = getNestedProp(nf, prop);
            if (JSON.stringify(oldVal) !== JSON.stringify(newVal)) {
                changes.push({
                    field: id,
                    property: prop,
                    from: String(oldVal ?? ''),
                    to: String(newVal ?? ''),
                });
            }
        }
    }

    // Detect removed fields
    for (const id of Object.keys(oldFields)) {
        if (!newFields[id]) {
            changes.push({ field: id, property: 'field', from: 'existed', to: '(removed)' });
        }
    }

    return changes;
}

function flattenFields(schema: any): Record<string, any> {
    const fields: Record<string, any> = {};
    const sections = schema?.sections || schema?.formConfig?.sections || [];
    for (const section of sections) {
        for (const field of (section.fields || [])) {
            fields[field.id] = field;
        }
    }
    return fields;
}

function getNestedProp(obj: any, path: string): any {
    return path.split('.').reduce((o, k) => o?.[k], obj);
}

// ─── Quick Actions (Schema-Aware) ───────────────────────────────────────────

function getQuickActions(schema: any, previewState: any) {
    const fields = flattenFields(schema);
    const fieldCount = Object.keys(fields).length;
    const hasValidation = Object.values(fields).some((f: any) => f.validation);
    const hasLogic = Object.values(fields).some((f: any) => f.logic || f.showWhen);
    const sectionCount = (schema?.sections || []).length;

    const actions = [
        {
            label: 'Optimizuj layout',
            icon: Layout,
            prompt: 'Analiziraj layout svih polja i predloži optimalan raspored u grid kolone (half, third, quarter). Sva kratka polja (datum, broj, checkbox) stavi u uže kolone.',
            show: fieldCount > 3,
        },
        {
            label: 'Proveri validacije',
            icon: ShieldCheck,
            prompt: 'Proveri validacije za svako polje. Dodaj nedostajuće: email format, min/max za brojeve, required za bitna polja. Vrati ažuriranu šemu.',
            show: true,
        },
        {
            label: 'Dodaj sekciju',
            icon: Plus,
            prompt: `Forma ima ${sectionCount} sekcija i ${fieldCount} polja. Predloži novu logičnu sekciju koja bi poboljšala organizaciju forme.`,
            show: true,
        },
        {
            label: 'Grupiši u kolone',
            icon: Columns,
            prompt: 'Grupiši srodna polja u redove po 2 ili 3 kolone. Na primer, ime i prezime u isti red (half+half), grad i poštanski broj zajedno (half+half).',
            show: fieldCount > 4,
        },
        {
            label: 'Ukloni polje',
            icon: Trash2,
            prompt: `Prikaži listu svih ${fieldCount} polja sa njihovim ID-jevima. Pitaj me koje polje da uklonim.`,
            show: fieldCount > 1,
        },
        {
            label: 'Dodaj uslovnu logiku',
            icon: EyeOff,
            prompt: 'Predloži showWhen/hideWhen uslovnu logiku za polja koja bi trebalo da budu vidljiva samo pod određenim uslovima.',
            show: !hasLogic && fieldCount > 5,
        },
        {
            label: 'Uporedi promene',
            icon: GitCompare,
            prompt: 'Sumiraj sve promene koje smo napravili u ovoj chat sesiji. Prikaži šta je bilo pre i posle za svaku promenu.',
            show: true,
        },
    ];

    return actions.filter(a => a.show).slice(0, 5);
}

// ─── SSE Helper ─────────────────────────────────────────────────────────────

const API_BASE_URL = typeof window !== 'undefined' && (window as any)._env_?.VITE_API_BASE_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// ─── Component ──────────────────────────────────────────────────────────────

export function FormChatPanel({
    currentSchema,
    previewState,
    messages,
    setMessages,
    onSchemaUpdate,
    onEnrichedGenerate,
}: FormChatPanelProps) {
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [streamingText, setStreamingText] = useState('');
    const [changedFieldIds, setChangedFieldIds] = useState<Set<string>>(new Set());
    const [useStreaming, setUseStreaming] = useState(true);
    const [appliedMessages, setAppliedMessages] = useState<Set<number>>(new Set());
    const [lastAppliedSchema, setLastAppliedSchema] = useState<any>(null);
    const scrollRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLTextAreaElement>(null);
    const abortRef = useRef<AbortController | null>(null);
    const schemaBeforeChatRef = useRef<any>(null);

    // Store initial schema for diff tracking
    useEffect(() => {
        if (!schemaBeforeChatRef.current && currentSchema && Object.keys(currentSchema).length > 0) {
            schemaBeforeChatRef.current = JSON.parse(JSON.stringify(currentSchema));
        }
    }, [currentSchema]);

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, streamingText]);

    // Compute quick actions based on current schema
    const quickActions = useMemo(() =>
        getQuickActions(currentSchema, previewState),
        [currentSchema, previewState]
    );

    // ─── Send message (standard) ────────────────────────────────────────

    const sendMessageStandard = useCallback(async (text: string) => {
        const userMessage: ChatMessage = {
            role: 'user',
            content: text.trim(),
            timestamp: new Date(),
        };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);
        setError(null);

        try {
            const history = messages.map(m => ({ role: m.role, content: m.content }));
            const response = await api.post('/forms/chat', {
                message: text.trim(),
                current_schema: currentSchema,
                chat_history: history,
                preview_state: previewState,
            });

            const assistantMessage: ChatMessage = {
                role: 'assistant',
                content: response.reply,
                updatedSchema: response.updated_schema,
                schemaDiff: response.schema_diff,
                ragSources: response.rag_sources,
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, assistantMessage]);

            if (response.updated_schema) {
                // Compute diff for highlighting
                const diff = computeSchemaDiff(currentSchema, response.updated_schema);
                setChangedFieldIds(new Set(diff.map(d => d.field)));
                onSchemaUpdate(response.updated_schema);

                // Auto-clear highlights after 5s
                setTimeout(() => setChangedFieldIds(new Set()), 5000);
            }
        } catch (err: any) {
            setError(err.message || 'Chat greška.');
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `⚠️ Greška: ${err.message || 'Nepoznata greška'}`,
                timestamp: new Date(),
            }]);
        } finally {
            setLoading(false);
        }
    }, [messages, currentSchema, previewState, onSchemaUpdate]);

    // ─── Send message (SSE streaming) ───────────────────────────────────

    const sendMessageStreaming = useCallback(async (text: string) => {
        const userMessage: ChatMessage = {
            role: 'user',
            content: text.trim(),
            timestamp: new Date(),
        };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);
        setStreamingText('');
        setError(null);

        const controller = new AbortController();
        abortRef.current = controller;

        try {
            const history = messages.map(m => ({ role: m.role, content: m.content }));

            const response = await fetch(`${API_BASE_URL}/forms/chat/stream`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text.trim(),
                    current_schema: currentSchema,
                    chat_history: history,
                    preview_state: previewState,
                }),
                signal: controller.signal,
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const reader = response.body?.getReader();
            if (!reader) throw new Error('No reader');

            const decoder = new TextDecoder();
            let fullText = '';
            let metadata: any = null;

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (!line.startsWith('data: ')) continue;
                    try {
                        const data = JSON.parse(line.slice(6));

                        if (data.type === 'token') {
                            fullText += data.content;
                            setStreamingText(fullText);
                        } else if (data.type === 'metadata') {
                            metadata = data;
                        } else if (data.type === 'error') {
                            throw new Error(data.content);
                        }
                        // 'done' type — stream complete
                    } catch (parseErr) {
                        // Skip malformed lines
                    }
                }
            }

            // Finalize message
            const assistantMessage: ChatMessage = {
                role: 'assistant',
                content: fullText,
                updatedSchema: metadata?.updated_schema,
                schemaDiff: metadata?.schema_diff ? {
                    changes: metadata.schema_diff.changes || [],
                    explanation: metadata.schema_diff.explanation || '',
                } : undefined,
                ragSources: metadata?.rag_sources,
                timestamp: new Date(),
            };

            setMessages(prev => [...prev, assistantMessage]);
            setStreamingText('');
            // AUTO-REFRESH REMOVED - user will now click 'Primeni'
        } catch (err: any) {
            if (err.name === 'AbortError') return;
            setError(err.message || 'Stream greška.');
            setStreamingText('');
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `⚠️ Greška: ${err.message || 'Nepoznata greška'}`,
                timestamp: new Date(),
            }]);
        } finally {
            setLoading(false);
            abortRef.current = null;
        }
    }, [messages, currentSchema, previewState, onSchemaUpdate]);

    // ─── Unified send ───────────────────────────────────────────────────

    const sendMessage = useCallback((text: string) => {
        if (!text.trim() || loading) return;
        if (useStreaming) {
            sendMessageStreaming(text);
        } else {
            sendMessageStandard(text);
        }
    }, [loading, useStreaming, sendMessageStandard, sendMessageStreaming]);

    // ─── Stop streaming ─────────────────────────────────────────────────

    const stopStreaming = useCallback(() => {
        if (abortRef.current) {
            abortRef.current.abort();
            setLoading(false);
            if (streamingText || loading) {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: (streamingText || 'Analiza...') + ' [prekinuto]',
                    timestamp: new Date(),
                }]);
                setStreamingText('');
            }
        }
    }, [streamingText, loading, setMessages]);

    // ─── New Chat ───────────────────────────────────────────────────────

    const handleClearChat = useCallback(() => {
        if (window.confirm('Da li ste sigurni da želite da obrišete istoriju chata?')) {
            setMessages([]);
            setStreamingText('');
            setError(null);
            schemaBeforeChatRef.current = currentSchema ? JSON.parse(JSON.stringify(currentSchema)) : null;
        }
    }, [setMessages, currentSchema]);

    // ─── Generate enriched prompt ───────────────────────────────────────

    const handleSummarize = useCallback(async () => {
        if (messages.length === 0) return;
        setLoading(true);
        try {
            const history = messages.map(m => ({ role: m.role, content: m.content }));
            const result = await api.post('/forms/chat/summarize', {
                current_schema: currentSchema,
                chat_history: history,
                preview_state: previewState,
            });
            onEnrichedGenerate(result.enriched_prompt);
        } catch (err: any) {
            setError(err.message || 'Summarize greška.');
        } finally {
            setLoading(false);
        }
    }, [messages, currentSchema, previewState, onEnrichedGenerate]);

    // ─── Key handler ────────────────────────────────────────────────────

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage(input);
        }
    };

    // ─── Overall diff from session start ────────────────────────────────

    const sessionDiff = useMemo(() => {
        if (!schemaBeforeChatRef.current) return [];
        return computeSchemaDiff(schemaBeforeChatRef.current, currentSchema);
    }, [currentSchema]);

    // ─── Render ─────────────────────────────────────────────────────────

    return (
        <div className="flex flex-col h-full border border-border rounded-xl overflow-hidden bg-card/30">
            {/* Header */}
            <div className="px-4 py-3 border-b border-border bg-muted/20 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-primary/10">
                        <MessageSquare className="w-4 h-4 text-primary" />
                    </div>
                    <div>
                        <h3 className="text-sm font-semibold text-foreground">Form AI Chat</h3>
                        <p className="text-[10px] text-muted-foreground">Kontekstualan za JSON šemu</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    {/* New Chat Button */}
                    <button
                        onClick={handleClearChat}
                        className="p-1.5 rounded-lg hover:bg-muted text-muted-foreground transition-colors"
                        title="Započni novi chat"
                    >
                        <Plus className="w-3.5 h-3.5" />
                    </button>

                    {/* Streaming toggle */}
                    <button
                        onClick={() => setUseStreaming(!useStreaming)}
                        className={clsx(
                            "text-[10px] px-2 py-0.5 rounded-full border transition-all",
                            useStreaming
                                ? "bg-green-500/10 text-green-400 border-green-500/20"
                                : "bg-muted/50 text-muted-foreground border-border"
                        )}
                        title={useStreaming ? "SSE streaming uključen" : "Standard mode"}
                    >
                        {useStreaming ? '⚡ Stream' : '📦 Batch'}
                    </button>
                    {messages.length > 0 && (
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium">
                            {messages.length} msg
                        </span>
                    )}
                </div>
            </div>

            {/* Session Diff Banner */}
            {sessionDiff.length > 0 && (
                <div className="px-3 py-2 bg-amber-500/5 border-b border-amber-500/10 flex items-center gap-2">
                    <GitCompare className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                    <span className="text-[10px] text-amber-400 font-medium">
                        {sessionDiff.length} promena od početka sesije
                    </span>
                    <div className="flex gap-1 ml-auto flex-wrap justify-end">
                        {sessionDiff.slice(0, 4).map((d, i) => (
                            <span key={i} className="text-[9px] px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400/80 font-mono">
                                {d.field}
                            </span>
                        ))}
                        {sessionDiff.length > 4 && (
                            <span className="text-[9px] text-amber-400/60">+{sessionDiff.length - 4}</span>
                        )}
                    </div>
                </div>
            )}

            {/* Messages */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
                {messages.length === 0 && !streamingText ? (
                    <div className="flex flex-col items-center justify-center h-full text-center space-y-4 py-8">
                        <div className="p-4 rounded-2xl bg-gradient-to-br from-primary/10 to-purple-500/10 border border-primary/10">
                            <Wand2 className="w-8 h-8 text-primary/60" />
                        </div>
                        <div>
                            <h4 className="text-sm font-semibold text-foreground mb-1">AI Asistent za Formu</h4>
                            <p className="text-xs text-muted-foreground max-w-[200px]">
                                Pitaj me o JSON šemi, layout-u, validacijama ili DynUI komponentama.
                            </p>
                        </div>

                        {/* Quick Actions */}
                        <div className="space-y-1.5 w-full">
                            {quickActions.map((action, i) => (
                                <button
                                    key={i}
                                    onClick={() => sendMessage(action.prompt)}
                                    className="w-full flex items-center gap-2 px-3 py-2 text-xs text-muted-foreground hover:text-foreground hover:bg-muted/50 rounded-lg transition-all text-left group"
                                >
                                    <action.icon className="w-3.5 h-3.5 text-primary/60 group-hover:text-primary transition-colors shrink-0" />
                                    <span>{action.label}</span>
                                    <ArrowRight className="w-3 h-3 ml-auto opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    <>
                        {messages.map((msg, i) => (
                            <div key={i} className={clsx("flex gap-2.5", msg.role === 'user' ? "justify-end" : "justify-start")}>
                                {msg.role === 'assistant' && (
                                    <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center shrink-0 mt-0.5">
                                        <Bot className="w-3.5 h-3.5 text-primary" />
                                    </div>
                                )}
                                <div className={clsx(
                                    "max-w-[85%] rounded-xl px-3.5 py-2.5 text-sm leading-relaxed",
                                    msg.role === 'user'
                                        ? "bg-primary text-primary-foreground rounded-br-sm"
                                        : "bg-muted/50 border border-border/50 text-foreground rounded-bl-sm"
                                )}>
                                    <div className="whitespace-pre-wrap">{msg.content}</div>

                                    {/* Schema Diff Badge & Actions */}
                                    {msg.schemaDiff && msg.schemaDiff.changes?.length > 0 && (
                                        <div className="mt-2.5 pt-2 border-t border-border/30">
                                            <div className="flex items-center justify-between mb-1.5">
                                                <div className="flex items-center gap-1.5">
                                                    <CheckCircle2 className="w-3 h-3 text-green-400" />
                                                    <span className="text-[10px] font-semibold text-green-400">
                                                        {msg.schemaDiff.changes.length} promena predložena
                                                    </span>
                                                </div>

                                                <div className="flex gap-2">
                                                    {!appliedMessages.has(i) ? (
                                                        <button
                                                            onClick={() => {
                                                                if (msg.updatedSchema) {
                                                                    setLastAppliedSchema(currentSchema);
                                                                    onSchemaUpdate(msg.updatedSchema);
                                                                    setAppliedMessages(prev => new Set(prev).add(i));
                                                                    const diff = computeSchemaDiff(currentSchema, msg.updatedSchema);
                                                                    setChangedFieldIds(new Set(diff.map(d => d.field)));
                                                                    setTimeout(() => setChangedFieldIds(new Set()), 5000);
                                                                }
                                                            }}
                                                            className="flex items-center gap-1 px-2 py-0.5 rounded bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-all text-[10px] font-bold border border-green-500/30 shadow-sm shadow-green-500/10"
                                                        >
                                                            <Zap className="w-2.5 h-2.5" />
                                                            Primeni izmene
                                                        </button>
                                                    ) : (
                                                        <button
                                                            onClick={() => {
                                                                if (lastAppliedSchema) {
                                                                    onSchemaUpdate(lastAppliedSchema);
                                                                    setAppliedMessages(prev => {
                                                                        const next = new Set(prev);
                                                                        next.delete(i);
                                                                        return next;
                                                                    });
                                                                }
                                                            }}
                                                            className="flex items-center gap-1 px-2 py-0.5 rounded bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-all text-[10px] font-bold border border-red-500/20"
                                                        >
                                                            <Trash2 className="w-2.5 h-2.5" />
                                                            Vrati na staro
                                                        </button>
                                                    )}
                                                </div>
                                            </div>
                                            <div className="space-y-1 bg-black/10 rounded-lg p-2">
                                                {msg.schemaDiff.changes.map((change: SchemaChange, ci: number) => (
                                                    <div key={ci} className="flex items-center gap-1.5 text-[10px] font-mono">
                                                        <span className="text-blue-400 font-semibold">{change.field}</span>
                                                        <span className="text-muted-foreground/60">{change.property}</span>
                                                        {change.from && (
                                                            <span className="px-1 rounded bg-red-500/10 text-red-400 line-through">
                                                                {change.from}
                                                            </span>
                                                        )}
                                                        <ArrowRight className="w-2.5 h-2.5 text-muted-foreground/40" />
                                                        <span className="px-1 rounded bg-green-500/10 text-green-400 font-medium">
                                                            {change.to}
                                                        </span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* RAG Sources */}
                                    {msg.ragSources && msg.ragSources.length > 0 && (
                                        <div className="mt-2 pt-2 border-t border-border/30 flex flex-wrap gap-1">
                                            <BookOpen className="w-3 h-3 text-muted-foreground/50" />
                                            {msg.ragSources.slice(0, 3).map((src, si) => (
                                                <span key={si} className="text-[9px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground/70 truncate max-w-[120px]" title={src}>
                                                    {src.split('/').pop()}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                                {msg.role === 'user' && (
                                    <div className="w-6 h-6 rounded-full bg-muted flex items-center justify-center shrink-0 mt-0.5">
                                        <User className="w-3.5 h-3.5 text-muted-foreground" />
                                    </div>
                                )}
                            </div>
                        ))}

                        {/* Streaming indicator */}
                        {streamingText && (
                            <div className="flex gap-2.5">
                                <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                                    <Bot className="w-3.5 h-3.5 text-primary" />
                                </div>
                                <div className="max-w-[85%] bg-muted/50 border border-border/50 rounded-xl rounded-bl-sm px-3.5 py-2.5">
                                    <div className="text-sm leading-relaxed whitespace-pre-wrap text-foreground">
                                        {streamingText}
                                        <span className="inline-block w-1.5 h-4 bg-primary/60 ml-0.5 animate-pulse rounded-sm" />
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Loading (non-streaming) */}
                        {loading && !streamingText && (
                            <div className="flex gap-2.5">
                                <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                                    <Bot className="w-3.5 h-3.5 text-primary" />
                                </div>
                                <div className="bg-muted/50 border border-border/50 rounded-xl rounded-bl-sm px-3.5 py-2.5">
                                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                                        <span>Analiziram šemu...</span>
                                    </div>
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>

            {/* Changed Fields Highlight Bar */}
            {changedFieldIds.size > 0 && (
                <div className="mx-3 mb-2 flex items-center gap-2 p-2 rounded-lg bg-green-500/10 text-green-400 text-[10px] border border-green-500/20 animate-pulse">
                    <CheckCircle2 className="w-3 h-3 shrink-0" />
                    <span className="font-medium">Ažurirano:</span>
                    <div className="flex gap-1 flex-wrap">
                        {Array.from(changedFieldIds).slice(0, 5).map(id => (
                            <span key={id} className="px-1.5 py-0.5 rounded bg-green-500/20 font-mono text-[9px]">{id}</span>
                        ))}
                    </div>
                </div>
            )}

            {/* Error */}
            {error && (
                <div className="mx-4 mb-2 flex items-center gap-2 p-2 rounded-lg bg-red-500/10 text-red-400 text-xs">
                    <XCircle className="w-3.5 h-3.5 shrink-0" />
                    <span className="truncate">{error}</span>
                    <button onClick={() => setError(null)} className="ml-auto text-[10px] hover:text-red-300 shrink-0">✕</button>
                </div>
            )}

            {/* Input */}
            <div className="p-3 border-t border-border bg-card/50">
                {/* Summarize button */}
                {messages.length >= 2 && (
                    <button
                        onClick={handleSummarize}
                        disabled={loading}
                        className="w-full mb-2 flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs rounded-lg bg-green-600/10 text-green-400 hover:bg-green-600/20 border border-green-500/20 transition-all disabled:opacity-50 font-medium"
                    >
                        <Sparkles className="w-3.5 h-3.5" />
                        Generiši obogaćeni prompt za orkestrator
                    </button>
                )}

                <div className="flex items-end gap-2">
                    <textarea
                        ref={inputRef}
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Pitaj o formi, layout-u, validacijama..."
                        className="flex-1 bg-background border border-border rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:ring-1 focus:ring-primary/30 min-h-[38px] max-h-[100px] placeholder:text-muted-foreground/50"
                        rows={1}
                        disabled={loading}
                    />
                    {loading ? (
                        <button
                            onClick={stopStreaming}
                            className="p-2 rounded-lg bg-red-500/80 text-white hover:bg-red-500 transition-all shrink-0 animate-pulse shadow-lg shadow-red-500/20"
                            title="Zaustavi generisanje"
                        >
                            <StopCircle className="w-4 h-4" />
                        </button>
                    ) : (
                        <button
                            onClick={() => sendMessage(input)}
                            disabled={!input.trim()}
                            className="p-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-all disabled:opacity-30 disabled:cursor-not-allowed shrink-0"
                        >
                            <Send className="w-4 h-4" />
                        </button>
                    )}
                </div>
                <div className="mt-1.5 text-[10px] text-muted-foreground/50 text-center">
                    Enter za slanje · Shift+Enter novi red · {useStreaming ? '⚡ Streaming' : '📦 Batch'} mod
                </div>
            </div>
        </div>
    );
}
