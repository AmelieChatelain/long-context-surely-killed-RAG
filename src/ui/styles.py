"""Custom CSS styles for enhanced UI."""

CUSTOM_CSS = """
<style>
/* Fixed height metric containers for alignment */
.metric-container {
    min-height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.35rem;
    padding: 1rem;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    margin-bottom: 1rem;
    background: white;
}

.metric-title {
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #6c757d;
}

.metric-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #212529;
}

.metric-delta {
    font-size: 0.85rem;
    font-weight: 600;
    color: #0d6efd;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.metric-subtitle {
    font-size: 0.9rem;
    color: #495057;
}

.metric-summary {
    min-height: auto;
    margin-bottom: 0.75rem;
}

/* Highlighted metrics for key comparisons */
.metric-highlight {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.metric-highlight .metric-title,
.metric-highlight .metric-value,
.metric-highlight .metric-delta,
.metric-highlight .metric-subtitle {
    color: white;
}

/* Time metric highlighting */
.metric-time {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    border: none;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.metric-time .metric-title,
.metric-time .metric-value,
.metric-time .metric-delta,
.metric-time .metric-subtitle {
    color: white;
}

/* Column alignment */
.stColumn {
    display: flex;
    flex-direction: column;
}

/* Comparison summary styling */
.comparison-summary {
    background: #f8f9fa;
    border: 2px solid #dee2e6;
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.comparison-summary-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #343a40;
}

.comparison-best {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    color: white;
    border: none;
    box-shadow: 0 6px 12px rgba(17, 153, 142, 0.3);
}

.comparison-good {
    background: linear-gradient(135deg, #fce38a 0%, #f38181 100%);
    color: #333;
    border: none;
    box-shadow: 0 4px 8px rgba(252, 227, 138, 0.3);
}

.comparison-expensive {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    color: white;
    border: none;
    box-shadow: 0 4px 8px rgba(255, 107, 107, 0.3);
}

.comparison-best .metric-title,
.comparison-best .metric-value,
.comparison-best .metric-delta,
.comparison-best .metric-subtitle,
.comparison-good .metric-title,
.comparison-good .metric-value,
.comparison-good .metric-delta,
.comparison-good .metric-subtitle,
.comparison-expensive .metric-title,
.comparison-expensive .metric-value,
.comparison-expensive .metric-delta,
.comparison-expensive .metric-subtitle {
    color: inherit;
}

.comparison-best .metric-title,
.comparison-best .metric-value,
.comparison-best .metric-delta,
.comparison-best .metric-subtitle,
.comparison-expensive .metric-title,
.comparison-expensive .metric-value,
.comparison-expensive .metric-delta,
.comparison-expensive .metric-subtitle {
    color: white;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .metric-container {
        min-height: 100px;
        padding: 0.5rem;
    }
    
    .metric-highlight .metric-value,
    .metric-time .metric-value {
        font-size: 1.2em;
    }
}

/* Cost breakdown styling */
.cost-breakdown {
    background: #f8f9fa;
    border-left: 4px solid #007bff;
    padding: 1rem;
    margin-top: 0.5rem;
    border-radius: 0 8px 8px 0;
}

/* Scenario headers */
.scenario-header {
    font-size: 1.3em;
    font-weight: 600;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e9ecef;
}

/* Token display styling */
.token-display {
    font-family: 'Courier New', monospace;
    background: #f1f3f4;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.9em;
}
</style>
"""


def apply_custom_styles():
    """Apply custom CSS styles to the Streamlit app."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
