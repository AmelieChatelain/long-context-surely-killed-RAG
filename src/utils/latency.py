"""Latency estimation utilities.

Based on empirical measurements from Artificial Analysis (Dec 2025):
https://artificialanalysis.ai/models/claude-4-sonnet

And Anthropic's prompt caching documentation:
https://www.anthropic.com/news/prompt-caching
"""

from typing import Optional

# Latency constants (Claude 4 Sonnet, measured Dec 2025)
BASE_NET_OVERHEAD = 0.15  # s, network + provider jitter
TTFT_100 = 1.9  # s (TTFT at ~100 prompt tokens; optimistic P50 lower bound)
TTFT_1K = 2.4  # s (TTFT at 1k prompt tokens)
TTFT_10K = 2.0  # s (TTFT at 10k prompt tokens)
TTFT_100K = 4.3  # s (TTFT at 100k prompt tokens)

# Prompt caching acceleration (Anthropic reports 2-10x, we use 4x as conservative middle ground)
CACHE_SPEEDUP_FACTOR = 0.25  # Cached TTFT = 25% of uncached

# RAG-specific constants
EMBEDDING_THROUGHPUT = 1500.0  # tokens/second for Cohere embed-v4.0
RETRIEVAL_BASE_LATENCY = 0.010  # 10ms base retrieval time
RETRIEVAL_SCALING_FACTOR = 0.00002  # 2ms per 100 top_k
RERANK_24_DOCS_TIME = 0.150  # 150ms for 24 documents
RERANK_96_DOCS_TIME = 0.280  # 280ms for 96 documents


def _prefill_time(prompt_tokens: int, uses_cache: bool = False) -> float:
    """Calculate prefill time based on prompt token count.

    Uses optimistic lower-bound TTFT values (P50) from Artificial Analysis.
    Cache speedup applies 4x acceleration (TTFT reduced to 25%).
    """
    scale_factor = CACHE_SPEEDUP_FACTOR if uses_cache else 1.0
    
    if prompt_tokens <= 100:
        base_ttft = TTFT_100
    elif prompt_tokens <= 1_000:
        base_ttft = TTFT_1K
    elif prompt_tokens <= 10_000:
        base_ttft = TTFT_10K
    else:
        base_ttft = TTFT_100K
    
    return BASE_NET_OVERHEAD + scale_factor * base_ttft


def _streaming_throughput(prompt_tokens: int) -> float:
    """Calculate streaming throughput based on prompt token count.
    
    Measured values (optimistic P50 medians) show degradation with longer
    contexts due to increased KV-cache processing overhead.
    """
    if prompt_tokens <= 1_000:
        return 150.0  # tok/s (measured at 100-1k tokens)
    elif prompt_tokens <= 10_000:
        return 120.0  # tok/s (measured at 10k tokens)
    elif prompt_tokens <= 50_000:
        return 90.0  # tok/s (interpolated between 10k and 100k measurements)
    else:
        return 62.0  # tok/s (measured at 100k tokens)


def estimate_latency(prompt_tokens: int, completion_tokens: int, uses_cache: bool = False) -> dict[str, float]:
    """Estimate latency components for a request."""
    ttft = _prefill_time(prompt_tokens, uses_cache=uses_cache)
    throughput = _streaming_throughput(prompt_tokens)
    decode_time = completion_tokens / throughput if completion_tokens else 0.0
    total = ttft + decode_time
    
    return {
        "ttft": ttft,
        "decode": decode_time,
        "total": total,
        "throughput": throughput,
    }


def estimate_embedding_latency(corpus_tokens: int) -> float:
    """Estimate time to generate embeddings for the entire corpus."""
    return corpus_tokens / EMBEDDING_THROUGHPUT


def estimate_retrieval_latency(top_k: int) -> float:
    """Estimate vector search retrieval latency."""
    return RETRIEVAL_BASE_LATENCY + (top_k / 100) * RETRIEVAL_SCALING_FACTOR


def estimate_reranking_latency(doc_count: int) -> float:
    """Estimate reranking latency based on document count."""
    if doc_count <= 24:
        return RERANK_24_DOCS_TIME
    elif doc_count >= 96:
        return RERANK_96_DOCS_TIME
    else:
        # Linear interpolation between 24 and 96 documents
        return RERANK_24_DOCS_TIME + (doc_count - 24) * (RERANK_96_DOCS_TIME - RERANK_24_DOCS_TIME) / (96 - 24)


def estimate_rag_latency(
    corpus_tokens: int,
    top_k: int,
    prompt_tokens: int,
    completion_tokens: int,
    monthly_requests: int,
    updates_per_month: int = 1,
    *,
    rerank_top_k: Optional[int] = None,
    uses_cache: bool = False,
) -> dict[str, float]:
    """Estimate complete RAG latency including indexing, retrieval, reranking, and LLM generation."""
    # Indexing (total time per update, amortized per request)
    indexing_time_per_update = estimate_embedding_latency(corpus_tokens)
    total_indexing_time_monthly = indexing_time_per_update * updates_per_month
    amortized_indexing_time = (total_indexing_time_monthly / monthly_requests) if monthly_requests else 0.0
    
    # Retrieval
    retrieval_time = estimate_retrieval_latency(top_k)
    
    # Reranking (done on top_k documents retrieved)
    rerank_docs = rerank_top_k if rerank_top_k is not None else top_k
    reranking_time = estimate_reranking_latency(rerank_docs)
    
    # LLM generation
    llm_latency = estimate_latency(prompt_tokens, completion_tokens, uses_cache)
    
    # Total RAG latency (including indexing)
    total_rag_latency = amortized_indexing_time + retrieval_time + reranking_time + llm_latency["total"]
    
    # Total e2e time without indexing (for comparison)
    e2e_without_indexing = retrieval_time + reranking_time + llm_latency["total"]
    
    return {
        "indexing_per_update": indexing_time_per_update,
        "indexing_total_monthly": total_indexing_time_monthly,
        "indexing_total": total_indexing_time_monthly,
        "indexing_amortized": amortized_indexing_time,
        "retrieval": retrieval_time,
        "reranking": reranking_time,
        "llm_ttft": llm_latency["ttft"],
        "llm_decode": llm_latency["decode"],
        "llm_total": llm_latency["total"],
        "e2e_without_indexing": e2e_without_indexing,
        "total": total_rag_latency,
        "throughput": llm_latency["throughput"],
    }
