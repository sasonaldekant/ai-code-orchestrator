# Package manifest — Domain‑Specific AI Code Orchestrator (v3)

This archive contains all normative and reference artefacts needed to understand and implement the domain‑specific AI Code Orchestrator.  Documents are provided in Markdown (`.md`) and Word (`.docx`) formats.

## 1. Normative Documents

| Category | Path | Purpose |
|---|---|---|
| Architecture Strategy & Conceptual Model | `docs/Architecture_Strategy_Domain_Specific_AI_Code_Orchestrator.md` / `.docx` | Defines the system’s purpose, principles, conceptual model, layers, governance, lifecycle, quality model and risk strategy. |
| Functional & Technical Specification | `docs/Functional_Technical_Specification.md` / `.docx` | Defines functional requirements, workflows, non‑functional constraints and references schema and API contracts. |
| Schema Contracts | `schemas/*.schema.json` | JSON Schema files defining the structure of outputs for each phase, domain context, tasks, milestones, vector documents, workflow assignments, bounded contexts, trace events and cost reports. |
| API Contract | `api/openapi.yaml` | OpenAPI 3.1 specification describing the `/run` and `/query` endpoints and referencing JSON schemas. |
| CLI Command Specs | `api/cli_commands.md` | Human‑readable specification of CLI commands and arguments. |

## 2. Reference Documents

| Category | Path | Purpose |
|---|---|---|
| Domain‑Specific Code Examples | `docs/Domain_Specific_Code_Examples.md` / `.docx` | Non‑normative examples of ingesters, retriever, context optimiser, prompt templates and lifecycle orchestrator methods. |
| Project Status & Next Steps | `notes/Project_Status_and_Next_Steps.md` / `.docx` | Analysis of current repository state vs. documentation and recommended next steps. |
| Source Inputs | `notes/Domain_Strategy_Source.md`, `notes/ADVANCED_RAG_Source.md`, `notes/Enhanced_Documentation_v2_Source.md`, `notes/Documentation_v3_Source.md` | Copies of input documents used to derive the strategy and specification. |

## 3. How to Use This Package

1. **Read the Architecture Strategy** to understand the conceptual boundaries and guiding principles.
2. **Read the Functional & Technical Specification** to see how the system operates, including phase workflows and constraints.  Refer to the Schema Contracts for formal data structures.
3. **Browse the Code Examples** for implementation ideas and patterns.
4. **Consult the Project Status** to prioritise implementation tasks relative to current code.
5. Use the **OpenAPI spec** and **CLI specs** for integration and automation.
