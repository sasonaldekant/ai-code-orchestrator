"""
Enhanced cost management with real-time tracking and multi-tier budgets.

This module provides comprehensive cost tracking and budget enforcement
for LLM API calls across multiple providers (OpenAI, Anthropic, Google).

Features:
- Multi-tier budgets (per-task, hourly, daily)
- Real-time cost tracking per model and provider
- Alert system at 80% threshold
- Per-phase cost breakdown
- Cost reports and exports
- Historical tracking

Version: 2.0.0
"""

from __future__ import annotations

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class ModelPricing:
    """Pricing information for a specific model."""
    input_per_million: float  # USD per million input tokens
    output_per_million: float  # USD per million output tokens
    provider: str
    context_window: int = 128000


@dataclass
class UsageRecord:
    """Single usage record for cost tracking."""
    timestamp: float
    model: str
    provider: str
    phase: str
    tokens_input: int
    tokens_output: int
    tokens_total: int
    cost_usd: float
    task_id: Optional[str] = None


@dataclass
class CostAlert:
    """Alert when budget threshold is reached."""
    timestamp: float
    level: str  # "warning" or "critical"
    budget_type: str  # "task", "hour", "day"
    current_cost: float
    budget_limit: float
    percentage: float
    message: str


@dataclass
class CostReport:
    """Comprehensive cost report."""
    start_time: float
    end_time: float
    total_cost: float
    total_tokens: int
    by_model: Dict[str, Dict[str, float]]  # model -> {cost, tokens}
    by_provider: Dict[str, Dict[str, float]]  # provider -> {cost, tokens}
    by_phase: Dict[str, Dict[str, float]]  # phase -> {cost, tokens}
    num_calls: int
    alerts: List[CostAlert]


