# Improving RAG Management and GUI Inspection

This plan outlines improvements to the Admin Panel for better RAG inspection and knowledge ingestion.

## Proposed Changes

### [Backend API]

#### [MODIFY] [admin_routes.py](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/api/admin_routes.py)
- Update `validate_ingestion` and `execute_ingestion` to handle:
    - `instruction_docs`: Defaults filter to `.md, .txt`.
    - `specialization_rules`: Defaults filter to `.yaml, .json, .yml`.
- This ensures the orchestrator can specifically ingest documentation and rules folders.

### [Web UI]

#### [MODIFY] [IngestionPanel.tsx](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/ui/src/components/admin/IngestionPanel.tsx)
- Add new ingestion types: "Instruction Docs" and "Specialization Rules".
- Add a "Browse Documents" button in the collection list.

#### [MODIFY] [KnowledgeExplorer.tsx](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/ui/src/components/admin/KnowledgeExplorer.tsx)
- Implement a paginated document browser view.
- Allow users to see the full content of ingested chunks.

### [Scripts]

#### [NEW] [start_all.bat](file:///c:/Users/mgasic/Documents/AIProjects/ai-code-orchestrator/start_all.bat)
- Create a batch script to start Backend, UI, and Extension (watch) in separate windows.

## Verification Plan

### Manual Verification
1. **Ingest Docs**: Create a folder with `.md` files and ingest them using the "Instruction Docs" type.
2. **Browse RAG**: Go to the Knowledge Explorer, select the collection, and click "Browse Documents".
3. **Verify Focus**: Ensure the orchestrator retrieves context from these new docs during a generation task.
4. **Test Specialization**: Ingest a `.yaml` rule and verify it influences the agent's output.
