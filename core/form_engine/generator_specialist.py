import logging
import json
from typing import Dict, Any, List
from core.llm_client_v2 import LLMClientV2
from core.cost_manager import CostManager
from rag.domain_aware_retriever import DomainAwareRetriever

logger = logging.getLogger(__name__)

class FormGeneratorSpecialist:
    """
    Converts natural language descriptions into DynUI Form Templates (JSON).
    """
    
    def __init__(self, llm_client: LLMClientV2 = None, cost_manager: CostManager = None, retriever: DomainAwareRetriever = None):
        if not llm_client:
            cm = cost_manager or CostManager()
            self.llm_client = LLMClientV2(cm)
        else:
            self.llm_client = llm_client
        self.retriever = retriever or DomainAwareRetriever()
            
    async def generate_template(self, user_request: str) -> Dict[str, Any]:
        """
        Generates a JSON form template based on user natural language request using RAG.
        """
        # 1. RAG Search for components
        logger.info(f"Retrieving DynUI context for: {user_request}")
        docs = self.retriever.retrieve_tier(3, user_request, top_k=5)
        context = "\n".join([f"Source: {d['source']}\n{d['content']}" for d in docs])

        system_prompt = f"""
        You are a DynUI Template Generator. Your task is to output a VALID JSON following the DynUI Form Template Schema.
        
        Available DynUI Context (Tier 3):
        {context}

        Rules:
        1. Only use these types: text, email, password, select, checkbox, textarea, date, number.
        2. 'select' type MUST have 'options' array.
        3. 'id' must be camelCase and unique.
        4. include 'actions' with at least a submit button.
        
        Output format: STRICT JSON ONLY.
        """
        
        user_prompt = f"Create a form template for: {user_request}"
        
        response = await self.llm_client.complete(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="gpt-4o",
            json_mode=True
        )
        
        try:
            template = json.loads(response.content)
            return template
        except Exception as e:
            logger.error(f"Failed to parse generated template: {e}")
            raise

    async def generate_from_data(self, data_sample: Dict[str, Any]) -> Dict[str, Any]:
        """
        Infers a form template based on a provided JSON data sample using an LLM.
        """
        data_str = json.dumps(data_sample, indent=2)
        logger.info("Inferring form template from data sample...")

        system_prompt = """
        You are a DynUI Template Architect. Your task is to analyze a JSON data sample and generate a corresponding DynUI Form Template that would be used to create/edit such data.
        
        Guidelines:
        1. Field 'id' MUST exactly match the key in the JSON object.
        2. Field 'label' should be a localized, human-friendly title (e.g., "firstName" -> "First Name").
        3. Infer the best DynUI type:
           - String -> 'text' (or 'email', 'date', 'textarea' if value suggests it)
           - Number -> 'number'
           - Boolean -> 'checkbox'
           - Array/Enum -> 'select' (extract options from value if possible)
        4. Always include a 'submit' action.
        
        Output format: STRICT JSON ONLY following DynUI schema.
        """
        
        user_prompt = f"Analyze this data sample and create a form template:\n{data_str}"
        
        response = await self.llm_client.complete(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="gpt-4o",
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except Exception as e:
            logger.error(f"Failed to infer template from data: {e}")
            raise
