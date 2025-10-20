"""Reusable UI components for the calculator."""

from typing import Optional

import streamlit as st

from ..calculators.base import CalculationResult
from ..utils.formatting import format_currency, format_latency, format_number, format_percentage


def build_metric_card_html(
    title: str,
    value: str,
    *,
    subtitle: Optional[str] = None,
    delta: Optional[str] = None,
    variant: str = "default",
) -> str:
    """Build HTML markup for a stylized metric card."""
    base_class = "metric-container"
    variant_classes = {
        "default": "",
        "highlight": "metric-highlight",
        "accent": "metric-time",
        "summary-best": "comparison-best metric-summary",
        "summary-good": "comparison-good metric-summary",
        "summary-expensive": "comparison-expensive metric-summary",
    }
    classes = " ".join(filter(None, [base_class, variant_classes.get(variant, "")]))

    delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ""
    subtitle_html = f'<div class="metric-subtitle">{subtitle}</div>' if subtitle else ""

    lines: list[str] = [f'<div class="{classes}">']
    if title:
        lines.append(f'  <div class="metric-title">{title}</div>')
    if value:
        lines.append(f'  <div class="metric-value">{value}</div>')
    if delta_html:
        lines.append(f"  {delta_html}")
    if subtitle_html:
        lines.append(f"  {subtitle_html}")
    lines.append("</div>")

    card_html = "\n".join(lines)
    return card_html


def render_metric_card(
    title: str,
    value: str,
    *,
    subtitle: Optional[str] = None,
    delta: Optional[str] = None,
    variant: str = "default",
) -> None:
    """Render a stylized metric card with consistent layout."""
    card_html = build_metric_card_html(
        title,
        value,
        subtitle=subtitle,
        delta=delta,
        variant=variant,
    )
    st.markdown(card_html, unsafe_allow_html=True)


def render_comparison_column(result: CalculationResult) -> None:
    """Render a standardized comparison column with aligned metrics."""
    # Scenario-specific metric (varies by type)
    input_value: str

    if "kb_size_pages" in result.additional_metrics:
        render_metric_card(
            "Knowledge Base",
            f"{format_number(int(result.additional_metrics['kb_size_pages']))} pages",
            subtitle=f"{format_number(int(result.additional_metrics['kb_size_tokens']))} tokens",
        )
        input_value = f"{format_number(result.input_tokens)}"
    elif "retrieved_pages" in result.additional_metrics:
        n_chunks = int(result.additional_metrics["chunks_used"])
        tokens_per_chunk = int(result.additional_metrics["tokens_per_chunk"])
        render_metric_card(
            "Retrieved Context",
            f"~{result.additional_metrics['retrieved_pages']} pages",
            subtitle=f"{n_chunks} chunks x {tokens_per_chunk} tokens",
        )
        input_value = f"{format_number(result.input_tokens)}"
    elif "llm_calls" in result.additional_metrics:
        failed_attempts = int(result.additional_metrics["failed_attempts"])
        delta = f"{failed_attempts} retries" if failed_attempts else None
        render_metric_card(
            "Number of LLM Calls",
            result.additional_metrics["llm_calls"],
            delta=delta,
        )
        input_value = f"{result.additional_metrics['tokens_per_call']}"
    else:
        input_value = f"{format_number(result.input_tokens)}"
    # Standard metrics (aligned across all columns)
    render_metric_card(
        "Number of Input Tokens per Request",
        input_value,
    )
    render_metric_card(
        "Cost per Request",
        format_currency(result.cost_per_request, 4),
    )

    # Highlighted key metrics
    render_metric_card(
        "Monthly Cost",
        format_currency(result.monthly_cost),
        variant="highlight",
    )

    ttft_str, decode_str, _, throughput_str = format_latency(result.latency)
    avg_time_str = f"{result.avg_time_seconds:.2f}s"
    render_metric_card(
        "Avg e2e time",
        avg_time_str,
        subtitle=f"TTFT {ttft_str} + Throughput {throughput_str}",
        variant="accent",
    )

    # Additional latency details for context
    st.caption(f"Decode {decode_str}")

    # RAG latency breakdown (if applicable)
    if "indexing_amortized" in result.latency:
        render_latency_breakdown(result)

    # Cost breakdown
    render_cost_breakdown(result)


