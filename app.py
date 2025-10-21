"""Main Streamlit application entry point."""

import streamlit as st

from src.calculators.grep import GrepCalculator
from src.calculators.long_context import LongContextNoCache, LongContextWithCache
from src.calculators.rag import RAGCalculator
from src.ui.components import (
    render_brand_credit,
    render_comparison_column,
    render_comparison_summary,
    render_reference_library,
)
from src.ui.sidebar import render_sidebar
from src.ui.styles import apply_custom_styles


def main():
    """Main application entry point."""
    st.set_page_config(page_title="Long Context Surely Killed RAG", layout="wide")

    apply_custom_styles()

    header_col, credit_col = st.columns([4, 1], gap="small")
    with header_col:
        st.title("Long Context Surely Killed RAG")
    with credit_col:
        render_brand_credit(twitter_url="https://twitter.com/AmelieTabatta")

    params = render_sidebar()

    st.caption("Tune your scenario, compare run costs, and browse assumptions in the Reference Library tab.")

    calculator_tab, reference_tab = st.tabs(["📊 Calculator", "📚 Reference Library"])

    with calculator_tab:
        calculators = [
            LongContextNoCache(),
            LongContextWithCache(),
            GrepCalculator(),
            RAGCalculator(),
        ]

        results = [calc.calculate(params) for calc in calculators]

        st.markdown("---")
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.markdown('<div class="scenario-header">❌ Long Context (No Cache)</div>', unsafe_allow_html=True)
            render_comparison_column(results[0])

        with col2:
            st.markdown('<div class="scenario-header">✅ Long Context (Cache)</div>', unsafe_allow_html=True)
            render_comparison_column(results[1])

        with col3:
            st.markdown('<div class="scenario-header">🤖 Just Grep</div>', unsafe_allow_html=True)
            render_comparison_column(results[2])

        with col4:
            st.markdown('<div class="scenario-header">🔍 RAG w/ Vector DB</div>', unsafe_allow_html=True)
            render_comparison_column(results[3])

        with col5:
            render_comparison_summary(results)

    with reference_tab:
        render_reference_library()


if __name__ == "__main__":
    main()
