import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class CodeGenerator:
    """
    Generates React/TSX code and Business Logic layers from mapped DynUI structures.
    """

    def generate_component_code(self, mapped_data: Dict[str, Any]) -> str:
        """Generates the React component code that uses the generic FormEngine."""
        component_name = "Form"
        
        # We only need the generic FormEngine import and the schema
        code = f"""import React from 'react';
import {{ FormEngine }} from '@form-studio/form-engine';
import {{ submitForm }} from './api';
import {{ formSchema }} from './schema';

export function {component_name}() {{
  const handleSubmit = async (data: Record<string, any>) => {{
    console.log("Submitting form data:", JSON.stringify(data, null, 2));
    await submitForm(data);
  }};

  return (
    <FormEngine 
      schema={{formSchema as any}} 
      onSubmit={{handleSubmit}} 
    />
  );
}}
"""
        return code

    def _render_standard(self, sections, form_title=""):
        lines = []
        for s in sections:
            if s["title"] != "Default" and s["title"] != form_title:
                lines.append(f'        <DynBox as="h3">{{s["title"]}}</DynBox>')
            lines.append('        <DynBox display="grid" gridTemplateColumns="repeat(12, 1fr)" gap="md">')
            for f in s["fields"]:
                lines.append("  " + self._render_field(f))
            lines.append('        </DynBox>')
        return "\n".join(lines)

    def _render_stepper(self, sections):
        steps_data = []
        for i, s in enumerate(sections):
            fields_html = "\n".join([self._render_field(f) for f in s["fields"]])
            # Indent fields for better formatting
            indented_fields = fields_html.replace("\n", "\n  ")
            # StepItem requires an 'id'
            step_id = s.get("id", f"step-{i}")
            steps_data.append(f"""{{ 
            id: "{step_id}",
            title: "{s["title"]}", 
            content: (
              <DynBox display="grid" gridTemplateColumns="repeat(12, 1fr)" gap="md">
{indented_fields}
              </DynBox>
            ) 
          }}""")
        
        steps_str = ",\n".join(steps_data)
        
        return f"""        <DynStepper 
          steps={{{'[' + steps_str + ']'}}} 
          activeStep={{currentStep}} 
          onChange={{(_val, _step, index) => setCurrentStep(index)}} 
        />"""

    def _render_tabs(self, sections):
        tabs_data = []
        for s in sections:
            fields_html = "\n".join([self._render_field(f) for f in s["fields"]])
            indented_fields = fields_html.replace("\n", "\n  ")
            tabs_data.append(f"""{{ 
            label: "{s["title"]}", 
            content: (
              <DynBox padding="md">
                <DynBox display="grid" gridTemplateColumns="repeat(12, 1fr)" gap="md">
{indented_fields}
                </DynBox>
              </DynBox>
            ) 
          }}""")
        
        tabs_str = ",\n".join(tabs_data)
        
        return f"""        <DynResponsiveTabs 
          tabs={{{'[' + tabs_str + ']'}}} 
          defaultTab={{0}}
        />"""

    def _render_field(self, f):
        wrapper = f["wrapper"]
        wProps = f["wrapperProps"]
        field = f["field"]
        fProps = field["props"]
        visibility = f.get("visibility")
        
        field_props_list = [f'id="{field["id"]}"']
        for k, v in fProps.items():
            if k == "defaultValue" or v is None: continue
            if isinstance(v, bool) and v: field_props_list.append(k)
            elif isinstance(v, (int, float)): field_props_list.append(f"{k}={{{v}}}")
            elif isinstance(v, list):
                 import json
                 field_props_list.append(f"{k}={{{json.dumps(v, ensure_ascii=False)}}}")
            else: field_props_list.append(f'{k}="{v}"')
        
        field_props_list.append(f'value={{{field["id"]}}}')
        # Better camelCase for setter: set + ID with first letter capitalized
        setter_name = f"set{field['id'][0].upper()}{field['id'][1:]}"
        field_props_list.append(f'onChange={{(val: any) => {setter_name}(val)}}')

        if f.get("wrapperProps", {}).get("required"):
             field_props_list.append('required')

        field_str = f'<{field["component"]} {" ".join(field_props_list)} />'
        
        # Handle label, required, error state, helpText on wrapper
        wrapper_props_str = ""
        if wProps.get("label"): wrapper_props_str += f' label="{wProps["label"]}"'
        if wProps.get("required"): wrapper_props_str += ' required'
        if wProps.get("helpText"): wrapper_props_str += f' helpText="{wProps["helpText"]}"'

        rendered_field_raw = f"""<{wrapper} {wrapper_props_str}>
  {field_str}
</{wrapper}>"""

        col_span = wProps.get("colSpan", "full")
        
        rendered_field = f"""        <DynBox colSpan="{col_span}">
          {rendered_field_raw.replace(chr(10), chr(10) + '          ')}
        </DynBox>"""
        
        if visibility:
            depends_on = visibility.get("dependsOn")
            condition = visibility.get("condition", "equals")
            val = visibility.get("value")
            
            # Format value for JS comparison
            if isinstance(val, str):
                js_val = f"'{val}'"
            elif isinstance(val, bool):
                js_val = "true" if val else "false"
            else:
                js_val = str(val)
                
            cond_str = ""
            if condition == "equals": cond_str = f"{depends_on} === {js_val}"
            elif condition == "notEquals": cond_str = f"{depends_on} !== {js_val}"
            elif condition == "contains": cond_str = f"{depends_on}?.includes({js_val})"
            elif condition == "greaterThan": cond_str = f"{depends_on} > {js_val}"
            elif condition == "lessThan": cond_str = f"{depends_on} < {js_val}"
            else: cond_str = f"{depends_on} === {js_val}"
            
            # Wrap in JS conditional render
            return f"        {{{cond_str} && (\n{rendered_field}\n        )}}"
            
        return rendered_field

    def _generate_render_helpers(self):
        # We can add more specific TSX helpers here if needed
        return ""

    def generate_api_code(self, mapped_data: Dict[str, Any]) -> str:
        """Generates api.ts for the form's data fetching and submission."""
        return """export async function submitForm(payload: any) {
  // Simulacija slanja na backend
  console.log("Submitting payload to backend:", payload);
  await new Promise(resolve => setTimeout(resolve, 800));
  return { success: true, message: "Forma je uspešno procesuirana" };
}

export async function fetchLookupData(lookupRef: string, params?: any) {
  console.log(`Fetching dynamic lookup: ${lookupRef}`, params);
  // Ovde bi išao stvarni API poziv
  return [];
}
"""

    def generate_calculations_code(self, mapped_data: Dict[str, Any]) -> str:
        """Generates calculations.ts for business logic operations."""
        return """/**
 * Business logic i kalkulacije koje se izvršavaju pre slanja.
 */
export function applyBusinessLogic(data: any) {
  const result = { ...data };
  
  // Automatsko čišćenje nepotrebnih polja ili kalkulacije (npr. zbir premije)
  
  return result;
}
"""

    def generate_schema_code(self, data: Dict[str, Any]) -> str:
        """Generates schema.ts exporting the original template JSON for FormEngine."""
        import json
        
        # Construct a perfectly formatted FormSchema object by combining 
        # original field data with the layout span chosen by the AI Architect.
        form_schema = {
            "formId": data.get("metadata", {}).get("formId", "generated-form"),
            "metadata": data.get("metadata", {}),
            "logic": data.get("originalTemplate", {}).get("logic"),
            "sections": []
        }
        
        sections = data.get("sections", [])
        for i, section in enumerate(sections):
            schema_section = {
                "id": f"section-{i}",
                "title": section.get("title", ""),
                "fields": []
            }
            
            for f in section.get("fields", []):
                # Get the raw field data
                raw_field = f.get("originalData", {})
                
                # Copy it so we can inject layout
                field_def = dict(raw_field)
                
                # Inject layout span from the AI Architect's decision
                col_span = f.get("wrapperProps", {}).get("colSpan", "full")
                field_def["layout"] = { "span": col_span }
                
                # Migrate validation props to validation object so engine picks them up
                valid_keys = ["required", "pattern", "min", "max", "minLength", "maxLength", "errorMessage", "custom"]
                validation_obj = field_def.get("validation") or {}
                moved = False
                for k in valid_keys:
                    if k in field_def and field_def[k] is not None:
                        validation_obj[k] = field_def.pop(k)
                        moved = True
                
                if moved or validation_obj:
                    field_def["validation"] = validation_obj
                
                schema_section["fields"].append(field_def)
                
            form_schema["sections"].append(schema_section)
            
        # Serialize to formatted JSON string
        json_str = json.dumps(form_schema, indent=2, ensure_ascii=False)
        
        return f"""/**
 * Automatski generisana šema iz Form Studia.
 * Ovu šemu koristi interno @form-studio/form-engine za dinamičko renderovanje.
 */
export const formSchema = {json_str} as any;
"""

