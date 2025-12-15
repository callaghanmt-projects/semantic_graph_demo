import streamlit as st
from semanticscholar import SemanticScholar
from streamlit_agraph import agraph, Node, Edge, Config

# --- Page Config ---
st.set_page_config(page_title="The Rabbit Hole 🐇", layout="wide")

# --- Session State Management (The "Memory") ---
# We need this so the Reset button can actually clear the text box
if 'search_query' not in st.session_state:
    st.session_state.search_query = ''
if 'graph_data' not in st.session_state:
    st.session_state.graph_data = None
if 'pending_search_query' not in st.session_state:
    st.session_state.pending_search_query = ''

def reset_app():
    """Callback to wipe everything clean"""
    st.session_state.search_query = ''
    st.session_state.graph_data = None
    st.session_state.pending_search_query = ''

st.title("🐇 The Research Rabbit Hole")

st.markdown(
    """
    1. Type the title of a paper and press Enter.
    2. Check the suggested match and tick **Confirm & Map**.
    3. Explore the graph: drag nodes to rearrange, or click a node to
       see its bibliographic details and reuse it as a new starting point.
    """
)

# --- Rubric & Intro ---
with st.expander("📚 About the Data: What is Semantic Scholar?", expanded=False):
    st.markdown("""
    This app pulls data from **[Semantic Scholar](https://www.semanticscholar.org)**, a free, AI-powered research tool developed by the **Allen Institute for AI**.
    
    Unlike Google Scholar, Semantic Scholar uses **Natural Language Processing (NLP)** to:
    * Understand the *context* of citations.
    * Identify influential papers based on "Citation Velocity".
    """)

# --- Sidebar: Setup ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Semantic Scholar API Key", type="password", help="Leave blank for free tier.")
    
    if api_key:
        sch = SemanticScholar(api_key=api_key)
        st.success("Validated: Pro Mode Active 🚀")
    else:
        sch = SemanticScholar()
        st.info("Free Mode Active (Rate Limited) 🐢")

    st.divider()
    st.subheader("Graph limits")
    max_refs = st.slider("Max References (Backward)", 1, 20, 5)
    max_cites = st.slider("Max Citations (Forward)", 1, 20, 5)

# --- Helper Functions ---
def clean_title(title, length=30):
    if not title: return "Unknown Title"
    return title[:length] + "..." if len(title) > length else title

@st.cache_data(show_spinner=False)
def build_graph(paper_id, _client, limit_refs, limit_cites):
    details = _client.get_paper(
        paper_id, 
        fields=['title', 'authors', 'year', 'references.title', 'references.paperId', 'citations.title', 'citations.paperId']
    )
    nodes = []
    edges = []
    
    # Central Node
    nodes.append(Node(id=details.paperId, label=clean_title(details.title), size=25, color="#FF4B4B", title=details.title))

    # References (Blue)
    if details.references:
        for ref in details.references[:limit_refs]:
            if ref.paperId and ref.title:
                nodes.append(Node(id=ref.paperId, label=clean_title(ref.title), size=15, color="#1E88E5"))
                edges.append(Edge(source=ref.paperId, target=details.paperId, label="influenced", color="#BDC3C7"))

    # Citations (Green)
    if details.citations:
        for cite in details.citations[:limit_cites]:
            if cite.paperId and cite.title:
                nodes.append(Node(id=cite.paperId, label=clean_title(cite.title), size=15, color="#43A047"))
                edges.append(Edge(source=details.paperId, target=cite.paperId, label="sparked", color="#BDC3C7"))       
    return nodes, edges


def render_paper_metadata(paper, header="📄 Selected paper"):
    """Display basic bibliographic details for a Semantic Scholar paper object."""
    if not paper:
        return

    authors = []
    for author in getattr(paper, "authors", []) or []:
        name = getattr(author, "name", None)
        if not name and isinstance(author, dict):
            name = author.get("name")
        if name:
            authors.append(name)

    authors_str = ", ".join(authors) if authors else "Unknown authors"
    year = getattr(paper, "year", None) or "n.d."

    st.subheader(header)
    st.markdown(f"**{getattr(paper, 'title', 'Untitled')}**")
    st.caption(f"{authors_str} ({year})")

    venue = getattr(paper, "venue", None)
    if venue:
        st.write(f"Venue: {venue}")

    url = getattr(paper, "url", None)
    if url:
        st.write(f"[View on Semantic Scholar]({url})")

    abstract = getattr(paper, "abstract", None)
    if abstract:
        snippet = abstract[:600] + ("..." if len(abstract) > 600 else "")
        st.markdown(snippet)

