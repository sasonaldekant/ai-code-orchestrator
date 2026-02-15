# AI Code Orchestrator Client

VS Code Client for the AI Code Orchestrator system.

## Features

- **Run Task**: Execute AI coding tasks directly from VS Code.
- **Add Context**: Right-click files or use the explore view to add them as context for the next task.
- **RAG Tier Insights**: Visual feedback on which data tiers (Rules, Tokens, Components) are being utilized for each step.
- **Premium UI**: Modern dark-mode interface with smooth transitions and improved typography.
- **Budget Control**: Set session-specific budget limits to control costs.

## Requirements

- Python 3.10+
- AI Code Orchestrator backend running at `localhost:8000` (configurable).

## Extension Settings

This extension contributes the following settings:

* `aiOrchestrator.pythonPath`: Path to the python executable (default: `python`).
* `aiOrchestrator.projectRoot`: Path to the AI Code Orchestrator root directory.
* `aiOrchestrator.apiBaseUrl`: Base URL for the backend API.

## Release Notes

### 0.1.0

- **UI Engine Upgrade**: Redesigned the sidebar with a premium, high-fidelity dark aesthetic.
- **Tier Visualization**: Added support for "Tier Badges" showing RAG data usage (Rules, Tokens, etc.).
- **Claude 3.7 Support**: Added support for the latest Claude models.
- **Bug Fixes**: Improved venv auto-detection and cost alert parsing.

### 0.0.1

Initial release.
