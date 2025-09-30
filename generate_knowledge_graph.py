from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from pyvis.network import Network

from dotenv import load_dotenv
import os
import asyncio

# Load the .env file
load_dotenv()

# Get API key from environment
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found in .env. Please set it before running.")

# Initialize Gemini LLM with API key
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    google_api_key=api_key
)

graph_transformer = LLMGraphTransformer(llm=llm)


# Extract graph data from input text (via LLM)
async def extract_graph_data(text):
    documents = [Document(page_content=text)]
    graph_documents = await graph_transformer.aconvert_to_graph_documents(documents)
    return graph_documents


def visualize_graph(graph_documents):
    net = Network(
        height="1200px",
        width="100%",
        directed=True,
        notebook=False,
        bgcolor="#222222",
        font_color="white",
        filter_menu=True,
        cdn_resources='remote'
    )

    nodes = graph_documents[0].nodes
    relationships = graph_documents[0].relationships

    node_dict = {node.id: node for node in nodes}
    valid_edges = []
    valid_node_ids = set()

    for rel in relationships:
        if rel.source.id in node_dict and rel.target.id in node_dict:
            valid_edges.append(rel)
            valid_node_ids.update([rel.source.id, rel.target.id])

    for node_id in valid_node_ids:
        node = node_dict[node_id]
        try:
            net.add_node(node.id, label=node.id, title=node.type, group=node.type)
        except:
            continue

    for rel in valid_edges:
        try:
            net.add_edge(rel.source.id, rel.target.id, label=rel.type.lower())
        except:
            continue

    net.set_options("""
        {
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -100,
                    "centralGravity": 0.01,
                    "springLength": 200,
                    "springConstant": 0.08
                },
                "minVelocity": 0.75,
                "solver": "forceAtlas2Based"
            }
        }
    """)

    output_file = "knowledge_graph.html"
    try:
        net.save_graph(output_file)
        print(f"Graph saved to {os.path.abspath(output_file)}")
        return net
    except Exception as e:
        print(f"Error saving graph: {e}")
        return None


def generate_knowledge_graph(text):
    """Generate a graph using Gemini (LLM) from plain text."""
    graph_documents = asyncio.run(extract_graph_data(text))
    net = visualize_graph(graph_documents)
    return net


def generate_graph_from_triples(triples):
    """
    Generate a knowledge graph directly from subject-predicate-object triples.

    Args:
        triples (list of tuples): Each tuple is (subject, relation, object)

    Returns:
        pyvis.network.Network: The visualized network graph object
    """
    net = Network(
        height="1200px",
        width="100%",
        directed=True,
        bgcolor="#222222",
        font_color="white",
        filter_menu=True,
        cdn_resources='remote'
    )

    for subj, rel, obj in triples:
        # Add nodes
        net.add_node(subj, label=subj)
        net.add_node(obj, label=obj)
        # Add edge
        net.add_edge(subj, obj, label=rel)

    output_file = "knowledge_graph.html"
    try:
        net.save_graph(output_file)
        print(f"Graph saved to {os.path.abspath(output_file)}")
        return net
    except Exception as e:
        print(f"Error saving graph: {e}")
        return None
