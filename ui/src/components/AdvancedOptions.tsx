import { useState } from 'react';
import { DollarSign, Users, ShieldCheck, ChevronDown, ChevronUp } from 'lucide-react';
import clsx from 'clsx';

interface AdvancedOptionsProps {
    consensus: boolean;
    setConsensus: (val: boolean) => void;
    reviewStrategy: 'basic' | 'strict';
    setReviewStrategy: (val: 'basic' | 'strict') => void;
    showReviewStrategy?: boolean;
    showConsensusMode?: boolean;
}

export function AdvancedOptions({
    consensus, setConsensus,
    reviewStrategy, setReviewStrategy,
    showReviewStrategy = true,
    showConsensusMode = true
}: AdvancedOptionsProps) {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div className="w-full mt-2 border-t border-border/50 pt-2">
            <button
                type="button"
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors mb-2"
            >
                {isOpen ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                Advanced Options
            </button>

            {isOpen && (showReviewStrategy || showConsensusMode) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-3 bg-muted/20 rounded-lg border border-border/50 animate-in fade-in slide-in-from-top-2">

                    {/* Review Strategy */}
                    {showReviewStrategy && (
                        <div className="space-y-1.5">
                            <label className="text-[10px] uppercase font-bold text-muted-foreground flex items-center gap-1">
                                <ShieldCheck className="w-3 h-3" />
                                Review Strategy
                            </label>
                            <div className="flex bg-muted/50 rounded p-0.5">
                                <button
                                    type="button"
                                    onClick={() => setReviewStrategy('basic')}
                                    className={clsx(
                                        "flex-1 py-1 text-[10px] rounded transition-all",
                                        reviewStrategy === 'basic' ? "bg-background shadow text-foreground" : "text-muted-foreground hover:text-foreground"
                                    )}
                                >
                                    Basic
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setReviewStrategy('strict')}
                                    className={clsx(
                                        "flex-1 py-1 text-[10px] rounded transition-all",
                                        reviewStrategy === 'strict' ? "bg-background shadow text-primary font-medium" : "text-muted-foreground hover:text-foreground"
                                    )}
                                >
                                    Strict
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Consensus Mode */}
                    {showConsensusMode && (
                        <div className="space-y-1.5">
                            <label className="text-[10px] uppercase font-bold text-muted-foreground flex items-center gap-1">
                                <Users className="w-3 h-3" />
                                Consensus Mode
                            </label>
                            <button
                                type="button"
                                onClick={() => setConsensus(!consensus)}
                                className={clsx(
                                    "w-full py-1.5 px-2 rounded border text-xs flex items-center justify-between transition-all",
                                    consensus
                                        ? "bg-purple-500/10 border-purple-500/50 text-purple-400"
                                        : "bg-background border-border text-muted-foreground hover:text-foreground"
                                )}
                            >
                                <span>{consensus ? "Enabled" : "Disabled"}</span>
                                <div className={clsx(
                                    "w-2 h-2 rounded-full",
                                    consensus ? "bg-purple-500 shadow-[0_0_5px_rgba(168,85,247,0.5)]" : "bg-muted-foreground/30"
                                )} />
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
