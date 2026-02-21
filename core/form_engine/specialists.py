import logging
import json
from typing import Dict, Any, List
from core.llm_client_v2 import LLMClientV2
from core.cost_manager import CostManager

logger = logging.getLogger(__name__)

class FormArchitectSpecialist:
    """
    Analyzes a JSON form template and decides on the best layout using an LLM.
    """
    
    def __init__(self, llm_client: LLMClientV2 = None, cost_manager: CostManager = None):
        if not llm_client:
            cm = cost_manager or CostManager()
            self.llm_client = LLMClientV2(cm)
        else:
            self.llm_client = llm_client
        
    async def analyze_form(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes the template and returns a layout decision.
        """
        form_fields = (template.get("form") or {}).get("fields") or []
        sections = template.get("sections") or []
        fields = list(form_fields)
        for sec in sections:
            fields.extend(sec.get("fields") or [])
            
        field_count = len(fields)
        
        system_prompt = """
        You are a DynUI Form Architect. Your goal is to analyze a JSON form definition and 
        decide which DynUI layout component is most suitable for the user experience, AND 
        assign grid column spans (`colSpan`) to each field using the semantic 12-column system.
        
        Guidelines:
        1. 'standard': Used for simple forms (< 6 fields).
        2. 'stepper': Used for complex processes or long forms (> 8 fields) that can be split into steps.
        3. 'tabs': Used for forms with unrelated categories of settings.
        
        Grid Spanning (`colSpan`):
        DynUI supports 'full' (12 cols), 'half' (6 cols), 'third' (4 cols), 'quarter' (3 cols).
        You must decide the most visually pleasing layout for fields. 
        CRITICAL RULES FOR GRID SPANNING:
        - NEVER default to 'full' width unless it is strictly necessary (e.g. textarea, long text fields like Address).
        - ALWAYS try to pack minimum 2-3 inputs per row (using 'half' or 'third').
        - Evaluate the type and validation constraints (maxLength):
            - If field is JMBG, PIB, Phone Number, ZIP code -> MUST BE 'third' or 'quarter' since they are short.
            - If fields are logically related (First Name, Last Name) -> MUST BE 'half'.
        
        You MUST return a JSON object sticking to this schema:
        {
          "recommendedLayout": "standard" | "stepper" | "tabs",
          "reasoning": "...",
          "complexity": "low|medium|high",
          "structure": [
             {
               "title": "Section Title",
               "fields": [
                 { "id": "field_id", "colSpan": "half" | "full" | "third" | "quarter" }
               ]
             }
          ]
        }
        """
        
        user_prompt = f"""
        Analyze this form template and assign colSpan values:
        Title: {(template.get('metadata') or {}).get('title')}
        Description: {(template.get('metadata') or {}).get('description')}
        Fields:
        {json.dumps([{"id": f.get("id"), "label": f.get("label"), "type": f.get("type"), "maxLength": f.get("maxLength") or (f.get("validation") or {}).get("maxLength")} for f in fields], indent=2)}
        """
        
        logger.info(f"Calling Architect AI for form analysis with {field_count} fields...")
        try:
            response = await self.llm_client.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="gpt-4o",
                json_mode=True
            )
            decision = json.loads(response.content)
            return decision
        except Exception as e:
            logger.error(f"Failed AI architect analysis, applying fallback: {e}")
            return {
                "recommendedLayout": "standard",
                "reasoning": "Fallback applied due to error.",
                "complexity": "low",
                "structure": [{"title": "General", "fields": [{"id": f["id"], "colSpan": "full"} for f in fields]}]
            }
