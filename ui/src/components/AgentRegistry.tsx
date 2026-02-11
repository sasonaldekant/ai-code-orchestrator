import { useState, useEffect } from 'react';
import { Bot, Wrench, Shield, Search, Database, Code2, Cpu, Activity } from 'lucide-react';
import clsx from 'clsx';

interface Agent {
    id: string;
    name: string;
    description: string;
    role: string;
    tools: string[];
    type: 'phase' | 'specialist';
    status: string;
}

export function AgentRegistry() {
    const [agents, setAgents] = useState<Agent[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        setIsLoading(true);
        fetch('http://localhost:8000/agents/')
            .then(res => res.json())
            .then(data => {
                if (data.agents) {
                    setAgents(data.agents);
                }
            })
            .catch(err => console.error("Failed to load agents", err))
            .finally(() => setIsLoading(false));
    }, []);

    const getIcon = (role: string) => {
        switch (role.toLowerCase()) {
            case 'analyst': return <Search className="w-6 h-6 text-blue-400" />;
            case 'architect': return <Database className="w-6 h-6 text-purple-400" />;
            case 'implementation': return <Code2 className="w-6 h-6 text-amber-400" />;
            case 'testing': return <Shield className="w-6 h-6 text-green-400" />;
            case 'researcher': return <Bot className="w-6 h-6 text-cyan-400" />;
            default: return <Cpu className="w-6 h-6 text-muted-foreground" />;
        }
    };

    if (isLoading) {
        return <div className="flex items-center justify-center h-full text-muted-foreground animate-pulse">Scanning Agent Network...</div>;
    }

    return (
        <div className="p-6 h-full overflow-y-auto">
            <div className="mb-8">
                <h2 className="text-2xl font-bold flex items-center gap-3 mb-2">
                    <Bot className="w-8 h-8 text-primary" />
                    Agent Registry
                </h2>
                <p className="text-muted-foreground max-w-2xl">
                    Overview of active autonomous agents and their capabilities.
                    These agents collaborate to execute the orchestration pipeline.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {agents.map((agent) => (
                    <div
                        key={agent.id}
                        className="bg-card border border-border rounded-xl p-5 hover:border-primary/50 transition-all hover:shadow-lg group relative overflow-hidden"
                    >
                        {/* Background Effect */}
                        <div className="absolute top-0 right-0 p-2 opacity-5 group-hover:opacity-10 transition-opacity">
                            {getIcon(agent.role)}
                        </div>

                        {/* Header */}
                        <div className="flex items-start justify-between mb-4">
                            <div className="p-3 bg-muted/20 rounded-lg group-hover:bg-primary/10 transition-colors">
                                {getIcon(agent.role)}
                            </div>
                            <div className={clsx(
                                "text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border",
                                agent.status === 'active' ? "bg-green-500/10 text-green-500 border-green-500/20" : "bg-blue-500/10 text-blue-500 border-blue-500/20"
                            )}>
                                {agent.status}
                            </div>
                        </div>

                        {/* Info */}
                        <h3 className="text-lg font-semibold mb-1">{agent.name}</h3>
                        <p className="text-sm text-muted-foreground mb-4 min-h-[40px]">
                            {agent.description}
                        </p>

                        {/* Tools */}
                        <div>
                            <div className="text-xs font-semibold text-muted-foreground mb-2 flex items-center gap-1">
                                <Wrench className="w-3 h-3" />
                                CAPABILITIES
                            </div>
                            <div className="flex flex-wrap gap-1.5">
                                {agent.tools.length > 0 ? (
                                    agent.tools.map((tool, idx) => (
                                        <span
                                            key={idx}
                                            className="px-2 py-1 text-[10px] bg-muted rounded border border-border text-foreground/80 font-mono"
                                        >
                                            {tool}
                                        </span>
                                    ))
                                ) : (
                                    <span className="text-xs text-muted-foreground italic">No specific tools declared</span>
                                )}
                            </div>
                        </div>

                        {/* Activity Indicator (Fake for now) */}
                        {agent.status === 'active' && (
                            <div className="mt-4 pt-4 border-t border-border flex items-center gap-2 text-xs text-muted-foreground">
                                <Activity className="w-3 h-3 text-green-500 animate-pulse" />
                                <span>Standing by</span>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
