# Implement GUI Enhancements (Nexus Control Center)

## 1. Documentation

- [x] **Functional Specification**: Created `functional_specification.md`.
- [x] **User Manual**: Created `user_manual.md`.

## 2. Phase 1: Advanced Run Options (Frontend)

- [ ] **Create Component**: `AdvancedOptions.tsx` (Collapsible drawer).
  - [ ] Budget Input.
  - [ ] Consensus Toggle.
  - [ ] Review Strategy Selector.
- [ ] **Update Main UI**: Integrate `AdvancedOptions` into `OrchestratorUI.tsx`.
- [ ] **State Management**: Lift state to `OrchestratorUI` to pass to API.

## 3. Phase 2: Configuration API (Backend)

- [ ] **Create Endpoints**: `api/config_routes.py`.
  - [ ] `GET /config/settings`: Read `model_mapping.yaml`.
  - [ ] `POST /config/settings`: Update settings.
- [ ] **Update App**: Register new router in `api/app.py`.

## 4. Phase 3: Global Settings (Frontend)

- [ ] **Create Modal**: `SettingsModal.tsx`.
  - [ ] API Key Management (Masked inputs).
  - [ ] Model Selection Dropdowns.
- [ ] **Wire Up**: Connect "Settings" button in Sidebar to Modal.

## 5. Verification

- [ ] **Test Run**: Execute a request with custom Advanced Options.
- [ ] **Test Config**: Change a model setting and verify persistence.
