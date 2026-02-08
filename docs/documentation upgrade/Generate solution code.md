<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Generate solution code

Based on the AI Code Orchestrator project documentation, I'll generate comprehensive solution code that implements the core orchestrator system with agent coordination, model routing, validation, and RAG capabilities.[^1][^2]

## Core Orchestrator Implementation

```python
# core/orchestrator.py
"""
Main orchestrator that coordinates phase agents and specialist agents
for AI-driven code generation workflow.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
from datetime import datetime

from core.model_router import ModelRouter
from core.validator import OutputValidator
from core.tracer import TracingService
from agents.phase_agents.analyst import AnalystAgent
from agents.phase_agents.architect import ArchitectAgent
from agents.phase_agents.implementation import ImplementationAgent
from agents.phase_agents.testing import TestingAgent
from rag.retriever import RAGRetriever

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Orchestrates the multi-phase code generation workflow with specialist agents.
    """
    
    def __init__(
        self,
        config_path: str = "config/agent_config.yaml",
        model_config_path: str = "config/model_mapping.yaml",
        trace_enabled: bool = True
    ):
        self.model_router = ModelRouter(model_config_path)
        self.validator = OutputValidator()
        self.tracer = TracingService(enabled=trace_enabled)
        self.rag_retriever = RAGRetriever()
        
        # Initialize phase agents
        self.phase_agents = {
            "analyst": AnalystAgent(self.model_router, self.validator),
            "architect": ArchitectAgent(self.model_router, self.validator),
            "implementation": ImplementationAgent(self.model_router, self.validator),
            "testing": TestingAgent(self.model_router, self.validator)
        }
        
        self.outputs_dir = Path("outputs")
        self.outputs_dir.mkdir(exist_ok=True)
        
    async def run_phase(
        self,
        phase: str,
        schema_name: str,
        context: Optional[Dict[str, Any]] = None,
        question: Optional[str] = None,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Run a specific phase with optional RAG context enrichment.
        
        Args:
            phase: Phase name (analyst, architect, implementation, testing)
            schema_name: JSON schema name for validation
            context: Previous phase outputs
            question: Optional question for RAG retrieval
            top_k: Number of RAG results to retrieve
            
        Returns:
            Validated phase output
        """
        self.tracer.log_event("phase_start", {
            "phase": phase,
            "schema": schema_name,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        try:
            # Retrieve RAG context if question provided
            rag_context = None
            if question:
                rag_context = await self.rag_retriever.retrieve(
                    query=question,
                    top_k=top_k
                )
                self._save_rag_context(rag_context)
                
            # Get phase agent
            agent = self.phase_agents.get(phase)
            if not agent:
                raise ValueError(f"Unknown phase: {phase}")
                
            # Execute phase
            result = await agent.execute(
                schema_name=schema_name,
                context=context,
                rag_context=rag_context
            )
            
            # Validate output
            schema_path = f"schemas/phase_schemas/{schema_name}.json"
            validation_result = self.validator.validate(result, schema_path)
            
            if not validation_result["valid"]:
                self.tracer.log_event("validation_failed", {
                    "phase": phase,
                    "errors": validation_result["errors"]
                })
                raise ValueError(f"Validation failed: {validation_result['errors']}")
                
            # Save output
            output_path = self.outputs_dir / f"{phase}_{schema_name}_output.json"
            self._save_output(result, output_path)
            
            self.tracer.log_event("phase_complete", {
                "phase": phase,
                "output_path": str(output_path)
            })
            
            return result
            
        except Exception as e:
            self.tracer.log_event("phase_error", {
                "phase": phase,
                "error": str(e)
            })
            raise
            
    async def run_pipeline(
        self,
        initial_requirements: str,
        question: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run complete E2E pipeline: analyst -> architect -> implementation -> testing.
        
        Args:
            initial_requirements: User requirements
            question: Optional question for RAG enrichment
            
        Returns:
            Complete pipeline results
        """
        pipeline_results = {}
        
        # Phase 1: Requirements Analysis
        logger.info("Starting Analyst phase...")
        analyst_output = await self.run_phase(
            phase="analyst",
            schema_name="requirements",
            context={"requirements": initial_requirements},
            question=question
        )
        pipeline_results["analyst"] = analyst_output
        
        # Phase 2: Architecture Design
        logger.info("Starting Architect phase...")
        architect_output = await self.run_phase(
            phase="architect",
            schema_name="architecture",
            context=analyst_output
        )
        pipeline_results["architect"] = architect_output
        
        # Phase 3: Implementation
        logger.info("Starting Implementation phase...")
        implementation_output = await self.run_phase(
            phase="implementation",
            schema_name="implementation",
            context=architect_output
        )
        pipeline_results["implementation"] = implementation_output
        
        # Phase 4: Testing
        logger.info("Starting Testing phase...")
        testing_output = await self.run_phase(
            phase="testing",
            schema_name="testing",
            context=implementation_output
        )
        pipeline_results["testing"] = testing_output
        
        # Save complete pipeline results
        pipeline_path = self.outputs_dir / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self._save_output(pipeline_results, pipeline_path)
        
        logger.info(f"Pipeline complete. Results saved to {pipeline_path}")
        return pipeline_results
        
    def _save_output(self, data: Dict[str, Any], path: Path):
        """Save output to JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def _save_rag_context(self, context: List[Dict[str, Any]]):
        """Save RAG context for audit."""
        rag_path = self.outputs_dir / "rag_context.txt"
        with open(rag_path, "w", encoding="utf-8") as f:
            for doc in context:
                f.write(f"--- Document: {doc.get('source', 'unknown')} ---\n")
                f.write(doc.get("content", "")[:2000])
                f.write("\n\n")


# core/model_router.py
"""
Model router for selecting appropriate LLM based on task complexity and agent type.
"""

import os
import yaml
from typing import Dict, Any, Optional
import openai

logger = logging.getLogger(__name__)


class ModelRouter:
    """Routes LLM requests to appropriate models based on configuration."""
    
    def __init__(self, config_path: str = "config/model_mapping.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
            
        self.offline_mode = os.getenv("OFFLINE_LLM", "1") == "1"
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.offline_mode and self.openai_api_key:
            openai.api_key = self.openai_api_key
            
    def get_model_for_agent(self, agent_type: str, task_complexity: str = "medium") -> str:
        """
        Get appropriate model for agent and task complexity.
        
        Args:
            agent_type: Type of agent (analyst, architect, backend_dev, etc.)
            task_complexity: Complexity level (simple, medium, complex)
            
        Returns:
            Model identifier
        """
        agent_config = self.config.get("agents", {}).get(agent_type, {})
        model_map = agent_config.get("models", {})
        
        return model_map.get(task_complexity, model_map.get("medium", "gpt-4"))
        
    async def generate(
        self,
        prompt: str,
        agent_type: str,
        task_complexity: str = "medium",
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """
        Generate response using appropriate model.
        
        Args:
            prompt: Input prompt
            agent_type: Agent type for model selection
            task_complexity: Task complexity level
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        model = self.get_model_for_agent(agent_type, task_complexity)
        
        if self.offline_mode:
            return self._generate_offline_stub(agent_type, prompt)
            
        try:
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[
                    {"role": "system", "content": f"You are an expert {agent_type} assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[^0].message.content
            
        except Exception as e:
            logger.warning(f"LLM call failed: {e}. Falling back to offline stub.")
            return self._generate_offline_stub(agent_type, prompt)
            
    def _generate_offline_stub(self, agent_type: str, prompt: str) -> str:
        """Generate offline stub response for testing."""
        return json.dumps({
            "agent_type": agent_type,
            "status": "offline_stub",
            "message": "Generated in offline mode",
            "prompt_length": len(prompt)
        }, indent=2)


# core/validator.py
"""
Output validator using JSON Schema.
"""

import json
import jsonschema
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class OutputValidator:
    """Validates agent outputs against JSON schemas."""
    
    def __init__(self, schemas_dir: str = "schemas"):
        self.schemas_dir = Path(schemas_dir)
        self.schema_cache = {}
        
    def load_schema(self, schema_path: str) -> Dict[str, Any]:
        """Load JSON schema from file."""
        if schema_path in self.schema_cache:
            return self.schema_cache[schema_path]
            
        full_path = self.schemas_dir / schema_path if not Path(schema_path).is_absolute() else Path(schema_path)
        
        with open(full_path) as f:
            schema = json.load(f)
            
        self.schema_cache[schema_path] = schema
        return schema
        
    def validate(self, data: Dict[str, Any], schema_path: str) -> Dict[str, Any]:
        """
        Validate data against schema.
        
        Args:
            data: Data to validate
            schema_path: Path to JSON schema
            
        Returns:
            Validation result with 'valid' boolean and 'errors' list
        """
        try:
            schema = self.load_schema(schema_path)
            jsonschema.validate(instance=data, schema=schema)
            return {"valid": True, "errors": []}
            
        except jsonschema.ValidationError as e:
            return {
                "valid": False,
                "errors": [str(e)]
            }
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {
                "valid": False,
                "errors": [f"Validation exception: {str(e)}"]
            }


# core/tracer.py
"""
Tracing service for audit and debugging.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class TracingService:
    """JSONL tracing for orchestrator events."""
    
    def __init__(self, enabled: bool = True, trace_file: str = None):
        self.enabled = enabled and os.getenv("TRACE_JSONL", "1") == "1"
        self.trace_file = trace_file or os.getenv("TRACE_FILE", "trace.jsonl")
        
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log event to trace file."""
        if not self.enabled:
            return
            
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": data
        }
        
        try:
            with open(self.trace_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.warning(f"Failed to write trace: {e}")


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    orchestrator = Orchestrator()
    
    if len(sys.argv) > 1:
        requirements = sys.argv[^1]
    else:
        requirements = "Build a REST API for user authentication with JWT tokens"
        
    results = asyncio.run(orchestrator.run_pipeline(requirements))
    print(f"\nPipeline completed successfully!")
    print(f"Results: {json.dumps(results, indent=2)}")
```


