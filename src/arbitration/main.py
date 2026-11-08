
from src.arbitration.graph import run_agents_graph


def main():
    graph = run_agents_graph()

    initial_state = {
        "original_question": "What is the capital of France?",
        "generated_output": "The capital of France is Berlin.",
        "critiques": [],
        "disagreements": [],
        "requires_adjudication": False,
        "verdict": None,
        "failed_critics": [],
    }

    result = graph.invoke(initial_state)

    for critique in result["critiques"]:
        print(f"\nDimension: {critique.dimension.value}")
        print(f"Score: {critique.score}")
        print(f"Confidence: {critique.confidence}")
        print(f"Issues: {critique.issues}")

    print("\n=== DISAGREEMENT DETECTION ===")
    print(f"Disagreements: {result['disagreements']}")
    print(f"Requires adjudication: {result['requires_adjudication']}")


if __name__ == "__main__":
    main()
