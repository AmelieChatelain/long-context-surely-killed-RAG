from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class TierPricing:
    """Per-million token prices for a tier capped at `up_to_tokens`."""

    up_to_tokens: Optional[int]
    input_per_million: float
    output_per_million: float
    cache_write_per_million: float
    cache_read_per_million: float
    cache_storage_per_million_hour: float = 0.0


@dataclass(frozen=True)
class PricingPlan:
    """Pricing configuration for a specific model."""

    key: str
    label: str
    provider: str
    model_name: str
    context_window: int
    tiers: Tuple[TierPricing, ...]
    notes: str = ""

    def _tier_for_tokens(self, tokens: int) -> TierPricing:
        for tier in self.tiers:
            if tier.up_to_tokens is None or tokens <= tier.up_to_tokens:
                return tier
        return self.tiers[-1]

    def input_price(self, tokens: int) -> float:
        """Price per million input tokens."""
        return self._tier_for_tokens(tokens).input_per_million

    def output_price(self, tokens: int) -> float:
        """Price per million output tokens."""
        return self._tier_for_tokens(tokens).output_per_million

    def cache_write_price(self, tokens: int) -> float:
        """Price per million tokens for cache writes."""
        return self._tier_for_tokens(tokens).cache_write_per_million

    def cache_read_price(self, tokens: int) -> float:
        """Price per million tokens for cache reads."""
        return self._tier_for_tokens(tokens).cache_read_per_million

    def cache_storage_price_per_hour(self, tokens: int) -> float:
        """Price per million tokens for cache storage per hour."""
        return self._tier_for_tokens(tokens).cache_storage_per_million_hour


class PricingCatalog:
    """Registry of supported pricing plans."""

    def __init__(self, plans: Dict[str, PricingPlan], default_key: str) -> None:
        if default_key not in plans:
            raise ValueError(f"Default pricing key '{default_key}' is not in the provided plan set.")
        self._plans = plans
        self._default_key = default_key

    @property
    def default_key(self) -> str:
        return self._default_key

    def available_plans(self) -> Tuple[PricingPlan, ...]:
        """Return plans sorted by display label."""
        return tuple(sorted(self._plans.values(), key=lambda plan: plan.label))

    def get_plan(self, plan_key: Optional[str] = None) -> PricingPlan:
        """Return the pricing plan for the provided key or the default plan."""
        key = plan_key or self._default_key
        try:
            return self._plans[key]
        except KeyError as exc:
            raise KeyError(f"Unknown pricing plan '{key}'") from exc

    def input_price(self, tokens: int, plan_key: Optional[str] = None) -> float:
        return self.get_plan(plan_key).input_price(tokens)

    def output_price(self, tokens: int, plan_key: Optional[str] = None) -> float:
        return self.get_plan(plan_key).output_price(tokens)

    def cache_write_price(self, tokens: int, plan_key: Optional[str] = None) -> float:
        return self.get_plan(plan_key).cache_write_price(tokens)

    def cache_read_price(self, tokens: int, plan_key: Optional[str] = None) -> float:
        return self.get_plan(plan_key).cache_read_price(tokens)

    def cache_storage_price_per_hour(self, tokens: int, plan_key: Optional[str] = None) -> float:
        return self.get_plan(plan_key).cache_storage_price_per_hour(tokens)


DEFAULT_PLAN_KEY = "claude-3.5-sonnet-1m"

PRICING_PLANS: Dict[str, PricingPlan] = {
    DEFAULT_PLAN_KEY: PricingPlan(
        key=DEFAULT_PLAN_KEY,
        label="Anthropic Claude Sonnet",
        provider="Anthropic",
        model_name="Claude Sonnet",
        context_window=1_000_000,
        tiers=(
            TierPricing(
                up_to_tokens=200_000,
                input_per_million=3.0,
                output_per_million=15.0,
                cache_write_per_million=3.75,
                cache_read_per_million=0.3,
            ),
            TierPricing(
                up_to_tokens=None,
                input_per_million=6.0,
                output_per_million=22.5,
                cache_write_per_million=7.5,
                cache_read_per_million=0.6,
            ),
        ),
        notes="Matches the previous default calculation based on Claude 3.5 Sonnet 1M context pricing.",
    ),
    "gemini-2.5-flash": PricingPlan(
        key="gemini-2.5-flash",
        label="Google Gemini 2.5 Flash",
        provider="Google",
        model_name="Gemini 2.5 Flash",
        context_window=1_000_000,
        tiers=(
            TierPricing(
                up_to_tokens=None,
                input_per_million=0.30,
                output_per_million=2.5,
                cache_write_per_million=0.30,
                cache_read_per_million=0.03,
                cache_storage_per_million_hour=1.0,
            ),
        ),
        notes=(
            "Assumes Gemini prompt caching bills cached tokens at $0.03 per million when reused and "
            "that cache creation costs match regular input pricing ($0.30 per million tokens), with "
            "a storage rate of $1.00 per million tokens per hour."
        ),
    ),
}

# Global pricing catalog
pricing = PricingCatalog(PRICING_PLANS, DEFAULT_PLAN_KEY)

__all__ = [
    "TierPricing",
    "PricingPlan",
    "PricingCatalog",
    "pricing",
    "DEFAULT_PLAN_KEY",
    "PRICING_PLANS",
]
