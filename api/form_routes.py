from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, field_validator, model_validator
from typing import Dict, Any, Optional, List
import json
import logging

from core.form_engine.mapper import DynUIMapper
from core.form_engine.specialists import FormArchitectSpecialist
from core.form_engine.orchestrator import FormEngineOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/forms", tags=["forms"])

mapper = DynUIMapper()
architect = FormArchitectSpecialist()


def _extract_logic_summary(raw: dict) -> dict:
    """
    Extracts all logic, validations, lookups and interdependencies from a raw JSON template
    that are NOT directly rendered in the Preview UI.
    Returns a structured dict for the frontend Logic Inspector panel.
    """
    logic = raw.get("logic") or {}
    lookups = raw.get("lookups") or {}
    sections = raw.get("sections") or []
    form_fields = (raw.get("form") or {}).get("fields") or []

    # Flatten fields from both formats
    all_fields = list(form_fields)
    for sec in sections:
        all_fields.extend(sec.get("fields", []))

    # 1. Conditional Visibility Rules
    visibility_rules = []
    for rule in logic.get("conditionalVisibility") or []:
        visibility_rules.append({
            "target": rule.get("targetField"),
            "showWhen": rule.get("showWhen"),
        })
    # Also pick up section-level showWhen
    for sec in sections:
        if sec.get("showWhen"):
            visibility_rules.append({
                "target": sec.get("id"),
                "targetTitle": sec.get("title"),
                "showWhen": sec["showWhen"],
            })

    # 2. Cross-field Validation Rules
    cross_validations = []
    for rule in logic.get("crossFieldValidation") or []:
        cross_validations.append({
            "rule": rule.get("rule"),
            "errorMessage": rule.get("errorMessage"),
            "errorTarget": rule.get("errorTarget"),
        })

    # 3. Lookup Definitions
    lookup_defs = []
    # From top-level lookups block
    for key, val in lookups.items():
        lookup_defs.append({
            "name": key,
            "endpoint": val.get("endpoint"),
            "method": val.get("method", "GET"),
            "cache": val.get("cache", False),
            "cacheTTL": val.get("cacheTTL"),
        })
    # Also collect lookupRef fields for fields that reference lookups
    lookup_fields = []
    for f in all_fields:
        if f.get("lookupRef"):
            lookup_fields.append({
                "fieldId": f["id"],
                "label": f.get("label"),
                "lookupRef": f["lookupRef"],
                "dependsOn": (f.get("lookupParams") or {}).get("dependsOn"),
            })

    # 4. Custom field-level validators
    custom_validators = []
    for f in all_fields:
        validation = f.get("validation") or {}
        custom = validation.get("custom")
        if custom:
            custom_validators.append({
                "fieldId": f["id"],
                "label": f.get("label"),
                "rule": custom.get("rule"),
                "errorMessage": custom.get("errorMessage"),
            })

    return {
        "visibilityRules": visibility_rules,
        "crossValidations": cross_validations,
        "lookupDefinitions": lookup_defs,
        "lookupFields": lookup_fields,
        "customValidators": custom_validators,
        "hasLogic": bool(visibility_rules or cross_validations or custom_validators),
    }


# ─── Pydantic Models ───────────────────────────────────────────────────────

class FieldVisibility(BaseModel):
    dependsOn: str
    condition: str = "equals"
    value: Any = None

class FieldValidation(BaseModel):
    required: Optional[bool] = None
    min: Optional[float] = None
    max: Optional[float] = None
    minLength: Optional[int] = None
    maxLength: Optional[int] = None
    pattern: Optional[str] = None

class FormField(BaseModel):
    id: str
    type: str = "text"
    label: str
    required: Optional[bool] = False
    placeholder: Optional[str] = None
    helperText: Optional[str] = None
    errorMessage: Optional[str] = None
    defaultValue: Optional[Any] = None
    options: Optional[List[Any]] = None
    dropdownRef: Optional[str] = None
    lookupRef: Optional[str] = None        # For dynamic dropdown data (e.g. "nationalities")
    lookupParams: Optional[Dict[str, Any]] = None  # e.g. {"dependsOn": "opstina"}
    visibility: Optional[FieldVisibility] = None
    validation: Optional[FieldValidation] = None
    layout: Optional[Dict[str, Any]] = None  # Responsive layout hints, ignored for now
    min: Optional[float] = None
    max: Optional[float] = None
    minLength: Optional[int] = None
    maxLength: Optional[int] = None
    pattern: Optional[str] = None
    step: Optional[float] = None

