import * as React from 'react';
import { useState } from 'react';
import { OrchestratorUI } from './components/OrchestratorUI';
import { AdminLayout } from './components/admin/AdminLayout';
import { DynButton } from '@dyn-ui/react';

type View = 'orchestrator' | 'admin';

function App() {
    const [currentView, setCurrentView] = useState<View>('orchestrator');

    return (
        <React.StrictMode>
            <div className="h-screen w-screen bg-black/10 p-2 md:p-4 box-border">
                <div className="h-full w-full bg-background border border-border/50 rounded-xl overflow-hidden shadow-2xl flex flex-col">
                    {currentView === 'orchestrator' && (
                        <div className="h-full flex flex-col">
                            <div className="p-4 border-b flex items-center gap-4">
                                <h1 className="text-xl font-bold">Orchestrator</h1>
                                <DynButton kind="primary" size="sm" onClick={() => console.log('DynButton clicked')}>
                                    Test DynButton
                                </DynButton>
                            </div>
                            <OrchestratorUI onOpenSettings={() => setCurrentView('admin')} />
                        </div>
                    )}
                    {currentView === 'admin' && (
                        <AdminLayout onBack={() => setCurrentView('orchestrator')} />
                    )}
                </div>
            </div>
        </React.StrictMode>
    );
}

export default App;
