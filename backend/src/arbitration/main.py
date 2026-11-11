
from langchain_openai import ChatOpenAI

from src.arbitration.graph import run_agents_graph


def generate_response(question: str) -> str:
    llm = ChatOpenAI(model="gpt-5-mini")
    response = llm.invoke(question)
    return str(response.content)


def main():
    question = input("Question: ").strip()

    if not question:
        print("Question cannot be empty.")
        return

    generated_output = generate_response(question)

    print("\n=== GENERATED RESPONSE ===")
    print(generated_output)

    graph = run_agents_graph()

    result = graph.invoke({
        "original_question": question,
        "generated_output": generated_output,
        "critiques": [],
        "failed_critics": [],
    })

    print("\n=== CRITICS ===")
    for critique in result["critiques"]:
        print(
            f"{critique.dimension.value}: "
            f"{critique.score}/5"
        )

        for issue in critique.issues:
            print(
                f"  [{issue.severity.value}] "
                f"{issue.description}"
            )

    print("\n=== VERDICT ===")
    verdict = result["verdict"]

    if verdict:
        print(verdict.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
