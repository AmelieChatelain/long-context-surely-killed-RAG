"""Main Streamlit application entry point."""

import streamlit as st

from src.ui.sidebar import render_sidebar
from src.ui.components import render_comparison_column, render_comparison_summary
from src.ui.styles import apply_custom_styles
from src.calculators.long_context import LongContextNoCache, LongContextWithCache
from src.calculators.rag import RAGCalculator
from src.calculators.grep import GrepCalculator


def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(page_title="RAG vs Long Context Pricing", layout="wide")
    
    # Apply custom styles
    apply_custom_styles()
    
    # App header
    st.title("RAG vs Long Context: Cost Calculator")
    
    st.info("""
    **Tokens per page reference:**
    - **Sparse (400)**: Code, tables, bullet lists
    - **Typical (600)**: Standard documents, research papers (~1 page = 600 tokens)
    - **Dense (800)**: Dense prose, novels, technical docs
    - **Images (1100)**: PDF Pages processed as images
    """)
    
    # Render sidebar and get parameters
    params = render_sidebar()
    
    # Initialize calculators
    calculators = [
        LongContextNoCache(),
        LongContextWithCache(),
        GrepCalculator(),
        RAGCalculator(),
    ]
    
    # Calculate results
    results = [calc.calculate(params) for calc in calculators]
    
    # Render comparison columns
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


if __name__ == "__main__":
    main()
