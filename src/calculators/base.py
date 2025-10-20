"""Base calculator interface and result types."""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class CalculationResult:
    """Standardized result from any calculator."""
    scenario_name: str
    monthly_cost: float
    cost_per_request: float
    avg_time_seconds: float
    input_tokens: int
    latency: dict[str, float]
    cost_breakdown: dict[str, float]
    additional_metrics: dict[str, str]


class Calculator(Protocol):
    """Protocol for all calculator implementations."""
    
    def calculate(self, params) -> CalculationResult:
        """Calculate costs and metrics for the given parameters."""
        ...
