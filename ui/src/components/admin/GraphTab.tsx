
import React, { useState, useEffect, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { RefreshCw, Filter } from 'lucide-react';

interface GraphNode {
    id: string;
    type: string;
    name: string;
    file_path: string;
    val: number; // For visualization size
    color: string;
}

interface GraphEdge {
    source: string;
    target: string;
    type: string;
}

interface GraphData {
    nodes: GraphNode[];
    links: GraphEdge[];
}

const GraphTab: React.FC = () => {
    const [data, setData] = useState<GraphData>({ nodes: [], links: [] });
    const [loading, setLoading] = useState(false);
    const [stats, setStats] = useState<{ nodes: number; edges: number } | null>(null);
    const graphRef = useRef<any>(null);

    const fetchGraph = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/admin/graph');
            if (!res.ok) throw new Error('Failed to fetch graph');
            const json = await res.json();

            // Transform data for react-force-graph
            // Backend returns: { nodes: [...], edges: [...] }
            // react-force-graph expects: { nodes: [...], links: [...] }

            const nodes = json.nodes.map((n: any) => ({
                id: n.id,
                name: n.name,
                type: n.type,
                file_path: n.file_path,
                // Visual props
                val: n.type === 'file' ? 10 : n.type === 'class' ? 7 : 4,
                color: n.type === 'file' ? '#3b82f6' : // blue
                    n.type === 'class' ? '#eab308' : // yellow
                        n.type === 'function' ? '#10b981' : // green
                            '#64748b' // gray (module/other)
            }));

            const links = json.edges.map((e: any) => ({
                source: e.source,
                target: e.target,
                type: e.type,
                color: '#cbd5e1'
            }));

            setData({ nodes, links });
            setStats({ nodes: nodes.length, edges: links.length });
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const buildGraph = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/admin/graph/build', { method: 'POST' });
            if (!res.ok) throw new Error('Failed to build graph');
            await fetchGraph(); // Refresh after build
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchGraph();
    }, []);

    return (
        <div className="h-full flex flex-col bg-gray-900 text-white rounded-lg overflow-hidden border border-gray-700">
            {/* Toolbar */}
            <div className="p-4 border-b border-gray-700 flex justify-between items-center bg-gray-800">
                <div className="flex items-center gap-4">
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        🕸️ Knowledge Graph
                        {stats && (
                            <span className="text-xs font-normal text-gray-400 bg-gray-700 px-2 py-0.5 rounded-full">
                                {stats.nodes} Nodes • {stats.edges} Edges
                            </span>
                        )}
                    </h2>
                </div>

                <div className="flex gap-2">
                    <button
                        onClick={buildGraph}
                        disabled={loading}
                        className="p-2 bg-blue-600 hover:bg-blue-700 rounded-md text-sm font-medium flex items-center gap-2 transition-colors disabled:opacity-50"
                    >
                        <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                        {loading ? 'Rebuilding...' : 'Rebuild Graph'}
                    </button>
                </div>
            </div>

            {/* Graph Area */}
            <div className="flex-1 relative bg-black/50">
                {/* Legend Overlay */}
                <div className="absolute top-4 left-4 z-10 bg-gray-800/80 p-3 rounded-md backdrop-blur-sm border border-gray-700 text-xs">
                    <div className="flex items-center gap-2 mb-1"><div className="w-3 h-3 rounded-full bg-blue-500"></div> File</div>
                    <div className="flex items-center gap-2 mb-1"><div className="w-3 h-3 rounded-full bg-yellow-500"></div> Class</div>
                    <div className="flex items-center gap-2 mb-1"><div className="w-3 h-3 rounded-full bg-green-500"></div> Function</div>
                    <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-gray-500"></div> Module</div>
                </div>

                {data.nodes.length > 0 ? (
                    <ForceGraph2D
                        ref={graphRef}
                        graphData={data}
                        nodeLabel="id"
                        nodeColor="color"
                        nodeRelSize={6}
                        linkColor={() => '#475569'}
                        linkDirectionalArrowLength={3.5}
                        linkDirectionalArrowRelPos={1}
                        backgroundColor="#0f172a"
                        onNodeClick={(node: any) => {
                            // Zoom to node interactively
                            graphRef.current?.centerAt(node.x, node.y, 1000);
                            graphRef.current?.zoom(8, 2000);
                        }}
                    />
                ) : (
                    <div className="flex flex-col items-center justify-center h-full text-gray-400">
                        <Filter className="w-12 h-12 mb-4 opacity-20" />
                        <p>No graph data available.</p>
                        <p className="text-sm mt-2">Click "Rebuild Graph" to analyze the codebase.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default GraphTab;
