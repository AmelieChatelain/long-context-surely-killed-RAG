from dataclasses import dataclass

from .pricing import DEFAULT_PLAN_KEY


@dataclass
class KnowledgeBaseParams:
    """Knowledge base configuration parameters."""
    pages: int
    tokens_per_page: int
    updates_per_month: int
    cache_storage_hours_per_month: int = 24 * 30
    
    @property
    def total_tokens(self) -> int:
        return self.pages * self.tokens_per_page


@dataclass
class QueryParams:
    """Query configuration parameters."""
    query_tokens: int = 50
    output_tokens: int = 1000


@dataclass
class RAGParams:
    """RAG-specific parameters."""
    top_k: int
    tokens_per_chunk: int = 800
    embedding_price_per_million: float = 0.12
    rerank_price_per_query: float = 0.002
    rerank_top_k: int = 20
    vector_db_base_cost: float = 26.0


@dataclass
class GrepParams:
    """Grep baseline parameters."""
    avg_tries: int
    avg_docs_retrieved: int
    avg_pages_per_document: int = 10
    
    def false_file_tokens(self, tokens_per_page: int) -> int:
        return self.avg_docs_retrieved * self.avg_pages_per_document * tokens_per_page
    
    def true_file_tokens(self, tokens_per_page: int) -> int:
        return self.avg_pages_per_document * tokens_per_page


@dataclass
class PricingParams:
    """Selected pricing configuration for the calculators."""
    plan_key: str = DEFAULT_PLAN_KEY


@dataclass
class AppParams:
    """All application parameters."""
    knowledge_base: KnowledgeBaseParams
    query: QueryParams
    rag: RAGParams
    grep: GrepParams
    pricing: PricingParams
    requests_per_day: int
    
    @property
    def monthly_requests(self) -> int:
        return self.requests_per_day * 30
