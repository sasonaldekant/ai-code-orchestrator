import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class CodeGenerator:
    """
    Generates React/TSX code and Business Logic layers from mapped DynUI structures.
    """

    def generate_component_code(self, mapped_data: Dict[str, Any]) -> str:
        """Generates the React component code with complex layout support."""
        metadata = mapped_data.get("metadata", {})
        component_name = "Form"
        sections = mapped_data.get("sections", [])
        actions = mapped_data.get("mappedActions", [])
        layout = mapped_data.get("layout", "standard")

        # Collect necessary imports
        dynui_imports = {"DynBox", "DynFlex"}
        for s in sections:
            for f in s["fields"]:
                dynui_imports.add(f["wrapper"])
                dynui_imports.add(f["field"]["component"])
        for a in actions:
            dynui_imports.add(a["component"])

        # Layout specific imports
        if layout == "stepper": dynui_imports.add("DynStepper")
        if layout == "tabs": dynui_imports.add("DynResponsiveTabs")
        if layout == "accordion": dynui_imports.add("DynAccordion")

        imports_str = f"import {{ {', '.join(sorted(list(dynui_imports)))} }} from '@dyn-ui/react';"
        
        # Generate state hooks (flatten all fields)
        state_lines = []
        all_field_ids = []
        for s in sections:
            for f in s["fields"]:
                field_id = f["field"]["id"]
                all_field_ids.append(field_id)
                default_val = f["field"]["props"].get("defaultValue", "")
                if default_val is None:
                    default_val = "''"
                elif isinstance(default_val, str) and not default_val.startswith("'"):
                    default_val = f"'{default_val}'"
                elif isinstance(default_val, bool):
                    default_val = "true" if default_val else "false"
                state_lines.append(f"  const [{field_id}, set{field_id.capitalize()}] = useState({default_val});")

        if layout == "stepper":
            state_lines.append("  const [currentStep, setCurrentStep] = useState(0);")

        # Layout selection logic helpers
        render_content = ""
        
        form_title = metadata.get('title', 'Form')
        if layout == "standard":
            render_content = self._render_standard(sections, form_title)
        elif layout == "stepper":
            render_content = self._render_stepper(sections)
        elif layout == "tabs":
            render_content = self._render_tabs(sections)
        else:
            render_content = self._render_standard(sections, form_title)

        # Generate actions
        action_render_lines = []
        for a in actions:
            aProps = a["props"]
            props_str = f'label="{aProps["label"]}" color="{aProps["color"]}" type="{aProps["type"]}"'
            action_render_lines.append(f'          <{a["component"]} {props_str} />')

        # Combine into full component
        code = f"""import React, {{ useState }} from 'react';
{imports_str}
import {{ submitForm }} from './api';

export function {component_name}() {{
{chr(10).join(state_lines)}

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {{
    e.preventDefault();
    if (!e.currentTarget.checkValidity()) {{
      return;
    }}
    
    const payload = {{ {", ".join(all_field_ids)} }};
    console.log("Submitting form data:", JSON.stringify(payload, null, 2));
    await submitForm(payload);
  }};

  return (
    <form onSubmit={{handleSubmit}} noValidate={{false}}>
      <DynBox as="div" style={{{{ display: 'flex', flexDirection: 'column', gap: 'var(--dyn-spacing-md)' }}}}>
        <DynBox as="h2" style={{{{ marginBottom: 'var(--dyn-spacing-sm)' }}}}>{metadata.get('title', 'Form')}</DynBox>
        
{render_content}

        <DynFlex direction="row" gap="sm" style={{{{ marginTop: 'var(--dyn-spacing-md)' }}}}>
{chr(10).join(action_render_lines)}
        </DynFlex>
      </DynBox>
    </form>
  );
}}

{self._generate_render_helpers()}
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
            steps_data.append(f'{{ title: "{s["title"]}", content: (<DynBox display="grid" gridTemplateColumns="repeat(12, 1fr)" gap="md">{fields_html.replace("<", "    <")}</DynBox>) }}')
        
        return f"""        <DynStepper 
          steps={{{'[' + ', '.join(steps_data) + ']'}}} 
          currentStep={{currentStep}} 
          onChange={{setCurrentStep}} 
        />"""

    def _render_tabs(self, sections):
        tabs_data = []
        for s in sections:
            fields_html = "\n".join([self._render_field(f) for f in s["fields"]])
            tabs_data.append(f'{{ label: "{s["title"]}", content: (<DynBox padding="md"><DynBox display="grid" gridTemplateColumns="repeat(12, 1fr)" gap="md">{fields_html.replace("<", "    <")}</DynBox></DynBox>) }}')
        
        return f"""        <DynResponsiveTabs 
          tabs={{{'[' + ', '.join(tabs_data) + ']'}}} 
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
        field_props_list.append(f'onChange={{(val: any) => set{field["id"].capitalize()}(val)}}')

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
        """Generates schema.ts with real Zod validation based on fields."""
        # data might be the whole template or the mapped_data dict which contains 'originalTemplate'
        template = data.get("originalTemplate") or data
        
        # Detect format
        sections = template.get("sections") or []
        form_fields = (template.get("form") or {}).get("fields") or []
        
        all_fields = list(form_fields)
        for s in sections:
            all_fields.extend(s.get("fields", []))
            
        zod_props = []
        for f in all_fields:
            fid = f.get("id")
            if not fid: continue
            
            ftype = f.get("type", "text")
            required = f.get("required", False) or (f.get("validation") or {}).get("required", False)
            
            # Map to Zod type
            if ftype in ("number", "integer"):
                z_line = f'  {fid}: z.number()'
            elif ftype in ("checkbox", "switch"):
                z_line = f'  {fid}: z.boolean()'
            else:
                z_line = f'  {fid}: z.string()'
                
            if not required:
                z_line += ".optional()"
            
            zod_props.append(z_line + ",")

        props_str = "\n".join(zod_props)
        
        return f"""import {{ z }} from 'zod';

/**
 * Automatski generisana Zod shema na osnovu Form Studio šablona.
 */
export const formSchema = z.object({{
{props_str}
}});

export type FormData = z.infer<typeof formSchema>;
"""

