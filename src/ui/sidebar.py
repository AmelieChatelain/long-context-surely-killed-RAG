"""Sidebar parameter input components."""

import streamlit as st
from ..models.parameters import (
    AppParams,
    KnowledgeBaseParams,
    QueryParams,
    RAGParams,
    GrepParams,
    PricingParams,
)
from ..models.pricing import pricing


def render_sidebar() -> AppParams:
    """Render sidebar inputs and return parameter object."""
    st.sidebar.header("Parameters")
    
    # Document density options
    density_options = {
        "Sparse (400 tok/page)": 400,
        "Typical (600 tok/page)": 600,
        "Dense (800 tok/page)": 800,
        "Images (1100 tok/page)": 1100,
    }
    
    density_choice = st.sidebar.selectbox(
        "Document Density", 
        options=list(density_options.keys()), 
        index=1
    )
    tokens_per_page = density_options[density_choice]
    
    # Knowledge base parameters
    kb_pages = st.sidebar.number_input(
        "Knowledge Base Size (pages)", 
        min_value=100, 
        max_value=10_000, 
        value=1_000, 
        step=100
    )
    
    kb_size = kb_pages * tokens_per_page
    st.sidebar.caption(f"= {kb_size:,} tokens")
    
    knowledge_updates_per_month = st.sidebar.number_input(
        "Knowledge Base Updates per Month", 
        min_value=0, 
        max_value=30, 
        value=4, 
        step=1
    )
    
    requests_per_day = st.sidebar.number_input(
        "Requests per Day", 
        min_value=100, 
        max_value=100_000, 
        value=1_000, 
        step=100
    )

    # Pricing selection
    st.sidebar.markdown("---")
    st.sidebar.markdown("**LLM Pricing Reference**")

    pricing_plans = pricing.available_plans()
    label_to_key = {plan.label: plan.key for plan in pricing_plans}
    labels = list(label_to_key.keys())
    default_label = pricing.get_plan().label
    default_index = labels.index(default_label) if default_label in labels else 0

    selected_label = st.sidebar.selectbox(
        "Choose the model pricing to use",
        options=labels,
        index=default_index,
        help="Controls which set of per-token prices feed the cost estimations.",
    )
    selected_plan = pricing.get_plan(label_to_key[selected_label])
    st.sidebar.caption(
        f"{selected_plan.provider} · {selected_plan.model_name} · {selected_plan.context_window:,} token context window"
    )
    
    # Grep baseline parameters
    st.sidebar.markdown("### Grep baseline")
    grep_tries = st.sidebar.number_input(
        "Avg tries to hit the right file", 
        min_value=1, 
        max_value=10, 
        value=4, 
        step=1
    )
    grep_num_docs_retrieved = st.sidebar.number_input(
        "Avg number of documents retrieved per grep call", 
        min_value=1, 
        max_value=10, 
        value=1, 
        step=1
    )
    
    # Fixed parameters display
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""**Input/Output Parameters**:

- **Query Size**: {QueryParams.query_tokens} tokens
- **Output Size**: {QueryParams.output_tokens} tokens
""")
    
    # RAG parameters
    st.sidebar.markdown("---")
    st.sidebar.markdown("**RAG Parameters**")
    
    top_k = st.sidebar.number_input(
        "Top-K Chunks Used per Query", 
        min_value=1, 
        max_value=20, 
        value=3, 
        step=1
    )
    
    # Vector DB costs
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Vector DB Costs**")
    
    vector_db_base_cost = st.sidebar.number_input(
        "Base Cost ($/month)", 
        min_value=0.0, 
        value=26.0, 
        step=1.0
    )
    
    # Create parameter objects
    knowledge_base = KnowledgeBaseParams(
        pages=kb_pages,
        tokens_per_page=tokens_per_page,
        updates_per_month=knowledge_updates_per_month
    )
    
    query = QueryParams()
    
    rag = RAGParams(
        top_k=top_k,
        vector_db_base_cost=vector_db_base_cost
    )
    
    grep = GrepParams(
        avg_tries=grep_tries,
        avg_docs_retrieved=grep_num_docs_retrieved
    )
    pricing_params = PricingParams(plan_key=selected_plan.key)
    
    return AppParams(
        knowledge_base=knowledge_base,
        query=query,
        rag=rag,
        grep=grep,
        pricing=pricing_params,
        requests_per_day=requests_per_day
    )
