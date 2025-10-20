"""RAG calculator with vector database costs."""

import math

from ..models.parameters import AppParams
from ..models.pricing import pricing
from ..utils.latency import estimate_rag_latency
from .base import CalculationResult


class RAGCalculator:
    """Calculator for RAG with vector database."""

    def calculate(self, params: AppParams) -> CalculationResult:
        retrieved_tokens = params.rag.top_k * params.rag.tokens_per_chunk
        prompt_tokens = retrieved_tokens + params.query.query_tokens
        retrieved_pages = retrieved_tokens / params.knowledge_base.tokens_per_page
        plan_key = params.pricing.plan_key
        monthly_requests = params.monthly_requests

        # LLM costs per request
        input_cost_per_request = (prompt_tokens / 1_000_000) * pricing.input_price(prompt_tokens, plan_key)
        output_cost_per_request = (
            (params.query.output_tokens / 1_000_000) * pricing.output_price(prompt_tokens, plan_key)
        )
        llm_cost_per_request = input_cost_per_request + output_cost_per_request

        # Rerank batching constraints (Cohere rerank-3.5 has a 4,096 token limit)
        rerank_docs = max(params.rag.top_k, params.rag.rerank_top_k)
        rerank_context_limit = params.rag.rerank_context_limit or 4096
        tokens_available_for_docs = max(0, rerank_context_limit - params.query.query_tokens)
        tokens_per_candidate = params.rag.tokens_per_chunk or 1
        docs_per_rerank_call = max(1, tokens_available_for_docs // tokens_per_candidate)
        rerank_calls_per_request = math.ceil(rerank_docs / docs_per_rerank_call) if rerank_docs else 0

        # Vector DB costs
        embedding_tokens_total = params.knowledge_base.pages * params.knowledge_base.tokens_per_page
        embedding_cost_per_reindex = (embedding_tokens_total / 1_000_000) * params.rag.embedding_price_per_million
        monthly_embedding_cost = embedding_cost_per_reindex * params.knowledge_base.updates_per_month

        rerank_cost_per_request = params.rag.rerank_price_per_query * rerank_calls_per_request
        rerank_cost_monthly = rerank_cost_per_request * monthly_requests

        vector_db_monthly_cost = params.rag.vector_db_base_cost + monthly_embedding_cost + rerank_cost_monthly
        vector_db_cost_per_request = vector_db_monthly_cost / monthly_requests if monthly_requests else 0.0

        cost_per_request = llm_cost_per_request + vector_db_cost_per_request
        monthly_cost = llm_cost_per_request * monthly_requests + vector_db_monthly_cost

        # Latency calculations
        latency = estimate_rag_latency(
            corpus_tokens=params.knowledge_base.total_tokens,
            top_k=params.rag.top_k,
            prompt_tokens=prompt_tokens,
            completion_tokens=params.query.output_tokens,
            monthly_requests=params.monthly_requests,
            updates_per_month=params.knowledge_base.updates_per_month,
            rerank_top_k=params.rag.rerank_top_k,
        )
        avg_time_seconds = latency["total"]

        return CalculationResult(
            scenario_name="RAG w/ Vector DB",
            monthly_cost=monthly_cost,
            cost_per_request=cost_per_request,
            avg_time_seconds=avg_time_seconds,
            input_tokens=prompt_tokens,
            latency=latency,
            cost_breakdown={
                "llm_input": input_cost_per_request,
                "llm_output": output_cost_per_request,
                "vector_db_base": params.rag.vector_db_base_cost,
                "embedding": monthly_embedding_cost,
                "rerank": rerank_cost_monthly,
                "vector_db_per_request": vector_db_cost_per_request,
            },
            additional_metrics={
                "monthly_requests": str(monthly_requests),
                "retrieved_pages": f"{retrieved_pages:.1f}",
                "chunks_used": str(params.rag.top_k),
                "tokens_per_chunk": str(params.rag.tokens_per_chunk),
                "indexing_per_update_hours": f"{latency['indexing_per_update'] / 3600:.2f}",
                "indexing_total_monthly_hours": f"{latency['indexing_total_monthly'] / 3600:.2f}",
                "indexing_per_request_ms": f"{latency['indexing_amortized'] * 1000:.1f}",
                "retrieval_ms": f"{latency['retrieval'] * 1000:.1f}",
                "reranking_ms": f"{latency['reranking'] * 1000:.1f}",
                "e2e_without_indexing_s": f"{latency['e2e_without_indexing']:.2f}",
                "rerank_calls_per_request": str(rerank_calls_per_request),
                "docs_per_rerank_call": str(docs_per_rerank_call),
            },
        )
