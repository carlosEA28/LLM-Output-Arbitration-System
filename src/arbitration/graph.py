from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.arbitration.states import ArbitrationState
from src.nodes.critics import (
    accuracy_critic,
    logic_critic,
    completeness_critic,
)
from src.nodes.parse_input import parse_input


def run_agents_graph() -> CompiledStateGraph:
    graph = StateGraph(ArbitrationState)

    graph.add_node("parse_input", parse_input)
    graph.add_node("accuracy_critic", accuracy_critic)
    graph.add_node("logic_critic", logic_critic)
    graph.add_node("completeness_critic", completeness_critic)

    graph.add_edge(START, "parse_input")

    graph.add_edge("parse_input", "accuracy_critic")
    graph.add_edge("parse_input", "logic_critic")
    graph.add_edge("parse_input", "completeness_critic")

    graph.add_edge("accuracy_critic", END)
    graph.add_edge("logic_critic", END)
    graph.add_edge("completeness_critic", END)

    return graph.compile()
