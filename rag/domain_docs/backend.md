# Backend Notes

## DynUI AI Code Orchestrator Guidelines

This document details backend rules when working within the form generation space.

- **Stack**: Python, FastAPI.
- **RAG Architecture**: Uses an AI Architect agent (`FormArchitectSpecialist`) to intelligently assign an optimal UI layout logic (e.g., column spans inside CSS grid, default layout structures) before generating JSON components.
- **FormEngine Output**: The backend generates strictly Pydantic validated output matching `@form-studio/form-engine` schemas.
- **ColSpan Strategy**: Backend *must* enforce logic for generating `half`, `third`, `quarter` layout spans if horizontal packing is viable instead of simply dumping `full` length components everywhere, evaluating parameters like `maxLength`.
