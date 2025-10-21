# RAG vs Long Context Cost Calculator

A little Streamlit app for checking how much RAG vs long-context setups really cost. Stream it, tweak a few sliders, and see how rAg iS dEaD jUsT uSe LoNg cOnTeXt. The demo is available now at [Long Context Surely Killed RAG](https://long-context-surely-killed-rag.streamlit.app/).

## Get rolling

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Why bother

- Four head-to-head modes: long context (with/without cache), plain grep, and RAG with a vector DB
- Inputs in pages instead of raw tokens so you can think in documents, not math
- If you don't like my heuristics, get into the code! The latency heuristics are mostly in `src/utils/latency.py` and the pricing ones are in `src/models/pricing.py`.

## Want the nitty-gritty?

All the deeper notes, price tables, and design docs live in `./resources`.