class FormAction(BaseModel):
    id: Optional[str] = None
    type: str = "submit"
    label: str = "Submit"
    variant: Optional[str] = "primary"
    color: Optional[str] = None
    endpoint: Optional[str] = None

class FormDefinition(BaseModel):
    fields: List[FormField]
    actions: Optional[List[FormAction]] = None

class FormMetadata(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None    # Alias used in some schemas
    version: Optional[str] = "1.0"
    description: Optional[str] = None
    formType: Optional[str] = None
    outputSchema: Optional[bool] = False

    @model_validator(mode='after')
    def resolve_title(self):
        # Support `name` as an alias for `title`
        if not self.title and self.name:
            self.title = self.name
        if not self.title:
            self.title = "Untitled Form"
        return self

class SectionDefinition(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    sectionNumber: Optional[str] = None
    description: Optional[str] = None
    fields: List[FormField]
    showWhen: Optional[Dict[str, Any]] = None  # Section-level conditional visibility

class FormSchemaInput(BaseModel):
    metadata: Optional[FormMetadata] = None
    form: Optional[FormDefinition] = None
    sections: Optional[List[SectionDefinition]] = None  # Sectioned format support
    logic: Optional[Dict[str, Any]] = None              # Cross-field and visibility logic
    lookups: Optional[Dict[str, Any]] = None            # Lookup endpoint definitions
    formId: Optional[str] = None                        # Optional form identifier

    @model_validator(mode='after')
    def build_form_from_sections(self):
        """If `form` is absent but `sections` are present, flatten fields into form."""
        if self.form is None and self.sections:
            all_fields = []
            for section in self.sections:
                all_fields.extend(section.fields)
            if not all_fields:
                raise ValueError("Form must have at least one field.")
            self.form = FormDefinition(fields=all_fields)
        elif self.form is None and not self.sections:
            raise ValueError("Either 'form' or 'sections' must be provided.")
        return self

class PreviewRequest(BaseModel):
    schema_data: FormSchemaInput
    layout_override: Optional[str] = None  # "standard", "tabs", "stepper"

class GenerateRequest(BaseModel):
    schema_data: FormSchemaInput
    project_name: str
    layout_override: Optional[str] = None


# ─── Preview Endpoint (Deterministic, 0 AI tokens) ─────────────────────────

@router.post("/preview")
async def preview_form(req: PreviewRequest):
    """
    Deterministic form preview. Takes a JSON schema, runs it through
    the mapper + layout architect, and returns a FormConfig-compatible
    object for live DynUI rendering. No AI tokens consumed.
    """
    try:
        template = req.schema_data.model_dump(mode="json")

        # Run deterministic layout analysis
        layout_decision = await architect.analyze_form(template)

        # Override layout if user specified
        if req.layout_override:
            layout_decision["recommendedLayout"] = req.layout_override

        # Generate preview config (FormEngine-compatible)
        preview = mapper.generate_preview_config(template, layout_decision)

        # Add metadata
        meta = template.get("metadata") or {}
        sections = template.get("sections") or []
        total_fields = (
            len(template.get("form", {}).get("fields", []))
            or sum(len(s.get("fields", [])) for s in sections)
        )
        preview["metadata"] = {
            "title": meta.get("title", "Untitled Form"),
            "description": meta.get("description", ""),
            "fieldCount": total_fields,
        }

        # Add mapped actions
        actions = (template.get("form") or {}).get("actions") or []
        if not actions:
            actions = [{"type": "submit", "label": "Submit", "variant": "primary"}]
        preview["actions"] = [mapper.map_action(a) for a in actions]

        # Add Logic Summary for the Inspector Panel
        preview["logicSummary"] = _extract_logic_summary(template)

        return preview

    except Exception as e:
        logger.error(f"Preview generation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/preview/upload")
async def preview_from_upload(file: UploadFile = File(...)):
    """
    Upload a JSON file and get a preview config back.
    """
    try:
        content = await file.read()
        raw = json.loads(content.decode("utf-8"))

        # Validate through Pydantic
        schema_input = FormSchemaInput(**raw)
        template = schema_input.model_dump(mode="json")

        layout_decision = await architect.analyze_form(template)
        preview = mapper.generate_preview_config(template, layout_decision)

        meta = template.get("metadata", {})
        preview["metadata"] = {
            "title": meta.get("title", file.filename or "Uploaded Form"),
            "description": meta.get("description", ""),
            "fieldCount": len(template.get("form", {}).get("fields", [])),
        }

        actions = template.get("form", {}).get("actions", [])
        if not actions:
            actions = [{"type": "submit", "label": "Submit", "variant": "primary"}]
        preview["actions"] = [mapper.map_action(a) for a in actions]

        return preview

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file.")
    except Exception as e:
        logger.error(f"Upload preview failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ─── Output Schema Generation ──────────────────────────────────────────────

@router.post("/output-schema")
async def generate_output_schema(req: PreviewRequest):
    """
    Generates the output JSON schema that the form would produce.
    Useful for understanding what data structure the form creates.
    """
    try:
        fields = req.schema_data.form.fields
        properties = {}
        required_fields = []

        for f in fields:
            type_map = {
                "text": "string", "email": "string", "password": "string",
                "tel": "string", "textarea": "string", "date": "string",
                "number": "number", "checkbox": "boolean", "switch": "boolean",
                "select": "string", "dropdown": "string", "radio": "string",
                "upload": "string", "label": "string",
            }
            json_type = type_map.get(f.type, "string")

            prop: Dict[str, Any] = {"type": json_type}
            if f.label:
                prop["description"] = f.label
            if f.options:
                enum_vals = []
                for opt in f.options:
                    if isinstance(opt, dict):
                        enum_vals.append(opt.get("value", str(opt)))
                    else:
                        enum_vals.append(str(opt))
                prop["enum"] = enum_vals

            properties[f.id] = prop
            if f.required:
                required_fields.append(f.id)

        output_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": req.schema_data.metadata.title if req.schema_data.metadata else "FormOutput",
            "type": "object",
            "properties": properties,
            "required": required_fields
        }

        return output_schema

    except Exception as e:
        logger.error(f"Output schema generation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ─── Full Generation Endpoint (AI-Powered, post-Approve) ───────────────────

from api.event_bus import bus, Event, EventType

@router.post("/generate")
async def generate_project(req: GenerateRequest):
    """
    Full AI-powered project generation. Only called AFTER user approves
    the preview. This is the expensive path that creates a complete
    React/Vite project with DynUI components.
    """
    try:
        await bus.publish(Event(type=EventType.LOG, agent="FormEngine", content=f"Pokrećem generisanje projekta: {req.project_name}"))
        template = req.schema_data.model_dump(mode="json")

        # Save template to disk for the orchestrator
        import tempfile
        from pathlib import Path

        temp_dir = Path("examples/form_templates")
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = temp_dir / f"approved_{req.project_name}.json"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(template, f, indent=2, ensure_ascii=False)

        await bus.publish(Event(type=EventType.LOG, agent="FormEngine", content="JSON Šablon uspešno sačuvan na serveru."))

        # Run full generation pipeline
        engine = FormEngineOrchestrator()
        await bus.publish(Event(type=EventType.LOG, agent="FormEngine", content="Mapiranje DynUI form komponenti u toku..."))
        project_path = await engine.generate_ui_project(str(temp_path), req.project_name, req.layout_override)
        
        await bus.publish(Event(type=EventType.DONE, agent="FormEngine", content=f"Projekat {req.project_name} uspešno izgenerisan!"))

        return {
            "status": "success",
            "project_path": project_path,
            "project_name": req.project_name,
            "message": f"Project '{req.project_name}' generated successfully."
        }

    except Exception as e:
        logger.error(f"Project generation failed: {e}")
        await bus.publish(Event(type=EventType.ERROR, agent="FormEngine", content=f"Generisanje otkazano zbog greške: {str(e)}"))
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import FileResponse
import shutil
import os

@router.get("/download/{project_name}")
async def download_project(project_name: str):
    """
    Downloads the generated project as a ZIP archive.
    """
    try:
        from pathlib import Path
        # point to the new monorepo location
        base_dir = Path("outputs") / "forms-workspace" / "apps"
        project_dir = base_dir / project_name
        
        if not project_dir.exists() or not project_dir.is_dir():
            logger.error(f"Project directory not found: {project_dir}")
            raise HTTPException(status_code=404, detail="Project not found.")
            
        # Create a temp ZIP file in outputs/archives
        archives_dir = Path("outputs") / "archives"
        archives_dir.mkdir(parents=True, exist_ok=True)
        zip_base_name = archives_dir / project_name
        
        # Create ZIP archive (shutil.make_archive appends .zip automatically)
        zip_full_path = shutil.make_archive(str(zip_base_name), 'zip', str(project_dir))
        
        return FileResponse(
            path=zip_full_path, 
            media_type='application/zip', 
            filename=f"{project_name}.zip"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ZIP project: {e}")
        raise HTTPException(status_code=500, detail="Failed to create project archive.")
