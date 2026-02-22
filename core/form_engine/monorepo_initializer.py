import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class FormMonorepoInitializer:
    """
    Initializes and manages the Monorepo skeleton (Turborepo + pnpm) for Form Studio.
    This skeleton is created only ONCE per environment, storing all generated forms as individual apps.
    """
    
    def __init__(self, base_workspace: str = "outputs/forms-workspace"):
        self.workspace_path = Path(base_workspace)
        
    def ensure_workspace(self) -> Path:
        """
        Creates the workspace skeleton if it doesn't exist.
        Returns the path to the established workspace.
        """
        if self.is_initialized():
            logger.info(f"Monorepo workspace already initialized at {self.workspace_path}")
            return self.workspace_path
            
        logger.info(f"Initializing new Monorepo workspace at {self.workspace_path}...")
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        
        self._create_root_package_json()
        self._create_turbo_json()
        self._create_pnpm_workspace()
        self._create_shared_ui_package()
        
        # Mark as initialized
        (self.workspace_path / ".forms-workspace-manifest.json").write_text(
            json.dumps({"version": "1.0", "type": "form-studio-monorepo"}),
            encoding="utf-8"
        )
        
        # Create apps directory (initially empty)
        (self.workspace_path / "apps").mkdir(exist_ok=True)
        
        return self.workspace_path
        
    def is_initialized(self) -> bool:
        """Checks if the workspace has already been built."""
        return (self.workspace_path / ".forms-workspace-manifest.json").exists()
        
    def get_apps_dir(self) -> Path:
        """Returns the path to the apps directory within the monorepo."""
        return self.ensure_workspace() / "apps"
        
    def _create_root_package_json(self):
        package_json = {
            "name": "form-studio-workspace",
            "private": True,
            "scripts": {
                "build": "turbo run build",
                "dev": "turbo run dev",
                "lint": "turbo run lint",
                "verify": "turbo run verify"
            },
            "devDependencies": {
                "turbo": "latest"
            },
            "engines": {
                "node": ">=16"
            }
        }
        with open(self.workspace_path / "package.json", "w", encoding="utf-8") as f:
            json.dump(package_json, f, indent=2)
            
    def _create_turbo_json(self):
        turbo_json = {
            "$schema": "https://turbo.build/schema.json",
            "pipeline": {
                "build": {
                    "dependsOn": ["^build"],
                    "outputs": ["dist/**"]
                },
                "lint": {},
                "dev": {
                    "cache": False,
                    "persistent": True
                },
                "verify": {
                    "dependsOn": ["^build"],
                    "cache": true
                }
            }
        }
        with open(self.workspace_path / "turbo.json", "w", encoding="utf-8") as f:
            json.dump(turbo_json, f, indent=2)
            
    def _create_pnpm_workspace(self):
        content = "packages:\n  - 'apps/*'\n  - 'packages/*'\n"
        with open(self.workspace_path / "pnpm-workspace.yaml", "w", encoding="utf-8") as f:
            f.write(content)
            
    def _create_shared_ui_package(self):
        shared_dir = self.workspace_path / "packages" / "shared-ui"
        shared_dir.mkdir(parents=True, exist_ok=True)
        
        # Package JSON for shared UI
        package_json = {
            "name": "@form-studio/shared-ui",
            "version": "1.0.0",
            "private": True,
            "main": "index.ts",
            "dependencies": {
                "react": "^18.3.1",
                "react-dom": "^18.3.1",
                "@dyn-ui/react": "workspace:*",
                "lucide-react": "latest",
                "clsx": "latest"
            },
            "scripts": {
                "verify": "tsc --noEmit"
            },
            "devDependencies": {
                "typescript": "^5.2.0",
                "@types/react": "^18.3.1",
                "@types/node": "latest"
            }
        }
        with open(shared_dir / "package.json", "w", encoding="utf-8") as f:
            json.dump(package_json, f, indent=2)
            
        # Example index export
        (shared_dir / "index.ts").write_text("// Shared DynUI exports will go here\nexport {};", encoding="utf-8")
