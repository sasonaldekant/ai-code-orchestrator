# Functional Specification: Nexus Control Center (v3.0)

## 1. Introduction

The **Nexus Control Center** is a major upgrade to the AI Code Orchestrator's GUI, transforming it from a simple chat interface into a comprehensive management console. This document defines the functional requirements and technical architecture for the new "Settings", "Advanced Options", and "Agent Registry" features.

## 2. System Architecture

The solution uses a **React (Frontend)** + **FastAPI (Backend)** architecture.

- **Frontend**: Manages local state for transient options (Advanced Run Options) and syncs global settings via API.
- **Backend**: Exposes new endpoints to read/write configuration files (`config/*.yaml`, `.env`).

## 3. Functional Requirements

### 3.1. Advanced Run Options (Per-Request)

**User Story**: As a user, I want to customize the execution parameters for a specific request without changing global defaults.
**UI Location**: Collapsible "Advanced Options" drawer in the main input area.
**Parameters**:

- **Budget Limit** (`float`): Maximum dollar amount for the run.
- **Review Strategy** (`enum`): `Basic`, `Strict` (Producer-Reviewer loop intensity).
- **Consensus Mode** (`bool`): Force multi-model consensus for architectural decisions.
- **Output Format** (`enum`): `Standard`, `Code Only`, `Plan Only`.

### 3.2. Global Settings Management

**User Story**: As a user, I want to configure API keys and default models without editing YAML files.
**UI Location**: Modal dialog triggered by the "Settings" icon in the sidebar.
**Features**:

- **API Keys**: Secure input fields for `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc. (Masked).
- **Model Mapping**: Dropdowns to select default models for each phase (Analyst, Architect, Implementer).
- **System Limits**: Sliders for `Max Retries`, `Timeout`, and `Global Budget Cap`.
- **Persistence**: "Save" button writes changes to `config/model_mapping.yaml` and `.env`.

### 3.3. Agent Registry & Control

**User Story**: As a user, I want to see which agents are active and disable specific tools for safety.
**UI Location**: New Tab "Agent Registry".
**Features**:

- **Agent List**: Visual cards for `Orchestrator`, `RAG Agent`, `Vision Agent`.
- **Tool Toggle**: Switches to enable/disable specific tools (e.g., `run_command`, `write_file`).
- **Status**: Real-time indicator of agent availability.

## 4. Technical Implementation

### 4.1. API Endpoints (New)

```python
# GET /config/settings
# Returns current global configuration
response = {
    "models": { ... },
    "limits": { ... }
}

# POST /config/settings
# Updates configuration files
body = {
    "models": { ... },
    "api_keys": { ... } # Optional
}

# GET /agents/status
# Returns list of available agents and tools
```

### 4.2. Frontend Components

- `SettingsModal.tsx`: Formik/React-Hook-Form based modal for configuration.
- `AdvancedOptions.tsx`: Lightweight collapsible component for the chat input.
- `AgentRegistry.tsx`: Grid layout displaying `AgentCard` components.

## 5. Security Considerations

- **API Keys**: Never returned in plain text via GET requests (masked: `sk-...XXXX`).
- **Input Validation**: Strict validation on backend for numeric limits and file paths.
