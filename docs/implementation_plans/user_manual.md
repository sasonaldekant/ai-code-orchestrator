# Nexus AI Orchestrator - User Manual (v3.0)

## 1. Getting Started

### Installation

1.  **Prerequisites**: Python 3.11+, Node.js 18+.
2.  **Setup**:

    ```powershell
    # Clone repository
    git clone https://github.com/mgasic/ai-code-orchestrator.git
    cd ai-code-orchestrator

    # Backend Setup (Python 3.11 recommended)
    python -m venv venv_311
    .\venv_311\Scripts\Activate.ps1
    pip install -r requirements.txt

    # Frontend Setup
    cd ui
    npm install
    ```

### Launching the Application

1.  **Start Backend**: `python api/app.py` (Runs on `http://localhost:8000`)
2.  **Start Frontend**: `npm run dev` (Runs on `http://localhost:5173`)
3.  **Open Browser**: Navigate to `http://localhost:5173`.

---

## 2. Using the Dashboard

### A. The Chat Interface

The main interface allows you to submit feature requests in natural language.

- **Prompt**: Enter your request (e.g., "Create a new login page").
- **Image Upload**: Attach screenshots or mockups for context.
- **Deep Search**: Toggle this to enable internet research (Investigator Agent) before planning.
- **Auto-Fix**: Enable autonomous self-healing if code execution fails.

### B. Managing Knowledge

Navigate to the **"Manage Knowledge"** tab to add context to the AI.

1.  **Select Source Type**:
    - _Database Schema_: For backend models (Entity Framework, Django, etc.).
    - _Component Library_: For frontend components (React, Vue, etc.).
2.  **Enter Path**: Absolute path to your source folder (e.g., `E:\Projects\MyApp\backend`).
3.  **Ingest**: Click "Start Ingestion". The system will parse files and update the vector database.

### C. Advanced Options (Coming Soon)

For granular control over a specific run:

- **Budget Limit**: Set a maximum cost cap.
- **Consensus Mode**: Force multiple AI models to vote on architecture decisions.
- **Review Strategy**: Choose "Strict" for production-critical code.

---

## 3. Configuration & Settings

### Global Settings (Admin)

Access via the **Settings (Gear)** icon in the sidebar.

- **API Keys**: Manage your OpenAI/Anthropic keys securely.
- **Default Models**: Choose which AI model performs which role (Analyst, Architect, Developer).
- **System Limits**: Adjust timeout and retry attempts.

---

## 4. Troubleshooting

- **Ingestion Fails**: Ensure you are using the correct path and that `venv_311` is active.
- **Environment Issues**: If Python crashes, check compatibility notes in `walkthrough.md`.
