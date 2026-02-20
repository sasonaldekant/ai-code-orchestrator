import os
import json
import logging
from pathlib import Path
from typing import Dict, Any
from core.form_engine.monorepo_initializer import FormMonorepoInitializer

logger = logging.getLogger(__name__)

class ProjectGenerator:
    """
    Generates the physical file structure for a React TypeScript/DynUI app inside the Monorepo.
    """
    
    def __init__(self, base_path: str = "outputs/forms-workspace"):
        self.monorepo_initializer = FormMonorepoInitializer(base_workspace=base_path)
        
    def generate_structure(self, project_name: str) -> Path:
        """Creates the basic folder structure within the monorepo."""
        # Ensure monorepo exists
        workspace_path = self.monorepo_initializer.ensure_workspace()
        
        # Project directory
        project_dir = workspace_path / "apps" / project_name
        
        # Define folders to create
        folders = [
            "src",
            "src/components",
            "src/api",
            "src/utils"
        ]
        
        for folder in folders:
            (project_dir / folder).mkdir(parents=True, exist_ok=True)
            
        logger.info(f"Created app structure at {project_dir}")
        return project_dir

    def create_package_json(self, project_dir: Path, project_name: str):
        """Generates package.json with DynUI dependencies and shared UI linkage."""
        package_json = {
            "name": project_name,
            "version": "0.1.0",
            "private": True,
            "dependencies": {
                "react": "^18.3.1",
                "react-dom": "^18.3.1",
                "@dyn-ui/react": "workspace:*",
                "@form-studio/shared-ui": "workspace:*",
                "@form-studio/form-engine": "workspace:*",
                "lucide-react": "latest",
                "clsx": "latest",
                "zod": "^3.22.4"
            },
            "devDependencies": {
                "@types/react": "^19.2.2",
                "@types/react-dom": "^19.2.2",
                "@vitejs/plugin-react": "^4.2.0",
                "typescript": "^5.2.0",
                "vite": "^5.0.0"
            },
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "preview": "vite preview"
            }
        }
        
        with open(project_dir / "package.json", "w", encoding="utf-8") as f:
            json.dump(package_json, f, indent=2)

    def create_tsconfig(self, project_dir: Path):
        """Generates a standard tsconfig.json."""
        tsconfig = {
            "compilerOptions": {
                "target": "ESNext",
                "useDefineForClassFields": True,
                "lib": ["DOM", "DOM.Iterable", "ESNext"],
                "allowJs": False,
                "skipLibCheck": True,
                "esModuleInterop": False,
                "allowSyntheticDefaultImports": True,
                "strict": True,
                "forceConsistentCasingInFileNames": True,
                "module": "ESNext",
                "moduleResolution": "bundler",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "react-jsx"
            },
            "include": ["src"],
            "exclude": ["node_modules", "dist"],
            "references": [{ "path": "./tsconfig.node.json" }]
        }
        
        with open(project_dir / "tsconfig.json", "w", encoding="utf-8") as f:
            json.dump(tsconfig, f, indent=2)

    def create_vite_config(self, project_dir: Path):
        """Generates vite.config.ts."""
        content = """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
});
"""
        with open(project_dir / "vite.config.ts", "w", encoding="utf-8") as f:
            f.write(content)

    def create_tsconfig_node(self, project_dir: Path):
        """Generates tsconfig.node.json."""
        tsconfig_node = {
            "compilerOptions": {
                "composite": True,
                "skipLibCheck": True,
                "module": "ESNext",
                "moduleResolution": "Node",
                "allowSyntheticDefaultImports": True
            },
            "include": ["vite.config.ts"]
        }
        with open(project_dir / "tsconfig.node.json", "w", encoding="utf-8") as f:
            json.dump(tsconfig_node, f, indent=2)

    def create_vite_env(self, project_dir: Path):
        """Generates vite-env.d.ts."""
        content = '/// <reference types="vite/client" />\n'
        with open(project_dir / "src" / "vite-env.d.ts", "w", encoding="utf-8") as f:
            f.write(content)

    def generate_project_base(self, project_name: str) -> Path:
        """Runs the whole sequence to create a base project."""
        project_dir = self.generate_structure(project_name)
        self.create_package_json(project_dir, project_name)
        self.create_tsconfig(project_dir)
        self.create_tsconfig_node(project_dir)
        self.create_vite_config(project_dir)
        self.create_vite_env(project_dir)
        
        # Create index.html
        index_html = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""
        with open(project_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(index_html)
            
        # Create an entry main.tsx
        main_tsx = """import React from 'react';
import ReactDOM from 'react-dom/client';
import '@dyn-ui/react/dist/index.css';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
"""
        with open(project_dir / "src" / "main.tsx", "w", encoding="utf-8") as f:
            f.write(main_tsx)

        return project_dir
