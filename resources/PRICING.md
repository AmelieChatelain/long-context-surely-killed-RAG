## LLM Pricing

To estimate some pricing, we provide two different "plans" of pricing: one corresponding to [Anthropic's Claude Sonnet](https://www.claude.com/pricing#api), and the other corresponding to [Google's Gemini 2.5 Flash](https://ai.google.dev/gemini-api/docs/pricing#gemini-2.5-flash).

### Why these models?

I wanted to limit myself to models that could handle a context length of 1M. These two models can be used to get an idea of the cost difference between a cheap, fast model and a more intelligent, expensive one.

### Available Pricing Plans

| Plan | Provider | Context Window | Tier Condition | Input \$ / M tokens | Output \$ / M tokens | Cache Write \$ / M tokens | Cache Read \$ / M tokens | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `claude-3.5-sonnet-1m` | Anthropic Claude 3.5 Sonnet | 1,000,000 | ≤ 200k prompt tokens | 3.00 | 15.00 | 3.75 | 0.30 | Mirrors Anthropic's 1M context pricing for Claude 3.5 Sonnet. |
|  |  |  | > 200k prompt tokens | 6.00 | 22.50 | 7.50 | 0.60 | Higher-tier pricing once the prompt crosses 200k tokens. |
| `gemini-1.5-flash-1m` | Google Gemini 1.5 Flash | 1,000,000 | All prompt sizes | 0.35 | 1.05 | 0.44 | 0.035 | Prompt cache prices are scaled using the same ratios as Sonnet until Google publishes official figures. |

Updated on Oct 2025, prices are subject to changes.

## Retrieval Building Blocks

### Embedding

We price embeddings at **\$0.12 per 1M tokens**, matching Cohere's [embed v4](https://cohere.com/pricing). Note that we made the pessimistic assumption for RAG that the entire knowledge base would have to be reindexed at each update. Obviously, one of the advantage of building a RAG pipeline over a VectorDB is that updating one doc doesn't require to update everything!


### Reranking

Reranking uses Cohere's rerank-3.5 at **\$2.00 per 1,000 requests** (=\$0.002/query), also sourced from the same pricing page. The model is list-wise: the price does **not** scale with `rerank_top_k`, but it is bound by a **4,096 token** context window. We deduct the query length and fit as many retrieved chunks as possible per call, batching additional calls when `top_k × tokens_per_chunk` exceeds the remaining budget.

### Vector DB Base Cost

The Vector DB base cost defaults to **\$26/month**. This is an estimate that splits the difference between self-hosting (e.g. Weaviate on your own infrastructure can be cheaper, not counting maintenance) and managed services with minimum commitments (Pinecone begins around \$50/month, per [their pricing](https://www.pinecone.io/pricing/)). Override this value if you have concrete hosting numbers.

## Grep Baseline Assumptions

The grep fallback assumes **multiple failed attempts** before locating the right file. `GrepParams.avg_tries` controls how many prompts we pay for; the calculator bumps this to at least one and then repeats the prompt/answer loop for each failure, stacking both latency and LLM costs. This mirrors the reality that string search rarely hits on the first pass, especially across large codebases.
We also allow for the user to choose how many documents are retrieved and added to the context with each fail grep attempt, assuming a document is around 8 pages.
