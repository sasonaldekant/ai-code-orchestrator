import { useState } from 'react';
import { ChevronDown, ChevronUp, Brain, FileCode, CheckCircle, AlertCircle } from 'lucide-react';
import clsx from 'clsx';
import { motion, AnimatePresence } from 'framer-motion';

interface ThinkingBlockProps {
    logs: any[];
    title?: string;
}

export function ThinkingBlock({ logs, title = "Thinking Process" }: ThinkingBlockProps) {
    const [isOpen, setIsOpen] = useState(false);

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
                        <div className="p-4 space-y-3 font-mono text-xs max-h-[400px] overflow-y-auto custom-scrollbar">
                            {logs.map((log, idx) => (
                                <div key={idx} className="flex gap-3 animate-in fade-in slide-in-from-left-1 duration-300">
                                    <div className="mt-0.5 min-w-[16px]">
                                        {log.type === 'error' ? (
                                            <AlertCircle className="w-3 h-3 text-destructive" />
                                        ) : log.type === 'artifact' ? (
                                            <FileCode className="w-3 h-3 text-accent-foreground" />
                                        ) : (
                                            <CheckCircle className="w-3 h-3 text-muted-foreground/50" />
                                        )}
                                    </div>
                                    <div className={clsx(
                                        "flex-1 break-words",
                                        log.type === 'error' ? 'text-destructive' : 'text-muted-foreground'
                                    )}>
                                        <span className="font-semibold text-foreground/80 mr-2">[{log.agent}]:</span>
                                        {typeof log.content === 'string' ? log.content : JSON.stringify(log.content)}
                                    </div>
                                    <div className="text-[10px] text-muted-foreground/30 whitespace-nowrap">
                                        {new Date(log.timestamp).toLocaleTimeString()}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
