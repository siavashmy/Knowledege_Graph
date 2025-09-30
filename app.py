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
            triples = json.load(uploaded_json)
            # Validate triples format
            if not all("subject" in t and "relation" in t and "object" in t for t in triples):
                st.error("❌ Invalid JSON format. Each entry must have 'subject', 'relation', and 'object'.")
            else:
                if st.sidebar.button("Generate Knowledge Graph"):
                    with st.spinner("Generating knowledge graph from triples..."):
                        net = generate_graph_from_triples([(t["subject"], t["relation"], t["object"]) for t in triples])
                        if net:
                            st.success("Knowledge graph generated successfully from triples!")
                            output_file = "knowledge_graph.html"
                            HtmlFile = open(output_file, 'r', encoding='utf-8')
                            components.html(HtmlFile.read(), height=1000)
                        else:
                            st.error("❌ Failed to generate the knowledge graph.")
        except Exception as e:
            st.error(f"❌ Failed to read JSON file: {e}")
