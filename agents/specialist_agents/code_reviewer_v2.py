"""
Code Reviewer V2 Agent
Specialist agent for enhanced code review with security and performance focus.
"""

from typing import List, Dict, Any
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ReviewIssue:
    type: str # 'security', 'performance', 'maintainability', 'bug'
    severity: str # 'critical', 'high', 'medium', 'low'
    line: int
    message: str
    suggestion: str

@dataclass
class ReviewReport:
    score: float
    summary: str
    issues: List[ReviewIssue]
    passed: bool

class CodeReviewerV2:
    """
    Enhanced code reviewer that checks against specific checklists.
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    async def review_code(self, code: str, context: str = "") -> ReviewReport:
        """
        Perform a comprehensive code review.
        """
        prompt = f"""
        Review the following code for Security, Performance, and Maintainability issues.
        
        Context: {context}
        
        Code:
        ```
        {code[:3000]}
        ```
        
        Return a JSON report with a score (0-1), summary, and list of issues.
        """
        
        response = await self.llm_client.complete(
            messages=[{"role": "user", "content": prompt}],
            model="reviewer_v2" # Specific model for routing in mock
        )
        
        # Parse response (Mock will return JSON string)
        import json
        try:
            data = json.loads(response.content)
            
            issues = []
            for i in data.get("issues", []):
                issues.append(ReviewIssue(
                    type=i.get("type", "maintainability"),
                    severity=i.get("severity", "medium"),
                    line=i.get("line", 0),
                    message=i.get("message", "Issue detected"),
                    suggestion=i.get("suggestion", "")
                ))
                
            return ReviewReport(
                score=data.get("score", 0.0),
                summary=data.get("summary", "Review complete"),
                issues=issues,
                passed=data.get("score", 0.0) > 0.8
            )
        except Exception as e:
            logger.error(f"Failed to parse review response: {e}")
            return ReviewReport(0.0, f"Error: {e}", [], False)
