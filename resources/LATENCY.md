# Latency Estimation

This document explains the latency constants and estimation logic used in the cost comparison tool.

## Data Sources

Latency values are based on empirical measurements from [Artificial Analysis](https://artificialanalysis.ai/models/claude-4-sonnet) (snapshot from `resources/latency_per_token_input.png`, accessed December 2025) and Anthropic's [prompt caching documentation](https://www.anthropic.com/news/prompt-caching).

Artificial Analysis publishes rolling 72-hour P50 measurements across several providers. Because vendors rarely publish official TTFT or streaming throughput numbers, we use these third-party medians as **optimistic lower bounds** so that long-context and RAG configurations are compared on the fairest (best-case) footing.

## Claude 4 Sonnet Baseline Performance

### Time to First Token (TTFT)

TTFT represents the latency before the model begins streaming its response. Measured values for Claude 4 Sonnet:

| Context Length | TTFT (seconds) |
|---------------|----------------|
| 100 tokens    | 1.9            |
| 1k tokens     | 2.4            |
| 10k tokens    | 2.0            |
| 100k tokens   | 4.3            |

Values are the lowest (fastest) medians among the charted request types (e.g. `medium_coding`, `vision_single_image`) to remain optimistic about achievable performance.

### Output Speed (Throughput)

Throughput degrades with longer context windows due to increased KV-cache processing overhead:

| Context Length | Tokens/Second |
|---------------|---------------|
| ≤1k tokens    | 150           |
| ≤10k tokens   | 120           |
| ≤50k tokens   | 90*           |
| >50k tokens   | 62            |

*Estimated by interpolating between 10k (120 tok/s) and the measured 100k value (62 tok/s).

### Network Overhead

Base network latency (provider infrastructure + API gateway): **150ms**

This represents the minimum overhead before any model computation begins.

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
Measured latencies for reranking retrieved documents:

| Document Count | Latency (ms) |
|---------------|--------------|
| 24            | 150          |
| 96            | 280          |
| Other         | Linear interpolation |

## E2E Latency Calculation

**For uncached long context:**
```
Total = Network_Overhead + TTFT(context_size) + (output_tokens / Throughput(context_size))
```

**For cached long context:**
```
Total = Network_Overhead + TTFT(context_size) × 0.25 + (output_tokens / Throughput(context_size))
```

**For RAG:**
```
Total = Indexing_Amortized + Retrieval + Reranking + Network_Overhead + TTFT(chunks_size) + Decode
```

Where indexing is amortized across monthly requests:
```
Indexing_Amortized = (corpus_tokens / Embedding_Throughput) × updates_per_month / requests_per_month
```

## Limitations & Assumptions

1. **Single-region latency**: Values assume US-based API calls. International latency will be higher.
2. **No queueing**: Assumes immediate request processing. High load may add queueing delay.
3. **Provider opacity**: Vendors do not disclose TTFT or decode throughput figures. Artificial Analysis medians are used as optimistic lower bounds and may differ from your tenancy.
4. **Stable performance**: Real-world latency has variance (±20-30%). These are median estimates.
5. **Model updates**: Performance may change with model updates. Last verified: December 2025.
6. **RAG latency**: Assumes vector DB and reranker are colocated with low inter-service latency.

## Validation

To verify these estimates match your production environment:

```python
import time
from anthropic import Anthropic

client = Anthropic()
prompts = [100, 1000, 10000]  # token counts

for n_tokens in prompts:
    prompt = "word " * (n_tokens // 2)  # ~2 tokens per word
    
    start = time.time()
    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        ttft = None
        for event in stream:
            if ttft is None and event.type == "content_block_delta":
                ttft = time.time() - start
    
    total = time.time() - start
    print(f"{n_tokens} tokens → TTFT: {ttft:.2f}s, Total: {total:.2f}s")
```

Compare measured values against the tables above. Significant deviations (>30%) suggest updating the constants.
