import React from 'react';
import {
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    AreaChart, Area, PieChart, Pie, Cell
} from 'recharts';
import { Activity, TrendingUp, AlertCircle, DollarSign, Download, CheckCircle } from 'lucide-react';

const mockSuccessData = [
    { name: 'Mon', success: 85, error: 15 },
    { name: 'Tue', success: 88, error: 12 },
    { name: 'Wed', success: 92, error: 8 },
    { name: 'Thu', success: 90, error: 10 },
    { name: 'Fri', success: 95, error: 5 },
    { name: 'Sat', success: 98, error: 2 },
    { name: 'Sun', success: 96, error: 4 },
];

const mockCostData = [
    { name: 'GPT-4o', value: 45 },
    { name: 'Claude-3.5', value: 35 },
    { name: 'Gemini-2.5', value: 20 },
];

const COLORS = ['#0ea5e9', '#8b5cf6', '#ec4899'];

const COLORS_TIER = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'];

export function MonitoringDashboard() {
    const [metrics, setMetrics] = React.useState<any>(null);

    React.useEffect(() => {
        fetch('http://localhost:8000/admin/cascade-metrics')
            .then(res => res.json())
            .then(setMetrics)
            .catch(err => console.error("Failed to fetch cascade metrics", err));
    }, []);

    const tierData = metrics ? Object.entries(metrics.tier_usage).map(([key, value]) => ({
        name: `Tier ${key}`,
        value: Number(value)
    })) : [];

    // Simple ROI estimation (Mock logic for display if data is low)
    const totalRequests = metrics?.total_requests || 0;
    const tier0Requests = metrics?.tier_usage?.['0'] || 0;
    const tier1Requests = metrics?.tier_usage?.['1'] || 0;
    const savings = totalRequests > 0
        ? ((tier0Requests * 0.14 + tier1Requests * 0.13) / totalRequests * 100).toFixed(1)
        : "0.0";

    return (
        <div className="space-y-6">
            <header className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">System Monitoring</h2>
                    <p className="text-zinc-400">Real-time performance and cost analytics.</p>
                </div>
            </header>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    title="Cascade Savings (Est.)"
                    value={`$${(parseFloat(savings) * 1.5).toFixed(2)}`}
                    change={`${savings}% eff.`}
                    icon={<DollarSign className="w-5 h-5 text-emerald-400" />}
                />
                <StatCard
                    title="Total Requests"
                    value={metrics?.total_requests?.toString() || "0"}
                    change="Live"
                    icon={<Activity className="w-5 h-5 text-blue-400" />}
                />
                <StatCard
                    title="Avg. Latency"
                    value="1.2s"
                    change="-300ms"
                    icon={<TrendingUp className="w-5 h-5 text-purple-400" />}
                />
                <StatCard
                    title="Active Failures"
                    value="0"
                    change="Stable"
                    icon={<CheckCircle className="w-5 h-5 text-emerald-500" />}
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Tier Usage Chart */}
                <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
                    <h3 className="text-lg font-semibold mb-6 text-white">Model Tier Usage</h3>
                    <div className="h-[300px] flex flex-col items-center justify-center">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={tierData.length > 0 ? tierData : [{ name: 'No Data', value: 1 }]}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {tierData.map((_, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS_TIER[index % COLORS_TIER.length]} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#18181b', border: '1px solid #3f3f46', borderRadius: '8px' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                        <div className="mt-4 flex flex-wrap gap-2 justify-center">
                            {tierData.map((item, i) => (
                                <div key={item.name} className="flex items-center gap-2 text-xs">
                                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS_TIER[i] }} />
                                    <span className="text-zinc-400">{item.name}</span>
                                    <span className="font-mono text-zinc-300">{item.value}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Success Rate Chart (Existing Mock) */}
                <div className="lg:col-span-2 p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
                    <h3 className="text-lg font-semibold mb-6 text-white text-white">Success vs Error Rate (Last 7 Days)</h3>
                    <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={mockSuccessData}>
                                <defs>
                                    <linearGradient id="colorSuccess" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                                <XAxis dataKey="name" stroke="#777" />
                                <YAxis stroke="#777" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#18181b', border: '1px solid #3f3f46', borderRadius: '8px' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="success"
                                    stroke="#0ea5e9"
                                    fillOpacity={1}
                                    fill="url(#colorSuccess)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
}

function StatCard({ title, value, change, icon }: { title: string, value: string, change: string, icon: React.ReactNode }) {
    return (
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl hover:border-zinc-700 transition-colors">
            <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-zinc-400">{title}</span>
                {icon}
            </div>
            <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold text-white">{value}</span>
                <span className={`text-xs ${change.startsWith('+') ? 'text-emerald-400' : 'text-zinc-500'}`}>
                    {change}
                </span>
            </div>
        </div>
    );
}