class CostManager:
    """
    Enhanced cost manager with multi-tier budgets and real-time tracking.
    """
    
    # Pricing table (USD per million tokens)
    # Source: Public pricing as of Feb 2026
    PRICING = {
        # OpenAI
        "gpt-4o": ModelPricing(2.50, 10.0, "openai", 128000),
        "gpt-4o-mini": ModelPricing(0.15, 0.60, "openai", 128000),
        "gpt-4-turbo": ModelPricing(10.0, 30.0, "openai", 128000),
        "gpt-3.5-turbo": ModelPricing(0.50, 1.50, "openai", 16000),
        
        # Anthropic
        "claude-sonnet-4.5": ModelPricing(3.00, 15.0, "anthropic", 200000),
        "claude-3-7-sonnet": ModelPricing(3.00, 15.0, "anthropic", 200000),
        "claude-3-5-sonnet": ModelPricing(3.00, 15.0, "anthropic", 200000),
        "claude-3-opus": ModelPricing(15.0, 75.0, "anthropic", 200000),
        "claude-3-sonnet": ModelPricing(3.00, 15.0, "anthropic", 200000),
        "claude-3-haiku": ModelPricing(0.25, 1.25, "anthropic", 200000),
        
        # Google
        "gemini-2.5-pro": ModelPricing(1.25, 5.0, "google", 1000000),
        "gemini-1.5-pro": ModelPricing(1.25, 5.0, "google", 2000000),
        "gemini-1.5-flash": ModelPricing(0.075, 0.30, "google", 1000000),
    }
    
    def __init__(
        self,
        per_task_budget: float = 0.50,
        per_hour_budget: float = 5.0,
        per_day_budget: float = 40.0,
        alert_threshold: float = 0.8,  # Alert at 80%
        enable_history: bool = True,
        history_dir: Optional[str] = None
    ):
        """
        Initialize cost manager.
        """
        # Budgets
        self.per_task_budget = per_task_budget
        self.per_hour_budget = per_hour_budget
        self.per_day_budget = per_day_budget
        self.alert_threshold = alert_threshold
        
        # Tracking
        self.usage_records: List[UsageRecord] = []
        self.alerts: List[CostAlert] = []
        self.current_task_cost = 0.0
        self.current_task_id: Optional[str] = None
        self.current_phase: str = "unknown"
        self.total_cost = 0.0 # Maintain total_cost property for compatibility
        
        # Time-based tracking
        self.hour_start = time.time()
        self.day_start = time.time()
        self.hour_cost = 0.0
        self.day_cost = 0.0
        
        # Alert state
        self._task_alert_fired = False
        self._hour_alert_fired = False
        self._day_alert_fired = False
        
        # History persistence
        self.enable_history = enable_history
        if enable_history:
            self.history_dir = Path(history_dir or "./cost_history")
            self.history_dir.mkdir(exist_ok=True)
    
    def track_usage(
        self,
        provider: str,
        model: str,
        tokens_used: Dict[str, int],
        phase: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> float:
        """
        Track token usage and calculate cost.
        """
        # Normalize model name
        model_key = model.lower()
        if model_key not in self.PRICING:
            logger.warning(f"Unknown model {model}, using gpt-4o pricing")
            model_key = "gpt-4o"
        
        pricing = self.PRICING[model_key]
        
        # Calculate cost
        input_tokens = tokens_used.get("prompt", 0)
        output_tokens = tokens_used.get("completion", 0)
        total_tokens = tokens_used.get("total", input_tokens + output_tokens)
        
        cost = (
            (input_tokens / 1_000_000) * pricing.input_per_million +
            (output_tokens / 1_000_000) * pricing.output_per_million
        )
        
        # Create usage record
        record = UsageRecord(
            timestamp=time.time(),
            model=model,
            provider=provider,
            phase=phase or self.current_phase,
            tokens_input=input_tokens,
            tokens_output=output_tokens,
            tokens_total=total_tokens,
            cost_usd=cost,
            task_id=task_id or self.current_task_id
        )
        
        self.usage_records.append(record)
        
        # Update running totals
        self.current_task_cost += cost
        self.total_cost += cost
        self._update_time_based_costs(cost)
        
        # Check budgets and emit alerts
        self._check_budgets()
        
        # Persist if enabled
        if self.enable_history:
            self._append_to_history(record)
        
        logger.info(
            f"Usage tracked: {model} ({provider}), {total_tokens} tokens, "
            f"${cost:.4f} (task: ${self.current_task_cost:.4f})"
        )
        
        return cost
        
    def check_and_update(self, model: str, tokens_in: int, tokens_out: int) -> Tuple[bool, float]:
        """
        Compatibility method for V1 calls.
        Updates cost and returns (should_continue, cost).
        """
        # Infer provider from model name for compatibility
        provider = "openai"
        if "claude" in model:
            provider = "anthropic"
        elif "gemini" in model:
            provider = "google"
            
        cost = self.track_usage(
            provider=provider, 
            model=model, 
            tokens_used={"prompt": tokens_in, "completion": tokens_out, "total": tokens_in + tokens_out}
        )
        
        return self.can_proceed(), cost
    
    def can_proceed(self) -> bool:
        """
        Check if execution can proceed within budget constraints.
        """
        if self.current_task_cost >= self.per_task_budget:
            logger.error("Per-task budget exceeded")
            return False
        
        if self.hour_cost >= self.per_hour_budget:
            logger.error("Hourly budget exceeded")
            return False
        
        if self.day_cost >= self.per_day_budget:
            logger.error("Daily budget exceeded")
            return False
        
        return True
    
    def start_task(self, task_id: str, phase: str = "unknown"):
        """Start tracking a new task."""
        self.current_task_id = task_id
        self.current_phase = phase
        self.current_task_cost = 0.0
        self._task_alert_fired = False
        logger.info(f"Started tracking task: {task_id} (phase: {phase})")
    
    def end_task(self) -> float:
        """End current task and return its cost."""
        cost = self.current_task_cost
        logger.info(f"Task {self.current_task_id} completed. Cost: ${cost:.4f}")
        self.current_task_id = None
        self.current_task_cost = 0.0
        return cost
        
    def reset_task(self) -> None:
        """Compatibility method: alias for ending task (roughly)."""
        self.current_task_cost = 0.0
    
    def get_cumulative_cost(self) -> float:
        """Get cumulative cost across all usage."""
        return self.total_cost
    
    def get_cost_breakdown(self) -> Dict[str, float]:
        """Get cost breakdown by model."""
        breakdown = defaultdict(float)
        for r in self.usage_records:
            breakdown[r.model] += r.cost_usd
        return dict(breakdown)
    
    def generate_report(
        self,
        since: Optional[float] = None
    ) -> CostReport:
        """
        Generate comprehensive cost report.
        """
        # Filter records
        records = self.usage_records
        if since:
            records = [r for r in records if r.timestamp >= since]
        
        if not records:
            return CostReport(
                start_time=time.time(),
                end_time=time.time(),
                total_cost=0.0,
                total_tokens=0,
                by_model={},
                by_provider={},
                by_phase={},
                num_calls=0,
                alerts=self.alerts
            )
        
        # Aggregate by model
        by_model = defaultdict(lambda: {"cost": 0.0, "tokens": 0})
        for r in records:
            by_model[r.model]["cost"] += r.cost_usd
            by_model[r.model]["tokens"] += r.tokens_total
        
        # Aggregate by provider
        by_provider = defaultdict(lambda: {"cost": 0.0, "tokens": 0})
        for r in records:
            by_provider[r.provider]["cost"] += r.cost_usd
            by_provider[r.provider]["tokens"] += r.tokens_total
        
        # Aggregate by phase
        by_phase = defaultdict(lambda: {"cost": 0.0, "tokens": 0})
        for r in records:
            by_phase[r.phase]["cost"] += r.cost_usd
            by_phase[r.phase]["tokens"] += r.tokens_total
        
        total_cost = sum(r.cost_usd for r in records)
        total_tokens = sum(r.tokens_total for r in records)
        
        return CostReport(
            start_time=records[0].timestamp,
            end_time=records[-1].timestamp,
            total_cost=total_cost,
            total_tokens=total_tokens,
            by_model=dict(by_model),
            by_provider=dict(by_provider),
            by_phase=dict(by_phase),
            num_calls=len(records),
            alerts=self.alerts
        )
    
    def export_report(
        self,
        output_path: str,
        format: str = "json"
    ):
        """Export cost report to file."""
        report = self.generate_report()
        
        with open(output_path, "w") as f:
            if format == "json":
                json.dump(asdict(report), f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Cost report exported to {output_path}")
    
    def _update_time_based_costs(self, cost: float):
        """Update hourly and daily cost trackers."""
        now = time.time()
        
        # Check if hour has rolled over
        if now - self.hour_start >= 3600:
            logger.info(f"Hour completed. Cost: ${self.hour_cost:.4f}")
            self.hour_start = now
            self.hour_cost = 0.0
            self._hour_alert_fired = False
        
        # Check if day has rolled over
        if now - self.day_start >= 86400:
            logger.info(f"Day completed. Cost: ${self.day_cost:.4f}")
            self.day_start = now
            self.day_cost = 0.0
            self._day_alert_fired = False
        
        self.hour_cost += cost
        self.day_cost += cost
    
    def _check_budgets(self):
        """Check budgets and emit alerts if thresholds reached."""
        # Task budget
        task_pct = self.current_task_cost / self.per_task_budget
        if not self._task_alert_fired and task_pct >= self.alert_threshold:
            self._emit_alert(
                level="warning",
                budget_type="task",
                current=self.current_task_cost,
                limit=self.per_task_budget,
                percentage=task_pct
            )
            self._task_alert_fired = True
        
        # Hour budget
        hour_pct = self.hour_cost / self.per_hour_budget
        if not self._hour_alert_fired and hour_pct >= self.alert_threshold:
            self._emit_alert(
                level="warning",
                budget_type="hour",
                current=self.hour_cost,
                limit=self.per_hour_budget,
                percentage=hour_pct
            )
            self._hour_alert_fired = True
        
        # Day budget
        day_pct = self.day_cost / self.per_day_budget
        if not self._day_alert_fired and day_pct >= self.alert_threshold:
            self._emit_alert(
                level="warning",
                budget_type="day",
                current=self.day_cost,
                limit=self.per_day_budget,
                percentage=day_pct
            )
            self._day_alert_fired = True
    
    def _emit_alert(
        self,
        level: str,
        budget_type: str,
        current: float,
        limit: float,
        percentage: float
    ):
        """Emit cost alert."""
        alert = CostAlert(
            timestamp=time.time(),
            level=level,
            budget_type=budget_type,
            current_cost=current,
            budget_limit=limit,
            percentage=percentage,
            message=f"{level.upper()}: {budget_type} budget at {percentage:.0%} "
                    f"(${current:.4f} / ${limit:.2f})"
        )
        
        self.alerts.append(alert)
        logger.warning(alert.message)
    
    def _append_to_history(self, record: UsageRecord):
        """Append usage record to history file."""
        # Create daily history file
        date_str = datetime.fromtimestamp(record.timestamp).strftime("%Y-%m-%d")
        history_file = self.history_dir / f"usage_{date_str}.jsonl"
        
        with open(history_file, "a") as f:
            f.write(json.dumps(asdict(record)) + "\n")
