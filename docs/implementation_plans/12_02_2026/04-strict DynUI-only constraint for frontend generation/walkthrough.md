# Admin Settings & Extension Feedback Walkthrough

This document outlines the changes made to centralize administrative settings in the UI and improve the feedback loop in the VS Code extension.

## 1. Centralized Admin Settings

Admin settings (Temperature, Budget, Retries, Deep Search) have been moved from the VS Code extension sidebar to a dedicated **Global Settings** panel in the main UI.

### verification
1. Open the Admin Panel (`http://localhost:5173/admin`).
2. Click on the **Global Settings** tab (Slider icon) in the sidebar.
3. Verify you can adjust:
   - **Temperature**: Controls creativity (0.0 - 1.0).
   - **Max Retries**: Number of times to retry failed steps.
   - **Feedback Iterations**: Maximum feedback loops during code generation.
   - **Deep Search**: Toggle for detailed research mode.
4. Click **Save Changes** and ensure settings persist.

## 2. Enhanced UI Feedback (:::STEP: Tags)

The VS Code extension now provides detailed, granular feedback during task execution using `:::STEP:` tags.

### verification
1. Open the AI Code Orchestrator extension in VS Code.
2. Enter a task (e.g., "Create a simple calculator API").
3. Observe the chat interface. You should see distinct step indicators for:
   - **Thinking** (💭): "Analyzing Requirements", "Designing Architecture"
   - **Editing** (📝): "Generating Backend...", "Generating Frontend..."
   - **Analyzing** (🔍): "Testing Implementation"

## 3. Review Changes Workflow

A new "Review Changes" button allows you to inspect and discuss code before it is written to disk.

### verification
1. Request a code change (e.g., "Add a hello world endpoint").
2. Wait for the generation phase to complete.
3. A **"🔎 Review Changes"** button will appear in the chat.
4. Click it to open a diff view of the proposed changes (mock functionality for now, triggers `onReviewChanges` event).

## Technical Implementation

### Backend
- **`config/limits.yaml`**: Added `global` section for settings.
- **`api/config_routes.py`**: Added endpoints to read/write global settings.
- **`core/orchestrator_v2.py`**: Updated to load settings from `limits.yaml`.
- **`agents/phase_agents/implementation.py`**: Added `:::STEP:` and `:::FILES:` markers.

### Frontend (UI)
- **`ui/src/lib/api.ts`**: Created centralized API client.
- **`ui/src/components/admin/GlobalSettingsPanel.tsx`**: New component for settings management (refactored to use standard components).
- **`ui/src/components/admin/AdminLayout.tsx`**: Added routing for Global Settings.

### VS Code Extension
- **`SidebarProvider.ts`**: 
    - Added CSS for step styling.
    - Implemented `addStep` logic to parse `:::STEP:` messages.
    - Added `showReviewButton` to handle `:::FILES:` messages.

## 4. Strict DynUI Enforcement
Frontend generation is now strictly limited to DynUI components. Native HTML tags are forbidden, and a Fallback Protocol is in place for complex requirements.

### Changes
- Updated `rag/AI_CONTEXT.md` with strict "Assembler" mindset rules.
- Defined **Fallback Protocol** (Decompose, Compose, Propose).
- Updated `architect.txt` and `implementation_frontend.txt` with mandatory compliance rules.

## 5. RAG Management & GUI Inspection
The Admin Panel now provides a much more powerful interface for managing the orchestrator's knowledge base.

### Improvements
- **Document Browser**: Added a paginated document browser in the Knowledge Explorer. You can now list chunks, view full text, and inspect metadata.
- **Expanded Ingestion**: Added support for "Instruction Docs" (`.md`, `.txt`) and "Specialization Rules" (`.yaml`, `.json`).
- **Granular Control**: Individual document chunks can now be deleted from the GUI without deleting the entire collection.

## 6. Automation Scripts
- **`start_all.bat`**: A new batch script in the project root that launches the Backend API, Web UI, and Extension Watcher in separate windows with a single command.

## 7. Bug Fixes
- **VS Code Extension Syntax**: Fixed a critical syntax error in `SidebarProvider.ts` where nested template literals were causing premature termination of the main HTML string, resulting in compiler errors. Switched to single-quoted strings for inner HTML generation for better reliability.
