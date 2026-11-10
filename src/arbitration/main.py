
from langchain_openai import ChatOpenAI

from src.arbitration.graph import run_agents_graph


def main():
    question = input("Question: ").strip()

    if not question:
        print("Question cannot be empty.")
        return

    llm = ChatOpenAI(model="gpt-5-mini")
    response = llm.invoke(question)

    generated_output = str(response.content)

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
