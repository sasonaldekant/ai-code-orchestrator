import json
import logging
from pathlib import Path
from typing import Dict, Any

from core.form_engine.mapper import DynUIMapper
from core.form_engine.project_generator import ProjectGenerator
from core.form_engine.code_generator import CodeGenerator
from core.form_engine.specialists import FormArchitectSpecialist
from core.form_engine.generator_specialist import FormGeneratorSpecialist
from core.form_engine.form_cache import FormProjectCache

logger = logging.getLogger(__name__)

class FormEngineOrchestrator:
    """
    Ties together mapping, project generation, and code generation.
    """
    
    def __init__(self):
        self.mapper = DynUIMapper()
        self.project_gen = ProjectGenerator()
        self.code_gen = CodeGenerator()
        self.architect = FormArchitectSpecialist()
        self.generator = FormGeneratorSpecialist()
        self.cache = FormProjectCache()
        
    async def generate_from_prompt(self, prompt: str, project_name: str) -> str:
        """Generates a project starting from a natural language prompt."""
        logger.info(f"Generating template from prompt: {prompt}")
        template = await self.generator.generate_template(prompt)
        
        # Save template for reference
        temp_path = Path(f"examples/form_templates/generated_{project_name}.json")
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
            
        return await self.generate_ui_project(str(temp_path), project_name)

    async def generate_from_data(self, data_sample: Dict[str, Any], project_name: str) -> str:
        """Generates a project starting from a JSON data sample."""
        logger.info(f"Generating template from data sample for: {project_name}")
        template = await self.generator.generate_from_data(data_sample)
        
        # Save template for reference
        temp_path = Path(f"examples/form_templates/data_inferred_{project_name}.json")
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
            
        return await self.generate_ui_project(str(temp_path), project_name)

    async def generate_ui_project(self, template_path: str, project_name: str, layout_override=None, layout_decision_input=None, enriched_instructions=None):
        """
        Full project generation from a template. Returns path to the new project.
        enriched_instructions: Optional string from Form Studio AI Chat with user-refined details.
        """
        logger.info(f"Starting generation for project: {project_name}")
        
        # Load Template with explicit UTF-8
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load template: {e}")
            raise
            
        # 0. Canonicalize Metadata (Fixing common LLM output variants)
        if "metadata" not in template:
            template["metadata"] = {}
        
        # Try to find title in various places
        title = template.get("metadata", {}).get("title")
        if not title:
            title = template.get("form", {}).get("title")
        if not title:
            title = project_name.replace("-", " ").title()
            
        template["metadata"]["title"] = title

        # CACHE LAYER 1: Compute Structural Fingerprint
        fingerprint = self.cache.compute_fingerprint(template)
        
        # 1. Analyze for Layout (or use provided decision from Preview)
        if layout_decision_input:
            layout_decision = layout_decision_input
        else:
            layout_decision = await self.architect.analyze_form(template)

        if layout_override:
            layout_decision["recommendedLayout"] = layout_override
            
        layout = layout_decision["recommendedLayout"]
        logger.info(f"Layout decision: {layout} ({layout_decision.get('complexity', 'unknown')})")

        # Log enriched instructions from Form Studio Chat
        if enriched_instructions:
            logger.info(f"Enriched instructions received from Form Studio Chat ({len(enriched_instructions)} chars)")

        # CACHE LAYER 2: Bypass cache for now to ensure we get newly generated code
        cached_variant = None

        if cached_variant:
            component_code = cached_variant["component_code"]
            api_code = cached_variant["api_code"]
            calc_code = cached_variant["calc_code"]
            schema_code = cached_variant["schema_code"]
            logger.info("Using cached variant successfully! (0 AI tokens used)")
            # In a full implementation, we might return a flag indicating a cache hit.
        else:
            # 2. Map to DynUI
            mapped_data = self.mapper.process_template(template, layout_decision)
            
            # Inject enriched instructions into mapped data for code generation
            if enriched_instructions:
                mapped_data["enriched_instructions"] = enriched_instructions
            
            # 3. Generate Code
            component_code = self.code_gen.generate_component_code(mapped_data)
            api_code = self.code_gen.generate_api_code(mapped_data)
            calc_code = self.code_gen.generate_calculations_code(mapped_data)
            schema_code = self.code_gen.generate_schema_code(mapped_data)
            
            # Save to Cache
            self.cache.store_cached_variant(fingerprint, layout, component_code, api_code, calc_code, schema_code)
        
        # 4. Create Project Files inside Monorepo
        project_dir = self.project_gen.generate_project_base(project_name)
        
        # Write Main Component
        comp_name = "Form"
        comp_path = project_dir / "src" / f"{comp_name}.tsx"
        comp_path.write_text(component_code, encoding="utf-8")
        
        # Write Business Logic Layers
        (project_dir / "src" / "api.ts").write_text(api_code, encoding="utf-8")
        (project_dir / "src" / "calculations.ts").write_text(calc_code, encoding="utf-8")
        (project_dir / "src" / "schema.ts").write_text(schema_code, encoding="utf-8")
        
        # Update App.tsx to import and show the form
        app_tsx = f"""import {{ {comp_name} }} from './{comp_name}';
import {{ ThemeProvider, DynContainer }} from '@dyn-ui/react';

export default function App() {{
  return (
    <ThemeProvider>
      <DynContainer maxWidth="800px" style={{{{ margin: '0 auto', paddingTop: 'var(--dyn-spacing-xl)' }}}}>
        <{comp_name} />
      </DynContainer>
    </ThemeProvider>
  );
}}
"""
        (project_dir / "src" / "App.tsx").write_text(app_tsx, encoding="utf-8")
        
        logger.info(f"Project {project_name} generated successfully at {project_dir}")
        return str(project_dir)

    async def verify_project(self, project_name: str) -> Dict[str, Any]:
        """Runs a build/tsc verification on the generated project."""
        import subprocess
        workspace_dir = Path("outputs") / "forms-workspace"
        
        logger.info(f"Verifying project {project_name}...")
        try:
            # Run turbo verify for just this project
            process = subprocess.run(
                ["pnpm", "turbo", "run", "verify", "--filter", project_name],
                cwd=str(workspace_dir),
                capture_output=True,
                text=True,
                shell=True
            )
            
            if process.returncode == 0:
                return {"success": True, "output": process.stdout}
            else:
                return {"success": False, "error": process.stderr or process.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}
