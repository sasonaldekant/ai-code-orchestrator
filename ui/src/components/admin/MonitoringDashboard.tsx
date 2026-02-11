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

export function MonitoringDashboard() {
    return (
        <div className="space-y-6">
            <header className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">System Monitoring</h2>
                    <p className="text-zinc-400">Real-time performance and cost analytics.</p>
                </div>
                <button
                    onClick={() => window.open('http://127.0.0.1:8000/admin/audit-report', '_blank')}
                    className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium text-sm"
                >
                    <Download className="w-4 h-4" />
                    Download Audit Report
                </button>
            </header>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    title="Average Success Rate"
                    value="93.4%"
                    change="+2.1%"
                    icon={<Activity className="w-5 h-5 text-blue-400" />}
                />
                <StatCard
                    title="Avg. Latency"
                    value="2.4s"
                    change="-150ms"
                    icon={<TrendingUp className="w-5 h-5 text-purple-400" />}
                />
                <StatCard
                    title="Active Failures"
                    value="2"
                    change="Stable"
                    icon={<AlertCircle className="w-5 h-5 text-rose-400" />}
                />
                <StatCard
                    title="Total Cost (MTD)"
                    value="$142.50"
                    change="Within Budget"
                    icon={<DollarSign className="w-5 h-5 text-emerald-400" />}
                />
                <StatCard
                    title="Code Quality Index"
                    value="A+"
                    change="98/100"
                    icon={<CheckCircle className="w-5 h-5 text-blue-500" />}
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Success Rate Chart */}
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
                                <Area
                                    type="monotone"
                                    dataKey="error"
                                    stroke="#ec4899"
                                    fillOpacity={0.1}
                                    fill="#ec4899"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Cost Distribution */}
                <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
                    <h3 className="text-lg font-semibold mb-6 text-white">Cost Distribution by Model</h3>
                    <div className="h-[300px] flex flex-col items-center justify-center">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={mockCostData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {mockCostData.map((_, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#18181b', border: '1px solid #3f3f46', borderRadius: '8px' }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                        <div className="mt-4 space-y-2 w-full">
                            {mockCostData.map((item, i) => (
                                <div key={item.name} className="flex items-center justify-between text-sm">
                                    <div className="flex items-center gap-2">
                                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[i] }} />
                                        <span className="text-zinc-400">{item.name}</span>
                                    </div>
                                    <span className="font-mono text-zinc-300">{item.value}%</span>
                                </div>
                            ))}
                        </div>
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
