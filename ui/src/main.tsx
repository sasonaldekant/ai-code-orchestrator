import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import '@dyn-ui/design-tokens/styles/index.css'
import App from './App'

const container = document.getElementById('root') || document.getElementById('app');

if (!container) {
    throw new Error('Failed to find the root element');
}

createRoot(container).render(
    <StrictMode>
        <App />
    </StrictMode>,
)
