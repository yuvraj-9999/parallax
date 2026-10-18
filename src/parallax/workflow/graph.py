from langgraph.graph import END, START, StateGraph

from parallax.workflow.nodes import (
    architect_node,
    builder_node,
    skeptic_node,
    verdict_node,
)
from parallax.workflow.state import ParallaxState


def build_graph():
    """Build and compile the parallax-evaluation graph"""

    graph = StateGraph(ParallaxState)

    graph.add_node("builder", builder_node)
    graph.add_node("architect", architect_node)
    graph.add_node("skeptic", skeptic_node)
    graph.add_node("verdict", verdict_node)

    graph.add_edge(START, "builder")

    graph.add_edge("builder", "architect")
    graph.add_edge("builder", "skeptic")

    graph.add_edge(["architect", "skeptic"], "verdict")

    graph.add_edge("verdict", END)

    return graph.compile()

    