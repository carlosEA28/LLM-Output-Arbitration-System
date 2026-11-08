from typing import Literal

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.arbitration.states import ArbitrationState
from src.nodes.critics import (
    accuracy_critic,
    logic_critic,
    completeness_critic,
)
from src.nodes.parse_input import parse_input
from src.nodes.collect_critiques import collect_critiques
from src.nodes.detect_disagreements import detect_disagreements


def adjudicator(state: ArbitrationState) -> dict:
    return {}


def synthesize_verdict(state: ArbitrationState) -> dict:
    return {}


def route_after_disagreements(
    state: ArbitrationState,
) -> Literal["adjudicator", "synthesize_verdict"]:
    return "adjudicator" if state["requires_adjudication"] else "synthesize_verdict"


def run_agents_graph() -> CompiledStateGraph:
    graph = StateGraph(ArbitrationState)

    graph.add_node("parse_input", parse_input)
    graph.add_node("accuracy_critic", accuracy_critic)
    graph.add_node("logic_critic", logic_critic)
    graph.add_node("completeness_critic", completeness_critic)
    graph.add_node("collect_critiques", collect_critiques)
    graph.add_node("detect_disagreements", detect_disagreements)
    graph.add_node("adjudicator", adjudicator)
    graph.add_node("synthesize_verdict", synthesize_verdict)

    graph.add_edge(START, "parse_input")

    graph.add_edge("parse_input", "accuracy_critic")
    graph.add_edge("parse_input", "logic_critic")
    graph.add_edge("parse_input", "completeness_critic")

    graph.add_edge(
        ["accuracy_critic", "logic_critic", "completeness_critic"],
        "collect_critiques",
    )
    graph.add_edge("collect_critiques", "detect_disagreements")
    graph.add_conditional_edges(
        "detect_disagreements",
        route_after_disagreements,
        {
            "adjudicator": "adjudicator",
            "synthesize_verdict": "synthesize_verdict",
        },
    )
    graph.add_edge("adjudicator", "synthesize_verdict")
    graph.add_edge("synthesize_verdict", END)

    return graph.compile()
