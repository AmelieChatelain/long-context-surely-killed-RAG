"""Grep baseline calculator."""

from ..models.parameters import AppParams
from ..models.pricing import pricing
from ..utils.latency import estimate_latency
from .base import CalculationResult


class GrepCalculator:
    """Calculator for grep baseline approach."""

    def calculate(self, params: AppParams) -> CalculationResult:
        attempts = max(1, int(params.grep.avg_tries))
        failed_attempts = attempts - 1
        plan_key = params.pricing.plan_key

        # Calculate tokens for each attempt
        grep_false_file_tokens = params.grep.false_file_tokens(params.knowledge_base.tokens_per_page)
        grep_true_file_tokens = params.grep.true_file_tokens(params.knowledge_base.tokens_per_page)

        prompt_tokens_per_attempt = [
            params.query.query_tokens + (index + 1) * grep_false_file_tokens for index in range(failed_attempts)
        ]
        final_prompt_tokens = (
            params.query.query_tokens + failed_attempts * grep_false_file_tokens + grep_true_file_tokens
        )
        prompt_tokens_per_attempt.append(final_prompt_tokens)

        total_input_tokens = sum(prompt_tokens_per_attempt)

        # Cost calculations
        input_cost_per_request = sum(
            (tokens / 1_000_000) * pricing.input_price(tokens, plan_key) for tokens in prompt_tokens_per_attempt
        )
        output_cost_per_request = sum(
            (params.query.output_tokens / 1_000_000) * pricing.output_price(tokens, plan_key)
            for tokens in prompt_tokens_per_attempt
        )

        cost_per_request = input_cost_per_request + output_cost_per_request
        monthly_cost = cost_per_request * params.monthly_requests

        # Latency calculations
        latencies = [estimate_latency(tokens, params.query.output_tokens) for tokens in prompt_tokens_per_attempt]
        total_ttft = sum(lat["ttft"] for lat in latencies)
        total_decode = sum(lat["decode"] for lat in latencies)
        latency = {
            "ttft": total_ttft,
            "decode": total_decode,
            "total": total_ttft + total_decode,
            "throughput": latencies[-1]["throughput"],
        }
        avg_time_seconds = latency["total"]

        return CalculationResult(
            scenario_name="Just Grep",
            monthly_cost=monthly_cost,
            cost_per_request=cost_per_request,
            avg_time_seconds=avg_time_seconds,
            input_tokens=total_input_tokens,
            latency=latency,
            cost_breakdown={
                "input": input_cost_per_request,
                "output": output_cost_per_request,
            },
            additional_metrics={
                "monthly_requests": str(params.monthly_requests),
                "llm_calls": str(attempts),
                "failed_attempts": str(failed_attempts),
                "tokens_per_call": "|".join(f"{tokens:,}" for tokens in prompt_tokens_per_attempt),
            },
        )
