from src.arbitration.states import ArbitrationState
from src.nodes.critics import accuracy_critic


def main():
    state = ArbitrationState(
        original_question="What is the capital of France?",
        generated_output="The capital of France is Berlin."
    )
    llm = accuracy_critic(state)

    print(llm)

if __name__ == "__main__":
    main()
