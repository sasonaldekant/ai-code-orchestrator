import * as React from 'react';
import { useState } from 'react';
import { OrchestratorUI } from './components/OrchestratorUI';
import { AdminLayout } from './components/admin/AdminLayout';

type View = 'orchestrator' | 'admin';

function App() {
    const [currentView, setCurrentView] = useState<View>('orchestrator');

    return (
        <React.StrictMode>
            {currentView === 'orchestrator' && (
                <OrchestratorUI onOpenSettings={() => setCurrentView('admin')} />
            )}
            {currentView === 'admin' && (
                <AdminLayout onBack={() => setCurrentView('orchestrator')} />
            )}
        </React.StrictMode>
    );
}

export default App;
