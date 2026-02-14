import { useState } from 'react';
import { Settings, Database, Bot, DollarSign, BookOpen, ChevronLeft, Wrench, Activity, Share2, Lock, Sliders } from 'lucide-react';
import clsx from 'clsx';
import { IngestionPanel } from './IngestionPanel';
import { ModelConfigPanel } from './ModelConfigPanel';
import { BudgetPanel } from './BudgetPanel';
import { KnowledgeExplorer } from './KnowledgeExplorer';
import { MonitoringDashboard } from './MonitoringDashboard';
import { DeveloperToolsPanel } from './DeveloperToolsPanel';
import { ApiKeysPanel } from './ApiKeysPanel';
import { GlobalSettingsPanel } from './GlobalSettingsPanel';
import GraphTab from './GraphTab';

type AdminTab = 'ingestion' | 'models' | 'budgets' | 'knowledge' | 'tools' | 'monitoring' | 'graph' | 'keys' | 'global';

interface AdminLayoutProps {
    onBack: () => void;
}

export function AdminLayout({ onBack }: AdminLayoutProps) {
    const [activeTab, setActiveTab] = useState<AdminTab>('ingestion');

    const tabs = [
        { id: 'global' as const, label: 'Global Settings', icon: Sliders },
        { id: 'ingestion' as const, label: 'RAG Ingestion', icon: Database },
        { id: 'models' as const, label: 'Model Config', icon: Bot },
        { id: 'budgets' as const, label: 'Budgets & Limits', icon: DollarSign },
        { id: 'knowledge' as const, label: 'Knowledge Base', icon: BookOpen },
        { id: 'tools' as const, label: 'Developer Tools', icon: Wrench },
        { id: 'monitoring' as const, label: 'System Monitoring', icon: Activity },
        { id: 'graph' as const, label: 'Knowledge Graph', icon: Share2 },
        { id: 'keys' as const, label: 'API Credentials', icon: Lock },
    ];

    return (
        <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans">
            {/* Admin Sidebar */}
            <aside className="w-64 border-r border-border bg-card/30 flex flex-col">
                <div className="p-4 border-b border-border flex items-center gap-2">
                    <button
                        onClick={onBack}
                        className="p-1.5 hover:bg-muted rounded-lg transition-colors"
                    >
                        <ChevronLeft className="w-5 h-5" />
                    </button>
                    <Settings className="w-5 h-5 text-primary" />
                    <h1 className="font-semibold text-lg tracking-tight">Admin Panel</h1>
                </div>

                <nav className="flex-1 p-3 space-y-1">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={clsx(
                                "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all",
                                activeTab === tab.id
                                    ? "bg-primary/10 text-primary border border-primary/20"
                                    : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                            )}
                        >
                            <tab.icon className="w-4 h-4" />
                            {tab.label}
                        </button>
                    ))}
                </nav>

                <div className="p-4 border-t border-border text-xs text-muted-foreground">
                    <p>Orchestrator v3.0</p>
                    <p className="mt-1">Changes auto-save</p>
                </div>
            </aside>

            {/* Content Area */}
            <main className="flex-1 overflow-y-auto p-6 md:p-8">
                <div className="max-w-4xl mx-auto">
                    {activeTab === 'global' && <GlobalSettingsPanel />}
                    {activeTab === 'ingestion' && <IngestionPanel />}
                    {activeTab === 'models' && <ModelConfigPanel />}
                    {activeTab === 'budgets' && <BudgetPanel />}
                    {activeTab === 'knowledge' && <KnowledgeExplorer />}
                    {activeTab === 'tools' && <DeveloperToolsPanel />}
                    {activeTab === 'monitoring' && <MonitoringDashboard />}
                    {activeTab === 'graph' && <GraphTab />}
                    {activeTab === 'keys' && <ApiKeysPanel />}
                </div>
            </main>
        </div>
    );
}