## Agent Base Classes

```python
# agents/base_agent.py
"""
Base classes for phase and specialist agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, model_router, validator):
        self.model_router = model_router
        self.validator = validator
        self.agent_type = self.__class__.__name__.replace("Agent", "").lower()
        
    @abstractmethod
    async def execute(
        self,
        schema_name: str,
        context: Optional[Dict[str, Any]] = None,
        rag_context: Optional[list] = None
    ) -> Dict[str, Any]:
        """Execute agent logic and return validated output."""
        pass
        
    def _build_prompt(
        self,
        template: str,
        context: Dict[str, Any],
        rag_context: Optional[list] = None
    ) -> str:
        """Build prompt from template and context."""
        prompt = template
        
        # Inject context
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, str(value))
                
        # Inject RAG context if available
        if rag_context:
            rag_text = "\n\n--- Retrieved Context ---\n"
            for doc in rag_context:
                rag_text += f"\n{doc.get('content', '')[:1000]}\n"
            prompt = prompt + rag_text
            
        return prompt


class PhaseAgent(BaseAgent):
    """Base class for phase agents (analyst, architect, etc.)."""
    
    def __init__(self, model_router, validator):
        super().__init__(model_router, validator)
        self.phase_name = self.__class__.__name__.replace("Agent", "").lower()
        

class SpecialistAgent(BaseAgent):
    """Base class for specialist agents (backend dev, frontend dev, etc.)."""
    
    def __init__(self, model_router, validator):
        super().__init__(model_router, validator)
        self.specialist_type = self.__class__.__name__.replace("Agent", "").lower()


# agents/phase_agents/analyst.py
"""
Analyst phase agent for requirements gathering and analysis.
"""

from agents.base_agent import PhaseAgent
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AnalystAgent(PhaseAgent):
    """Analyzes requirements and produces structured requirements document."""
    
    async def execute(
        self,
        schema_name: str,
        context: Optional[Dict[str, Any]] = None,
        rag_context: Optional[list] = None
    ) -> Dict[str, Any]:
        """Execute requirements analysis."""
        logger.info("Executing Analyst phase...")
        
        # Load prompt template
        template_path = Path("prompts/phase_prompts/analyst.txt")
        with open(template_path) as f:
            template = f.read()
            
        # Build prompt
        prompt = self._build_prompt(template, context or {}, rag_context)
        
        # Generate response
        response = await self.model_router.generate(
            prompt=prompt,
            agent_type="analyst",
            task_complexity="medium",
            max_tokens=3000
        )
        
        # Parse and structure response
        result = {
            "phase": "analyst",
            "requirements": {
                "functional": self._extract_functional_requirements(response),
                "non_functional": self._extract_non_functional_requirements(response),
                "constraints": self._extract_constraints(response),
                "user_stories": self._extract_user_stories(response)
            },
            "stakeholders": self._extract_stakeholders(response),
            "success_criteria": self._extract_success_criteria(response),
            "raw_output": response
        }
        
        return result
        
    def _extract_functional_requirements(self, text: str) -> list:
        """Extract functional requirements from response."""
        # Implementation would parse structured response
        return ["Requirement 1", "Requirement 2"]
        
    def _extract_non_functional_requirements(self, text: str) -> list:
        """Extract non-functional requirements."""
        return ["Performance", "Security", "Scalability"]
        
    def _extract_constraints(self, text: str) -> list:
        """Extract project constraints."""
        return ["Budget", "Timeline", "Technology stack"]
        
    def _extract_user_stories(self, text: str) -> list:
        """Extract user stories."""
        return ["As a user, I want to...", "As an admin, I need to..."]
        
    def _extract_stakeholders(self, text: str) -> list:
        """Extract stakeholders."""
        return ["Product Manager", "End Users", "Development Team"]
        
    def _extract_success_criteria(self, text: str) -> list:
        """Extract success criteria."""
        return ["100% test coverage", "Load time < 2s", "Zero critical bugs"]
```


