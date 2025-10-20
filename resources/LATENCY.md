## Data Sources

Latency values are based on empirical measurements from [Artificial Analysis](https://artificialanalysis.ai/models/claude-4-sonnet) and Anthropic's [prompt caching documentation](https://www.anthropic.com/news/prompt-caching).

Artificial Analysis publishes rolling 72-hour P50 measurements across several providers.

Because vendors rarely publish official TTFT or streaming throughput numbers, we use these third-party medians as **optimistic lower bounds** so that long-context and RAG configurations are compared on the fairest (best-case) footing.

## Prompt Caching

When using [Anthropic's prompt caching](https://www.anthropic.com/news/prompt-caching), cached prompt segments:

- Cost 90% less (10% of standard input token pricing)
- Process significantly faster

**Cache acceleration factor: 4x** (TTFT reduced to 25% of uncached time)

This conservative estimate accounts for:

- Cache lookup overhead (~10-20ms)
- Reduced KV-cache computation
- Variance across context lengths

Note: Anthropic reports cache speedups ranging from 2-10x depending on cache size. We use 4x as a reasonable middle ground for 10k+ token caches.

## RAG-Specific Latencies

### Embedding Generation

- **Model**: Cohere embed-v4.0
- **Throughput**: 1,500 tokens/second
- **Use case**: Indexing corpus documents

### Vector Retrieval

- **Base latency**: 10ms
- **Scaling factor**: 2ms per 100 documents in top_k
- **Example**: top_k=300 → 10ms + (300/100 × 2ms) = 16ms

### Reranking (Cohere rerank-v3.5)

We estimate around 150ms to rerank 24 documents: benchmarks can be found ib [Oracle's documentation](https://docs.oracle.com/en-us/iaas/Content/generative-ai/benchmark-cohere-rerank-3-5.htm).

## E2E Latency Calculation

**For uncached long context:**

```text
Total = Network_Overhead + TTFT(context_size) + (output_tokens / Throughput(context_size))
```

**For cached long context:**

```text
Total = Network_Overhead + TTFT(context_size) × 0.25 + (output_tokens / Throughput(context_size))
```

**For RAG:**

```text
Total = Indexing_Amortized + Retrieval + Reranking + Network_Overhead + TTFT(chunks_size) + Decode
```

Where indexing is amortized across monthly requests:

```text
Indexing_Amortized = (corpus_tokens / Embedding_Throughput) × updates_per_month / requests_per_month
```

## Limitations & Assumptions

1. **Single-region latency**: Values assume US-based API calls. International latency will be higher.
2. **No queueing**: Assumes immediate request processing. High load may add queueing delay.
3. **Provider opacity**: Vendors do not disclose TTFT or decode throughput figures. Artificial Analysis medians are used as optimistic lower bounds and may differ from your tenancy.
4. **Stable performance**: Real-world latency has variance (±20-30%). These are median estimates.
5. **Model updates**: Performance may change with model updates.
