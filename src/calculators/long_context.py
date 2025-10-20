"""Long context calculators (with and without cache)."""

from ..models.parameters import AppParams
from ..models.pricing import pricing
from ..utils.latency import estimate_latency
from .base import CalculationResult


class LongContextNoCache:
    """Calculator for long context without prompt caching."""
    
    def calculate(self, params: AppParams) -> CalculationResult:
        prompt_tokens = params.knowledge_base.total_tokens + params.query.query_tokens
        plan_key = params.pricing.plan_key
        
        # Cost calculations
        input_cost_per_request = (prompt_tokens / 1_000_000) * pricing.input_price(prompt_tokens, plan_key)
        output_cost_per_request = (params.query.output_tokens / 1_000_000) * pricing.output_price(prompt_tokens, plan_key)
        cost_per_request = input_cost_per_request + output_cost_per_request
        monthly_cost = cost_per_request * params.monthly_requests
        
        # Latency calculations
        latency = estimate_latency(prompt_tokens, params.query.output_tokens)
        avg_time_seconds = latency['total']
        
        return CalculationResult(
            scenario_name="Long Context (No Cache)",
            monthly_cost=monthly_cost,
            cost_per_request=cost_per_request,
            avg_time_seconds=avg_time_seconds,
            input_tokens=prompt_tokens,
            latency=latency,
            cost_breakdown={
                "input": input_cost_per_request,
                "output": output_cost_per_request,
            },
            additional_metrics={
                "kb_size_pages": str(params.knowledge_base.pages),
                "kb_size_tokens": str(params.knowledge_base.total_tokens),
                "monthly_requests": str(params.monthly_requests),
            }
        )


class LongContextWithCache:
    """Calculator for long context with prompt caching."""
    
    def calculate(self, params: AppParams) -> CalculationResult:
        prompt_tokens = params.knowledge_base.total_tokens + params.query.query_tokens
        plan_key = params.pricing.plan_key
        
        # Cache write cost (monthly)
        cache_write_cost = (
            (params.knowledge_base.total_tokens / 1_000_000)
            * pricing.cache_write_price(params.knowledge_base.total_tokens, plan_key)
            * params.knowledge_base.updates_per_month
        )
        cache_storage_cost = (
            (params.knowledge_base.total_tokens / 1_000_000)
            * pricing.cache_storage_price_per_hour(params.knowledge_base.total_tokens, plan_key)
            * params.knowledge_base.cache_storage_hours_per_month
        )
        
        # Per-request costs
        cache_read_cost_per_request = (
            (params.knowledge_base.total_tokens / 1_000_000)
            * pricing.cache_read_price(params.knowledge_base.total_tokens, plan_key)
        )
        query_input_cost_per_request = (
            (params.query.query_tokens / 1_000_000) * pricing.input_price(prompt_tokens, plan_key)
        )
        output_cost_per_request = (
            (params.query.output_tokens / 1_000_000) * pricing.output_price(prompt_tokens, plan_key)
        )
        
        cost_per_request = cache_read_cost_per_request + query_input_cost_per_request + output_cost_per_request
        monthly_cost = cache_write_cost + cache_storage_cost + (cost_per_request * params.monthly_requests)
        
        # Latency calculations (cached)
        cached_ttft_tokens = int(params.knowledge_base.total_tokens * 0.15) + params.query.query_tokens
        latency = estimate_latency(cached_ttft_tokens, params.query.output_tokens, uses_cache=True)
        avg_time_seconds = latency['total']
        
        return CalculationResult(
            scenario_name="Long Context (Cache)",
            monthly_cost=monthly_cost,
            cost_per_request=cost_per_request,
            avg_time_seconds=avg_time_seconds,
            input_tokens=prompt_tokens,
            latency=latency,
            cost_breakdown={
                "cache_write": cache_write_cost,
                "cache_storage": cache_storage_cost,
                "cache_read": cache_read_cost_per_request,
                "query_input": query_input_cost_per_request,
                "output": output_cost_per_request,
            },
            additional_metrics={
                "kb_size_pages": str(params.knowledge_base.pages),
                "kb_size_tokens": str(params.knowledge_base.total_tokens),
                "monthly_requests": str(params.monthly_requests),
                "cache_writes_per_month": str(params.knowledge_base.updates_per_month),
                "cache_storage_hours_per_month": str(params.knowledge_base.cache_storage_hours_per_month),
            }
        )