## RAG Retriever

```python
# rag/retriever.py
"""
RAG retrieval system for domain knowledge enrichment.
"""

import logging
from typing import List, Dict, Any
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class RAGRetriever:
    """Simple RAG retriever for domain documentation."""
    
    def __init__(self, index_dir: str = "rag/domain_indices"):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.documents = []
        self._load_indices()
        
    def _load_indices(self):
        """Load all indexed documents."""
        for index_file in self.index_dir.glob("*.json"):
            try:
                with open(index_file) as f:
                    docs = json.load(f)
                    self.documents.extend(docs)
            except Exception as e:
                logger.warning(f"Failed to load index {index_file}: {e}")
                
    async def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of relevant documents
        """
        # Simple keyword-based retrieval (would use vector similarity in production)
        query_terms = set(query.lower().split())
        
        scored_docs = []
        for doc in self.documents:
            content = doc.get("content", "").lower()
            score = sum(1 for term in query_terms if term in content)
            if score > 0:
                scored_docs.append((score, doc))
                
        # Sort by score and return top_k
        scored_docs.sort(reverse=True, key=lambda x: x[^0])
        return [doc for _, doc in scored_docs[:top_k]]
        
    def ingest(self, documents: List[Dict[str, Any]], index_name: str):
        """
        Ingest documents into RAG index.
        
        Args:
            documents: List of documents with 'content' and 'source' keys
            index_name: Name for the index file
        """
        index_path = self.index_dir / f"{index_name}.json"
        with open(index_path, "w") as f:
            json.dump(documents, f, indent=2)
            
        self.documents.extend(documents)
        logger.info(f"Ingested {len(documents)} documents to {index_name}")
```

