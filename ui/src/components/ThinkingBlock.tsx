import { useState } from 'react';
import { ChevronDown, ChevronUp, Brain, FileCode, CheckCircle, AlertCircle, Sparkles } from 'lucide-react';
import clsx from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';

interface ThinkingBlockProps {
    logs: any[];
    title?: string;
}

export function ThinkingBlock({ logs, title = "Thinking Process" }: ThinkingBlockProps) {
    const [isOpen, setIsOpen] = useState(true);

    // Group logs by agent/phase if needed, or just show raw sequence for now

    return (
        <div className="border border-border rounded-lg bg-card/50 overflow-hidden my-4 shadow-sm">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-full px-4 py-3 flex items-center justify-between hover:bg-muted/50 transition-colors"
            >
                <div className="flex items-center gap-3">
                    <div className="p-1.5 bg-primary/10 rounded-md">
                        <Brain className="w-4 h-4 text-primary" />
                    </div>
                    <span className="font-medium text-sm text-foreground/90">{title}</span>
                    <span className="text-xs text-muted-foreground ml-2">
                        {logs.length} steps
                    </span>
                </div>

                {isOpen ? (
                    <ChevronUp className="w-4 h-4 text-muted-foreground" />
                ) : (
                    <ChevronDown className="w-4 h-4 text-muted-foreground" />
                )}
            </button>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="border-t border-border bg-background/50"
                    >
                        <div className="p-4 space-y-3 font-mono text-xs max-h-[500px] overflow-y-auto custom-scrollbar">
                            {logs
                                .filter(log => log.type !== 'done' || (typeof log.content === 'string')) // Filter out big result blobs
                                .map((log, idx) => {
                                    const isInfo = log.type === 'info';
                                    const isError = log.type === 'error';
                                    const isThought = log.type === 'thought';
                                    const timestamp = log.timestamp ? new Date(log.timestamp) : new Date();
                                    const isValidTimestamp = !isNaN(timestamp.getTime());

                                    return (
                                        <div key={idx} className={clsx(
                                            "flex gap-3 p-2 rounded-md transition-colors",
                                            isInfo ? "bg-indigo-500/10 border border-indigo-500/20 shadow-sm" :
                                                isThought ? "bg-primary/5 hover:bg-primary/10" : "hover:bg-muted/30"
                                        )}>
                                            <div className="mt-0.5 min-w-[16px]">
                                                {isError ? (
                                                    <AlertCircle className="w-3 h-3 text-destructive" />
                                                ) : isInfo ? (
                                                    <Sparkles className="w-3 h-3 text-indigo-400" />
                                                ) : log.type === 'artifact' ? (
                                                    <FileCode className="w-3 h-3 text-accent-foreground" />
                                                ) : isThought ? (
                                                    <Brain className="w-3 h-3 text-primary/50" />
                                                ) : (
                                                    <CheckCircle className="w-3 h-3 text-muted-foreground/30" />
                                                )}
                                            </div>
                                            <div className={clsx(
                                                "flex-1 break-words",
                                                isError ? 'text-destructive' :
                                                    isInfo ? 'text-indigo-100 text-[13px] font-sans whitespace-pre-wrap' :
                                                        'text-muted-foreground/80'
                                            )}>
                                                <span className="font-semibold text-foreground/70 mr-2">[{log.agent || 'Agent'}]:</span>
                                                {typeof log.content === 'string'
                                                    ? log.content.replace(/###\s+/g, '')
                                                    : JSON.stringify(log.content, null, 2)}
                                            </div>
                                            <div className="text-[10px] text-muted-foreground/40 whitespace-nowrap self-start tabular-nums">
                                                {isValidTimestamp ? timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '--:--:--'}
                                            </div>
                                        </div>
                                    );
                                })}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
