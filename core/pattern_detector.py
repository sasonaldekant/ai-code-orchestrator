"""
Pattern Detector for AI Code Orchestrator v3.0

This module analyzes error logs to identify recurring issues
and generates prevention rules.
"""

from __future__ import annotations

import logging
import json
import re
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from collections import Counter
from pathlib import Path

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler
    HAS_ML_DEPS = True
except ImportError:
    HAS_ML_DEPS = False

logger = logging.getLogger(__name__)

@dataclass
class ErrorPattern:
    """A detected pattern of recurring errors."""
    id: str
    description: str
    frequency: int
    examples: List[str]
    category: str = "generic"
    suggested_fix: Optional[str] = None
    confidence: float = 0.0

class PatternDetector:
    """
    Detects patterns in error logs using clustering and heuristic analysis.
    """
    
    def __init__(self, use_ml: bool = True):
        self.known_patterns = {}
        self.use_ml = use_ml and HAS_ML_DEPS
        self.encoder = None
        if self.use_ml:
            try:
                # Use a lightweight model for speed
                self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("PatternDetector initialized with ML support.")
            except Exception as e:
                logger.warning(f"Failed to load sentence-transformer: {e}")
                self.use_ml = False

        # Pre-load some known anti-patterns (regex based)
        self.regex_patterns = {
            "missing_import": r"NameError: name '(\w+)' is not defined",
            "syntax_error": r"SyntaxError: invalid syntax",
            "attribute_error": r"AttributeError: '(\w+)' object has no attribute '(\w+)'",
            "type_error": r"TypeError: (.*)",
            "broad_exception": r"Broad exception catch found", # From static analysis
        }

    def analyze_errors(self, error_logs: List[Dict[str, Any]]) -> List[ErrorPattern]:
        """
        Analyze a list of error logs to find patterns.
        """
        if not error_logs:
            return []

        patterns = []
        
        # 1. Heuristic/Regex Clustering
        heuristic_patterns = self._heuristic_analysis(error_logs)
        patterns.extend(heuristic_patterns)
        
        # 2. ML Semantic Clustering (if enabled)
        if self.use_ml and len(error_logs) >= 3:
            try:
                semantic_patterns = self._semantic_analysis(error_logs)
                patterns.extend(semantic_patterns)
            except Exception as e:
                logger.error(f"Semantic analysis failed: {e}")
                
        return patterns

    def _heuristic_analysis(self, error_logs: List[Dict[str, Any]]) -> List[ErrorPattern]:
        cluster_counts = Counter()
        cluster_examples = {}
        
        for log in error_logs:
            msg = log.get("message", "")
            matched = False
            
            for p_name, p_regex in self.regex_patterns.items():
                match = re.search(p_regex, msg)
                if match:
                    key = p_name
                    if p_name == "missing_import":
                        key = f"missing_import:{match.group(1)}"
                    elif p_name == "attribute_error":
                        key = f"attribute_error:{match.group(2)}"
                        
                    cluster_counts[key] += 1
                    if key not in cluster_examples: cluster_examples[key] = []
                    if msg not in cluster_examples[key]: cluster_examples[key].append(msg)
                    matched = True
                    break
            
            if not matched:
                key = f"unknown:{msg[:30]}"
                cluster_counts[key] += 1
                if key not in cluster_examples: cluster_examples[key] = []
                if msg not in cluster_examples[key]: cluster_examples[key].append(msg)

        results = []
        for key, count in cluster_counts.items():
            if count >= 2:
                results.append(ErrorPattern(
                    id=f"pat_h_{abs(hash(key)) % 10000}",
                    description=f"Heuristic Pattern: {key}",
                    frequency=count,
                    examples=cluster_examples[key][:3],
                    category="heuristic",
                    confidence=0.7,
                    suggested_fix=self._suggest_fix(key)
                ))
        return results

    def _semantic_analysis(self, error_logs: List[Dict[str, Any]]) -> List[ErrorPattern]:
        messages = [log.get("message", "") for log in error_logs]
        embeddings = self.encoder.encode(messages)
        
        # Normalize and cluster
        X = StandardScaler().fit_transform(embeddings)
        # DBSCAN: eps controls cluster distance, min_samples is frequency threshold
        db = DBSCAN(eps=0.5, min_samples=2).fit(X)
        labels = db.labels_
        
        results = []
        unique_labels = set(labels)
        for label in unique_labels:
            if label == -1: continue # Noise
            
            cluster_indices = [i for i, l in enumerate(labels) if l == label]
            cluster_msgs = [messages[i] for i in cluster_indices]
            
            results.append(ErrorPattern(
                id=f"pat_s_{label}_{abs(hash(cluster_msgs[0])) % 1000}",
                description="Semantic pattern detected across similar error messages.",
                frequency=len(cluster_msgs),
                examples=list(set(cluster_msgs))[:3],
                category="semantic",
                confidence=0.85,
                suggested_fix="Review frequent semantic errors across modules."
            ))
        return results

    def _suggest_fix(self, pattern_key: str) -> str:
        if "missing_import" in pattern_key:
            module = pattern_key.split(":")[1] if ":" in pattern_key else "module"
            return f"Ensure '{module}' is imported in the affected file."
        if "syntax_error" in pattern_key:
            return "Run a linter to check for missing brackets or invalid syntax."
        if "broad_exception" in pattern_key:
            return "Use a specific exception type (e.g., ValueError) instead of bare 'except:'."
        return "Analyze the stack trace for deeper logic issues."