# --- Main Interface ---

# If a new search query was staged by a button click, apply it
# before instantiating the text input bound to this key.
if st.session_state.pending_search_query:
    st.session_state.search_query = st.session_state.pending_search_query
    st.session_state.pending_search_query = ''

# Layout: Search Bar (3 cols) | Reset Button (1 col)
col_search, col_reset = st.columns([4, 1])

with col_search:
    # We bind this input to 'st.session_state.search_query'
    query = st.text_input(
        "Enter a paper title to jump in:", 
        key="search_query",
        placeholder="e.g. Attention is All You Need"
    )

with col_reset:
    # Use some vertical spacing to align the button with the text box
    st.markdown("##") 
    st.button("🔄 Reset App", on_click=reset_app, type="secondary", use_container_width=True)

# --- Logic Flow ---
if query:
    # 1. Search Step
    with st.spinner("Searching..."):
        try:
            results = sch.search_paper(query, limit=1)
        except Exception as e:
            st.error(f"Search failed: {e}")
            results = []

    if results:
        candidate = results[0]
        
        # 2. Confirmation Step
        st.info("### 🔎 Is this the paper?")
        
        col_meta, col_confirm = st.columns([3, 1])
        with col_meta:
            st.markdown(f"**{candidate.title}** ({candidate.year})")
            if candidate.abstract:
                st.caption(f"{candidate.abstract[:300]}...")
        
        with col_confirm:
            # We use a unique key based on the query so the checkbox resets if the query changes
            confirm = st.checkbox("✅ Confirm & Map", key=f"confirm_{query}")

        # 3. Graph Generation Step
        if confirm:
            with st.spinner("Tracing citation network..."):
                try:
                    nodes, edges = build_graph(candidate.paperId, sch, max_refs, max_cites)

                    # Use a hierarchical left-to-right layout with larger spacing
                    # and physics disabled so dragged node positions "stick".
                    config = Config(
                        width=None,
                        height=600,
                        directed=True,
                        physics=False,
                        hierarchical=True,
                        direction="LR",
                        levelSeparation=250,
                        nodeSpacing=200,
                        treeSpacing=300,
                    )

                    st.success(f"Graph generated: {len(nodes)} papers found.")
                    selected = agraph(nodes=nodes, edges=edges, config=config)

                    # If the user clicks a node in the graph, fetch and show
                    # bibliographic details and offer to reuse that paper.
                    if selected:
                        # The component may return an id or a small dict; handle both.
                        paper_id = None
                        if isinstance(selected, dict):
                            paper_id = selected.get("id") or selected.get("paperId")
                        elif isinstance(selected, (str, int)):
                            paper_id = str(selected)

                        if paper_id:
                            with st.spinner("Fetching paper details..."):
                                try:
                                    paper = sch.get_paper(
                                        paper_id,
                                        fields=[
                                            "title",
                                            "authors",
                                            "year",
                                            "venue",
                                            "url",
                                            "abstract",
                                        ],
                                    )
                                except Exception as e:
                                    st.error(f"Failed to fetch paper details: {e}")
                                    paper = None

                            if paper:
                                render_paper_metadata(paper)
                                if st.button(
                                    "🔍 Use this paper as search seed",
                                    key=f"use_seed_{paper.paperId}",
                                ):
                                    # Stage the new query so it is applied
                                    # on the next run *before* the text
                                    # input widget is instantiated.
                                    st.session_state.pending_search_query = paper.title or ""
                                    st.info(
                                        "Search updated with selected paper title. "
                                        "You can now confirm & remap from the top section."
                                    )
                        else:
                            st.warning("Could not determine the selected paper from the graph click.")
                    
                except Exception as e:
                    st.error(f"Graph error: {e}")

    else:
        st.warning("No papers found.")

# --- Footer ---
if query:
    st.divider()
    st.markdown("### 🧠 Why this matters")
    st.info("By verifying the paper first, we ensure the 'seed node' is ground truth, preventing the AI from hallucinating the starting point.")

    st.markdown("### 🔍 Graph key")
    st.markdown(
        "- **Red node**: Selected seed paper  \n"
        "- **Blue nodes**: Papers this work cites (ancestors)  \n"
        "- **Green nodes**: Papers that cite this work (descendants)"
    )