def render_latency_breakdown(result: CalculationResult) -> None:
    """Render expandable latency breakdown for RAG systems."""
    with st.expander("Latency Breakdown"):
        latency = result.latency

        # Indexing section
        st.write("**Indexing (amortized):**")
        st.text(f"Per update: {latency['indexing_per_update']:.2f}s ({latency['indexing_per_update'] / 3600:.2f}h)")
        st.text(
            f"Monthly total: {latency['indexing_total_monthly']:.2f}s ({latency['indexing_total_monthly'] / 3600:.2f}h)"
        )
        st.text(f"Per request: {latency['indexing_amortized'] * 1000:.1f}ms")

        # Retrieval section
        st.write("**Retrieval:**")
        st.text(f"Vector search: {latency['retrieval'] * 1000:.1f}ms")

        # Reranking section
        st.write("**Reranking:**")
        st.text(f"Document reranking: {latency['reranking'] * 1000:.1f}ms")

        # LLM section
        st.write("**LLM Generation:**")
        st.text(f"TTFT: {latency['llm_ttft']:.2f}s")
        st.text(f"Decode: {latency['llm_decode']:.2f}s")
        st.text(f"Total LLM: {latency['llm_total']:.2f}s")

        # Summary
        st.write("**Summary:**")
        st.text(f"E2E without indexing: {latency['e2e_without_indexing']:.2f}s")
        st.text(f"Total with indexing: {latency['total']:.2f}s")


def render_cost_breakdown(result: CalculationResult) -> None:
    """Render expandable cost breakdown."""
    with st.expander("Cost Breakdown"):
        per_request_labels = {
            "input": "LLM input",
            "output": "LLM output",
            "llm_input": "LLM input",
            "llm_output": "LLM output",
            "query_input": "Query input",
            "cache_read": "Cache read",
            "vector_db_per_request": "Vector DB amortized share",
        }
        monthly_labels = {
            "cache_write": "Cache write",
            "vector_db_base": "Vector DB base",
            "embedding": "Embedding refresh",
            "rerank": "Rerank",
        }

        monthly_requests_raw = result.additional_metrics.get("monthly_requests")
        try:
            monthly_requests = int(monthly_requests_raw) if monthly_requests_raw is not None else None
        except ValueError:
            monthly_requests = None

        cache_writes_raw = result.additional_metrics.get("cache_writes_per_month")
        try:
            cache_writes = int(cache_writes_raw) if cache_writes_raw is not None else None
        except ValueError:
            cache_writes = None

        per_request_entries: list[tuple[str, float]] = []
        monthly_entries: list[tuple[str, float]] = []
        other_entries: list[tuple[str, float]] = []

        for key, value in result.cost_breakdown.items():
            if key in monthly_labels:
                monthly_entries.append((key, value))
            elif key in per_request_labels:
                per_request_entries.append((key, value))
            else:
                other_entries.append((key, value))

        if per_request_entries:
            st.markdown("**Per-request costs**")
            for key, value in per_request_entries:
                label = per_request_labels.get(key, key.replace("_", " ").title())
                st.text(f"{label}: {format_currency(value, 4)}/request")

        if monthly_entries:
            st.markdown("**Monthly costs**")
            for key, value in monthly_entries:
                label = monthly_labels.get(key, key.replace("_", " ").title())
                if key == "cache_write":
                    multiplier_text = f" ({format_number(cache_writes)}x)" if cache_writes is not None else ""
                    st.text(f"{label}{multiplier_text}: {format_currency(value)}/month")
                elif key == "rerank" and monthly_requests:
                    per_request_share = value / monthly_requests
                    st.text(
                        f"{label}: {format_currency(value)}/month ({format_currency(per_request_share, 4)}/request)"
                    )
                else:
                    st.text(f"{label}: {format_currency(value)}/month")

        if other_entries:
            st.markdown("**Other costs**")
            for key, value in other_entries:
                st.text(f"{key.replace('_', ' ').title()}: {format_currency(value, 4)}")


def render_comparison_summary(results: list[CalculationResult]) -> None:
    """Render final comparison summary with visual highlights."""
    summary_sections: list[str] = ['<div class="comparison-summary">']
    summary_sections.append('<div class="comparison-summary-title">📊 Cost Comparison</div>')

    sorted_results = sorted(results, key=lambda r: r.monthly_cost)
    baseline_cost = next(
        (res.monthly_cost for res in results if res.scenario_name == "Long Context (No Cache)"),
        results[0].monthly_cost,
    )

    for index, result in enumerate(sorted_results):
        savings = ((baseline_cost - result.monthly_cost) / baseline_cost) * 100 if baseline_cost else 0.0
        subtitle = (
            f"Savings: {format_percentage(savings)} vs no cache"
            if result.scenario_name != "Long Context (No Cache)"
            else None
        )

        if index == 0:
            variant = "summary-best"
        elif index == 1:
            variant = "summary-good"
        else:
            variant = "summary-expensive"

        summary_sections.append(
            build_metric_card_html(
                title=result.scenario_name,
                value=f"{format_currency(result.monthly_cost)}/month",
                subtitle=subtitle,
                variant=variant,
            )
        )

    summary_sections.append("</div>")
    st.markdown("\n".join(summary_sections), unsafe_allow_html=True)
