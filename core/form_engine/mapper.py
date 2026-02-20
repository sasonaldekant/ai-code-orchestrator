import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ComponentMapping:
    json_type: str
    dynui_component: str
    default_props: Dict[str, Any]

class DynUIMapper:
    """
    Maps JSON template types to DynUI components and properties.
    """
    
    # Mapping table: JSON Type -> DynUI Component Configuration
    MAPPINGS = {
        "text": ComponentMapping("text", "DynInput", {"type": "text"}),
        "email": ComponentMapping("email", "DynInput", {"type": "email"}),
        "password": ComponentMapping("password", "DynInput", {"type": "password"}),
        "number": ComponentMapping("number", "DynInput", {"type": "number"}),
        "tel": ComponentMapping("tel", "DynInput", {"type": "tel"}),
        "textarea": ComponentMapping("textarea", "DynTextArea", {}),
        "select": ComponentMapping("select", "DynSelect", {}),
        "dropdown": ComponentMapping("dropdown", "DynDropdown", {}),
        "checkbox": ComponentMapping("checkbox", "DynCheckbox", {}),
        "switch": ComponentMapping("switch", "DynSwitch", {}),
        "radio": ComponentMapping("radio", "DynRadio", {}),
        "date": ComponentMapping("date", "DynDatePicker", {}),
        "upload": ComponentMapping("upload", "DynUpload", {}),
        "label": ComponentMapping("label", "DynLabel", {}),
        "divider": ComponentMapping("divider", "DynDivider", {}),
        "table": ComponentMapping("table", "DynTable", {}),
    }

    # Dummy data per field type for preview rendering
    DUMMY_DATA = {
        "text": "John Doe",
        "email": "john.doe@example.com",
        "password": "••••••••",
        "number": 42,
        "tel": "+381 64 123 4567",
        "textarea": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "select": None,  # Will use first option
        "dropdown": None,
        "checkbox": False,
        "switch": False,
        "radio": None,
        "date": "2025-01-15",
        "upload": None,
        "label": "",
        "divider": None,
        "table": None,
    }

    def get_dummy_value(self, field_json: Dict[str, Any]) -> Any:
        """Returns a realistic dummy value for a field based on its type and id."""
        field_type = field_json.get("type", "text")
        field_id = field_json.get("id", "").lower()
        
        # Smart defaults based on field id patterns
        if field_type == "text":
            if "name" in field_id and "first" in field_id: return "Marko"
            if "name" in field_id and "last" in field_id: return "Petrović"
            if "name" in field_id: return "Marko Petrović"
            if "city" in field_id or "location" in field_id: return "Belgrade"
            if "address" in field_id: return "Knez Mihailova 12"
            if "company" in field_id: return "TechCorp d.o.o."
            if "title" in field_id or "role" in field_id: return "Senior Developer"
            if "url" in field_id or "link" in field_id or "linkedin" in field_id: return "https://linkedin.com/in/example"
        
        if field_type == "select" or field_type == "dropdown":
            options = field_json.get("options", [])
            if options:
                first = options[0]
                return first.get("value", first) if isinstance(first, dict) else first
            return ""
        
        if field_type == "radio":
            options = field_json.get("options", [])
            if options:
                first = options[0]
                return first.get("value", first) if isinstance(first, dict) else first
            return ""
        
        return self.DUMMY_DATA.get(field_type, "")

    def map_field(self, field_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps a single field JSON definition to DynUI component structure.
        """
        json_type = field_json.get("type", "text")
        mapping = self.MAPPINGS.get(json_type)
        
        if not mapping:
            logger.warning(f"No mapping found for type '{json_type}'. Falling back to DynInput.")
            mapping = self.MAPPINGS["text"]

        # Basic component structure
        component = {
            "component": mapping.dynui_component,
            "id": field_json["id"],
            "props": {**mapping.default_props}
        }

        # Handle options for select/dropdown/radio (normalize to object format)
        if json_type in ("select", "dropdown", "radio") and "options" in field_json:
            raw_options = field_json["options"]
            normalized_options = []
            for opt in raw_options:
                if isinstance(opt, dict):
                    normalized_options.append({
                        "value": str(opt.get("value", "")),
                        "label": opt.get("label", str(opt.get("value", "")))
                    })
                else:
                    normalized_options.append({"value": str(opt), "label": str(opt)})
            component["props"]["options"] = normalized_options

        # Handle dropdownRef / lookupRef for external lists
        if json_type in ("dropdown", "select"):
            if "dropdownRef" in field_json:
                component["props"]["dropdownRef"] = field_json["dropdownRef"]
            if "lookupRef" in field_json:
                # lookupRef is a named lookup endpoint key (resolved at runtime)
                component["props"]["lookupRef"] = field_json["lookupRef"]
                if "lookupParams" in field_json:
                    component["props"]["lookupParams"] = field_json["lookupParams"]

        # Handle common props
        if "placeholder" in field_json:
            component["props"]["placeholder"] = field_json["placeholder"]
        
        if "defaultValue" in field_json:
            component["props"]["defaultValue"] = field_json["defaultValue"]

        # Handle validation props
        validation = field_json.get("validation") or {}
        for vkey in ["min", "max", "minLength", "maxLength", "pattern", "step"]:
            if vkey in field_json:
                component["props"][vkey] = field_json[vkey]
            if vkey in validation:
                component["props"][vkey] = validation[vkey]

        # Build result with wrapper
        result = {
            "wrapper": "DynFieldContainer",
            "wrapperProps": {
                "label": field_json.get("label", field_json["id"]),
                "required": field_json.get("required", False) or validation.get("required", False),
                "helperText": field_json.get("helperText", "")
            },
            "field": component,
            "originalData": field_json
        }

        # Visibility / conditional dependency
        visibility = field_json.get("visibility")
        if visibility and isinstance(visibility, dict):
            result["visibility"] = {
                "dependsOn": visibility.get("dependsOn"),
                "condition": visibility.get("condition", "equals"),
                "value": visibility.get("value")
            }

        return result

    def _extract_sections_from_template(self, template: Dict[str, Any]) -> tuple:
        """
        Returns (fields_json_flat, sections_for_layout) from either:
        - Standard format: { "form": { "fields": [...] } }
        - Sectioned format: { "sections": [ { "title", "fields": [...] } ] }
        
        Returns a tuple of:
        - all_fields: flat list of all field dicts
        - sections: list of {"id", "title", "fieldIds", "showWhen"} for layout
        - has_native_sections: bool indicating whether native sections were found
        """
        # Case 1: Top-level sections array (insurance-v5 style)
        top_sections = template.get("sections")
        if top_sections:
            all_fields = []
            sections = []
            for sec in top_sections:
                sec_fields = sec.get("fields", [])
                all_fields.extend(sec_fields)
                sections.append({
                    "id": sec.get("id", ""),
                    "title": sec.get("title", "Section"),
                    "fields": [{"id": f["id"], "colSpan": "full"} for f in sec_fields],
                    "showWhen": sec.get("showWhen"),
                    "description": sec.get("description"),
                })
            return all_fields, sections, True

        # Case 2: Standard flat format { form: { fields: [...] } }
        form = template.get("form") or {}
        fields_json = form.get("fields", [])
        return fields_json, [], False

    def _resolve_visibility_from_logic(self, template: Dict[str, Any]) -> Dict[str, Dict]:
        """
        Extracts section-level conditional visibility from the `logic.conditionalVisibility` block.
        Returns a dict mapping targetField (section id) -> showWhen rule.
        """
        logic = template.get("logic") or {}
        cv = logic.get("conditionalVisibility") or []
        result = {}
        for rule in cv:
            target = rule.get("targetField")
            when = rule.get("showWhen")
            if target and when:
                result[target] = when
        return result

    def map_action(self, action_json: Dict[str, Any]) -> Dict[str, Any]:
        """Maps an action (button) JSON definition."""
        return {
            "component": "DynButton",
            "props": {
                "label": action_json["label"],
                "color": action_json.get("variant", action_json.get("color", "primary")),
                "type": "submit" if action_json["type"] == "submit" else "button"
            },
            "endpoint": action_json.get("endpoint")
        }

    def process_template(self, template: Dict[str, Any], layout_decision: Dict[str, Any] = None) -> Dict[str, Any]:
        """Processes the whole JSON template and returns mapping structure."""
        fields_json, native_sections, has_native_sections = self._extract_sections_from_template(template)
        
        # Create map of ID -> Field JSON for easy lookup
        fields_by_id = {f["id"]: f for f in fields_json}
        
        # Determine the structure to map
        if has_native_sections:
            structure = native_sections
            layout = layout_decision["recommendedLayout"] if layout_decision else (
                "stepper" if len(native_sections) > 3 else "tabs" if len(native_sections) > 1 else "standard"
            )
        else:
            if not layout_decision:
                layout_decision = {
                    "recommendedLayout": "standard",
                    "structure": [{"title": "General", "fields": [{"id": f["id"], "colSpan": "full"} for f in fields_json]}]
                }
            structure = layout_decision["structure"]
            layout = layout_decision["recommendedLayout"]

        mapped_sections = []
        for section in structure:
            mapped_fields = []
            for f_info in section.get("fields", []):
                # Ensure backward compatibility with old layout cache if present
                if isinstance(f_info, str):
                    fid = f_info
                    colspan = "full"
                else:
                    fid = f_info["id"]
                    colspan = f_info.get("colSpan", "full")
                
                if fid in fields_by_id:
                    mapped_field = self.map_field(fields_by_id[fid])
                    # Add colspan to field wrapper metadata
                    mapped_field["wrapperProps"]["colSpan"] = colspan
                    mapped_fields.append(mapped_field)
            
            mapped_sections.append({
                "title": section["title"],
                "fields": mapped_fields
            })

        # Actions
        form_actions = (template.get("form") or {}).get("actions") or []
        mapped_actions = [self.map_action(a) for a in form_actions]
        
        return {
            "metadata": template.get("metadata", {}),
            "layout": layout,
            "sections": mapped_sections,
            "mappedActions": mapped_actions,
            "originalTemplate": template # Pass along for tools that need raw info (like schema/logic)
        }

    def _check_circular_dependencies(self, fields_json: List[Dict[str, Any]]) -> List[str]:
        """Detect circular dependencies in visibility rules."""
        graph = {}
        for f in fields_json:
            visibility = f.get("visibility")
            if visibility and visibility.get("dependsOn"):
                graph[f["id"]] = visibility.get("dependsOn")
                
        warnings = []
        for start_node in graph:
            visited = set()
            current = start_node
            path = []
            while current in graph:
                if current in visited:
                    warnings.append(f"Circular dependency detected in visibility rules involving fields: {' -> '.join(path + [current])}")
                    break
                visited.add(current)
                path.append(current)
                current = graph[current]
                
        # Return unique warnings
        return list(set(warnings))

    def generate_preview_config(self, template: Dict[str, Any], layout_decision: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generates a FormConfig-compatible object for use with DynUI FormEngine preview.
        Supports both flat (form.fields) and sectioned (top-level sections[]) JSON formats.
        Returns { formConfig, dummyValues, fieldMeta, warnings }.
        """
        fields_json, native_sections, has_native_sections = self._extract_sections_from_template(template)
        visibility_rules = self._resolve_visibility_from_logic(template)

        if not fields_json:
            return {"formConfig": {"sections": []}, "dummyValues": {}, "fieldMeta": {},
                    "layout": "standard", "complexity": "low", "warnings": ["No fields found."]}

        # For sectioned format: use native sections as layout structure
        if has_native_sections:
            # Apply logic.conditionalVisibility to sections that don't already have showWhen
            for sec in native_sections:
                if not sec.get("showWhen") and sec["id"] in visibility_rules:
                    sec["showWhen"] = visibility_rules[sec["id"]]

            layout = layout_decision["recommendedLayout"] if layout_decision else (
                "stepper" if len(native_sections) > 3 else "tabs" if len(native_sections) > 1 else "standard"
            )
            effective_sections = native_sections
        else:
            # Standard flat format path
            if not layout_decision:
                layout_decision = {
                    "recommendedLayout": "standard",
                    "structure": [{"title": "General", "fields": [{"id": f["id"], "colSpan": "full"} for f in fields_json]}]
                }
            layout = layout_decision["recommendedLayout"]
            effective_sections = layout_decision["structure"]
        fields_by_id = {f["id"]: f for f in fields_json}
        warnings = self._check_circular_dependencies(fields_json)

        # ─── FormEngine FieldType map ───────────────────────────────────────
        fe_type_map = {
            "text": "text", "email": "email", "tel": "tel", "number": "number",
            "date": "date", "radio": "radio", "select": "dropdown", "dropdown": "dropdown",
            "checkbox": "checkbox", "password": "text", "textarea": "text",
            "switch": "checkbox", "upload": "text", "label": "text", "divider": "text",
            "table": "text",
        }

        # ─── Build FormConfig sections ──────────────────────────────────────
        config_sections = []
        for section in effective_sections:
            section_fields = []
            
            # Extract IDs from the new 'fields' format or old 'fieldIds' (backward compatibility)
            raw_fields = section.get("fields", [])
            if not raw_fields and "fieldIds" in section:
                raw_fields = [{"id": fid, "colSpan": "full"} for fid in section["fieldIds"]]
            
            for f_info in raw_fields:
                fid = f_info if isinstance(f_info, str) else f_info["id"]
                col_span = "full" if isinstance(f_info, str) else f_info.get("colSpan", "full")

                if fid not in fields_by_id:
                    warnings.append(f"Field '{fid}' referenced in section '{section['title']}' but not found.")
                    continue
                fj = fields_by_id[fid]
                json_type = fj.get("type", "text")
                fe_type = fe_type_map.get(json_type, "text")

                field_entry: Dict[str, Any] = {
                    "id": fid,
                    "label": fj.get("label", fid),
                    "type": fe_type,
                    "layout": {"span": col_span}
                }

                validation_dict = fj.get("validation") or {}
                required = fj.get("required") or validation_dict.get("required", False)
                if required:
                    field_entry["required"] = True
                if fj.get("placeholder"):
                    field_entry["placeholder"] = fj["placeholder"]
                if fj.get("helpText"):
                    field_entry["helpText"] = fj["helpText"]
                elif fj.get("helperText"):
                    field_entry["helpText"] = fj["helperText"]

                # Validation constraints
                for vk in ["minLength", "maxLength", "pattern", "min", "max", "step"]:
                    val = fj.get(vk) if fj.get(vk) is not None else validation_dict.get(vk)
                    if val is not None:
                        field_entry[vk] = val

                # Options - static
                if fe_type in ("radio", "dropdown") and fj.get("options"):
                    field_entry["options"] = [
                        {"value": str(o.get("value", "")), "label": o.get("label", str(o.get("value", "")))} if isinstance(o, dict)
                        else {"value": str(o), "label": str(o)}
                        for o in fj["options"]
                    ]
                # Options - dynamic via lookupRef
                elif fe_type == "dropdown" and fj.get("lookupRef"):
                    field_entry["lookupRef"] = fj["lookupRef"]
                    field_entry["options"] = [{"value": "__loading__", "label": f"(Loaded from: {fj['lookupRef']})"}]

                section_fields.append(field_entry)

            section_entry: Dict[str, Any] = {
                "title": section["title"],
                "fields": section_fields,
            }
            # Pass section-level visibility for the frontend to handle
            if section.get("showWhen"):
                section_entry["showWhen"] = section["showWhen"]

            config_sections.append(section_entry)

        # Generate dummy values
        dummy_values = {}
        for fj in fields_json:
            dummy_values[fj["id"]] = fj.get("defaultValue", self.get_dummy_value(fj))

        # Field metadata (visibility rules, component type hints, lookupRef)
        field_meta = {}
        for fj in fields_json:
            meta: Dict[str, Any] = {"originalType": fj.get("type", "text")}
            if fj.get("visibility"):
                meta["visibility"] = fj["visibility"]
            if fj.get("lookupRef"):
                meta["lookupRef"] = fj["lookupRef"]
                meta["lookupParams"] = fj.get("lookupParams", {})
            field_meta[fj["id"]] = meta

        # Cross-field validation from logic block
        logic_warnings = []
        cross_validation = (template.get("logic") or {}).get("crossFieldValidation") or []
        for rule in cross_validation:
            logic_warnings.append(f"Cross-field rule: {rule.get('rule')}")
        warnings.extend(logic_warnings)

        # Check for unmapped types
        for fj in fields_json:
            if fj.get("type") not in self.MAPPINGS:
                warnings.append(f"Field '{fj['id']}' has unknown type '{fj.get('type')}', mapped as text.")

        return {
            "formConfig": {"sections": config_sections},
            "dummyValues": dummy_values,
            "fieldMeta": field_meta,
            "layout": layout,
            "complexity": layout_decision.get("complexity", "low") if layout_decision else ("high" if len(native_sections) > 3 else "medium"),
            "warnings": warnings
        }