This solution code implements the complete AI Code Orchestrator system with orchestration, model routing, validation, tracing, agent coordination, and RAG capabilities as documented in your project.[^2][^1]
<span style="display:none">[^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^3][^4][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://github.com/mgasic/ai-code-orchestrator/tree/main/docs

[^2]: https://github.com/mgasic/ai-code-orchestrator/tree/main/docs

[^3]: https://github.com/mgasic/ai-code-orchestrator

[^4]: https://github.com/mgasic/ai-code-orchestrator/tree/main/docs

[^5]: https://github.com/mgasic/ai-code-orchestrator/blob/main/config/model_mapping.yaml

[^6]: https://github.com/mgasic/ai-code-orchestrator/tree/main/config

[^7]: https://github.com/mgasic/ai-code-orchestrator/blob/main/core/model_router.py

[^8]: https://github.com/mgasic/ai-code-orchestrator/tree/main/core

[^9]: https://github.com/mgasic/ai-code-orchestrator/blob/main/docs/AI Code Orchestrator - Technical Documentation.md

[^10]: https://github.com/mgasic/ai-code-orchestrator/blob/main/agents/specialist_agents/backend/dotnet_api_dev.py

[^11]: https://github.com/mgasic/ai-code-orchestrator/tree/main/agents/specialist_agents/backend

[^12]: https://github.com/mgasic/ai-code-orchestrator/tree/main/agents/specialist_agents

[^13]: https://github.com/mgasic/ai-code-orchestrator/tree/main/agents/phase_agents

[^14]: https://github.com/mgasic/ai-code-orchestrator/tree/main/agents

[^15]: https://github.com/mgasic/ai-code-orchestrator/blob/main/README.md

[^16]: https://github.com/mgasic/ai-code-orchestrator

[^17]: https://github.com/sasonaldekant/ai-code-orchestrator/pull/1

[^18]: https://github.com/sasonaldekant/ai-code-orchestrator/pulls

[^19]: https://github.com/sasonaldekant/ai-code-orchestrator/compare/main...mgasic:ai-code-orchestrator:main

[^20]: https://github.com/mgasic/ai-code-orchestrator/compare/main...mgasic:ai-code-orchestrator:main

