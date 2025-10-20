# RAG vs Long Context Pricing Calculator

Interactive Streamlit app to compare costs between RAG and long context approaches with enhanced UI and modular architecture.

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Features

- **Modular Architecture**: Clean separation of concerns with calculators, models, and UI components
- **Enhanced UI**: Aligned comparison metrics with visual hierarchy and highlighting
- **Input in pages** (not tokens): Select document density and page count
- **Four comparison modes**:
  - **Long Context (No Cache)**: Full KB sent every request (💀 expensive)
  - **Long Context (Cache)**: KB cached monthly, only query tokens charged per request
  - **Just Grep**: Multi-attempt file search baseline
  - **RAG w/ Vector DB**: Only retrieved chunks + query per request

## Document Density Options

- **Sparse (400 tok/page)**: Code, tables, bullet lists
- **Typical (600 tok/page)**: Standard docs, research papers (default)
- **Dense (800 tok/page)**: Dense prose, novels, technical documentation
- **Images (1100 tok/page)**: PDF Pages processed as images

## Architecture

```
src/
├── models/          # Data models and pricing configuration
├── calculators/     # Business logic for each approach
├── ui/             # UI components and styling
└── utils/          # Utility functions
```

## Deployment

The app is ready for deployment on Streamlit Cloud or any platform supporting Streamlit.
