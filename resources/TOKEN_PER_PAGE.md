Use these density buckets to map document types to approximate token counts when configuring the calculators.

## Density Buckets

- **Sparse (400 tokens/page)**: Code snippets, structured tables, and short bullet lists with ample whitespace.
- **Typical (600 tokens/page)**: Standard prose such as reports, technical blogs, or research papers around a single page.
- **Dense (800 tokens/page)**: Long-form narrative, tightly packed technical documentation, or novel-style paragraphs.
- **Images (1,100 tokens/page)**: Pages rendered from images (e.g., OCR’d PDFs). Calibrated against the token footprint reported for a 700×1,260 image in the [Qwen2.5-VL technical report](https://arxiv.org/abs/2502.13923).
