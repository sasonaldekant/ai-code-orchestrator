"""
Cost management and budgeting.

This module tracks the number of tokens consumed by each large language model
call, converts the usage into a USD cost based on per‑model pricing and
enforces budget limits.  If a budget is exceeded, callers are expected to
respect the `should_continue` flag and halt further processing.

Pricing data is approximate and reflects public information as of 2026.  See
the documentation for more details.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class ModelPricing:
    """Stores per‑million token pricing for input and output tokens."""
    input: float
    output: float


class CostManager:
    """Tracks token usage and estimates costs with budget enforcement."""

    def __init__(
        self,
        per_task_budget: float = 0.50,
        per_hour_budget: float = 5.0,
        per_day_budget: float = 40.0,
    ) -> None:
        # pricing in USD per million tokens
        self.prices: Dict[str, ModelPricing] = {
            "gpt-4o": ModelPricing(input=2.50, output=10.0),
            "gpt-4o-mini": ModelPricing(input=0.15, output=0.60),
            "claude-3-5-sonnet": ModelPricing(input=3.00, output=15.0),
            "gemini-2.5-pro": ModelPricing(input=1.25, output=5.0),
        }
        # budgets
        self.per_task_budget = per_task_budget
        self.per_hour_budget = per_hour_budget
        self.per_day_budget = per_day_budget
        # running totals
        self.total_cost: float = 0.0
        self.task_cost: float = 0.0

    def estimate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        """Estimate the USD cost for a given token usage and model."""
        pricing = self.prices.get(model, self.prices.get("gpt-4o", ModelPricing(2.50, 10.0)))
        cost = (tokens_in / 1_000_000) * pricing.input + (tokens_out / 1_000_000) * pricing.output
        return cost

    def check_and_update(self, model: str, tokens_in: int, tokens_out: int) -> Tuple[bool, float]:
        """
        Update internal cost counters and return whether the call should proceed.

        Parameters
        ----------
        model : str
            Name of the model used.
        tokens_in : int
            Number of input tokens used.
        tokens_out : int
            Number of output tokens used.

        Returns
        -------
        Tuple[bool, float]
            (should_continue, cost_of_call)
        """
        cost = self.estimate_cost(model, tokens_in, tokens_out)
        self.total_cost += cost
        self.task_cost += cost
        # budget enforcement
        if self.task_cost > self.per_task_budget or self.total_cost > self.per_day_budget:
            logger.warning(
                f"Budget exceeded: task {self.task_cost:.2f} / {self.per_task_budget}, total {self.total_cost:.2f} / {self.per_day_budget}"
            )
            return False, cost
        if self.task_cost > 0.8 * self.per_task_budget:
            logger.info(
                f"Approaching task budget: {self.task_cost:.2f} of {self.per_task_budget} consumed"
            )
        return True, cost

    def reset_task(self) -> None:
        """Reset the per‑task cost (call when starting a new high‑level task)."""
        self.task_cost = 0.0
