# Import necessary modules
import streamlit as st
import streamlit.components.v1 as components  # For embedding custom HTML
from generate_knowledge_graph import generate_knowledge_graph, generate_graph_from_triples
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Check for API key
if not os.getenv("GOOGLE_API_KEY"):
    st.error("❌ GOOGLE_API_KEY not found. Please add it to your .env file before running.")
    st.stop()

# Set up Streamlit page configuration
st.set_page_config(
    page_icon=None, 
    layout="wide",  
    initial_sidebar_state="auto", 
    menu_items=None
)

# Set the title of the app
st.title("Knowledge Graph From Text or Triples")


def run_semantic_query(triples, focus_goal="EMI_YS"):
    """
    Simple semantic query over triples.

    Accepts either a list of dicts with keys subject/relation/object or a list of tuples.
    Returns three lists: degraded_goals (outgoing conflicts_with), weights that increase the focus,
    and weights that decrease the focus.
    """
    # normalize to tuples
    if len(triples) > 0 and isinstance(triples[0], dict):
        T = [(t["subject"], t["relation"], t["object"]) for t in triples]
    else:
        T = triples

    degraded_goals = sorted({o for (s, r, o) in T if s == focus_goal and r == "conflicts_with"})
    increased_by_weights = sorted({s for (s, r, o) in T if o == focus_goal and r == "weight_increases_goal"})
    decreased_by_weights = sorted({s for (s, r, o) in T if o == focus_goal and r == "weight_decreases_goal"})

    return degraded_goals, increased_by_weights, decreased_by_weights

# Sidebar section for user input method
st.sidebar.title("Input method")
input_method = st.sidebar.radio(
    "Choose an input method:",
    ["Upload txt", "Input text", "Upload triples (JSON)"],  
)

# Case 1: User chooses to upload a .txt file
if input_method == "Upload txt":
    uploaded_file = st.sidebar.file_uploader(label="Upload file", type=["txt"])
    
    if uploaded_file is not None:
        text = uploaded_file.read().decode("utf-8")
        if st.sidebar.button("Generate Knowledge Graph"):
            with st.spinner("Generating knowledge graph..."):
                net = generate_knowledge_graph(text)
                if net:
                    st.success("Knowledge graph generated successfully!")
                    output_file = "knowledge_graph.html"
                    HtmlFile = open(output_file, 'r', encoding='utf-8')
                    components.html(HtmlFile.read(), height=1000)
                else:
                    st.error("❌ Failed to generate the knowledge graph.")

# Case 2: User chooses to directly input text
elif input_method == "Input text":
    text = st.sidebar.text_area("Input text", height=300)

    if text:
        if st.sidebar.button("Generate Knowledge Graph"):
            with st.spinner("Generating knowledge graph..."):
                net = generate_knowledge_graph(text)
                if net:
                    st.success("Knowledge graph generated successfully!")
                    output_file = "knowledge_graph.html"
                    HtmlFile = open(output_file, 'r', encoding='utf-8')
                    components.html(HtmlFile.read(), height=1000)
                else:
                    st.error("❌ Failed to generate the knowledge graph.")

# Case 3: User uploads a JSON file with triples
elif input_method == "Upload triples (JSON)":
    uploaded_json = st.sidebar.file_uploader(label="Upload JSON file", type=["json"])

    if uploaded_json is not None:
        try:
            triples_payload = json.load(uploaded_json)

            # Accept both:
            # (A) [{"subject":..., "relation":..., "object":...}, ...]
            # (B) {"triples": [{"subject":..., "relation":..., "object":...}, ...]}
            if isinstance(triples_payload, dict) and "triples" in triples_payload:
                triples_list = triples_payload["triples"]
            elif isinstance(triples_payload, list):
                triples_list = triples_payload
            else:
                st.error("❌ Invalid JSON format. Expected a list of triples or an object with a 'triples' key.")
                st.stop()

            # Validate list entries
            if not all(isinstance(t, dict) and "subject" in t and "relation" in t and "object" in t for t in triples_list):
                st.error("❌ Invalid JSON format. Each entry must have 'subject', 'relation', and 'object'.")
                st.stop()

            # Semantic query example UI
            st.sidebar.subheader("Semantic query example")

            focus = st.sidebar.text_input("Focus goal id", value="EMI_YS")

            if st.sidebar.button("Run Semantic Query"):
                degraded, inc_w, dec_w = run_semantic_query(triples_list, focus_goal=focus)

                st.markdown(f"### Semantic query results for `{focus}`")
                st.write("**Goals predicted to degrade (conflicts_with):**", degraded if degraded else "None found")
                st.write("**Weights that increase this goal (weight_increases_goal):**", inc_w if inc_w else "None found")
                st.write("**Weights that decrease this goal (weight_decreases_goal):**", dec_w if dec_w else "None found")

            if st.sidebar.button("Generate Knowledge Graph"):
                with st.spinner("Generating knowledge graph from triples..."):
                    net = generate_graph_from_triples([(t["subject"], t["relation"], t["object"]) for t in triples_list])
                    if net:
                        st.success("Knowledge graph generated successfully from triples!")
                        output_file = "knowledge_graph.html"
                        HtmlFile = open(output_file, 'r', encoding='utf-8')
                        components.html(HtmlFile.read(), height=1000)
                    else:
                        st.error("❌ Failed to generate the knowledge graph.")
        except Exception as e:
            st.error(f"❌ Failed to read JSON file: {e}")
