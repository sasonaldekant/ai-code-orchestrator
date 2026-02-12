import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
            '@dyn-ui/react': path.resolve(__dirname, './src/dyn-ui'),
            '@dyn-ui/design-tokens': path.resolve(__dirname, './src/dyn-design-tokens')
        }
    }
})
