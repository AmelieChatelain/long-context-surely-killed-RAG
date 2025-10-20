# LLM Pricing Methodology

The cost calculators convert tokens to "per million" units and then apply the
pricing schedule for the selected model. A pricing plan (`src/models/pricing.py`)
contains one or more tiers describing how much to charge for input, output, and
prompt-caching tokens.

## Calculation Steps
- Determine the total prompt tokens for the request.
- Select the tier whose `up_to_tokens` bound covers the prompt length (falling
  back to the final tier for very large prompts).
- Convert the token volume to millions (`tokens / 1_000_000`) and multiply it by
  the tier's per-million price for the relevant cost component.
- For scenarios that use Anthropic-style prompt caching, apply the tier's cache
  write/read prices and amortise them across updates and requests.

## Available Pricing Plans

| Plan | Provider | Context Window | Tier Condition | Input $ / M tokens | Output $ / M tokens | Cache Write $ / M tokens | Cache Read $ / M tokens | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `claude-3.5-sonnet-1m` | Anthropic Claude 3.5 Sonnet | 1,000,000 | ≤ 200k prompt tokens | 3.00 | 15.00 | 3.75 | 0.30 | Mirrors Anthropic's 1M context pricing for Claude 3.5 Sonnet. |
|  |  |  | > 200k prompt tokens | 6.00 | 22.50 | 7.50 | 0.60 | Higher-tier pricing once the prompt crosses 200k tokens. |
| `gemini-1.5-flash-1m` | Google Gemini 1.5 Flash | 1,000,000 | All prompt sizes | 0.35 | 1.05 | 0.44 | 0.035 | Prompt cache prices are scaled using the same ratios as Sonnet until Google publishes official figures. |

When a plan only provides a single tier, that tier is used for every prompt
length. Additional models can be added by defining a new `PricingPlan` with the
appropriate tier breakpoints.

## Sources
- Anthropic Claude 3.5 Sonnet pricing (July 2024): Anthropic documentation and prompt caching FAQ.
- Google Gemini 1.5 Flash pricing (June 2024): Google AI Studio pay-as-you-go pricing guide.
