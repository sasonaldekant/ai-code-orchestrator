"""
Documentation Generator Agent
Specialist agent for generating technical documentation.
"""

from typing import Dict, Any, Optional
import logging
from dataclasses import dataclass

# Assuming a base agent class or similar interface exists, 
# but for specialist agents we often just use the LLM client directly.
# Let's check if there's a base agent.
# Using standalone class for now as per other specialist agents.

logger = logging.getLogger(__name__)

@dataclass
class DocArtifact:
    type: str # 'openapi', 'readme', 'comments'
    content: str
    format: str # 'yaml', 'json', 'markdown'

class DocGeneratorAgent:
    """
    Generates documentation for code and projects.
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    async def generate_api_docs(self, code: str, language: str = "python") -> DocArtifact:
        """
        Generate OpenAPI/Swagger specification for API code.
        """
        prompt = f"""
        Generate OpenAPI 3.0 specification (YAML) for the following {language} API code.
        Focus on endpoints, request/response schemas, and descriptions.
        
        Code:
        ```
        {code[:2000]}
        ```
        """
        
        response = await self.llm_client.complete(
            messages=[{"role": "user", "content": prompt}],
            model="doc_specialist"
        )
        
        content = response.content
        if "```yaml" in content:
            content = content.split("```yaml")[1].split("```")[0].strip()
            
        return DocArtifact(
            type="openapi",
            content=content,
            format="yaml"
        )

    async def generate_readme(self, project_name: str, description: str, features: list) -> DocArtifact:
        """
        Generate a professional README.md for a project.
        """
        features_list = "\n".join([f"- {f}" for f in features])
        prompt = f"""
        Generate a comprehensive README.md for:
        Project: {project_name}
        Description: {description}
        Features:
        {features_list}
        
        Include sections: Overview, Features, valid Badges, Installation, Usage, License.
        """
        
        response = await self.llm_client.complete(
            messages=[{"role": "user", "content": prompt}],
            model="doc_specialist"
        )
        
        content = response.content
        if "```markdown" in content:
             content = content.split("```markdown")[1].split("```")[0].strip()
        elif "```" in content: # Fallback
             content = content.split("```")[1].split("```")[0].strip()
             
        return DocArtifact(
            type="readme",
            content=content,
            format="markdown"
        )
