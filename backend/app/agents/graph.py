from langgraph.graph import END, START, StateGraph

from app.agents.nodes.retriever_node import retriever_node
from app.agents.nodes.router_node import router_node
from app.agents.nodes.synthesizer_node import synthesizer_node
from app.agents.state import AgentState


def build_agent_graph():
    """Builds the multi-video agentic RAG workflow."""
    workflow = StateGraph(AgentState)

    workflow.add_node("router", router_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("synthesizer", synthesizer_node)

    workflow.add_edge(START, "router")
    workflow.add_edge("router", "retriever")
    workflow.add_edge("retriever", "synthesizer")
    workflow.add_edge("synthesizer", END)

    return workflow.compile()


# Compiled graph (singleton)
agent_graph = build_agent_graph()