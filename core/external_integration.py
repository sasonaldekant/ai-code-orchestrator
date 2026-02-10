
"""
Core logic for External AI Integration (Phase 14).
Handles prompt generation and response ingestion.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib

# Assuming these exist from previous phases
from rag.vector_store import Document, ChromaVectorStore
from core.graph.schema import KnowledgeGraph

logger = logging.getLogger(__name__)

class ExternalIntegration:
    def __init__(self, vector_store: Optional[ChromaVectorStore] = None):
        self.vector_store = vector_store

    def generate_prompt(self, 
                        query: str, 
                        context_files: List[Dict[str, str]], 
                        target_model: str = "generic") -> str:
        """
        Generates a sophisticated prompt for external Pro models.
        
        Args:
            query: The user's complex question/task.
            context_files: List of dicts {'path': str, 'content': str}.
            target_model: 'chatgpt_o1', 'perplexity', 'generic'.
        """
        
        prompt = ""
        
        # 1. Header & Role
        prompt += "# Role\n"
        prompt += "You are a Senior Principal Software Architect and Code Expert.\n"
        prompt += "You are assisting an AI Code Orchestrator system.\n\n"
        
        # 2. Context Dump
        prompt += "# Project Context\n"
        prompt += "The following files are relevant to the user request:\n\n"
        
        for file in context_files:
            prompt += f"--- START FILE: {file.get('path', 'unknown')} ---\n"
            prompt += f"{file.get('content', '')}\n"
            prompt += f"--- END FILE ---\n\n"
            
        # 3. Task Specifics
        prompt += "# User Request\n"
        prompt += f"{query}\n\n"
        
        # 4. Model-Specific Instructions
        prompt += "# Instructions\n"
        if target_model == "chatgpt_o1":
            prompt += "1. THINK STEP-BY-STEP. Analyze the architecture deeply.\n"
            prompt += "2. Provide a comprehensive solution.\n"
            prompt += "3. If suggesting code changes, provide FULL file content where possible or clean DIFFs.\n"
        elif target_model == "perplexity":
            prompt += "1. Research the latest libraries and patterns related to this stack.\n"
            prompt += "2. Cite specific GitHub issues or documentation versions.\n"
        else:
            prompt += "1. Provide a clear, actionable answer.\n"
            prompt += "2. Use markdown formatting.\n"
            
        return prompt

    def detect_task_complexity(self, query: str, context_files: List[Any]) -> Dict[str, Any]:
        """
        Analyzes the task to see if it qualifies for External Delegation.
        Returns a recommendation.
        """
        # 1. Estimate Tokens (Rough calc: 4 chars = 1 token)
        total_chars = len(query)
        for f in context_files:
            total_chars += len(f.get('content', ''))
            
        est_tokens = total_chars / 4
        
        recommendation = {
            "should_delegate": False,
            "reason": "Task is within local capacity.",
            "suggested_tool": None,
            "est_tokens": int(est_tokens)
        }
        
        # 2. Heuristics
        keywords_reasoning = ["architecture", "refactor", "design pattern", "security audit", "rewrite"]
        keywords_research = ["latest", "library", "comparison", "versus", "best practice", "error"]
        
        is_reasoning = any(k in query.lower() for k in keywords_reasoning)
        is_research = any(k in query.lower() for k in keywords_research)
        
        # Thresholds
        TRANSFORMER_LIMIT = 8000 # Configurable
        
        if est_tokens > TRANSFORMER_LIMIT:
             recommendation["should_delegate"] = True
             recommendation["reason"] = f"Context size ({int(est_tokens)} tokens) exceeds local limit."
             recommendation["suggested_tool"] = "chatgpt_plus" # Canvas is good for large context
             
        elif is_reasoning:
             recommendation["should_delegate"] = True
             recommendation["reason"] = "Task involves complex reasoning/architecture."
             recommendation["suggested_tool"] = "chatgpt_o1"
             
        elif is_research:
             recommendation["should_delegate"] = True
             recommendation["reason"] = "Task requires external knowledge/research."
             recommendation["suggested_tool"] = "perplexity"
             
        return recommendation

    def generate_search_plan(self, query: str, context_files: List[Any]) -> str:
        """
        [Hybrid Strategy]
        Asks an external Pro model to generate a search strategy for the local agent.
        """
        # 1. Build Meta-Prompt
        prompt = "# Role\n"
        prompt += "You are a Senior Principal Architect. You are guiding a junior 'Retrieval Agent' who has access to a codebase.\n"
        prompt += "The agent has these tools: `search_code(query)`, `read_file(path)`, `list_dir(path)`.\n\n"
        
        prompt += "# Context\n"
        prompt += f"User Query: {query}\n"
        prompt += "Attached Files Summary:\n"
        for f in context_files:
            prompt += f"- {f.get('path')}\n"
            
        prompt += "\n# Task\n"
        prompt += "Create a strict, step-by-step execution plan for the Retrieval Agent to answer the query.\n"
        prompt += "Do NOT answer the query yourself. Just tell the agent what to search/read.\n"
        prompt += "Format: Numbered list of actions.\n"
        
        return prompt

    def ingest_response(self, 
                        question: str, 
                        answer: str, 
                        source: str = "external_ai") -> str:
        """
        Ingest an external AI's answer into the 'external_knowledge' collection.
        Returns the ID of the new document.
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
            
        # Create a document
        timestamp = datetime.now().isoformat()
        
        # Hash content for ID
        content_hash = hashlib.md5((question + answer).encode()).hexdigest()
        
        text_content = f"Question: {question}\n\nAnswer (Source: {source}):\n{answer}"
        
        doc = Document(
            id=f"ext_{content_hash}",
            text=text_content,
            metadata={
                "type": "external_knowledge",
                "source": source,
                "timestamp": timestamp,
                "question": question[:100]
            }
        )
        
        self.vector_store.add_documents([doc])
        logger.info(f"Ingested external response: {doc.id}")
        
        return doc.id
