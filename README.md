# 🐇 The Research Rabbit Hole: GenAI CoP Demonstrator

**A semantic graph exploration tool for the Open University GenAI Community of Practice.**

This application demonstrates how to retrieve structured "truth" data from the Semantic Scholar API and visualise the connections between academic papers. It serves as a counter-example to pure LLM text generation, showing how **Knowledge Graphs** can ground AI in verifiable citations.

## 🎯 What this app does

1. **Visualises impact:** Instead of just reading a paper, it visualises the "Citation Velocity"—showing which papers influenced a work (ancestors) and which papers were sparked by it (descendants).
2. **Demonstrates "RAG" concepts:** It highlights the difference between an LLM *hallucinating* a citation and an API *retrieving* a confirmed link.
3. **Hybrid Access:** It works for everyone (Free Mode) but unlocks higher speeds for power users (Authenticated Mode).

## 🚀 How to Run Locally

We use [uv](https://github.com/astral-sh/uv) for fast Python package management.

### Prerequisites

* Python 3.10 or higher
* `uv` installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Installation

1. **Clone the repository:**

    ```bash
    git clone <your-repo-url>
    cd semantic_graph_demo
    ```

2. **Sync dependencies:**
    `uv` will automatically create a virtual environment and install the exact libraries needed.

    ```bash
    uv sync
    ```

3. **Run the App:**

    ```bash
    uv run streamlit run app.py
    ```

## ☁️ How to Deploy (Streamlit Cloud)

1. Push this code to GitHub.
2. Log in to [share.streamlit.io](https://share.streamlit.io/).
3. Click **"New App"** and select this repository.
4. Streamlit will detect the `requirements.txt` file and install the libraries automatically.

## 🔑 API keys (optional)

This app is designed to be **zero‑config** for the free tier, but can also use a private API key for higher limits.

* **Default:** If no key is configured, the app uses the public Semantic Scholar API (lower rate limits, slower).
* **Local key (recommended):** Create a text file called `semantic_scholar_api_key.txt` in the project root (next to `app.py`) containing **only** your key. This file is already listed in `.gitignore`, so it will not be committed to Git.
* On start‑up the app will automatically load this file and use the key; there is no longer a UI field for entering keys.

## 📚 Tech Stack

* **Streamlit:** For the user interface.
* **Streamlit-Agraph:** For the interactive physics-based graph visualization.
* **Semantic Scholar API:** For the academic metadata.
* **UV:** For dependency management.
