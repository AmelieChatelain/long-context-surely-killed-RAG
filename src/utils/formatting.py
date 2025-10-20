"""Formatting utilities for display."""


def format_currency(amount: float, precision: int = 2) -> str:
    """Format currency with appropriate precision."""
    if amount >= 1000:
        return f"${amount:,.0f}"
    else:
        return f"${amount:.{precision}f}"


def format_number(number: int) -> str:
    """Format large numbers with commas."""
    return f"{number:,}"


def format_latency(latency: dict[str, float]) -> tuple[str, str, str, str]:
    """Format latency components for display."""
    # Handle both standard latency and RAG latency formats
    if 'llm_ttft' in latency:
        # RAG latency format
        return (
            f"{latency['llm_ttft']:.2f}s",
            f"{latency['llm_decode']:.2f}s", 
            f"{latency['total']:.2f}s",
            f"{latency['throughput']:.0f} tok/s",
        )
    else:
        # Standard latency format
        return (
            f"{latency['ttft']:.2f}s",
            f"{latency['decode']:.2f}s", 
            f"{latency['total']:.2f}s",
            f"{latency['throughput']:.0f} tok/s",
        )


def format_percentage(value: float, precision: int = 1) -> str:
    """Format percentage with sign."""
    return f"{value:+.{precision}f}%"
