
import React, { useState, useEffect, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { RefreshCw, Play, Clock } from 'lucide-react';

interface SwarmNode {
    id: string;
    label: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    agent?: string;
    color?: string;
}

interface SwarmLink {
    source: string;
    target: string;
}

interface SwarmData {
    nodes: SwarmNode[];
    links: SwarmLink[];
}

const SwarmVis: React.FC = () => {
    const [data, setData] = useState<SwarmData>({ nodes: [], links: [] });
    const [loading, setLoading] = useState(false);
    const [autoRefresh, setAutoRefresh] = useState(true);
    const graphRef = useRef<any>(null);

    const fetchSwarmData = async () => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/admin/swarm/dag');
            if (!res.ok) throw new Error('Failed to fetch swarm DAG');
            const json = await res.json();

            // Map colors based on status
            const statusColors = {
                pending: '#64748b',   // slate-500
                running: '#3b82f6',   // blue-500
                completed: '#10b981', // emerald-500
                failed: '#ef4444'     // red-500
            };

            const nodes = json.nodes.map((n: any) => ({
                ...n,
                color: statusColors[n.status as keyof typeof statusColors] || '#64748b'
            }));

            setData({ nodes, links: json.links });
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSwarmData();
        let interval: any;
        if (autoRefresh) {
            interval = setInterval(fetchSwarmData, 3000); // 3s polling
        }
        return () => clearInterval(interval);
    }, [autoRefresh]);

    return (
        <div className="flex flex-col h-full bg-slate-900 rounded-xl border border-slate-800 shadow-2xl overflow-hidden">
            {/* Header */}
            <div className="p-4 bg-slate-800/50 border-b border-slate-700 flex justify-between items-center">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-500/10 rounded-lg">
                        <Play className="w-5 h-5 text-blue-400" />
                    </div>
                    <div>
                        <h3 className="text-white font-semibold">Swarm Monitor</h3>
                        <p className="text-xs text-slate-400">Real-time Multi-Agent Coordination</p>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <input
                            type="checkbox"
                            id="auto-refresh"
                            checked={autoRefresh}
                            onChange={(e) => setAutoRefresh(e.target.checked)}
                            className="w-4 h-4 rounded border-slate-700 bg-slate-800 text-blue-500 focus:ring-blue-500/20"
                        />
                        <label htmlFor="auto-refresh" className="text-xs text-slate-300 cursor-pointer">Live Updates</label>
                    </div>
                    <button
                        onClick={fetchSwarmData}
                        disabled={loading}
                        className="p-2 hover:bg-slate-700 rounded-lg transition-colors disabled:opacity-50"
                    >
                        <RefreshCw className={`w-4 h-4 text-slate-400 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </div>

            {/* Legend & Stats */}
            <div className="px-4 py-2 bg-slate-800/30 border-b border-slate-700 flex gap-6 text-[10px] uppercase tracking-wider font-bold">
                <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-slate-500"></div> <span className="text-slate-400">Pending</span></div>
                <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div> <span className="text-blue-400">Running</span></div>
                <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-emerald-500"></div> <span className="text-emerald-400">Completed</span></div>
                <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-red-500"></div> <span className="text-red-400">Failed</span></div>
            </div>

            {/* Graph Container */}
            <div className="flex-1 min-h-[400px] relative bg-[#0a0f18] overflow-hidden">
                {data.nodes.length > 0 ? (
                    <ForceGraph2D
                        ref={graphRef}
                        graphData={data}
                        nodeLabel={(node: any) => `${node.id}: ${node.label} (${node.agent})`}
                        nodeColor="color"
                        nodeRelSize={8}
                        linkColor={() => '#334155'}
                        linkDirectionalArrowLength={4}
                        linkDirectionalArrowRelPos={1}
                        linkDirectionalParticles={2}
                        linkDirectionalParticleSpeed={() => 0.005}
                        backgroundColor="transparent"
                        cooldownTicks={100}
                        onNodeClick={(node: any) => {
                            graphRef.current?.centerAt(node.x, node.y, 800);
                            graphRef.current?.zoom(4, 1000);
                        }}
                    />
                ) : (
                    <div className="flex flex-col items-center justify-center h-full text-slate-500 space-y-4">
                        <div className="w-16 h-16 bg-slate-800/50 rounded-full flex items-center justify-center">
                            <Clock className="w-8 h-8 opacity-20" />
                        </div>
                        <p className="text-sm font-medium italic">No active swarm session detected...</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SwarmVis;
